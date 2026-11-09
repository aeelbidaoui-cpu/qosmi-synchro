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

M_PRIX = """mutation call($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants { id } userErrors { field message } } }"""
M_STOCK = """mutation($input: InventorySetQuantitiesInput!, $cle: String!) {
  inventorySetQuantities(input: $input) @idempotent(key: $cle) {
    inventoryAdjustmentGroup { id } userErrors { code field message } } }"""
Q_ETAT = """{ products(query: "status:active OR status:draft") { edges { node { id handle status tags featuredMedia { id }
  dujour: metafield(namespace: "qosmi", key: "du_jour") { value }
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
    pris = {tuple((x["optionName"], x["name"]) for x in var["optionValues"]) for var in inp["variants"]}
    for sku, v in par_sku.items():
        if sku in cibles:
            continue
        ov = {o["name"]: o["value"] for o in v.get("selectedOptions", [])}
        if any(n not in noms for n in ov):
            continue  # ancien format sans correspondance d'option
        if tuple((o["name"], ov.get(o["name"]) or "—") for o in inp["productOptions"]) in pris:
            continue  # même format repris par un nouveau code : l'ancien est remplacé
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


Q_OPTIONS = "id options { id name optionValues { id name } }"
Q_TRADUISIBLES = """query($ids: [ID!]!) { translatableResourcesByIds(first: 250, resourceIds: $ids) {
  nodes { resourceId translatableContent { key value digest } } } }"""


def traduire_fiches(s, sc, fiches):
    """Traductions NL d'une liste de fiches : (« handle » ou « id », valeur, produit préparé)."""
    n = 0
    for genre, valeur, p in fiches:
        if genre == "handle":
            d = s.gql("query($h: String!) { productByIdentifier(identifier: {handle: $h}) { %s } }" % Q_OPTIONS,
                      {"h": valeur}).get("productByIdentifier")
        else:
            d = s.gql("query($id: ID!) { product(id: $id) { %s } }" % Q_OPTIONS, {"id": valeur}).get("product")
        if not d:
            continue
        ids = [d["id"]] + [o["id"] for o in d["options"]] + [v["id"] for o in d["options"] for v in o["optionValues"]]
        for nd in s.gql(Q_TRADUISIBLES, {"ids": ids})["translatableResourcesByIds"]["nodes"]:
            c = {k["key"]: k for k in nd["translatableContent"]}
            t = []
            if nd["resourceId"] == d["id"]:
                for cle, val in (("title", p["titre_nl"]), ("body_html", p["desc_nl"]), ("product_type", p["type_nl"])):
                    if cle in c and val:
                        t.append({"locale": "nl", "key": cle, "value": val, "translatableContentDigest": c[cle]["digest"]})
            elif "name" in c:
                v = c["name"]["value"]
                nl = dict(sv.TRAD_OPTIONS).get(v) if "/ProductOption/" in nd["resourceId"] else sv.valeur_nl(v)
                if nl and nl != v:
                    t.append({"locale": "nl", "key": "name", "value": nl, "translatableContentDigest": c["name"]["digest"]})
            if t:
                s.gql(sc.M_TRAD, {"resourceId": nd["resourceId"], "translations": t})
                n += len(t)
    return n


def selection():
    """config/selection.json : marques et catégories affichées sur le site (le reste reste en brouillon)."""
    chemin = os.path.join(os.path.dirname(sl.SITE), "selection.json")
    if not os.path.exists(chemin):
        return None
    d = json.load(open(chemin, encoding="utf-8"))
    global INTERDITS
    INTERDITS = {e.lstrip("0") for e in d.get("ean_interdits", {})}
    return {m.lower() for m in d.get("marques", [])}, set(d.get("categories", []))


INTERDITS = set()  # 09/11/2026 : EAN aux ingrédients interdits dans l'UE (Lilial, D5) : jamais affichés


ARABES, CONC = None, None


def visible(p, sel):
    """Affichée si la marque et la catégorie sont dans la sélection ET si le parfum a une bonne photo
    (demande d'Amine du 07/11/2026 : pas de photo ou photo de mauvaise qualité = pas affiché).
    Parfums arabes : affichés comme les autres depuis le 08/11/2026 21 h 27 (au moins 5 € net, même plus cher que le concurrent)."""
    global ARABES, CONC
    if not p.get("photo_ok", True):
        return False
    if any(str(v.get("ean", "")).lstrip("0") in INTERDITS for v in p.get("variantes", [])):
        return False
    if not (sel is None or (p["marque"].lower() in sel[0] and p["type_fr"] in sel[1])):
        return False
    if ARABES is None:
        ARABES, CONC = sl.marques_arabes(), sl.concurrent()
    # 08/11/2026 21 h 27 : Amine lève la condition « moins cher que le concurrent » ; les parfums arabes s'affichent comme
    # les autres, au prix qui garde au moins 5 € net (marge_arabes_eur), même s'il est plus cher que le concurrent.
    return True


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
    sel = selection()
    statuts = []  # (id, statut) : fiches à afficher ou à masquer selon la sélection
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
    conc, dujour = sl.concurrent(), []  # prix du concurrent (interne) ; marques « parfum du jour » à changer
    nouveaux_p, structurels_p = [], []
    for p in produits:
        ids = [vs_qs[v["sku"]]["produit"] for v in p["variantes"] if v["sku"] in vs_qs]
        if not ids:  # nouveau parfum
            h, i = p["handle"], 2
            while p["handle"] in handles:
                p["handle"] = "%s-%d" % (h, i)
                i += 1
            handles.add(p["handle"])
            e = sv.entree(p, lieu_id, {"handle": p["handle"]})
            e["input"]["status"] = statut_nouv if visible(p, sel) else "DRAFT"
            nouveaux.append(e)
            nouveaux_p.append((e, p))
            continue
        pid = collections.Counter(ids).most_common(1)[0][0]
        existante = boutique[pid]
        voulu = ("ACTIVE" if statut_nouv == "ACTIVE" else existante["status"]) if visible(p, sel) else "DRAFT"
        if voulu == "ACTIVE" and existante["status"] != "ACTIVE" and not existante.get("featuredMedia"):
            voulu = existante["status"]  # pas de photo sur la fiche : elle reste masquée
        if voulu != existante["status"]:
            statuts.append((pid, voulu))
        skus_fiche = {v["sku"] for v in existante["variantes"]}
        for v in p["variantes"]:
            vus.add(v["sku"])
        if any(v["sku"] not in skus_fiche for v in p["variantes"]):  # nouveau format
            e = entree_complete(p, existante, lieu_id, statut_nouv)
            structurels.append(e)
            structurels_p.append((e, p))
        # « Le parfum du jour » : le format en stock le plus avantageux face au concurrent (prix sous le sien), sinon rien
        meilleur, ecart_max = "", 0.0
        for v in p["variantes"]:
            a = vs_qs.get(v["sku"])
            ref = conc.get((v.get("ean") or "").lstrip("0"))
            if a and a["produit"] == pid and ref and int(v["stock"]) > 0 and float(v["prix"]) < float(ref[0]) - 0.004:
                if float(ref[0]) - float(v["prix"]) > ecart_max:
                    meilleur, ecart_max = a["id"], float(ref[0]) - float(v["prix"])
        if meilleur != ((existante.get("dujour") or {}).get("value") or ""):
            dujour.append((pid, meilleur))
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
    n_aff = sum(1 for _, st in statuts if st == "ACTIVE")
    resume = ("%d formats suivis · %d stocks changés (dont %d sortis de la liste) · %d prix/coûts changés · "
              "%d fiches complétées · %d nouvelles fiches · %d fiches affichées et %d masquées selon la sélection"
              % (n_cible, len(stocks), len(disparus), n_prix, len(structurels), len(nouveaux), n_aff,
                 len(statuts) - n_aff))
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
    # traductions NL : seulement les fiches créées ou complétées pendant ce passage
    a_traduire = [("handle", e["input"]["handle"], p_) for e, p_ in nouveaux_p] + \
                 [("id", e["identifier"]["id"], p_) for e, p_ in structurels_p]
    if a_traduire:
        try:
            n = traduire_fiches(s, sc, a_traduire)
            ligne_journal("  traductions NL : %d éléments" % n)
        except Exception as ex:
            ligne_journal("  traductions NL non faites (%s)" % str(ex)[:150])
    if nouveaux and statut_nouv == "ACTIVE":  # nouvelles fiches visibles sur la boutique en ligne
        try:
            ids = []
            for e in nouveaux:
                d = s.gql("query($h: String!) { productByIdentifier(identifier: {handle: $h}) { id } }",
                          {"h": e["input"]["handle"]}).get("productByIdentifier")
                if d:
                    ids.append(d["id"])
            publier_fiches(s, ids)
        except Exception as ex:
            ligne_journal("  publication des nouvelles fiches à refaire (%s)" % str(ex)[:150])
    # 1 bis. fiches affichées / masquées selon la sélection (masquer = brouillon, jamais supprimer)
    if statuts:
        if len(statuts) > 40:
            chemin = os.path.join(sl.RAPPORTS, "site_synchro_statuts.jsonl")
            with open(chemin, "w", encoding="utf-8") as f:
                for pid, st in statuts:
                    f.write(json.dumps({"product": {"id": pid, "status": st}}) + "\n")
            sc.bilan_resultats(sc.attendre(s, sc.lancer_mutation(s, sc.M_MAJ, chemin, "synchro-statuts"), "synchro-statuts"),
                               "synchro-statuts")
        else:
            for pid, st in statuts:
                d = s.gql(sc.M_MAJ, {"product": {"id": pid, "status": st}})["productUpdate"]
                if d["userErrors"]:
                    erreurs += 1
        publier_fiches(s, [pid for pid, st in statuts if st == "ACTIVE"]) if len(statuts) <= 40 else None
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
    # 4. « Le parfum du jour » : métachamp qosmi.du_jour = format moins cher que le concurrent (vide sinon). Jamais le prix du concurrent.
    for i in range(0, len(dujour), 25):
        mf = [{"ownerId": pid, "namespace": "qosmi", "key": "du_jour", "type": "single_line_text_field", "value": val}
              for pid, val in dujour[i:i + 25] if val]
        vides = [pid for pid, val in dujour[i:i + 25] if not val]
        if mf:
            d = s.gql("mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) { userErrors { message } } }", {"m": mf})
            if d["metafieldsSet"]["userErrors"]:
                erreurs += 1
        if vides:
            s.gql("mutation($m: [MetafieldIdentifierInput!]!) { metafieldsDelete(metafields: $m) { userErrors { message } } }",
                  {"m": [{"ownerId": pid, "namespace": "qosmi", "key": "du_jour"} for pid in vides]})
    if dujour:
        resume += " · %d marques « parfum du jour » mises à jour" % len(dujour)
    ligne_journal("OK %s · %d erreur(s) · %d s" % (resume, erreurs, time.time() - debut))
    return 0 if not erreurs else 1


M_PUBLIER = """mutation call($id: ID!, $input: [PublicationInput!]!) { publishablePublish(id: $id, input: $input) {
  userErrors { field message } } }"""


def publication_boutique(s):
    pubs = s.gql("{ publications(first: 20) { nodes { id name } } }")["publications"]["nodes"]
    return next((p["id"] for p in pubs if p["name"] in ("Online Store", "Boutique en ligne")), None)


def publications_vente(s):
    """Boutique en ligne + Google & YouTube (installé le 08/11/2026) + Facebook & Instagram (09/11/2026) :
    les canaux où une fiche active doit apparaître (une fiche en brouillon n'est envoyée à aucun d'eux)."""
    pubs = s.gql("{ publications(first: 20) { nodes { id name } } }")["publications"]["nodes"]
    return [p["id"] for p in pubs if p["name"] in ("Online Store", "Boutique en ligne")
            or any(m in p["name"].lower() for m in ("google", "facebook"))]


def publier_fiches(s, ids):
    """Rend visibles sur la boutique en ligne et sur Google des fiches déjà ACTIVES (une par une : pour les nouveautés de l'heure)."""
    pubs = publications_vente(s)
    for pid in ids if pubs else []:
        s.gql(M_PUBLIER, {"id": pid, "input": [{"publicationId": p} for p in pubs]})


def photos_manquantes():
    """Liste des parfums masqués faute de photo autorisée de bonne qualité (marque et catégorie dans la sélection) :
    rapports/theme/photos_manquantes.csv (marque, nom, formats, EAN, handle), par marque. Sert à chercher les photos."""
    import csv
    if os.environ.get("SOLELUNA_EMAIL"):
        listes_serveur()
    produits = sv.preparer(exemples=False)
    sel = selection()
    lignes = []
    for p in produits:
        if p.get("photo_ok", True) or (sel and not (p["marque"].lower() in sel[0] and p["type_fr"] in sel[1])):
            continue
        lignes.append({"marque": p["marque"], "nom": p["titre_fr"], "formats": " / ".join(v["format_fr"] for v in p["variantes"]),
                       "ean": " ".join(sorted({v["ean"] for v in p["variantes"] if v.get("ean")})), "handle": p["handle"],
                       "stock": sum(int(v.get("stock") or 0) for v in p["variantes"])})
    lignes.sort(key=lambda x: (x["marque"].lower(), x["nom"].lower()))
    dossier = os.path.join(os.path.dirname(ICI), "rapports", "theme")
    os.makedirs(dossier, exist_ok=True)
    with open(os.path.join(dossier, "photos_manquantes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()) if lignes else ["marque"], delimiter=";")
        w.writeheader()
        w.writerows(lignes)
    par = collections.Counter(x["marque"] for x in lignes)
    print("Parfums masqués faute de photo : %d" % len(lignes))
    for m, n in par.most_common(30):
        print("  %s : %d" % (m, n))


def testeurs_suspens():
    """08/11/2026, demande d'Amine : testeurs en suspens (question juridique à vérifier avec son avocat).
    Retire du site les formats « testeur » déjà présents : une fiche qui n'a QUE des testeurs passe en brouillon ;
    sur une fiche mixte, les variantes testeur sont supprimées (le passage horaire les recrée si
    config/site.json « testeurs_en_suspens » repasse à false) et l'étiquette « Testeurs » est retirée."""
    from shopify_api import Shopify
    import site_charger as sc
    if not reglage("testeurs_en_suspens", False):
        raise SystemExit("config/site.json : testeurs_en_suspens n'est pas à true — rien à faire.")
    s = Shopify()
    boutique, _ = etat_boutique(s, sc)

    def est_testeur(v):
        return any("testeur" in (o.get("value") or "").lower() for o in v.get("selectedOptions") or [])
    brouillons, mixtes, n_var, erreurs = 0, 0, 0, 0
    for p in boutique.values():
        if not any((v.get("sku") or "").startswith("QS-") for v in p["variantes"]):
            continue
        tv = [v for v in p["variantes"] if est_testeur(v)]
        if not tv:
            continue
        if len(tv) == len(p["variantes"]):
            if p["status"] != "DRAFT":
                e = s.gql(sc.M_MAJ, {"product": {"id": p["id"], "status": "DRAFT"}})["productUpdate"]["userErrors"]
                erreurs += bool(e)
                brouillons += 1
            continue
        e = s.gql("""mutation($p: ID!, $v: [ID!]!) { productVariantsBulkDelete(productId: $p, variantsIds: $v) {
                     userErrors { field message } } }""", {"p": p["id"], "v": [v["id"] for v in tv]})["productVariantsBulkDelete"]["userErrors"]
        if e:
            erreurs += 1
            print("  erreur %s : %s" % (p["handle"], e))
            continue
        s.gql("""mutation($id: ID!, $t: [String!]!) { tagsRemove(id: $id, tags: $t) { userErrors { message } } }""",
              {"id": p["id"], "t": ["Testeurs"]})
        mixtes += 1
        n_var += len(tv)
    print("Testeurs en suspens : %d fiches « testeur seul » passées en brouillon, %d formats testeur retirés de %d fiches, %d erreurs"
          % (brouillons, n_var, mixtes, erreurs))
    # la collection « Testeurs » est retirée de la boutique en ligne (republier : publishablePublish)
    col = s.gql('{ collectionByIdentifier(identifier: {handle: "testeurs"}) { id } }').get("collectionByIdentifier")
    if col:
        pubs = publications_vente(s)
        e = s.gql("""mutation($id: ID!, $i: [PublicationInput!]!) { publishableUnpublish(id: $id, input: $i) { userErrors { message } } }""",
                  {"id": col["id"], "i": [{"publicationId": x} for x in pubs]})["publishableUnpublish"]["userErrors"]
        print("Collection Testeurs retirée de la boutique : %s" % (e or "ok"))


def google():
    """Canal Google & YouTube (08/11/2026) : y publie toutes les fiches SoleLuna (actives ou en brouillon).
    Google ne reçoit que les fiches ACTIVES : une fiche masquée (brouillon) par le passage horaire disparaît aussi de Google."""
    from shopify_api import Shopify
    import site_charger as sc
    s = Shopify()
    pubs = s.gql("{ publications(first: 20) { nodes { id name } } }")["publications"]["nodes"]
    print("Canaux : %s" % ", ".join(p["name"] for p in pubs))
    g = next((p["id"] for p in pubs if "google" in p["name"].lower()), None)
    if not g:
        raise SystemExit("Canal Google & YouTube introuvable")

    def compte():
        for p in pubs:
            try:
                n = s.gql("query($p: ID!) { publishedProductsCount(publicationId: $p) { count } }", {"p": p["id"]})
                print("  publiées sur %s : %s" % (p["name"], n["publishedProductsCount"]["count"]))
            except Exception as e:
                print("  %s : comptage impossible (%s)" % (p["name"], str(e)[:120]))
    compte()
    boutique, _ = etat_boutique(s, sc)
    cibles = [p["id"] for p in boutique.values() if any((v.get("sku") or "").startswith("QS-") for v in p["variantes"])]
    actives = sum(1 for p in cibles if boutique[p]["status"] == "ACTIVE")
    print("Fiches SoleLuna : %d (dont %d actives) à publier sur Google & YouTube" % (len(cibles), actives))
    os.makedirs(sl.RAPPORTS, exist_ok=True)
    chemin = os.path.join(sl.RAPPORTS, "site_publication_google.jsonl")
    with open(chemin, "w", encoding="utf-8") as f:
        for pid in cibles:
            f.write(json.dumps({"id": pid, "input": [{"publicationId": g}]}) + "\n")
    sc.bilan_resultats(sc.attendre(s, sc.lancer_mutation(s, M_PUBLIER, chemin, "publication-google"), "publication-google"),
                       "publication-google")
    compte()


def activer():
    """Passe en ACTIF toutes les fiches SoleLuna en brouillon et les publie sur la boutique en ligne
    (décision d'Amine du 04/11/2026 ; la boutique reste protégée par mot de passe)."""
    ligne_journal("Activation en bloc désactivée le 07/11/2026 : elle réafficherait les fiches masquées "
                  "(marques hors sélection, fiches sans bonne photo). Le passage horaire choisit seul ce qui est affiché.")
    return
    from shopify_api import Shopify
    import site_charger as sc
    s = Shopify()
    boutique, _ = etat_boutique(s, sc)
    cibles = [p["id"] for p in boutique.values()
              if any((v.get("sku") or "").startswith("QS-") for v in p["variantes"])]
    brouillons = [p for p in cibles if boutique[p]["status"] == "DRAFT"]
    ligne_journal("Fiches SoleLuna : %d, dont %d en brouillon à activer" % (len(cibles), len(brouillons)))
    os.makedirs(sl.RAPPORTS, exist_ok=True)
    if brouillons:
        chemin = os.path.join(sl.RAPPORTS, "site_activation_envoi.jsonl")
        with open(chemin, "w", encoding="utf-8") as f:
            for pid in brouillons:
                f.write(json.dumps({"product": {"id": pid, "status": "ACTIVE"}}) + "\n")
        sc.bilan_resultats(sc.attendre(s, sc.lancer_mutation(s, sc.M_MAJ, chemin, "activation"), "activation"), "activation")
    pub = publication_boutique(s)
    if not pub:
        ligne_journal("Canal « Boutique en ligne » introuvable : fiches actives mais non publiées.")
        return
    chemin = os.path.join(sl.RAPPORTS, "site_publication_envoi.jsonl")
    with open(chemin, "w", encoding="utf-8") as f:
        for pid in cibles:
            f.write(json.dumps({"id": pid, "input": [{"publicationId": pub}]}) + "\n")
    sc.bilan_resultats(sc.attendre(s, sc.lancer_mutation(s, M_PUBLIER, chemin, "publication"), "publication"), "publication")
    ligne_journal("Fiches actives et publiées sur la boutique en ligne : %d" % len(cibles))


def photos_marques():
    """Remplace sur Shopify les photos des fiches Mancera et Montale par les photos officielles des marques."""
    from shopify_api import Shopify
    import site_charger as sc
    if os.environ.get("SOLELUNA_EMAIL"):
        listes_serveur()
    produits = sv.preparer(exemples=False)
    s = Shopify()
    lieu_id = sc.lieu(s)
    boutique, variantes = etat_boutique(s, sc)
    vs_qs = {v["sku"]: v for v in variantes.values() if (v.get("sku") or "").startswith("QS-")}
    officielles = set()
    for nom in ("photos_marques.json", "photos_riklis.json", "photos_skins.json", "photos_parfumerie.json", "photos_acquadiparma.json", "photos_parfuma.json", "photos_bijenkorf.json", "photos_ici.json", "photos_elo.json", "photos_creed.json", "photos_ch.json", "photos_puig.json", "photos_notino.json", "photos_dg.json", "photos_jm.json", "photos_mm.json", "photos_tfi.json", "photos_ck.json", "photos_tt.json", "photos_lvmh.json", "photos_m2.json", "photos_m3.json", "photos_rosendo.json", "photos_retirees.json", "photos_manque.json", "photos_trouvees.json"):
        chemin = os.path.join(os.path.dirname(sl.SITE), nom)
        if os.path.exists(chemin):
            ph = json.load(open(chemin, encoding="utf-8"))
            officielles |= set(ph.get("par_ean", {}).values()) | set(ph.get("par_nom", {}).values()) | set(ph.get("par_fiche", {}).values())
    chemin = os.path.join(os.path.dirname(sl.SITE), "photos_cadrees.json")
    if os.path.exists(chemin):  # photos recadrées : mêmes photos autorisées, flacon remis à la même taille
        cadrees = json.load(open(chemin, encoding="utf-8"))["par_url"]
        officielles |= {cadrees[u] for u in officielles if u in cadrees}
    # fiches dont une photo autorisée diffère de la photo actuelle sur Shopify
    deja = {}
    chemin_etat = os.path.join(sl.RAPPORTS, "site_photos_posees.json")
    if os.path.exists(chemin_etat):
        deja = json.load(open(chemin_etat, encoding="utf-8"))
    ok = err = 0
    essai = os.environ.get("PHOTOS_ESSAI", "")  # ex. « parfumerie.be » : une seule fiche, puis contrôle du téléchargement
    essai_pid = None
    seule = os.environ.get("PHOTOS_FICHE", "")  # une fiche précise renvoyée telle quelle (ex. pour réparer une photo)
    for p in produits:
        photos = sorted({v["photo_source"] for v in p["variantes"] if v["photo_source"] in officielles})
        if seule:
            if p["handle"] != seule or essai_pid:
                continue
            photos = photos or sorted({v["photo_source"] for v in p["variantes"] if v["photo_source"]})
            essai = essai or "http"
        elif not photos or deja.get(p["handle"]) == photos:
            continue
        if essai and (essai_pid or not any(essai in u for u in photos)):
            continue
        ids = [vs_qs[v["sku"]]["produit"] for v in p["variantes"] if v["sku"] in vs_qs]
        if not ids:
            continue
        pid = collections.Counter(ids).most_common(1)[0][0]
        e = entree_complete(p, boutique[pid], lieu_id, boutique[pid]["status"])
        d = s.gql(sc.M_SET, e)["productSet"]
        if d["userErrors"]:
            err += 1
            ligne_journal("  erreur %s : %s" % (p["titre_fr"], json.dumps(d["userErrors"], ensure_ascii=False)[:200]))
        else:
            ok += 1
            deja[p["handle"]] = photos
            if essai:
                essai_pid = pid
                ligne_journal("  essai sur « %s » : %s" % (p["titre_fr"], ", ".join(photos)))
    if essai_pid:
        for _ in range(12):
            time.sleep(10)
            m = s.gql("""query($id: ID!) { product(id: $id) { media(first: 20) { nodes { status
                mediaErrors { code details } ... on MediaImage { image { url width height } } } } } }""",
                      {"id": essai_pid})["product"]["media"]["nodes"]
            if all(x["status"] in ("READY", "FAILED") for x in m):
                break
        for x in m:
            ligne_journal("  média %s %s %s" % (x["status"], json.dumps(x.get("image"))[:160], x.get("mediaErrors") or ""))
    os.makedirs(sl.RAPPORTS, exist_ok=True)
    json.dump(deja, open(chemin_etat, "w", encoding="utf-8"))
    ligne_journal("Photos autorisées posées : %d fiches (%d erreurs)" % (ok, err))


Q_MEDIAS = """{ products(query: "status:active") { edges { node { id title
  media { edges { node { ... on MediaImage { id status } } } } } } } }"""


def controle_medias(s=None):
    """Compte les photos en échec (FAILED) ou en cours sur les fiches actives, et nomme les fiches concernées."""
    from shopify_api import Shopify
    s = s or Shopify()
    d = s.gql("""mutation($q: String!) { bulkOperationRunQuery(query: $q) { bulkOperation { id } userErrors { message } } }""",
              {"q": Q_MEDIAS})["bulkOperationRunQuery"]
    if d["userErrors"]:
        ligne_journal("Contrôle des photos refusé : %s" % d["userErrors"])
        return
    op = d["bulkOperation"]["id"]
    while True:
        b = s.gql("query($id: ID!) { bulkOperation(id: $id) { status errorCode url } }", {"id": op})["bulkOperation"]
        if b["status"] in ("COMPLETED", "FAILED", "CANCELED", "EXPIRED"):
            break
        time.sleep(10)
    titres, statuts, echecs = {}, collections.Counter(), collections.Counter()
    if b.get("url"):
        for l in urllib.request.urlopen(b["url"]).read().decode("utf-8").splitlines():
            x = json.loads(l)
            if "__parentId" in x:
                statuts[x.get("status")] += 1
                if x.get("status") == "FAILED":
                    echecs[x["__parentId"]] += 1
            else:
                titres[x["id"]] = x["title"]
    ligne_journal("Contrôle des photos (fiches actives) : %s" % dict(statuts))
    for pid in list(echecs)[:30]:
        ligne_journal("  photo en échec : %s" % titres.get(pid, pid))


Q_QUALITE = """{ products(query: "status:active") { edges { node { id handle title vendor
  media { edges { node { ... on MediaImage { id status image { url width height } } } } } } } } }"""


def qualite_photos():
    """Relevé des photos des fiches actives (taille, origine) pour juger la qualité par marque : rapports/theme/qualite_photos.json."""
    from shopify_api import Shopify
    s = Shopify()
    d = s.gql("""mutation($q: String!) { bulkOperationRunQuery(query: $q) { bulkOperation { id } userErrors { message } } }""",
              {"q": Q_QUALITE})["bulkOperationRunQuery"]
    if d["userErrors"]:
        ligne_journal("Relevé des photos refusé : %s" % d["userErrors"])
        return
    op = d["bulkOperation"]["id"]
    while True:
        b = s.gql("query($id: ID!) { bulkOperation(id: $id) { status errorCode url } }", {"id": op})["bulkOperation"]
        if b["status"] in ("COMPLETED", "FAILED", "CANCELED", "EXPIRED"):
            break
        time.sleep(10)
    fiches = {}
    if b.get("url"):
        for l in urllib.request.urlopen(b["url"]).read().decode("utf-8").splitlines():
            x = json.loads(l)
            if "__parentId" in x:
                im = x.get("image") or {}
                fiches.setdefault(x["__parentId"], {"photos": []})["photos"].append(
                    {"url": (im.get("url") or "").split("?")[0], "l": im.get("width"), "h": im.get("height"), "statut": x.get("status")})
            else:
                fiches.setdefault(x["id"], {"photos": []}).update({"id": x["id"], "handle": x["handle"], "titre": x["title"], "marque": x["vendor"]})
    os.makedirs(os.path.join(os.path.dirname(ICI), "rapports", "theme"), exist_ok=True)
    json.dump(list(fiches.values()), open(os.path.join(os.path.dirname(ICI), "rapports", "theme", "qualite_photos.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    ligne_journal("Relevé des photos : %d fiches actives" % len(fiches))
    if "--masquer-photos-faibles" not in sys.argv:
        return
    # demande d'Amine du 07/11/2026 : une fiche sans photo ou avec une photo de mauvaise qualité ne doit pas être affichée
    import site_charger as sc
    seuil = int(reglage("photo_min_px", 500))
    faibles = [f for f in fiches.values()
               if max((min(p["l"], p["h"]) for p in f["photos"] if p.get("l") and p.get("h")), default=0) < seuil]
    ok = err = 0
    par_marque = collections.Counter()
    for f in faibles:
        d = s.gql(sc.M_MAJ, {"product": {"id": f["id"], "status": "DRAFT"}})["productUpdate"]
        if d["userErrors"]:
            err += 1
        else:
            ok += 1
            par_marque[f.get("marque")] += 1
    ligne_journal("Fiches masquées (photo absente ou < %d px) : %d (%d erreurs)" % (seuil, ok, err))
    for m, n in par_marque.most_common():
        ligne_journal("  %s : %d" % (m, n))
    json.dump([{"handle": f["handle"], "marque": f.get("marque"), "titre": f.get("titre")} for f in faibles],
              open(os.path.join(os.path.dirname(ICI), "rapports", "theme", "fiches_masquees_photos.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)


def textes():
    """Remet à jour la description, le titre et la méta-description Google (FR + NL) des fiches visibles."""
    from shopify_api import Shopify
    import site_charger as sc
    if os.environ.get("SOLELUNA_EMAIL"):
        listes_serveur()
    produits = sv.preparer(exemples=False)
    s = Shopify()
    boutique, _ = etat_boutique(s, sc)
    par_handle = {x.get("handle"): x for x in boutique.values()}
    sel = selection()
    vus = [p for p in produits if visible(p, sel) and p["handle"] in par_handle]
    ok = err = 0
    for p in vus:
        d = s.gql(sc.M_MAJ, {"product": {"id": par_handle[p["handle"]]["id"], "descriptionHtml": p["desc_fr"],
                                         "seo": {"title": p["seo_titre_fr"], "description": p["seo_desc_fr"]}}})["productUpdate"]
        if d["userErrors"]:
            err += 1
        else:
            ok += 1
    ligne_journal("Descriptions FR mises à jour : %d fiches (%d erreurs)" % (ok, err))
    n = sv.traduire(s, sc, vus)
    ligne_journal("Traductions NL envoyées : %s" % n)


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
        if "--activer" in sys.argv:
            activer()
            return 0
        if "--photos-marques" in sys.argv:
            photos_marques()
            if not os.environ.get("PHOTOS_ESSAI"):
                controle_medias()
            return 0
        if "--textes" in sys.argv:
            textes()
            return 0
        if "--qualite-photos" in sys.argv or "--masquer-photos-faibles" in sys.argv:
            qualite_photos()
            return 0
        if "--controle-photos" in sys.argv:
            controle_medias()
            return 0
        if "--photos-manquantes" in sys.argv:
            photos_manquantes()
            return 0
        if "--testeurs-suspens" in sys.argv:
            testeurs_suspens()
            textes()  # descriptions sans la phrase sur le format testeur
            return 0
        if "--google" in sys.argv:
            google()
            return 0
        try:
            return synchro(essai="--essai" in sys.argv)
        except Exception as e:
            ligne_journal("ÉCHEC %s : %s" % (type(e).__name__, str(e)[:300]))
            return 1


if __name__ == "__main__":
    sys.exit(main())
