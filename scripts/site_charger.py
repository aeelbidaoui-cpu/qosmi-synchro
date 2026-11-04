#!/usr/bin/env python3
"""Chargement du catalogue Qosmi sur Shopify (API Admin GraphQL).

Source : base/site_catalogue.csv (interne : contient les coûts, ne jamais l'envoyer à qui que ce soit).
Sur Shopify ne partent que : titre, description, marque, type, tags, prix TTC, EAN, référence Q-/QD-,
stock et photo (Shopify copie la photo sur ses propres serveurs, sous le nom de la fiche Qosmi).
Le coût est enregistré dans le champ « coût par article » de Shopify, visible seulement dans l'admin.

  python3 scripts/site_charger.py --test 20   → crée/met à jour 20 fiches une par une + traduction NL
  python3 scripts/site_charger.py --charger   → envoie tout le catalogue en une opération groupée
  python3 scripts/site_charger.py --etat      → où en est l'opération groupée
  python3 scripts/site_charger.py --traduire  → active le néerlandais et envoie toutes les traductions NL

Toutes les fiches sont créées en BROUILLON : rien n'est visible des clients avant l'ouverture.
Relançable sans risque : chaque fiche est retrouvée par son « handle » et mise à jour, jamais dupliquée.
"""
import csv, json, os, random, sys, time, urllib.request, uuid

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from shopify_api import Shopify, RACINE  # noqa: E402

CATALOGUE = os.path.join(RACINE, "base", "site_catalogue.csv")
ETAT = os.path.join(RACINE, "base", "site_operations.json")
RAPPORTS = os.path.join(RACINE, "rapports")
LANGUE2 = "nl"

M_SET = """mutation call($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
  productSet(input: $input, identifier: $identifier) {
    product { id handle }
    userErrors { field message code }
  }
}"""
M_TRAD = """mutation call($resourceId: ID!, $translations: [TranslationInput!]!) {
  translationsRegister(resourceId: $resourceId, translations: $translations) {
    translations { key locale }
    userErrors { field message code }
  }
}"""
Q_TRAD_BULK = """{ translatableResources(resourceType: PRODUCT) { edges { node {
  resourceId translatableContent { key value digest locale } } } } }"""


def journal(*a):
    ligne = " ".join(str(x) for x in a)
    print(ligne, flush=True)
    os.makedirs(RAPPORTS, exist_ok=True)
    with open(os.path.join(RAPPORTS, "site_chargement_journal.txt"), "a", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + ligne + "\n")


def lire():
    with open(CATALOGUE, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def lire_etat():
    try:
        with open(ETAT, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def ecrire_etat(**k):
    e = lire_etat()
    e.update(k)
    with open(ETAT, "w", encoding="utf-8") as f:
        json.dump(e, f, indent=1)


def lieu(s):
    d = s.gql("{ locations(first: 5) { nodes { id name isActive } } }")
    actifs = [l for l in d["locations"]["nodes"] if l["isActive"]]
    if not actifs:
        raise SystemExit("Aucun lieu de stock actif sur Shopify.")
    return actifs[0]["id"]


def entree(r, lieu_id):
    """Variables productSet pour une ligne du catalogue."""
    var = {"optionValues": [{"optionName": "Title", "name": "Default Title"}],
           "price": r["prix"], "sku": r["sku"], "barcode": r["ean"],
           "inventoryPolicy": "DENY", "taxable": True,
           "inventoryItem": {"tracked": True, "requiresShipping": True},
           "inventoryQuantities": [{"locationId": lieu_id, "name": "available",
                                    "quantity": max(0, int(float(r["stock"] or 0)))}]}
    if r.get("cout_ht"):
        var["inventoryItem"]["cost"] = r["cout_ht"]
    inp = {"handle": r["handle"], "title": r["titre_fr"], "descriptionHtml": r["desc_fr"],
           "vendor": r["marque"], "productType": r["type_fr"],
           "tags": [t.strip() for t in r["tags"].split(",") if t.strip()] +
                   (["en-stock-belgique"] if r["source"] == "depot" else []),
           "status": "DRAFT",
           "productOptions": [{"name": "Title", "values": [{"name": "Default Title"}]}],
           "variants": [var]}
    src = (r.get("photo_source") or "").split("?")[0]
    if src and os.path.splitext(src)[1]:  # une vraie image (certaines lignes fournisseur n'ont qu'un dossier)
        ext = os.path.splitext(src)[1].lower()
        inp["files"] = [{"originalSource": r["photo_source"], "contentType": "IMAGE",
                         "alt": r["titre_fr"], "filename": r["handle"][:120] + ext}]
    return {"input": inp, "identifier": {"handle": r["handle"]}}


def traductions(r, contenu):
    """TranslationInput NL à partir du contenu traduisible (clé → digest)."""
    t = []
    for cle, val in (("title", r["titre_nl"]), ("body_html", r["desc_nl"]), ("product_type", r["type_nl"])):
        if cle in contenu and val:
            t.append({"locale": LANGUE2, "key": cle, "value": val, "translatableContentDigest": contenu[cle]})
    return t


def activer_nl(s):
    d = s.gql("{ shopLocales { locale primary published } }")["shopLocales"]
    if not any(l["locale"] == LANGUE2 for l in d):
        r = s.gql('mutation { shopLocaleEnable(locale: "%s") { shopLocale { locale published } userErrors { message } } }' % LANGUE2)
        journal("Néerlandais ajouté à la boutique :", json.dumps(r["shopLocaleEnable"], ensure_ascii=False))
    else:
        journal("Néerlandais déjà présent dans la boutique.")


# ---------- test : quelques fiches une par une ----------
def test(n):
    s = Shopify()
    lignes = lire()
    depot = [r for r in lignes if r["source"] == "depot"]
    autres = [r for r in lignes if r["source"] != "depot" and r["photo_source"]]
    random.seed(7)
    choix = depot[:3] + random.sample(autres, max(0, n - 3))
    lieu_id = lieu(s)
    taxes = s.gql("{ shop { taxesIncluded } }")["shop"]["taxesIncluded"]
    journal("Prix TTC affichés (taxes incluses dans les prix) :", "oui" if taxes else
            "NON → Admin Shopify → Paramètres → Taxes et droits de douane : cocher « Tous les prix incluent les taxes »")
    activer_nl(s)
    ok = 0
    for r in choix:
        d = s.gql(M_SET, entree(r, lieu_id))["productSet"]
        if d["userErrors"]:
            journal("  ERREUR", r["sku"], json.dumps(d["userErrors"], ensure_ascii=False)[:400])
            continue
        pid = d["product"]["id"]
        tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }",
                   {"id": pid})["translatableResource"]
        contenu = {c["key"]: c["digest"] for c in tr["translatableContent"]}
        t = s.gql(M_TRAD, {"resourceId": pid, "translations": traductions(r, contenu)})["translationsRegister"]
        err = t["userErrors"]
        ok += 1
        journal("  OK", r["sku"], r["titre_fr"][:70], "| NL :", "ok" if not err else json.dumps(err, ensure_ascii=False)[:200])
    time.sleep(5)  # laisser Shopify copier les photos
    d = s.gql("""{ products(first: 50, query: "status:draft", sortKey: UPDATED_AT, reverse: true) { nodes {
                   handle media(first: 1) { nodes { status mediaErrors { message } } } } } }""")
    photos = [m["status"] for p in d["products"]["nodes"] for m in p["media"]["nodes"]]
    journal("Fiches envoyées : %d / %d. Photos : %s" % (ok, len(choix), {k: photos.count(k) for k in set(photos)}))
    journal("À voir dans l'admin : Produits → filtre Brouillon.")


# ---------- opérations groupées ----------
def televerser(s, chemin, ressource="BULK_MUTATION_VARIABLES"):
    d = s.gql("""mutation($i: [StagedUploadInput!]!) { stagedUploadsCreate(input: $i) {
                   stagedTargets { url resourceUrl parameters { name value } } userErrors { message } } }""",
              {"i": [{"resource": ressource, "filename": os.path.basename(chemin), "mimeType": "text/jsonl",
                      "httpMethod": "POST"}]})["stagedUploadsCreate"]
    if d["userErrors"]:
        raise SystemExit("Téléversement refusé : %s" % d["userErrors"])
    cible = d["stagedTargets"][0]
    limite = "----qosmi" + uuid.uuid4().hex
    morceaux = []
    for p in cible["parameters"]:
        morceaux.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                         % (limite, p["name"], p["value"])).encode())
    with open(chemin, "rb") as f:
        contenu = f.read()
    morceaux.append(("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n"
                     "Content-Type: text/jsonl\r\n\r\n" % (limite, os.path.basename(chemin))).encode())
    morceaux.append(contenu + ("\r\n--%s--\r\n" % limite).encode())
    req = urllib.request.Request(cible["url"], data=b"".join(morceaux), method="POST",
                                 headers={"Content-Type": "multipart/form-data; boundary=" + limite})
    with urllib.request.urlopen(req, timeout=600) as r:
        r.read()
    return [p["value"] for p in cible["parameters"] if p["name"] == "key"][0]


def lancer_mutation(s, mutation, chemin, nom):
    cle = televerser(s, chemin)
    d = s.gql("""mutation($m: String!, $p: String!) { bulkOperationRunMutation(mutation: $m, stagedUploadPath: $p) {
                   bulkOperation { id status } userErrors { field message } } }""",
              {"m": mutation, "p": cle})["bulkOperationRunMutation"]
    if d["userErrors"]:
        raise SystemExit("Opération refusée : %s" % d["userErrors"])
    op = d["bulkOperation"]["id"]
    ecrire_etat(**{nom: op})
    journal("Opération « %s » lancée : %s" % (nom, op))
    return op


def attendre(s, op, nom):
    debut = time.time()
    while True:
        b = s.gql("""query($id: ID!) { bulkOperation(id: $id) { status errorCode objectCount url partialDataUrl } }""",
                  {"id": op})["bulkOperation"]
        journal("  %s : %s, %s objets traités (%d min)" % (nom, b["status"], b["objectCount"], (time.time() - debut) // 60))
        if b["status"] in ("COMPLETED", "FAILED", "CANCELED", "EXPIRED"):
            return b
        time.sleep(60)


def bilan_resultats(b, nom):
    url = b.get("url") or b.get("partialDataUrl")
    if not url:
        journal("Pas de fichier de résultats pour", nom, "(code %s)" % b.get("errorCode"))
        return []
    chemin = os.path.join(RAPPORTS, "site_%s_resultats_%s.jsonl" % (nom, time.strftime("%Y-%m-%d_%Hh%M")))
    urllib.request.urlretrieve(url, chemin)
    lignes = [json.loads(l) for l in open(chemin, encoding="utf-8") if l.strip()]
    erreurs = []
    for l in lignes:
        dd = (l.get("data") or {})
        corps = next(iter(dd.values()), {}) if dd else {}
        if l.get("errors") or (corps or {}).get("userErrors"):
            erreurs.append(l)
    journal("%s : %d lignes, %d en erreur. Détail : %s" % (nom, len(lignes), len(erreurs), chemin))
    for e in erreurs[:15]:
        journal("   ", json.dumps(e, ensure_ascii=False)[:300])
    return lignes


def charger():
    s = Shopify()
    lieu_id = lieu(s)
    os.makedirs(RAPPORTS, exist_ok=True)
    chemin = os.path.join(RAPPORTS, "site_catalogue_envoi.jsonl")
    lignes = lire()
    with open(chemin, "w", encoding="utf-8") as f:
        for r in lignes:
            f.write(json.dumps(entree(r, lieu_id), ensure_ascii=False) + "\n")
    journal("Catalogue préparé : %d fiches (%.1f Mo)" % (len(lignes), os.path.getsize(chemin) / 1e6))
    op = lancer_mutation(s, M_SET, chemin, "catalogue")
    b = attendre(s, op, "catalogue")
    bilan_resultats(b, "catalogue")
    if b["status"] == "COMPLETED":
        traduire(s)


def traduire(s=None):
    s = s or Shopify()
    activer_nl(s)
    d = s.gql("""mutation($q: String!) { bulkOperationRunQuery(query: $q) { bulkOperation { id status } userErrors { message } } }""",
              {"q": Q_TRAD_BULK})["bulkOperationRunQuery"]
    if d["userErrors"]:
        raise SystemExit("Lecture groupée refusée : %s" % d["userErrors"])
    op = d["bulkOperation"]["id"]
    b = attendre(s, op, "lecture-traductions")
    if not b.get("url"):
        raise SystemExit("Lecture des contenus traduisibles impossible (%s)." % b.get("errorCode"))
    chemin = os.path.join(RAPPORTS, "site_contenus_traduisibles.jsonl")
    urllib.request.urlretrieve(b["url"], chemin)
    par_handle = {r["handle"]: r for r in lire()}
    sortie = os.path.join(RAPPORTS, "site_traductions_envoi.jsonl")
    n = 0
    with open(sortie, "w", encoding="utf-8") as f:
        for l in open(chemin, encoding="utf-8"):
            x = json.loads(l)
            contenu = {c["key"]: c for c in x.get("translatableContent", [])}
            h = (contenu.get("handle") or {}).get("value")
            r = par_handle.get(h)
            if not r:
                continue
            t = traductions(r, {k: v["digest"] for k, v in contenu.items()})
            if t:
                f.write(json.dumps({"resourceId": x["resourceId"], "translations": t}, ensure_ascii=False) + "\n")
                n += 1
    journal("Traductions NL préparées : %d fiches" % n)
    op = lancer_mutation(s, M_TRAD, sortie, "traductions")
    bilan_resultats(attendre(s, op, "traductions"), "traductions")


M_MAJ = """mutation call($product: ProductUpdateInput!) {
  productUpdate(product: $product) { product { id } userErrors { field message } }
}"""


def ids_shopify():
    """handle → id produit, d'après le dernier fichier de résultats du chargement."""
    import glob
    res = sorted(glob.glob(os.path.join(RAPPORTS, "site_catalogue_resultats_*.jsonl")))
    envoi = os.path.join(RAPPORTS, "site_catalogue_envoi.jsonl")
    with open(envoi, encoding="utf-8") as f:
        handles = [json.loads(l)["identifier"]["handle"] for l in f if l.strip()]
    ids = {}
    for chemin in res:
        for l in open(chemin, encoding="utf-8"):
            x = json.loads(l)
            p = ((x.get("data") or {}).get("productSet") or {}).get("product")
            if p:
                ids[p.get("handle") or handles[x["__lineNumber"]]] = p["id"]
    return ids


def maj_textes():
    """Met à jour titre + description FR de toutes les fiches déjà créées (sans toucher photos, prix, stock),
    reprend les fiches en échec, puis renvoie toutes les traductions NL."""
    s = Shopify()
    ids = ids_shopify()
    lignes = lire()
    chemin = os.path.join(RAPPORTS, "site_textes_envoi.jsonl")
    manquantes = []
    with open(chemin, "w", encoding="utf-8") as f:
        for r in lignes:
            pid = ids.get(r["handle"])
            if pid:
                f.write(json.dumps({"product": {"id": pid, "title": r["titre_fr"], "descriptionHtml": r["desc_fr"]}},
                                   ensure_ascii=False) + "\n")
            else:
                manquantes.append(r)
    journal("Textes à mettre à jour : %d fiches ; fiches à (re)créer : %d" % (len(ids), len(manquantes)))
    op = lancer_mutation(s, M_MAJ, chemin, "textes")
    bilan_resultats(attendre(s, op, "textes"), "textes")
    if manquantes:
        lieu_id = lieu(s)
        ok = 0
        for r in manquantes:
            d = s.gql(M_SET, entree(r, lieu_id))["productSet"]
            if d["userErrors"]:
                journal("  ERREUR", r["sku"], json.dumps(d["userErrors"], ensure_ascii=False)[:300])
            else:
                ok += 1
        journal("Fiches reprises : %d / %d" % (ok, len(manquantes)))
    traduire(s)


def reprendre():
    """Crée les fiches absentes de Shopify (une par une) avec leur traduction NL."""
    s = Shopify()
    ids = ids_shopify()
    lieu_id = lieu(s)
    manquantes = [r for r in lire() if r["handle"] not in ids]
    journal("Fiches à reprendre : %d" % len(manquantes))
    ok = 0
    for r in manquantes:
        d = s.gql(M_SET, entree(r, lieu_id))["productSet"]
        if d["userErrors"]:
            journal("  ERREUR", r["sku"], json.dumps(d["userErrors"], ensure_ascii=False)[:300])
            continue
        pid = d["product"]["id"]
        tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }",
                   {"id": pid})["translatableResource"]
        contenu = {c["key"]: c["digest"] for c in tr["translatableContent"]}
        s.gql(M_TRAD, {"resourceId": pid, "translations": traductions(r, contenu)})
        ok += 1
    journal("Fiches reprises : %d / %d (sans photo quand le fournisseur n'en a pas)" % (ok, len(manquantes)))


def etat():
    s = Shopify()
    for nom, op in lire_etat().items():
        b = s.gql("query($id: ID!) { bulkOperation(id: $id) { status errorCode objectCount createdAt completedAt } }",
                  {"id": op})["bulkOperation"]
        journal("%s : %s" % (nom, json.dumps(b, ensure_ascii=False)))
    d = s.gql("{ productsCount(query: \"status:draft\") { count } }")
    journal("Fiches en brouillon sur Shopify : %s" % d["productsCount"]["count"])


if __name__ == "__main__":
    if "--test" in sys.argv:
        i = sys.argv.index("--test")
        test(int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 20)
    elif "--charger" in sys.argv:
        charger()
    elif "--reprendre" in sys.argv:
        reprendre()
    elif "--maj-textes" in sys.argv:
        maj_textes()
    elif "--traduire" in sys.argv:
        traduire()
    elif "--etat" in sys.argv:
        etat()
    else:
        print(__doc__)
