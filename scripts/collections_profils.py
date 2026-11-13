#!/usr/bin/env python3
"""Collections par saison et par occasion (13/11/2026, demande d'Amine).

Collections manuelles remplies à partir de config/profils_parfums.json (saison « s » et occasions « o », données
Fragrance Index) : on ajoute les fiches qui correspondent et on retire celles qui ne correspondent plus.
Titre, texte, SEO et adresse en français + traduction néerlandaise. Tri : meilleures ventes.

  python3 scripts/collections_profils.py           # crée / met à jour
  python3 scripts/collections_profils.py --essai   # compte seulement
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESSAI = "--essai" in sys.argv
NOTE_FR = " Sélection faite d'après la saison et les moments où chaque parfum est le plus porté ; à prendre comme une indication."
NOTE_NL = " Selectie op basis van het seizoen en de momenten waarop elk parfum het meest gedragen wordt; louter indicatief."

# (handle FR, clé, valeur, titre FR, handle NL, titre NL, texte FR, texte NL, meta FR, meta NL)
COLLECTIONS = [
    ("parfums-hiver", "s", "hiver", "Parfums d'hiver", "winterparfums", "Winterparfums",
     "Quand il fait froid, on a envie de parfums enveloppants : notes ambrées, vanillées, boisées ou épicées, qui tiennent bien et restent près de la peau sous l'écharpe.",
     "Als het koud is, zin in omhullende geuren: amber, vanille, hout of kruiden, die lang blijven hangen, ook onder je sjaal.",
     "Parfums d'hiver : notes ambrées, vanillées, boisées et épicées. Flacons originaux et neufs, livrés partout en Belgique.",
     "Winterparfums: amber, vanille, hout en kruiden. Originele, nieuwe flacons, geleverd in heel België."),
    ("parfums-automne", "s", "automne", "Parfums d'automne", "herfstparfums", "Herfstparfums",
     "Pour l'automne, des parfums plus ronds : bois, cuir, épices douces, fruits mûrs et notes gourmandes, entre la fraîcheur de l'été et la chaleur de l'hiver.",
     "Voor de herfst ronde geuren: hout, leer, zachte kruiden, rijp fruit en zoete noten, tussen de frisheid van de zomer en de warmte van de winter.",
     "Parfums d'automne : bois, cuir, épices douces et notes gourmandes. Flacons originaux et neufs, livrés partout en Belgique.",
     "Herfstparfums: hout, leer, zachte kruiden en zoete noten. Originele, nieuwe flacons, geleverd in heel België."),
    ("parfums-printemps", "s", "printemps", "Parfums de printemps", "lenteparfums", "Lenteparfums",
     "Au printemps, place aux fleurs et à la fraîcheur : rose, fleur d'oranger, notes vertes, agrumes et muscs légers.",
     "In de lente kiezen we voor bloemen en frisheid: roos, oranjebloesem, groene noten, citrus en lichte muskus.",
     "Parfums de printemps : fleurs, notes vertes et agrumes. Flacons originaux et neufs, livrés partout en Belgique.",
     "Lenteparfums: bloemen, groene noten en citrus. Originele, nieuwe flacons, geleverd in heel België."),
    ("parfums-ete", "s", "ete", "Parfums d'été", "zomerparfums", "Zomerparfums",
     "En été, des parfums frais et lumineux : agrumes, notes marines, aromatiques et fruités, agréables même quand il fait chaud.",
     "In de zomer frisse, lichte geuren: citrus, zeeachtige, aromatische en fruitige noten, ook aangenaam als het warm is.",
     "Parfums d'été : agrumes, notes marines et fraîches. Flacons originaux et neufs, livrés partout en Belgique.",
     "Zomerparfums: citrus, zeeachtige en frisse noten. Originele, nieuwe flacons, geleverd in heel België."),
    ("parfums-bureau", "o", "bureau", "Parfums pour le bureau", "parfums-voor-op-kantoor", "Parfums voor op kantoor",
     "Des parfums qui se remarquent sans déranger : propres, frais ou boisés, avec un sillage mesuré, parfaits pour une journée de travail.",
     "Parfums die opvallen zonder te storen: fris, proper of houtig, met een gematigde sillage, ideaal voor een werkdag.",
     "Parfums pour le bureau : frais, propres, sillage mesuré. Flacons originaux et neufs, livrés partout en Belgique.",
     "Parfums voor op kantoor: fris, proper, gematigde sillage. Originele, nieuwe flacons, geleverd in heel België."),
    ("parfums-rendez-vous", "o", "rdv", "Parfums pour un rendez-vous", "parfums-voor-een-date", "Parfums voor een date",
     "Pour un rendez-vous, des parfums qui donnent envie de se rapprocher : chaleureux, sensuels, souvent ambrés, vanillés ou floraux.",
     "Voor een date: geuren die uitnodigen om dichterbij te komen, warm en sensueel, vaak met amber, vanille of bloemen.",
     "Parfums pour un rendez-vous : chaleureux et sensuels. Flacons originaux et neufs, livrés partout en Belgique.",
     "Parfums voor een date: warm en sensueel. Originele, nieuwe flacons, geleverd in heel België."),
    ("parfums-soiree", "o", "soiree", "Parfums de soirée", "parfums-om-uit-te-gaan", "Parfums om uit te gaan",
     "Pour sortir, des parfums qui ont du caractère : plus intenses, avec un beau sillage, qui tiennent toute la nuit.",
     "Om uit te gaan: parfums met karakter, intenser, met een mooie sillage, die de hele avond blijven.",
     "Parfums de soirée : intenses, avec du sillage. Flacons originaux et neufs, livrés partout en Belgique.",
     "Parfums om uit te gaan: intens, met sillage. Originele, nieuwe flacons, geleverd in heel België."),
    ("parfums-tous-les-jours", "o", "quotidien", "Parfums de tous les jours", "parfums-voor-elke-dag", "Parfums voor elke dag",
     "Les parfums qu'on porte sans y réfléchir : faciles, agréables, qui vont avec tout et à toutes les occasions.",
     "De parfums die je zonder nadenken draagt: makkelijk, aangenaam, ze passen bij alles en bij elke gelegenheid.",
     "Parfums de tous les jours : faciles et agréables. Flacons originaux et neufs, livrés partout en Belgique.",
     "Parfums voor elke dag: makkelijk en aangenaam. Originele, nieuwe flacons, geleverd in heel België."),
]


def main():
    P = json.load(open(os.path.join(RACINE, "config", "profils_parfums.json"), encoding="utf-8"))["parfums"]
    voulus = {c[0]: sorted(h for h, v in P.items() if c[2] in v.get(c[1], []) and "testeur" not in h and "tester" not in h)
              for c in COLLECTIONS}
    for c in COLLECTIONS:
        print("%-24s %4d fiches dans les profils" % (c[0], len(voulus[c[0]])))
    if ESSAI:
        return
    from shopify_api import Shopify
    from seo_boutique import traduire
    from site_theme import publication_boutique
    s = Shopify()
    pub = publication_boutique(s)
    ids, apres = {}, None
    while True:  # fiches actives et publiées seulement
        r = s.gql("""query($a: String) { products(first: 250, after: $a, query: "status:active published_status:published") {
                     nodes { id handle } pageInfo { hasNextPage endCursor } } }""", {"a": apres})["products"]
        ids.update({p["handle"]: p["id"] for p in r["nodes"]})
        if not r["pageInfo"]["hasNextPage"]:
            break
        apres = r["pageInfo"]["endCursor"]
    for h, cle, val, t_fr, h_nl, t_nl, x_fr, x_nl, m_fr, m_nl in COLLECTIONS:
        champs = {"title": t_fr, "descriptionHtml": "<p>%s%s</p>" % (x_fr, NOTE_FR), "sortOrder": "BEST_SELLING",
                  "seo": {"title": "%s | Qosmi" % t_fr, "description": m_fr}}
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
        # contenu actuel
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
        tr = traduire(s, cid, {"title": t_nl, "handle": h_nl, "body_html": "<p>%s%s</p>" % (x_nl, NOTE_NL),
                               "meta_title": "%s | Qosmi" % t_nl, "meta_description": m_nl})
        print("%-24s %4d fiches (+%d, -%d) · NL %s" % (h, len(cible), len(ajout), len(retrait), tr))


if __name__ == "__main__":
    main()
