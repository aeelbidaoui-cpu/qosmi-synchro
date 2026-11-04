#!/usr/bin/env python3
"""Qosmi : mise à jour automatique du site Shopify à partir de la liste SoleLuna (toutes les heures, à h+17).

Décision d'Amine du 04/11/2026 : Qosmi vend uniquement SoleLuna.

À chaque passage :
  1. relit la liste du compte wholesale-perfumes.eu (telecharger.py PERFUMEWHOLESALE) ;
  2. recalcule les fiches et leurs formats (site_variantes.preparer) et les prix (règle de config/site.json) ;
  3. lit l'état réel de la boutique (fiches brouillon + actives, formats, prix, coûts, stocks) ;
  4. n'envoie que les différences :
       - stock d'un format changé → nouveau stock ;
       - prix ou coût d'un format changé → nouveau prix / coût ;
       - nouveau format d'un parfum déjà en ligne → la fiche est complétée ;
       - nouveau parfum → nouvelle fiche, en BROUILLON tant que le site n'est pas ouvert (config/site.json « statut_nouvelles_fiches ») ;
       - format qui n'est plus dans la liste → stock 0 (jamais supprimé).
Garde-fous : un seul passage à la fois ; liste illisible ou anormalement courte → rien n'est touché.
Journal : rapports/site_synchro.log (une ligne par passage) et rapports/site_synchro_dernier.txt (détail).

  python3 scripts/site_synchro.py              → un passage (c'est ce que lance la tâche horaire)
  python3 scripts/site_synchro.py --essai      → calcule et affiche les changements, n'envoie RIEN
  python3 scripts/site_synchro.py --retirer-depot → archive sur Shopify les fiches du stock du dépôt (une fois)
"""
import collections, fcntl, json, os, subprocess, sys, time, urllib.request, uuid

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import site_soleluna as sl  # noqa: E402
import site_variantes as sv  # noqa: E402

JOURNAL = os.path.join(sl.RAPPORTS, "site_synchro.log")
VERROU = os.path.join(sl.BASE, ".site_synchro.lock")
A_TRADUIRE = os.path.join(sl.BASE, ".site_synchro_a_traduire")
TRADUIT = os.path.join(sl.BASE, ".site_synchro_traduit")

M_PRIX = """mutation call($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants { id } userErrors { field message } } }"""
M_STOCK = """mutation($input: InventorySetQuantitiesInput!, $cle: String!) {
  inventorySetQuantities(input: $input) @idempotent(key: $cle) {
    inventoryAdjustmentGroup { id } userErrors { code field message } } }"""
Q_ETAT = """{ products(query: "status:active OR status:draft") { edges { node { id handle status tags
  variants { edges { node { id sku price inventoryQuantity selectedOptions { name value }
    inventoryItem { id unitCost { amount } } } } } } } } }"""


def ligne_journal(texte):
    os.makedirs(sl.RAPPORTS, exist_ok=True)
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M  ") + texte + "\n")
    print(texte, flush=True)


def reglage(cle, defaut):
    try:
        with open(sl.SITE, encoding="utf-8") as f:
            return json.load(f).get(cle, defaut)
    except FileNotFoundError:
        return defaut


def etat_boutique(s, sc):
    d = s.gql("""mutation($q: String!) { bulkOperationRunQuery(query: $q) { bulkOperation { id } userErrors { message } } }""",
              {"q": Q_ETAT})["bulkOperationRunQuery"]
    if d["userErrors"]:
        raise RuntimeError("lecture de la boutique refusée : %s" % d["userErrors"])
    op = d["bulkOperation"]["id"]
    while True:  # attente silencieuse (le journal horaire reste lisible)
        b = s.gql("query($id: ID!) { bulkOperation(id: $id) { status errorCode url } }", {"id": op})["bulkOperation"]
        if b["status"] in ("COMPLETED", "FAILED", "CANCELED", "EXPIRED"):
            break
        time.sleep(10)
    if b["status"] != "COMPLETED":
        raise RuntimeError("lecture de la boutique impossible (%s)" % b.get("errorCode"))
    produits, variantes = {}, {}
    if b.get("url"):
        os.makedirs(sl.RAPPORTS, exist_ok=True)
        chemin = os.path.join(sl.RAPPORTS, "site_synchro_etat.jsonl")
        urllib.request.urlretrieve(b["url"], chemin)
        for l in open(chemin, encoding="utf-8"):
            x = json.loads(l)
            if "__parentId" in x:
                x["produit"] = x.pop("__parentId")
                variantes[x["id"]] = x
            else:
                x["variantes"] = []
                produits[x["id"]] = x
        for v in variantes.values():
            if v["produit"] in produits:
                produits[v["produit"]]["variantes"].append(v)
    return produits, variantes


def entree_complete(p, existante, lieu_id, statut):
    """productSet d'une fiche existante : formats de la liste + formats disparus (gardés, stock 0), ids conservés."""
    e = sv.entree(p, lieu_id, {"id": existante["id"]})
    inp = e["input"]
    inp["status"] = existante["status"]
    inp.pop("handle", None)  # l'adresse de la fiche ne change pas
    par_sku = {v["sku"]: v for v in existante["variantes"] if v.get("sku")}
    cibles = {v["sku"] for v in p["variantes"]}
    for var in inp["variants"]:
        ancien = par_sku.get(var["sku"])
        if ancien:
            var["id"] = ancien["id"]
            var.pop("inventoryQuantities", None)  # le stock passe par inventorySetQuantities
    noms = [o["name"] for o in inp["productOptions"]]
    for sku, v in par_sku.items():
        if sku in cibles:
            continue
        ov = {o["name"]: o["value"] for o in v.get("selectedOptions", [])}
        if any(n not in noms for n in ov):
            continue  # ancien format sans correspondance d'option
        valeurs = []
        for o in inp["productOptions"]:
            val = ov.get(o["name"]) or "—"
            if val not in [x["name"] for x in o["values"]]:
                o["values"].append({"name": val})
            valeurs.append({"optionName": o["name"], "name": val})
        inp["variants"].append({"id": v["id"], "optionValues": valeurs, "price": v["price"], "sku": sku})
    return e


AGENT = "Mozilla/5.0 (compatible; QosmiSynchro/1.0)"


def listes_serveur():
    """Sur le serveur : liste SoleLuna du compte (SOLELUNA_EMAIL / SOLELUNA_PASSWORD) et, si WF_URL est
    renseigné, liste Wholesale-Fragrances pour les photos des nouveaux produits."""
    import http.cookiejar, ssl, urllib.parse
    base = os.environ.get("SOLELUNA_SITE", "https://www.wholesale-perfumes.eu")
    ouvreur = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
                                          urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    ouvreur.addheaders = [("User-Agent", AGENT)]
    ouvreur.open(base + "/login/", timeout=60).read()
    corps = urllib.parse.urlencode({"login": os.environ["SOLELUNA_EMAIL"], "password": os.environ["SOLELUNA_PASSWORD"],
                                    "Submit": "Log in"}).encode()
    page = ouvreur.open(urllib.request.Request(base + "/login/", data=corps), timeout=60).read().decode("utf-8", "replace")
    if "/logout/" not in page:
        email, mdp = os.environ.get("SOLELUNA_EMAIL", ""), os.environ.get("SOLELUNA_PASSWORD", "")
        indices = []
        if not email or "@" not in email:
            indices.append("secret SOLELUNA_EMAIL vide ou sans @")
        if not mdp:
            indices.append("secret SOLELUNA_PASSWORD vide")
        if email != email.strip() or mdp != mdp.strip():
            indices.append("espace ou retour à la ligne en trop dans un secret")
        bas = page.lower()
        if "captcha" in bas or "cf-challenge" in bas or "challenge-platform" in bas:
            indices.append("le site demande une vérification anti-robot depuis le serveur")
        raise RuntimeError("connexion refusée par wholesale-perfumes.eu (%s)" % (
            " ; ".join(indices) or "identifiants refusés : vérifier les secrets SOLELUNA_EMAIL et SOLELUNA_PASSWORD"))
    with ouvreur.open(base + "/export_pricelist/csv", timeout=180) as rep:
        donnees = rep.read()
    if not donnees.decode("utf-8-sig", "replace").lstrip().startswith('"id";"BRAND"'):
        raise RuntimeError("le site n'a pas renvoyé la liste attendue (format changé ?)")
    if donnees.count(b"\r") + donnees.count(b"\n") < 100:
        raise RuntimeError("liste anormalement courte")
    os.makedirs(sl.BASE, exist_ok=True)
    with open(sl.SOURCE, "wb") as f:
        f.write(donnees)
    url_wf = os.environ.get("WF_URL")
    if url_wf:
        dossier = os.path.join(sl.RACINE, "stocklists", "WHOLESALEFRAGRANCES")
        chemin = os.path.join(dossier, "WHOLESALEFRAGRANCES_serveur.csv")
        if not os.path.exists(chemin) or time.time() - os.path.getmtime(chemin) > 20 * 3600:
            try:
                req = urllib.request.Request(url_wf, headers={"User-Agent": AGENT})
                with urllib.request.urlopen(req, timeout=120) as r:
                    wf = r.read()
                if len(wf) > 10000 and not wf.lstrip()[:15].lower().startswith((b"<!doctype", b"<html")):
                    os.makedirs(dossier, exist_ok=True)
                    with open(chemin, "wb") as f:
                        f.write(wf)
            except Exception as e:  # sans photos à jour, les nouveaux produits arrivent sans photo : pas bloquant
                ligne_journal("  liste photos non lue (%s)" % str(e)[:120])


def synchro(essai=False):
    from shopify_api import Shopify
    import site_charger as sc
    debut = time.time()
    if os.environ.get("SOLELUNA_EMAIL"):  # serveur : accès dans les « Secrets » du dépôt
        try:
            listes_serveur()
        except Exception as e:
            ligne_journal("ÉCHEC liste SoleLuna — rien n'est modifié sur le site : %s" % str(e)[:300])
            return 1
    else:  # Mac : accès dans le Trousseau
        r = subprocess.run([sys.executable, os.path.join(ICI, "telecharger.py"), "PERFUMEWHOLESALE"],
                           capture_output=True, text=True, cwd=ICI, env={**os.environ, "DEWAY_LISTE_SEULE": "1"})
        if r.returncode != 0:
            ligne_journal("ÉCHEC liste SoleLuna — rien n'est modifié sur le site : %s" % (r.stdout + r.stderr).strip()[-300:])
            return 1
    produits = sv.preparer(exemples=False)
    statut_nouv = reglage("statut_nouvelles_fiches", "DRAFT")
    s = Shopify()
    lieu_id = sc.lieu(s)
    boutique, variantes = etat_boutique(s, sc)
    vs_qs = {v["sku"]: v for v in variantes.values() if (v.get("sku") or "").startswith("QS-")}
    n_cible = sum(len(p["variantes"]) for p in produits)
    if vs_qs and n_cible < 0.5 * len(vs_qs):
        ligne_journal("ARRÊT : liste anormalement courte (%d formats contre %d sur le site) — rien n'est modifié." % (n_cible, len(vs_qs)))
        return 1
    handles = {p["handle"] for p in boutique.values()}
    structurels, nouveaux, prix, stocks, vus = [], [], collections.defaultdict(list), [], set()
    for p in produits:
        ids = [vs_qs[v["sku"]]["produit"] for v in p["variantes"] if v["sku"] in vs_qs]
        if not ids:  # nouveau parfum
            h, i = p["handle"], 2
            while p["handle"] in handles:
                p["handle"] = "%s-%d" % (h, i)
                i += 1
            handles.add(p["handle"])
            e = sv.entree(p, lieu_id, {"handle": p["handle"]})
            e["input"]["status"] = statut_nouv
            nouveaux.append(e)
            continue
        pid = collections.Counter(ids).most_common(1)[0][0]
        existante = boutique[pid]
        skus_fiche = {v["sku"] for v in existante["variantes"]}
        for v in p["variantes"]:
            vus.add(v["sku"])
        if any(v["sku"] not in skus_fiche for v in p["variantes"]):  # nouveau format
            structurels.append(entree_complete(p, existante, lieu_id, statut_nouv))
        for v in p["variantes"]:
            a = vs_qs.get(v["sku"])
            if not a or a["produit"] != pid:
                continue
            maj = {}
            if abs(float(a["price"]) - float(v["prix"])) > 0.004:
                maj["price"] = v["prix"]
            cout = ((a.get("inventoryItem") or {}).get("unitCost") or {}).get("amount")
            if cout is None or abs(float(cout) - float(v["cout_ht"])) > 0.004:
                maj["inventoryItem"] = {"cost": v["cout_ht"]}
            if maj:
                prix[pid].append({"id": a["id"], **maj})
            if int(a.get("inventoryQuantity") or 0) != int(v["stock"]):
                stocks.append((a["inventoryItem"]["id"], int(v["stock"])))
    disparus = [(v["inventoryItem"]["id"], 0) for sku, v in vs_qs.items()
                if sku not in vus and int(v.get("inventoryQuantity") or 0) != 0]
    stocks += disparus
    n_prix = sum(len(x) for x in prix.values())
    resume = ("%d formats suivis · %d stocks changés (dont %d sortis de la liste) · %d prix/coûts changés · "
              "%d fiches complétées · %d nouvelles fiches" % (n_cible, len(stocks), len(disparus), n_prix,
                                                               len(structurels), len(nouveaux)))
    if essai:
        print("ESSAI (rien n'est envoyé) : " + resume)
        for e in nouveaux[:5]:
            print("  nouvelle fiche :", e["input"]["title"])
        return 0
    erreurs = 0
    # 1. fiches nouvelles et complétées
    for nom, lot in (("nouvelles", nouveaux), ("completees", structurels)):
        if not lot:
            continue
        if len(lot) > 40:
            chemin = os.path.join(sl.RAPPORTS, "site_synchro_%s.jsonl" % nom)
            with open(chemin, "w", encoding="utf-8") as f:
                for e in lot:
                    f.write(json.dumps(e, ensure_ascii=False) + "\n")
            b = sc.attendre(s, sc.lancer_mutation(s, sc.M_SET, chemin, "synchro-" + nom), "synchro-" + nom)
            erreurs += sum(1 for l in sc.bilan_resultats(b, "synchro-" + nom)
                           if l.get("errors") or ((l.get("data") or {}).get("productSet") or {}).get("userErrors"))
        else:
            for e in lot:
                d = s.gql(sc.M_SET, e)["productSet"]
                if d["userErrors"]:
                    erreurs += 1
                    ligne_journal("  erreur fiche %s : %s" % (e["input"].get("title"), json.dumps(d["userErrors"], ensure_ascii=False)[:200]))
    # traductions NL des nouvelles fiches : au plus deux fois par jour (c'est une grosse opération)
    if nouveaux or structurels:
        open(A_TRADUIRE, "w").close()
    if os.path.exists(A_TRADUIRE) and time.time() - os.path.getmtime(A_TRADUIRE) > 0 and (
            not os.path.exists(TRADUIT) or time.time() - os.path.getmtime(TRADUIT) > 12 * 3600):
        try:
            sv.traduire(s, sc, produits)
            open(TRADUIT, "w").close()
            os.replace(A_TRADUIRE, A_TRADUIRE + ".fait")
        except Exception as ex:
            ligne_journal("  traductions NL à refaire au prochain passage (%s)" % str(ex)[:150])
    # 2. prix et coûts
    if n_prix > 300:
        chemin = os.path.join(sl.RAPPORTS, "site_synchro_prix.jsonl")
        with open(chemin, "w", encoding="utf-8") as f:
            for pid, vs in prix.items():
                f.write(json.dumps({"productId": pid, "variants": vs}) + "\n")
        b = sc.attendre(s, sc.lancer_mutation(s, M_PRIX, chemin, "synchro-prix"), "synchro-prix")
        sc.bilan_resultats(b, "synchro-prix")
    else:
        for pid, vs in prix.items():
            d = s.gql(M_PRIX, {"productId": pid, "variants": vs})["productVariantsBulkUpdate"]
            if d["userErrors"]:
                erreurs += 1
                ligne_journal("  erreur prix %s : %s" % (pid, json.dumps(d["userErrors"], ensure_ascii=False)[:200]))
    # 3. stocks (par paquets de 250)
    for i in range(0, len(stocks), 250):
        paquet = stocks[i:i + 250]
        d = s.gql(M_STOCK, {"cle": str(uuid.uuid4()), "input": {
            "name": "available", "reason": "correction",
            "referenceDocumentUri": "qosmi://synchro/%s" % time.strftime("%Y-%m-%dT%H:%M"),
            "quantities": [{"inventoryItemId": it, "locationId": lieu_id, "quantity": q, "changeFromQuantity": None}
                           for it, q in paquet]}})["inventorySetQuantities"]
        if d["userErrors"]:
            erreurs += 1
            ligne_journal("  erreur stocks : %s" % json.dumps(d["userErrors"], ensure_ascii=False)[:300])
    ligne_journal("OK %s · %d erreur(s) · %d s" % (resume, erreurs, time.time() - debut))
    return 0 if not erreurs else 1


def retirer_depot():
    """Archive les fiches du stock du dépôt (étiquette « en-stock-belgique ») : Qosmi vend uniquement SoleLuna."""
    from shopify_api import Shopify
    import site_charger as sc
    s = Shopify()
    boutique, _ = etat_boutique(s, sc)
    cibles = [p["id"] for p in boutique.values() if "en-stock-belgique" in (p.get("tags") or [])]
    ligne_journal("Fiches du dépôt à archiver : %d" % len(cibles))
    ok = 0
    for pid in cibles:
        d = s.gql(sc.M_MAJ, {"product": {"id": pid, "status": "ARCHIVED"}})["productUpdate"]
        ok += not d["userErrors"]
    if cibles:
        with open(os.path.join(sl.RAPPORTS, "site_archivage_depot_ids_%s.txt" % time.strftime("%Y-%m-%d_%Hh%M")), "w") as f:
            f.write("\n".join(cibles) + "\n")
    ligne_journal("Fiches du dépôt archivées : %d / %d (récupérables : Produits → Archivés)" % (ok, len(cibles)))


def main():
    os.makedirs(sl.BASE, exist_ok=True)
    with open(VERROU, "w") as verrou:
        try:
            fcntl.flock(verrou, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            ligne_journal("Passage précédent encore en cours — celui-ci est sauté.")
            return 0
        if "--retirer-depot" in sys.argv:
            retirer_depot()
            return 0
        try:
            return synchro(essai="--essai" in sys.argv)
        except Exception as e:
            ligne_journal("ÉCHEC %s : %s" % (type(e).__name__, str(e)[:300]))
            return 1


if __name__ == "__main__":
    sys.exit(main())
