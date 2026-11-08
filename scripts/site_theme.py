#!/usr/bin/env python3
"""Qosmi : thème de la boutique (Horizon).

  python3 scripts/site_theme.py --exporter   → copie les fichiers de réglage du thème publié dans rapports/theme/
                                              (lecture seule, rien n'est modifié)
  python3 scripts/site_theme.py --appliquer  → collections, menu, logo, puis une COPIE NON PUBLIÉE du thème
                                              « Qosmi A (aperçu) » avec la direction A. Le thème publié n'est pas touché.
"""
import json, os, sys, time, urllib.request, uuid

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import site_soleluna as sl  # noqa: E402

Q_THEMES = "{ themes(first: 20) { nodes { id name role themeStoreId processing updatedAt } } }"
Q_FICHIERS = """query($id: ID!, $apres: String) { theme(id: $id) { files(first: 250, after: $apres) {
  nodes { filename size } pageInfo { hasNextPage endCursor } } } }"""
Q_CONTENU = """query($id: ID!, $noms: [String!]) { theme(id: $id) { files(filenames: $noms, first: 50) {
  nodes { filename body { ... on OnlineStoreThemeFileBodyText { content } } } } } }"""


def exporter(apercu=False):
    from shopify_api import Shopify
    s = Shopify()
    themes = s.gql(Q_THEMES)["themes"]["nodes"]
    dossier = os.path.join(sl.RAPPORTS, "theme")
    os.makedirs(dossier, exist_ok=True)
    json.dump(themes, open(os.path.join(dossier, "_themes.json"), "w"), indent=1, ensure_ascii=False)
    main = next(t for t in themes if (t["name"] == APERCU if apercu else t["role"] == "MAIN"))
    print("Thème publié :", main["name"], main["id"])
    noms, apres = [], None
    while True:
        d = s.gql(Q_FICHIERS, {"id": main["id"], "apres": apres})["theme"]["files"]
        noms += [f["filename"] for f in d["nodes"]]
        if not d["pageInfo"]["hasNextPage"]:
            break
        apres = d["pageInfo"]["endCursor"]
    open(os.path.join(dossier, "_fichiers.txt"), "w").write("\n".join(noms) + "\n")
    voulus = [n for n in noms if n.startswith(("config/", "templates/", "blocks/_product-card", "snippets/product-card")) or
              (n.startswith("sections/") and n.endswith(".json")) or n in ("layout/theme.liquid", "locales/fr.json",
                                                                         "locales/nl.json", "locales/en.default.json")]
    for i in range(0, len(voulus), 40):
        d = s.gql(Q_CONTENU, {"id": main["id"], "noms": voulus[i:i + 40]})["theme"]["files"]["nodes"]
        for f in d:
            c = (f.get("body") or {}).get("content")
            if c is None:
                continue
            chemin = os.path.join(dossier, f["filename"])
            os.makedirs(os.path.dirname(chemin), exist_ok=True)
            open(chemin, "w", encoding="utf-8").write(c)
    print("Fichiers exportés : %d sur %d" % (len(voulus), len(noms)))


APERCU = "Qosmi A (aperçu)"
PARFUMS = ["Parfums femme", "Parfums homme", "Parfums mixtes", "Parfums enfants"]
SOINS = ["Soins du visage", "Soins du corps", "Cheveux", "Déodorants", "Homme", "Solaires et autobronzants",
         "Soins et beauté", "Maison"]
NICHE = ["Nishane", "Xerjoff", "Parfums de Marly", "Initio", "Mancera", "Montale", "Maison Francis Kurkdjian", "Creed",
         "Amouage", "By Kilian", "Le Labo", "Sospiro", "Frederic Malle", "Diptyque", "Juliette Has A Gun", "Ex Nihilo",
         "BDK Parfums", "Acqua di Parma", "Tiziana Terenzi", "Orto Parisi", "Nasomatto", "Mind Games",
         "Marc-Antoine Barrois", "Clive Christian", "Thomas Kosmala", "Histoires de Parfums", "Serge Lutens",
         "Goldfield & Banks", "Kajal", "Electimuss", "Vilhelm Parfumerie", "Jo Malone", "Escentric Molecules",
         "Lorenzo Pazzaglia", "Maison Crivelli", "Matiere Premiere", "Fugazzi", "Ormonde Jayne", "Bond No. 9",
         "Carner Barcelona", "Unique'e Luxury", "Zarkoperfume", "Liquides Imaginaires", "Franck Boclet", "Moresque"]
ORIENTAUX = ["Lattafa", "Armaf", "Al Haramain", "French Avenue", "Afnan", "Rasasi", "Ajmal", "Khadlaj", "Paris Corner",
             "Zimaya", "Maison Alhambra", "Fragrance World", "Ard Al Zaafaran", "Swiss Arabian", "Arabian Oud"]
# Parfums arabes (catégorie demandée par Amine le 08/11/2026) : maisons des Émirats, d'Arabie saoudite et d'Oman.
ARABES = sorted(set(ORIENTAUX + [
    "Amouage", "Al Wataniah", "Ahmed Al Maghribi", "Riiffs", "Emir", "Arabiyat Prestige", "Arabiyat Sugar", "Orientica",
    "Hamidi", "Nasma", "Grandeur", "Gulf Orchid", "Asdaaf", "Khalis", "Anfar", "Anfar 1950", "Maison Asrar", "Pendora Scents",
    "Privezarah", "Risala", "Risala Elite", "Nusuk", "Athoor Al Alam", "Azha Perfumes", "Dubai Garden", "Marquisa Dubai",
    "Niche Emarati", "Al Malakia", "Alghabra", "The Spirit of Dubai", "Dar El Ward", "Assala Prime", "La Fede", "Blend Oud",
    "House Of Perfumes"]))
COLLECTIONS = [  # (handle, titre, colonne, valeurs)
    ("parfums", "Parfums", "TYPE", PARFUMS), ("parfums-femme", "Parfums femme", "TYPE", ["Parfums femme"]),
    ("parfums-homme", "Parfums homme", "TYPE", ["Parfums homme"]), ("parfums-mixtes", "Parfums mixtes", "TYPE", ["Parfums mixtes"]),
    ("parfums-enfants", "Parfums enfants", "TYPE", ["Parfums enfants"]), ("niche", "Parfums de niche", "VENDOR", NICHE),
    ("orientaux", "Parfums orientaux", "VENDOR", ORIENTAUX), ("parfums-arabes", "Parfums arabes", "VENDOR", ARABES), ("testeurs", "Testeurs", "TAG", ["Testeurs"]),
    ("coffrets", "Coffrets", "TYPE", ["Coffrets"]), ("soins", "Soins", "TYPE", SOINS),
    ("maquillage", "Maquillage", "TYPE", ["Maquillage"]),
]
MENU = [("Parfums", "parfums", [("Femme", "parfums-femme"), ("Homme", "parfums-homme"), ("Mixte", "parfums-mixtes")]),
        ("Femme", "parfums-femme", []), ("Homme", "parfums-homme", []),
        ("Niche", "niche", []),  # Testeurs retiré le 08/11/2026 (en suspens, question juridique)
        # ("Parfums arabes", "parfums-arabes", []),  # 08/11/2026 : à activer quand les parfums arabes seront en ligne
        ("Marques", "page:marques", []),  # 08/11/2026 : Femme, Homme et Marques ajoutés (demande d'Amine)
        ("Journal", "blog:journal", [])]  # 08/11/2026 : le blog (scripts/blog.py)
LOGOS = ["qosmi-logo.png", "qosmi-logo-blanc.png", "qosmi-favicon.png"]


def erreurs(d, cle):
    e = (d.get(cle) or {}).get("userErrors") or []
    if e:
        raise RuntimeError("%s : %s" % (cle, json.dumps(e, ensure_ascii=False)[:400]))
    return d[cle]


def publication_boutique(s):
    pubs = s.gql("{ publications(first: 20) { nodes { id name } } }")["publications"]["nodes"]
    return next((p["id"] for p in pubs if p["name"] in ("Online Store", "Boutique en ligne")), pubs[0]["id"] if pubs else None)


def collections(s):
    pub = publication_boutique(s)
    ids = {}
    for handle, titre, col, valeurs in COLLECTIONS:
        regles = [{"column": col, "relation": "EQUALS", "condition": v} for v in valeurs]
        ex = s.gql("query($h: String!) { collectionByIdentifier(identifier: {handle: $h}) { id } }", {"h": handle}).get(
            "collectionByIdentifier")
        if ex:
            r = erreurs(s.gql("""mutation($c: CollectionInput!) { collectionUpdate(input: $c) { collection { id } userErrors { field message } } }""",
                              {"c": {"id": ex["id"], "title": titre, "ruleSet": {"appliedDisjunctively": True, "rules": regles}}}),
                        "collectionUpdate")
        else:
            r = erreurs(s.gql("""mutation($c: CollectionInput!) { collectionCreate(input: $c) { collection { id } userErrors { field message } } }""",
                              {"c": {"title": titre, "handle": handle, "sortOrder": "BEST_SELLING",
                                     "ruleSet": {"appliedDisjunctively": True, "rules": regles}}}), "collectionCreate")
        cid = r["collection"]["id"]
        ids[handle] = cid
        if pub:
            s.gql("""mutation($id: ID!, $p: ID!) { publishablePublish(id: $id, input: [{publicationId: $p}]) { userErrors { message } } }""",
                  {"id": cid, "p": pub})
        print("  collection", handle, "OK")
    return ids


def page_marques(s):
    """Page « Marques » : toutes les marques de la sélection, de A à Z, chacune vers ses parfums."""
    import html as _h, urllib.parse as _u
    marques = sorted(json.load(open(os.path.join(os.path.dirname(ICI), "config", "selection.json"), encoding="utf-8"))["marques"],
                     key=lambda m: m.lower())
    groupes = {}
    for m in marques:
        l = m[0].upper() if m[0].isalpha() else "#"
        groupes.setdefault(l, []).append(m)
    corps = ["<p>Toutes les maisons que nous proposons, des grands classiques aux créateurs de niche.</p>"]
    for l in sorted(groupes):
        liens = " · ".join('<a href="/collections/vendors?q=%s">%s</a>' % (_u.quote(m), _h.escape(m)) for m in groupes[l])
        corps.append("<h2>%s</h2><p>%s</p>" % (l, liens))
    champs = {"title": "Marques", "handle": "marques", "body": "\n".join(corps), "isPublished": True}
    d = s.gql('query($q: String!) { pages(first: 1, query: $q) { nodes { id } } }', {"q": "handle:marques"})["pages"]["nodes"]
    if d:
        r = erreurs(s.gql("mutation($id: ID!, $p: PageUpdateInput!) { pageUpdate(id: $id, page: $p) { page { id } userErrors { field message } } }",
                          {"id": d[0]["id"], "p": champs}), "pageUpdate")
    else:
        r = erreurs(s.gql("mutation($p: PageCreateInput!) { pageCreate(page: $p) { page { id } userErrors { field message } } }",
                          {"p": champs}), "pageCreate")
    print("  page Marques OK (%d marques)" % len(marques))
    return r["page"]["id"]


def menu(s, ids):
    menus = s.gql("{ menus(first: 20) { nodes { id handle title } } }")["menus"]["nodes"]
    m = next((x for x in menus if x["handle"] == "main-menu"), None)
    pages = {"page:marques": page_marques(s)} if any(h == "page:marques" for _, h, _ in MENU) else {}

    blogs = {b["handle"]: b["id"] for b in s.gql("{ blogs(first: 20) { nodes { id handle } } }")["blogs"]["nodes"]}

    def entree(t, h, sous=()):
        if h.startswith("blog:"):
            return {"title": t, "type": "BLOG", "resourceId": blogs[h[5:]], "items": []}
        if h.startswith("page:"):
            return {"title": t, "type": "PAGE", "resourceId": pages[h], "items": []}
        return {"title": t, "type": "COLLECTION", "resourceId": ids[h], "items": [entree(st, sh) for st, sh in sous]}
    items = [entree(t, h, sous) for t, h, sous in MENU]
    if m:
        erreurs(s.gql("""mutation($id: ID!, $t: String!, $h: String, $i: [MenuItemUpdateInput!]!) { menuUpdate(id: $id, title: $t, handle: $h, items: $i) { menu { id } userErrors { field message } } }""",
                      {"id": m["id"], "t": m["title"], "h": "main-menu", "i": items}), "menuUpdate")
    else:
        erreurs(s.gql("""mutation($t: String!, $h: String!, $i: [MenuItemCreateInput!]!) { menuCreate(title: $t, handle: $h, items: $i) { menu { id } userErrors { field message } } }""",
                      {"t": "Menu principal", "h": "main-menu", "i": items}), "menuCreate")
    print("  menu principal OK")


def televerser_image(s, chemin):
    nom = os.path.basename(chemin)
    deja = s.gql("query($q: String!) { files(first: 5, query: $q) { nodes { id fileStatus ... on MediaImage { image { url } } } } }",
                 {"q": "filename:%s" % nom})["files"]["nodes"]
    if deja:
        return
    cible = erreurs(s.gql("""mutation($i: [StagedUploadInput!]!) { stagedUploadsCreate(input: $i) { stagedTargets { url resourceUrl parameters { name value } } userErrors { message } } }""",
                          {"i": [{"resource": "IMAGE", "filename": nom, "mimeType": "image/png", "httpMethod": "POST"}]}),
                    "stagedUploadsCreate")["stagedTargets"][0]
    limite = "----qosmi" + uuid.uuid4().hex
    corps = b"".join(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (limite, p["name"], p["value"])).encode()
                     for p in cible["parameters"])
    corps += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\nContent-Type: image/png\r\n\r\n" % (limite, nom)).encode()
    corps += open(chemin, "rb").read() + ("\r\n--%s--\r\n" % limite).encode()
    urllib.request.urlopen(urllib.request.Request(cible["url"], data=corps, method="POST",
                                                  headers={"Content-Type": "multipart/form-data; boundary=" + limite}), timeout=120).read()
    erreurs(s.gql("""mutation($f: [FileCreateInput!]!) { fileCreate(files: $f) { files { id fileStatus } userErrors { field message } } }""",
                  {"f": [{"originalSource": cible["resourceUrl"], "contentType": "IMAGE", "filename": nom, "alt": "Qosmi"}]}), "fileCreate")
    print("  image", nom, "envoyée")


def fichiers_theme(s, tid, noms):
    d = s.gql(Q_CONTENU, {"id": tid, "noms": noms})["theme"]["files"]["nodes"]
    return {f["filename"]: f["body"]["content"] for f in d if (f.get("body") or {}).get("content") is not None}


def appliquer():
    from shopify_api import Shopify
    import theme_a
    s = Shopify()
    print("1. Collections")
    ids = collections(s)
    print("2. Menu")
    menu(s, ids)
    print("3. Logo et icône")
    racine = os.path.dirname(ICI)
    for n in LOGOS:
        televerser_image(s, os.path.join(racine, "assets", n))
    time.sleep(10)
    print("4. Copie du thème")
    themes = s.gql(Q_THEMES)["themes"]["nodes"]
    main = next(t for t in themes if t["role"] == "MAIN")
    apercu = next((t for t in themes if t["name"] == APERCU and t["role"] != "MAIN"), None)
    if not apercu:
        r = erreurs(s.gql("""mutation($id: ID!, $n: String) { themeDuplicate(id: $id, name: $n) { newTheme { id name role } userErrors { field message } } }""",
                          {"id": main["id"], "n": APERCU}), "themeDuplicate")
        apercu = r["newTheme"]
        for _ in range(60):
            t = s.gql("query($id: ID!) { theme(id: $id) { processing } }", {"id": apercu["id"]})["theme"]
            if not t["processing"]:
                break
            time.sleep(5)
    print("  thème", apercu["name"], apercu["id"], "(non publié)")
    print("5. Direction A")
    actuels = fichiers_theme(s, main["id"], theme_a.FICHIERS)
    for police in ("jost", "futura", "inter"):
        nouveaux = theme_a.construire(actuels, police)
        r = s.gql("""mutation($id: ID!, $f: [OnlineStoreThemeFilesUpsertFileInput!]!) { themeFilesUpsert(themeId: $id, files: $f) {
                     upsertedThemeFiles { filename } userErrors { filename code message } } }""",
                  {"id": apercu["id"], "f": [{"filename": n, "body": {"type": "TEXT", "value": v}} for n, v in nouveaux.items()]})["themeFilesUpsert"]
        if not r["userErrors"]:
            print("  fichiers envoyés :", ", ".join(f["filename"] for f in r["upsertedThemeFiles"]), "· police", police)
            break
        print("  refus avec la police %s : %s" % (police, json.dumps(r["userErrors"], ensure_ascii=False)[:600]))
        if not any("font" in json.dumps(e).lower() for e in r["userErrors"]):
            raise SystemExit("Fichiers refusés par Shopify (voir ci-dessus) : thème publié intact.")
    num = apercu["id"].rsplit("/", 1)[-1]
    boutique = os.environ.get("SHOPIFY_BOUTIQUE", "")
    print("APERÇU : https://%s/?preview_theme_id=%s" % (boutique.replace(".myshopify.com", ".myshopify.com"), num))
    print("ÉDITEUR : Admin Shopify → Boutique en ligne → Thèmes → « %s » → Personnaliser" % APERCU)


def appliquer_rk():
    """Qosmi façon Riklis Karto (07/11/2026) : thème « Qosmi A (aperçu) », publié le 08/11/2026 après accord d'Amine."""
    from shopify_api import Shopify
    import theme_rk
    s = Shopify()
    themes = s.gql(Q_THEMES)["themes"]["nodes"]
    apercu = next(t for t in themes if t["name"] == APERCU)  # publié le 08/11/2026 : c'est désormais le thème du site
    actuels = fichiers_theme(s, apercu["id"], theme_rk.FICHIERS)
    manquants = [n for n in theme_rk.FICHIERS if n not in actuels]
    if manquants:
        raise SystemExit("Fichiers introuvables dans l'aperçu : %s" % manquants)
    marques = json.load(open(os.path.join(os.path.dirname(ICI), "config", "selection.json"), encoding="utf-8"))["marques"]
    liquides, jsons = theme_rk.construire(actuels, marques)
    for lot, nom in ((liquides, "sections, style et mise en page"), (jsons, "modèles")):
        r = s.gql("""mutation($id: ID!, $f: [OnlineStoreThemeFilesUpsertFileInput!]!) { themeFilesUpsert(themeId: $id, files: $f) {
                     upsertedThemeFiles { filename } userErrors { filename code message } } }""",
                  {"id": apercu["id"], "f": [{"filename": n, "body": {"type": "TEXT", "value": v}} for n, v in lot.items()]})["themeFilesUpsert"]
        if r["userErrors"]:
            print("  REFUS (%s) : %s" % (nom, json.dumps(r["userErrors"], ensure_ascii=False)[:3000]))
            raise SystemExit(1)
        print("  %s envoyés : %s" % (nom, ", ".join(f["filename"] for f in r["upsertedThemeFiles"])))
    num = apercu["id"].rsplit("/", 1)[-1]
    print("APERÇU : https://qosmi.be/?preview_theme_id=%s" % num)


def publier():
    """Publie le thème « Qosmi A (aperçu) » (accord d'Amine du 08/11/2026). L'ancien thème reste dans la bibliothèque."""
    from shopify_api import Shopify
    s = Shopify()
    themes = s.gql(Q_THEMES)["themes"]["nodes"]
    t = next(t for t in themes if t["name"] == APERCU)
    if t["role"] == "MAIN":
        print("Déjà publié : %s" % t["name"])
        return
    ancien = next(x for x in themes if x["role"] == "MAIN")
    r = s.gql("mutation($id: ID!) { themePublish(id: $id) { theme { id name role } userErrors { field message } } }", {"id": t["id"]})["themePublish"]
    if r["userErrors"]:
        raise SystemExit("Refus : %s" % r["userErrors"])
    print("Publié : %s (l'ancien thème « %s » reste disponible dans Boutique en ligne → Thèmes)" % (r["theme"]["name"], ancien["name"]))


def menu_seul():
    from shopify_api import Shopify
    s = Shopify()
    menu(s, collections(s))


if __name__ == "__main__":
    if "--publier" in sys.argv:
        publier()
    elif "--menu" in sys.argv:
        menu_seul()
    elif "--theme-rk" in sys.argv:
        appliquer_rk()
    elif "--exporter-apercu" in sys.argv:
        exporter(apercu=True)
    elif "--exporter" in sys.argv:
        exporter()
    elif "--appliquer" in sys.argv:
        appliquer()
    else:
        print(__doc__)
