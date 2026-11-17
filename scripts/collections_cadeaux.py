#!/usr/bin/env python3
"""Collections « Idées cadeaux » par budget et pour lui / pour elle (17/11/2026, demande d'Amine).

Collections manuelles, seulement des parfums en vente (au moins un format disponible), hors testeurs, coffrets et
parfums enfants. Budget : la fiche entre si l'un de ses formats disponibles est dans la tranche de prix (prix TTC du
site). Tri : meilleures ventes. Titre, texte, SEO et adresse en FR + traduction NL. Relancé à chaque synchro pour
suivre le stock et les prix ; liées depuis la page Idées cadeaux de Noël.

  python3 scripts/collections_cadeaux.py           # crée / met à jour
  python3 scripts/collections_cadeaux.py --essai   # compte seulement
"""
import json, os, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ESSAI = "--essai" in sys.argv
TYPES = {"Parfums femme", "Parfums homme", "Parfums mixtes"}
LIVRE = " Parfums originaux et neufs, en stock, livrés partout en Belgique."
LIVRE_NL = " Originele, nieuwe parfums, op voorraad, geleverd in heel België."

# (handle, test, titre FR, handle NL, titre NL, texte FR, texte NL)
COLLECTIONS = [
    ("cadeaux-moins-30", lambda t, p: p < 30, "Cadeaux parfum à moins de 30 €", "parfumcadeaus-tot-30", "Parfumcadeaus tot 30 €",
     "Des idées de parfums à offrir à moins de 30 € : petits formats, eaux de toilette et belles découvertes.",
     "Parfums om cadeau te doen voor minder dan 30 €: kleine formaten, eaux de toilette en mooie ontdekkingen."),
    ("cadeaux-30-50", lambda t, p: 30 <= p < 50, "Cadeaux parfum de 30 à 50 €", "parfumcadeaus-30-50", "Parfumcadeaus van 30 tot 50 €",
     "Des parfums à offrir entre 30 et 50 €, pour faire plaisir sans se ruiner.",
     "Parfums om cadeau te doen tussen 30 en 50 €, om iemand te verwennen zonder je blauw te betalen."),
    ("cadeaux-50-80", lambda t, p: 50 <= p < 80, "Cadeaux parfum de 50 à 80 €", "parfumcadeaus-50-80", "Parfumcadeaus van 50 tot 80 €",
     "Des parfums de marque et de niche à offrir entre 50 et 80 €.",
     "Merk- en nicheparfums om cadeau te doen tussen 50 en 80 €."),
    ("cadeaux-plus-80", lambda t, p: p >= 80, "Cadeaux parfum à plus de 80 €", "parfumcadeaus-vanaf-80", "Parfumcadeaus vanaf 80 €",
     "Pour un grand cadeau : les parfums de prestige et de niche à plus de 80 €.",
     "Voor een groot cadeau: prestige- en nicheparfums vanaf 80 €."),
    ("cadeaux-pour-lui", lambda t, p: t == "Parfums homme", "Cadeaux parfum pour lui", "parfumcadeaus-voor-hem", "Parfumcadeaus voor hem",
     "Des parfums pour homme à offrir, des grands classiques aux créations de niche.",
     "Herenparfums om cadeau te doen, van grote klassiekers tot nichecreaties."),
    ("cadeaux-pour-elle", lambda t, p: t == "Parfums femme", "Cadeaux parfum pour elle", "parfumcadeaus-voor-haar", "Parfumcadeaus voor haar",
     "Des parfums pour femme à offrir, des grands classiques aux créations de niche.",
     "Damesparfums om cadeau te doen, van grote klassiekers tot nichecreaties."),
]


def catalogue():
    """{handle: (type, [prix des formats disponibles])} lu sur products.json (vide si la boutique ne répond pas)."""
    out = {}
    try:
        for page in range(1, 60):
            r = json.load(urllib.request.urlopen(urllib.request.Request("https://qosmi.be/products.json?limit=250&page=%d" % page,
                                                                        headers={"User-Agent": "QosmiSynchro/1.0"}), timeout=30))
            if not r.get("products"):
                break
            for x in r["products"]:
                h = x["handle"]
                if x.get("product_type") not in TYPES or "testeur" in h or "tester" in h:
                    continue
                prix = [float(v["price"]) for v in x["variants"] if v.get("available")]
                if prix:
                    out[h] = (x["product_type"], prix)
    except Exception as e:
        print("catalogue : %s" % e)
        return {}
    return out if len(out) > 300 else {}


def main():
    cat = catalogue()
    if not cat:
        print("catalogue illisible : rien changé")
        return
    voulus = {c[0]: {h for h, (t, prix) in cat.items() if any(c[1](t, p) for p in prix)} for c in COLLECTIONS}
    for c in COLLECTIONS:
        print("%-20s %4d parfums" % (c[0], len(voulus[c[0]])))
    if ESSAI:
        return
    from shopify_api import Shopify
    from seo_boutique import traduire
    from site_theme import publication_boutique
    s = Shopify()
    pub = publication_boutique(s)
    ids, apres = {}, None
    while True:
        r = s.gql("""query($a: String) { products(first: 250, after: $a, query: "status:active published_status:published") {
                     nodes { id handle } pageInfo { hasNextPage endCursor } } }""", {"a": apres})["products"]
        ids.update({p["handle"]: p["id"] for p in r["nodes"]})
        if not r["pageInfo"]["hasNextPage"]:
            break
        apres = r["pageInfo"]["endCursor"]
    for h, _, t_fr, h_nl, t_nl, x_fr, x_nl in COLLECTIONS:
        champs = {"title": t_fr, "descriptionHtml": "<p>%s%s</p>" % (x_fr, LIVRE), "sortOrder": "BEST_SELLING",
                  "seo": {"title": "%s | Qosmi" % t_fr, "description": (x_fr + LIVRE)[:155]}}
        ex = s.gql("query($h: String!) { collectionByIdentifier(identifier: {handle: $h}) { id } }", {"h": h}).get("collectionByIdentifier")
        if ex:
            r = s.gql("mutation($c: CollectionInput!) { collectionUpdate(input: $c) { collection { id } userErrors { field message } } }",
                      {"c": dict(champs, id=ex["id"])})["collectionUpdate"]
        else:
            r = s.gql("mutation($c: CollectionInput!) { collectionCreate(input: $c) { collection { id } userErrors { field message } } }",
                      {"c": dict(champs, handle=h)})["collectionCreate"]
        if r["userErrors"]:
            print("%s : ERREUR %s" % (h, r["userErrors"]))
            continue
        cid = r["collection"]["id"]
        if pub:
            s.gql("mutation($id: ID!, $p: ID!) { publishablePublish(id: $id, input: [{publicationId: $p}]) { userErrors { message } } }",
                  {"id": cid, "p": pub})
        dedans, apres = set(), None
        while True:
            r = s.gql("""query($id: ID!, $a: String) { collection(id: $id) { products(first: 250, after: $a) {
                         nodes { id } pageInfo { hasNextPage endCursor } } } }""", {"id": cid, "a": apres})["collection"]["products"]
            dedans |= {p["id"] for p in r["nodes"]}
            if not r["pageInfo"]["hasNextPage"]:
                break
            apres = r["pageInfo"]["endCursor"]
        cible = {ids[x] for x in voulus[h] if x in ids}
        ajout, retrait = sorted(cible - dedans), sorted(dedans - cible)
        for i in range(0, len(ajout), 250):
            e = s.gql("mutation($id: ID!, $p: [ID!]!) { collectionAddProducts(id: $id, productIds: $p) { userErrors { message } } }",
                      {"id": cid, "p": ajout[i:i + 250]})["collectionAddProducts"]["userErrors"]
            if e:
                print("  ajout : %s" % e)
        for i in range(0, len(retrait), 250):
            s.gql("mutation($id: ID!, $p: [ID!]!) { collectionRemoveProducts(id: $id, productIds: $p) { userErrors { message } } }",
                  {"id": cid, "p": retrait[i:i + 250]})
        tr = traduire(s, cid, {"title": t_nl, "handle": h_nl, "body_html": "<p>%s%s</p>" % (x_nl, LIVRE_NL),
                               "meta_title": "%s | Qosmi" % t_nl, "meta_description": (x_nl + LIVRE_NL)[:155]})
        print("%-20s %4d parfums (+%d, -%d) · NL %s" % (h, len(cible), len(ajout), len(retrait), tr))


if __name__ == "__main__":
    main()
