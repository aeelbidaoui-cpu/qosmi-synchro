#!/usr/bin/env python3
"""SEO de la boutique (08/11/2026) : titre et méta-description de l'accueil, textes des collections principales
(FR + NL), et contrôle des EAN (codes-barres) des fiches actives pour Google Shopping."""
import json, os, sys, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ACCUEIL = {
    "fr": ("Qosmi – Parfums de marque et de niche 100 % authentiques en Belgique",
           "Parfumerie en ligne belge : Xerjoff, Creed, Chanel, Dior, Tom Ford et plus de 60 maisons. Parfums authentiques et neufs, livrés en 1 à 2 jours ouvrables."),
    "nl": ("Qosmi – Merk- en nicheparfums, 100% origineel, in België",
           "Belgische online parfumerie: Xerjoff, Creed, Chanel, Dior, Tom Ford en meer dan 60 huizen. Originele, nieuwe parfums, geleverd binnen 1 tot 2 werkdagen."),
}
COLLECTIONS = {  # handle: (titre SEO, méta, texte de la page) FR puis NL
    "parfums": (("Parfums de marque et de niche | Qosmi",
                 "Tous nos parfums pour femme, homme et mixtes : grandes maisons et créateurs de niche, 100 % authentiques, livrés en Belgique en 1 à 2 jours ouvrables.",
                 "<p>Tous nos parfums, des grands classiques aux créateurs de niche. Chaque flacon est authentique et neuf, livré partout en Belgique en 1 à 2 jours ouvrables.</p>"),
                ("Merk- en nicheparfums | Qosmi",
                 "Al onze parfums voor dames, heren en unisex: grote huizen en nichemakers, 100% origineel, geleverd in België binnen 1 tot 2 werkdagen.",
                 "<p>Al onze parfums, van grote klassiekers tot nichemakers. Elke fles is origineel en nieuw, geleverd in heel België binnen 1 tot 2 werkdagen.</p>")),
    "parfums-femme": (("Parfums femme – Chanel, Dior, Guerlain et plus | Qosmi",
                       "Parfums pour femme 100 % authentiques : Chanel, Dior, Guerlain, Yves Saint Laurent, Lancôme et maisons de niche. Livraison en Belgique en 1 à 2 jours.",
                       "<p>Nos parfums pour femme : les grands classiques de Chanel, Dior, Guerlain ou Yves Saint Laurent, et des créations de niche plus confidentielles. Authentiques, neufs et livrés en 1 à 2 jours ouvrables.</p>"),
                      ("Damesparfums – Chanel, Dior, Guerlain en meer | Qosmi",
                       "100% originele damesparfums: Chanel, Dior, Guerlain, Yves Saint Laurent, Lancôme en nichehuizen. Levering in België binnen 1 tot 2 werkdagen.",
                       "<p>Onze damesparfums: de grote klassiekers van Chanel, Dior, Guerlain of Yves Saint Laurent en meer exclusieve nichecreaties. Origineel, nieuw en geleverd binnen 1 tot 2 werkdagen.</p>")),
    "parfums-homme": (("Parfums homme – Creed, Dior, Tom Ford et plus | Qosmi",
                       "Parfums pour homme 100 % authentiques : Creed, Dior Sauvage, Tom Ford, Parfums de Marly, Xerjoff et plus. Livraison en Belgique en 1 à 2 jours.",
                       "<p>Nos parfums pour homme : Creed, Dior, Tom Ford, Parfums de Marly, Xerjoff et bien d'autres. Authentiques, neufs et livrés partout en Belgique en 1 à 2 jours ouvrables.</p>"),
                      ("Herenparfums – Creed, Dior, Tom Ford en meer | Qosmi",
                       "100% originele herenparfums: Creed, Dior Sauvage, Tom Ford, Parfums de Marly, Xerjoff en meer. Levering in België binnen 1 tot 2 werkdagen.",
                       "<p>Onze herenparfums: Creed, Dior, Tom Ford, Parfums de Marly, Xerjoff en vele andere. Origineel, nieuw en geleverd in heel België binnen 1 tot 2 werkdagen.</p>")),
    "parfums-mixtes": (("Parfums mixtes et unisexes | Qosmi",
                        "Parfums mixtes à porter par tout le monde : Acqua di Parma, Le Labo, Maison Francis Kurkdjian, Xerjoff et plus. 100 % authentiques, livrés en Belgique.",
                        "<p>Des parfums pensés pour tout le monde : colognes fraîches, boisés, ambrés. Acqua di Parma, Maison Francis Kurkdjian, Xerjoff et d'autres maisons, authentiques et livrés en 1 à 2 jours ouvrables.</p>"),
                       ("Unisex parfums | Qosmi",
                        "Unisex parfums voor iedereen: Acqua di Parma, Le Labo, Maison Francis Kurkdjian, Xerjoff en meer. 100% origineel, geleverd in België.",
                        "<p>Parfums voor iedereen: frisse colognes, houtige en amberachtige geuren. Acqua di Parma, Maison Francis Kurkdjian, Xerjoff en andere huizen, origineel en geleverd binnen 1 tot 2 werkdagen.</p>")),
    "niche": (("Parfums de niche – Xerjoff, Nishane, Initio, Creed | Qosmi",
               "Parfumerie de niche en ligne : Xerjoff, Nishane, Initio, Parfums de Marly, Creed, Sospiro et plus. Flacons authentiques, livrés en Belgique en 1 à 2 jours.",
               "<p>Les créateurs de niche que nous aimons : Xerjoff, Nishane, Initio, Parfums de Marly, Creed, Sospiro et d'autres maisons d'exception. Authentiques, neufs et livrés en 1 à 2 jours ouvrables.</p>"),
              ("Nicheparfums – Xerjoff, Nishane, Initio, Creed | Qosmi",
               "Online nicheparfumerie: Xerjoff, Nishane, Initio, Parfums de Marly, Creed, Sospiro en meer. Originele flessen, geleverd in België binnen 1 tot 2 werkdagen.",
               "<p>De nichemakers waar we van houden: Xerjoff, Nishane, Initio, Parfums de Marly, Creed, Sospiro en andere bijzondere huizen. Origineel, nieuw en geleverd binnen 1 tot 2 werkdagen.</p>")),
    "testeurs": (("Testeurs de parfum authentiques moins chers | Qosmi",
                  "Testeurs de parfum : le même parfum authentique que la version en boîte, dans un emballage simple, moins cher. Livraison en Belgique en 1 à 2 jours.",
                  "<p>Un testeur, c'est le même parfum authentique que la version vendue en boîte, livré dans un emballage simple, parfois sans bouchon. Le contenu est identique, le prix plus doux.</p>"),
                 ("Originele parfumtesters, voordeliger | Qosmi",
                  "Parfumtesters: dezelfde originele parfum als in de doos, in een eenvoudige verpakking en voordeliger. Levering in België binnen 1 tot 2 werkdagen.",
                  "<p>Een tester is dezelfde originele parfum als de versie in de doos, geleverd in een eenvoudige verpakking, soms zonder dop. Dezelfde inhoud, een zachtere prijs.</p>")),
}


def traduire(s, rid, valeurs):
    tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }",
               {"id": rid})["translatableResource"]
    dig = {x["key"]: x["digest"] for x in (tr or {}).get("translatableContent", [])}
    t = [{"locale": "nl", "key": k, "value": v, "translatableContentDigest": dig[k]} for k, v in valeurs.items() if k in dig]
    if not t:
        return "rien à traduire (clés : %s)" % sorted(dig)
    e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) {
                 userErrors { field message } } }""", {"id": rid, "t": t})["translationsRegister"]["userErrors"]
    return e or "ok (%s)" % ", ".join(x["key"] for x in t)


def main():
    from shopify_api import Shopify
    s = Shopify()
    # --- accueil : métachamps global.title_tag / description_tag de la boutique
    shop = s.gql("{ shop { id } }")["shop"]["id"]
    fr = ACCUEIL["fr"]
    r = s.gql("""mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) { metafields { key } userErrors { field message } } }""",
              {"m": [{"ownerId": shop, "namespace": "global", "key": "title_tag", "type": "single_line_text_field", "value": fr[0]},
                     {"ownerId": shop, "namespace": "global", "key": "description_tag", "type": "multi_line_text_field", "value": fr[1]}]})
    print("Accueil FR :", r["metafieldsSet"]["userErrors"] or "ok")
    try:
        print("Accueil NL :", traduire(s, shop, {"meta_title": ACCUEIL["nl"][0], "meta_description": ACCUEIL["nl"][1]}))
    except Exception as e:
        print("Accueil NL : impossible —", str(e)[:200])
    # --- collections
    for h, ((t_fr, m_fr, b_fr), (t_nl, m_nl, b_nl)) in COLLECTIONS.items():
        c = s.gql("query($h: String!) { collectionByIdentifier(identifier: {handle: $h}) { id } }", {"h": h}).get("collectionByIdentifier")
        if not c:
            print("  collection %s introuvable" % h)
            continue
        r = s.gql("""mutation($c: CollectionInput!) { collectionUpdate(input: $c) { collection { id } userErrors { field message } } }""",
                  {"c": {"id": c["id"], "descriptionHtml": b_fr, "seo": {"title": t_fr, "description": m_fr}}})["collectionUpdate"]
        nl = traduire(s, c["id"], {"body_html": b_nl, "meta_title": t_nl, "meta_description": m_nl})
        print("  collection %-15s FR : %s · NL : %s" % (h, r["userErrors"] or "ok", nl))
    # --- EAN des fiches actives (Google Shopping)
    q = """{ productVariants(query: "product_status:active") { edges { node { id barcode sku product { id } } } } }"""
    d = s.gql("""mutation($q: String!) { bulkOperationRunQuery(query: $q) { bulkOperation { id } userErrors { message } } }""", {"q": q})
    op = d["bulkOperationRunQuery"]["bulkOperation"]["id"]
    while True:
        b = s.gql("query($id: ID!) { bulkOperation(id: $id) { status url } }", {"id": op})["bulkOperation"]
        if b["status"] in ("COMPLETED", "FAILED", "CANCELED", "EXPIRED"):
            break
        time.sleep(5)
    tot = avec = 0
    if b.get("url"):
        for l in urllib.request.urlopen(b["url"]).read().decode().splitlines():
            x = json.loads(l)
            tot += 1
            avec += 1 if (x.get("barcode") or "").strip() else 0
    print("EAN : %d formats actifs, %d avec code-barres, %d sans" % (tot, avec, tot - avec))


if __name__ == "__main__":
    main()
