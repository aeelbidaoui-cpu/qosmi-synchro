#!/usr/bin/env python3
"""Collections par saison et par occasion (13/11/2026, demande d'Amine).

Collections manuelles remplies à partir de config/profils_parfums.json (saison « s » et occasions « o », données
Fragrance Index) : on ajoute les fiches qui correspondent et on retire celles qui ne correspondent plus.
Titre, texte, SEO et adresse en français + traduction néerlandaise. Tri : meilleures ventes.
Seulement les parfums disponibles (sinon les épuisés remontent en tête, faute de ventes) ; lancé à chaque synchro
pour suivre le stock.

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

# 22/11/2026 (Amine, version anglaise) : handle FR -> (adresse EN, titre EN, texte EN, méta EN)
NOTE_EN = " Selection based on the season and the moments when each fragrance is most worn; for guidance only."
D9 = "Genuine, brand-new bottles, delivered in 9 European countries."
EN = {
    "parfums-hiver": ("winter-fragrances", "Winter fragrances",
                      "When it's cold, we crave enveloping scents: amber, vanilla, woody or spicy notes that last and stay close to the skin under your scarf.",
                      "Winter fragrances: amber, vanilla, woody and spicy notes. " + D9),
    "parfums-automne": ("autumn-fragrances", "Autumn fragrances",
                        "For autumn, rounder scents: woods, leather, soft spices, ripe fruit and gourmand notes, between summer freshness and winter warmth.",
                        "Autumn fragrances: woods, leather, soft spices and gourmand notes. " + D9),
    "parfums-printemps": ("spring-fragrances", "Spring fragrances",
                          "In spring, it's time for flowers and freshness: rose, orange blossom, green notes, citrus and light musks.",
                          "Spring fragrances: flowers, green notes and citrus. " + D9),
    "parfums-ete": ("summer-fragrances", "Summer fragrances",
                    "In summer, fresh and bright scents: citrus, marine, aromatic and fruity notes, pleasant even when it's hot.",
                    "Summer fragrances: citrus, marine and fresh notes. " + D9),
    "parfums-bureau": ("fragrances-for-the-office", "Fragrances for the office",
                       "Fragrances that get noticed without bothering anyone: clean, fresh or woody, with a moderate trail, perfect for a working day.",
                       "Office fragrances: fresh, clean, moderate trail. " + D9),
    "parfums-rendez-vous": ("fragrances-for-a-date", "Fragrances for a date",
                            "For a date, fragrances that draw people closer: warm and sensual, often amber, vanilla or floral.",
                            "Date fragrances: warm and sensual. " + D9),
    "parfums-soiree": ("evening-fragrances", "Evening fragrances",
                       "For a night out, fragrances with character: more intense, with a beautiful trail that lasts all night.",
                       "Evening fragrances: intense, with a strong trail. " + D9),
    "parfums-tous-les-jours": ("everyday-fragrances", "Everyday fragrances",
                               "The fragrances you wear without thinking: easy, pleasant, they go with everything and every occasion.",
                               "Everyday fragrances: easy and pleasant. " + D9),
}


# 23/11/2026 (Amine, plan SEO) : pages par note, pour les recherches « parfum vanille », « parfum oud »…
# (handle FR, accords (codes des profils, 5 premiers), mots des notes FR, titre FR, handle NL, titre NL, texte FR, texte NL,
#  handle EN, titre EN, texte EN)
NOTES = [
    ("parfums-vanille", {"vanille"}, ("vanille",), "Parfums à la vanille", "vanille-parfums", "Vanilleparfums",
     "La vanille apporte de la douceur et de la chaleur : gourmande avec le caramel ou la fève tonka, plus sombre avec le tabac ou les bois.",
     "Vanille geeft zachtheid en warmte: zoet met karamel of tonkaboon, donkerder met tabak of hout.",
     "vanilla-fragrances", "Vanilla fragrances",
     "Vanilla brings softness and warmth: gourmand with caramel or tonka bean, darker with tobacco or woods."),
    ("parfums-oud", {"oud"}, ("oud", "agarwood", "bois d'agar"), "Parfums à l'oud", "oud-parfums", "Oudparfums",
     "L'oud, ou bois d'agar, donne des parfums profonds, boisés et parfois fumés, souvent associés à la rose, au safran ou à l'ambre.",
     "Oud of agarhout geeft diepe, houtige en soms rokerige geuren, vaak samen met roos, saffraan of amber.",
     "oud-fragrances", "Oud fragrances",
     "Oud, or agarwood, gives deep, woody and sometimes smoky fragrances, often paired with rose, saffron or amber."),
    ("parfums-cuir", {"cuir"}, ("cuir", "daim"), "Parfums au cuir", "leer-parfums", "Leerparfums",
     "Les notes de cuir et de daim donnent du caractère : doux et poudrés, ou plus fumés et bruts.",
     "Leer- en suèdenoten geven karakter: zacht en poederig, of rokeriger en ruwer.",
     "leather-fragrances", "Leather fragrances",
     "Leather and suede notes add character: soft and powdery, or smokier and rawer."),
    ("parfums-rose", {"rose"}, ("rose",), "Parfums à la rose", "rozenparfums", "Rozenparfums",
     "La rose se porte de mille façons : fraîche et fruitée, poudrée, ou profonde avec l'oud et les épices.",
     "Roos draag je op duizend manieren: fris en fruitig, poederig, of diep met oud en kruiden.",
     "rose-fragrances", "Rose fragrances",
     "Rose can be worn in a thousand ways: fresh and fruity, powdery, or deep with oud and spices."),
    ("parfums-ambres", {"ambre"}, ("ambre", "ambre gris"), "Parfums ambrés", "amberparfums", "Amberparfums",
     "Les parfums ambrés sont chauds et enveloppants : résines, vanille, épices douces et bois.",
     "Amberparfums zijn warm en omhullend: harsen, vanille, zachte kruiden en hout.",
     "amber-fragrances", "Amber fragrances",
     "Amber fragrances are warm and enveloping: resins, vanilla, soft spices and woods."),
    ("parfums-boises", {"boise"}, ("santal", "cèdre", "vétiver"), "Parfums boisés", "houtige-parfums", "Houtige parfums",
     "Santal crémeux, cèdre sec, vétiver terreux : les parfums boisés sont élégants et faciles à porter toute l'année.",
     "Romig sandelhout, droge ceder, aardse vetiver: houtige parfums zijn elegant en het hele jaar draagbaar.",
     "woody-fragrances", "Woody fragrances",
     "Creamy sandalwood, dry cedar, earthy vetiver: woody fragrances are elegant and easy to wear all year round."),
    ("parfums-gourmands", {"gourmand", "caramel", "chocolat", "cafe", "miel", "noisette", "amande"}, ("caramel", "praliné", "chocolat", "café", "miel"),
     "Parfums gourmands", "zoete-parfums", "Zoete parfums",
     "Caramel, praliné, café, chocolat ou miel : des parfums qui rappellent la pâtisserie, chaleureux et réconfortants.",
     "Karamel, praliné, koffie, chocolade of honing: geuren die aan gebak doen denken, warm en troostend.",
     "gourmand-fragrances", "Gourmand fragrances",
     "Caramel, praline, coffee, chocolate or honey: fragrances that recall patisserie, warm and comforting."),
    ("parfums-agrumes", {"agrumes"}, ("bergamote", "citron", "mandarine", "pamplemousse"), "Parfums aux agrumes", "citrusparfums", "Citrusparfums",
     "Bergamote, citron, mandarine, pamplemousse : des parfums frais et lumineux, parfaits quand il fait beau.",
     "Bergamot, citroen, mandarijn, pompelmoes: frisse en heldere geuren, perfect als het mooi weer is.",
     "citrus-fragrances", "Citrus fragrances",
     "Bergamot, lemon, mandarin, grapefruit: fresh and bright fragrances, perfect in sunny weather."),
    ("parfums-musques", {"musque"}, ("musc", "musc blanc"), "Parfums musqués", "muskusparfums", "Muskusparfums",
     "Le musc donne un effet « peau propre », doux et proche du corps, ou plus sensuel selon les accords.",
     "Muskus geeft een effect van 'schone huid', zacht en dicht bij het lichaam, of sensueler naargelang de akkoorden.",
     "musky-fragrances", "Musky fragrances",
     "Musk gives a 'clean skin' effect, soft and close to the body, or more sensual depending on the accords."),
    ("parfums-epices", {"epice_chaud", "cannelle"}, ("cannelle", "cardamome", "safran", "poivre"), "Parfums épicés", "kruidige-parfums", "Kruidige parfums",
     "Cannelle, cardamome, safran ou poivre : des parfums épicés qui réchauffent et donnent du relief.",
     "Kaneel, kardemom, saffraan of peper: kruidige geuren die verwarmen en reliëf geven.",
     "spicy-fragrances", "Spicy fragrances",
     "Cinnamon, cardamom, saffron or pepper: spicy fragrances that warm up and add depth."),
    ("parfums-fleurs-blanches", {"fleurs_blanches", "tubereuse", "jasmin"}, ("jasmin", "tubéreuse", "fleur d'oranger", "gardénia"),
     "Parfums aux fleurs blanches", "witte-bloemen-parfums", "Parfums met witte bloemen",
     "Jasmin, tubéreuse, fleur d'oranger, gardénia : des fleurs blanches lumineuses, crémeuses ou solaires.",
     "Jasmijn, tuberoos, oranjebloesem, gardenia: stralende witte bloemen, romig of zonnig.",
     "white-floral-fragrances", "White floral fragrances",
     "Jasmine, tuberose, orange blossom, gardenia: radiant white flowers, creamy or sunny."),
    ("parfums-tabac", {"tabac"}, ("tabac", "feuille de tabac"), "Parfums au tabac", "tabaksparfums", "Tabaksparfums",
     "Le tabac donne des parfums chauds et miellés, souvent avec la vanille, le cuir ou les fruits secs.",
     "Tabak geeft warme, honingachtige geuren, vaak met vanille, leer of gedroogd fruit.",
     "tobacco-fragrances", "Tobacco fragrances",
     "Tobacco gives warm, honeyed fragrances, often with vanilla, leather or dried fruit."),
    ("parfums-iris", {"iris", "poudre"}, ("iris",), "Parfums à l'iris", "irisparfums", "Irisparfums",
     "L'iris donne des parfums poudrés, élégants et un peu froids, entre fleur et cosmétique.",
     "Iris geeft poederige, elegante en wat koele geuren, tussen bloem en cosmetica.",
     "iris-fragrances", "Iris fragrances",
     "Iris gives powdery, elegant and slightly cool fragrances, between flower and cosmetics."),
    ("parfums-frais-marins", {"aquatique", "ozonique", "frais"}, ("notes marines", "sel marin", "notes aquatiques"),
     "Parfums frais et marins", "frisse-zeeparfums", "Frisse en zilte parfums",
     "Notes marines, sel, air frais : des parfums légers qui rappellent la mer, faciles à porter en journée.",
     "Zeenoten, zout, frisse lucht: lichte geuren die aan de zee doen denken, makkelijk overdag te dragen.",
     "fresh-marine-fragrances", "Fresh and marine fragrances",
     "Marine notes, salt, fresh air: light fragrances that recall the sea, easy to wear during the day."),
]
NOTE_NOTES_FR = " Sélection faite d'après les accords et les notes de chaque parfum ; à prendre comme une indication."
NOTE_NOTES_NL = " Selectie op basis van de akkoorden en noten van elk parfum; louter indicatief."
NOTE_NOTES_EN = " Selection based on each fragrance's accords and notes; for guidance only."


def mots_suffisent(mots):
    return bool(set(mots) & {"oud", "agarwood", "bois d'agar", "cuir", "daim", "tabac", "feuille de tabac", "notes marines", "sel marin", "notes aquatiques"})


def membres_notes(P, accords, mots):
    out = []
    for h, v in P.items():
        if "testeur" in h or "tester" in h:
            continue
        ac = set((v.get("ac") or [])[:3])  # les 3 accords dominants
        notes = [n.lower() for k in ("t", "c", "f", "n") for n in ((v.get("nf") or {}).get(k) or [])]
        # la note seule suffit pour les matières marquantes (oud, cuir, tabac, notes marines) ; sinon accord dominant
        if ac & accords or (mots_suffisent(mots) and any(any(m == n or n.startswith(m + " ") for m in mots) for n in notes)):
            out.append(h)
    return sorted(out)


for _h, _ac, _mots, _tfr, _hnl, _tnl, _xfr, _xnl, _hen, _ten, _xen in NOTES:
    COLLECTIONS.append((_h, "NOTES", (_ac, _mots), _tfr, _hnl, _tnl, _xfr, _xnl,
                        "%s : une sélection de parfums originaux et neufs, livrés partout en Belgique." % _tfr,
                        "%s: een selectie van originele, nieuwe parfums, geleverd in heel België." % _tnl))
    EN[_h] = (_hen, _ten, _xen, "%s: a selection of genuine, brand-new fragrances, delivered in 9 European countries." % _ten)


def disponibles():
    """Fiches en vente (au moins un format disponible), lues sur products.json. Ensemble vide si la boutique ne répond pas."""
    import urllib.request
    h = set()
    try:
        for page in range(1, 60):
            r = json.load(urllib.request.urlopen(urllib.request.Request("https://qosmi.be/products.json?limit=250&page=%d" % page,
                                                                        headers={"User-Agent": "QosmiSynchro/1.0"}), timeout=30))
            if not r.get("products"):
                break
            h |= {x["handle"] for x in r["products"] if any(v.get("available") for v in x["variants"])}
    except Exception as e:
        print("disponibilités : %s" % e)
        return set()
    return h if len(h) > 300 else set()


def main():
    P = json.load(open(os.path.join(RACINE, "config", "profils_parfums.json"), encoding="utf-8"))["parfums"]
    voulus = {c[0]: (membres_notes(P, *c[2]) if c[1] == "NOTES" else
                     sorted(h for h, v in P.items() if c[2] in v.get(c[1], []) and "testeur" not in h and "tester" not in h))
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
    dispo = disponibles()
    print("parfums disponibles sur la boutique : %d" % len(dispo))
    for h, cle, val, t_fr, h_nl, t_nl, x_fr, x_nl, m_fr, m_nl in COLLECTIONS:
        nf, nn, ne = (NOTE_NOTES_FR, NOTE_NOTES_NL, NOTE_NOTES_EN) if cle == "NOTES" else (NOTE_FR, NOTE_NL, NOTE_EN)
        champs = {"title": t_fr, "descriptionHtml": "<p>%s%s</p>" % (x_fr, nf), "sortOrder": "BEST_SELLING",
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
        cible = {ids[x] for x in voulus[h] if x in ids and (not dispo or x in dispo)}
        ajout, retrait = sorted(cible - dedans), sorted(dedans - cible)
        for i in range(0, len(ajout), 250):
            e = s.gql("mutation($id: ID!, $p: [ID!]!) { collectionAddProducts(id: $id, productIds: $p) { userErrors { message } } }",
                      {"id": cid, "p": ajout[i:i + 250]})["collectionAddProducts"]["userErrors"]
            if e:
                print("  ajout : %s" % e)
        for i in range(0, len(retrait), 250):
            s.gql("mutation($id: ID!, $p: [ID!]!) { collectionRemoveProducts(id: $id, productIds: $p) { userErrors { message } } }",
                  {"id": cid, "p": retrait[i:i + 250]})
        tr = traduire(s, cid, {"title": t_nl, "handle": h_nl, "body_html": "<p>%s%s</p>" % (x_nl, nn),
                               "meta_title": "%s | Qosmi" % t_nl, "meta_description": m_nl})
        if h in EN:
            h_en, t_en, x_en, m_en = EN[h]
            tr += " · EN %s" % traduire(s, cid, {"title": t_en, "handle": h_en, "body_html": "<p>%s%s</p>" % (x_en, ne),
                                                 "meta_title": "%s | Qosmi" % t_en, "meta_description": m_en[:155]}, locale="en")
        print("%-24s %4d fiches (+%d, -%d) · NL %s" % (h, len(cible), len(ajout), len(retrait), tr))


if __name__ == "__main__":
    main()
