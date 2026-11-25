#!/usr/bin/env python3
"""SEO de la boutique (08/11/2026) : titre et méta-description de l'accueil, textes des collections principales
(FR + NL), et contrôle des EAN (codes-barres) des fiches actives pour Google Shopping."""
import json, os, sys, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ACCUEIL = {
    "fr": ("Qosmi – Parfums de marque et de niche 100 % authentiques en Belgique",
           "Parfumerie en ligne belge : Xerjoff, Creed, Chanel, Dior, Tom Ford et plus de 100 maisons. Parfums authentiques et neufs, livrés partout en Belgique."),
    "nl": ("Qosmi – Merk- en nicheparfums, 100% origineel, in België",
           "Belgische online parfumerie: Xerjoff, Creed, Chanel, Dior, Tom Ford en meer dan 100 huizen. Originele, nieuwe parfums, geleverd in heel België."),
}
COLLECTIONS = {  # handle: (titre SEO, méta, texte de la page) FR puis NL
    "parfums": (("Parfums de marque et de niche | Qosmi",
                 "Tous nos parfums pour femme, homme et mixtes : grandes maisons et créateurs de niche, 100 % authentiques, livrés partout en Belgique.",
                 "<p>Tous nos parfums, des grands classiques aux créateurs de niche. Chaque flacon est authentique et neuf, livré partout en Belgique.</p>"),
                ("Merk- en nicheparfums | Qosmi",
                 "Al onze parfums voor dames, heren en unisex: grote huizen en nichemakers, 100% origineel, geleverd in heel België.",
                 "<p>Al onze parfums, van grote klassiekers tot nichemakers. Elke fles is origineel en nieuw, geleverd in heel België.</p>")),
    "parfums-femme": (("Parfums femme – Chanel, Dior, Guerlain et plus | Qosmi",
                       "Parfums pour femme 100 % authentiques : Chanel, Dior, Guerlain, Yves Saint Laurent, Lancôme et maisons de niche. Livraison partout en Belgique, offerte dès 2 articles.",
                       "<p>Nos parfums pour femme : les grands classiques de Chanel, Dior, Guerlain ou Yves Saint Laurent, et des créations de niche plus confidentielles. Authentiques, neufs et livrés partout en Belgique.</p>"),
                      ("Damesparfums – Chanel, Dior, Guerlain en meer | Qosmi",
                       "100% originele damesparfums: Chanel, Dior, Guerlain, Yves Saint Laurent, Lancôme en nichehuizen. Levering in heel België, gratis vanaf 2 artikelen.",
                       "<p>Onze damesparfums: de grote klassiekers van Chanel, Dior, Guerlain of Yves Saint Laurent en meer exclusieve nichecreaties. Origineel, nieuw en geleverd in heel België.</p>")),
    "parfums-homme": (("Parfums homme – Creed, Dior, Tom Ford et plus | Qosmi",
                       "Parfums pour homme 100 % authentiques : Creed, Dior Sauvage, Tom Ford, Parfums de Marly, Xerjoff et plus. Livraison partout en Belgique, offerte dès 2 articles.",
                       "<p>Nos parfums pour homme : Creed, Dior, Tom Ford, Parfums de Marly, Xerjoff et bien d'autres. Authentiques, neufs et livrés partout en Belgique.</p>"),
                      ("Herenparfums – Creed, Dior, Tom Ford en meer | Qosmi",
                       "100% originele herenparfums: Creed, Dior Sauvage, Tom Ford, Parfums de Marly, Xerjoff en meer. Levering in heel België, gratis vanaf 2 artikelen.",
                       "<p>Onze herenparfums: Creed, Dior, Tom Ford, Parfums de Marly, Xerjoff en vele andere. Origineel, nieuw en geleverd in heel België.</p>")),
    "parfums-mixtes": (("Parfums mixtes et unisexes | Qosmi",
                        "Parfums mixtes à porter par tout le monde : Acqua di Parma, Le Labo, Maison Francis Kurkdjian, Xerjoff et plus. 100 % authentiques, livrés en Belgique.",
                        "<p>Des parfums pensés pour tout le monde : colognes fraîches, boisés, ambrés. Acqua di Parma, Maison Francis Kurkdjian, Xerjoff et d'autres maisons, authentiques et livrés partout en Belgique.</p>"),
                       ("Unisex parfums | Qosmi",
                        "Unisex parfums voor iedereen: Acqua di Parma, Le Labo, Maison Francis Kurkdjian, Xerjoff en meer. 100% origineel, geleverd in België.",
                        "<p>Parfums voor iedereen: frisse colognes, houtige en amberachtige geuren. Acqua di Parma, Maison Francis Kurkdjian, Xerjoff en andere huizen, origineel en geleverd in heel België.</p>")),
    "niche": (("Parfums de niche – Xerjoff, Nishane, Initio, Creed | Qosmi",
               "Parfumerie de niche en ligne : Xerjoff, Nishane, Initio, Parfums de Marly, Creed, Sospiro et plus. Flacons authentiques, livrés partout en Belgique.",
               "<p>Les créateurs de niche que nous aimons : Xerjoff, Nishane, Initio, Parfums de Marly, Creed, Sospiro et d'autres maisons d'exception. Authentiques, neufs et livrés partout en Belgique.</p>"),
              ("Nicheparfums – Xerjoff, Nishane, Initio, Creed | Qosmi",
               "Online nicheparfumerie: Xerjoff, Nishane, Initio, Parfums de Marly, Creed, Sospiro en meer. Originele flessen, geleverd in heel België.",
               "<p>De nichemakers waar we van houden: Xerjoff, Nishane, Initio, Parfums de Marly, Creed, Sospiro en andere bijzondere huizen. Origineel, nieuw en geleverd in heel België.</p>")),
    "parfums-arabes": (("Parfums arabes – Lattafa, Armaf, Al Haramain, Afnan | Qosmi",
                        "Parfums arabes authentiques : Lattafa, Armaf, Al Haramain, Afnan, Rasasi, Ajmal et d'autres maisons des Émirats. Oud, ambre, épices. Livrés en Belgique.",
                        "<p>Les grandes maisons de la parfumerie arabe : Lattafa, Armaf, Al Haramain, Afnan, Rasasi, Ajmal, Amouage et bien d'autres. "
                        "Des sillages généreux autour du oud, de l'ambre, de la rose et des épices, qui tiennent longtemps sur la peau. "
                        "Chaque flacon est authentique et neuf, livré partout en Belgique.</p>"),
                       ("Arabische parfums – Lattafa, Armaf, Al Haramain, Afnan | Qosmi",
                        "Originele Arabische parfums: Lattafa, Armaf, Al Haramain, Afnan, Rasasi, Ajmal en andere huizen uit de Emiraten. Oud, amber, kruiden. Geleverd in België.",
                        "<p>De grote huizen van de Arabische parfumerie: Lattafa, Armaf, Al Haramain, Afnan, Rasasi, Ajmal, Amouage en vele andere. "
                        "Rijke geuren rond oud, amber, roos en kruiden, die lang op de huid blijven. "
                        "Elke fles is origineel en nieuw, geleverd in heel België.</p>")),
    "testeurs": (("Testeurs de parfum authentiques moins chers | Qosmi",
                  "Testeurs de parfum : le même parfum authentique que la version en boîte, dans un emballage simple, moins cher. Livraison partout en Belgique, offerte dès 2 articles.",
                  "<p>Un testeur, c'est le même parfum authentique que la version vendue en boîte, avec son bouchon, livré dans un emballage simple. Le contenu est identique, le prix plus doux.</p>"),
                 ("Originele parfumtesters, voordeliger | Qosmi",
                  "Parfumtesters: dezelfde originele parfum als in de doos, in een eenvoudige verpakking en voordeliger. Levering in heel België, gratis vanaf 2 artikelen.",
                  "<p>Een tester is dezelfde originele parfum als de versie in de doos, met dop, geleverd in een eenvoudige verpakking. Dezelfde inhoud, een zachtere prijs.</p>")),
}

# 22/11/2026 (Amine, version anglaise) : accueil et collections principales en anglais (marchés hors Belgique / Pays-Bas)
ACCUEIL["en"] = ("Qosmi – 100% authentic designer and niche fragrances",
                 "Belgian online perfumery: Xerjoff, Creed, Chanel, Dior, Tom Ford and over 100 houses. Genuine, brand-new fragrances, delivered in 9 European countries.")
DANS_9 = "delivered in 9 European countries"
COLLECTIONS_EN = {
    "parfums": ("Designer and niche fragrances | Qosmi",
                "All our fragrances for women, men and unisex: great houses and niche creators, 100%% authentic, %s." % DANS_9,
                "<p>All our fragrances, from the great classics to niche creators. Every bottle is genuine and brand-new, %s.</p>" % DANS_9),
    "parfums-femme": ("Women's fragrances – Chanel, Dior, Guerlain and more | Qosmi",
                      "100%% authentic women's fragrances: Chanel, Dior, Guerlain, Yves Saint Laurent, Lancôme and niche houses, %s." % DANS_9,
                      "<p>Our women's fragrances: the great classics from Chanel, Dior, Guerlain or Yves Saint Laurent, and more exclusive niche creations. Genuine, brand-new and %s.</p>" % DANS_9),
    "parfums-homme": ("Men's fragrances – Creed, Dior, Tom Ford and more | Qosmi",
                      "100%% authentic men's fragrances: Creed, Dior Sauvage, Tom Ford, Parfums de Marly, Xerjoff and more, %s." % DANS_9,
                      "<p>Our men's fragrances: Creed, Dior, Tom Ford, Parfums de Marly, Xerjoff and many more. Genuine, brand-new and %s.</p>" % DANS_9),
    "parfums-mixtes": ("Unisex fragrances | Qosmi",
                       "Unisex fragrances for everyone: Acqua di Parma, Le Labo, Maison Francis Kurkdjian, Xerjoff and more. 100%% authentic, %s." % DANS_9,
                       "<p>Fragrances made for everyone: fresh colognes, woody and amber scents. Acqua di Parma, Maison Francis Kurkdjian, Xerjoff and other houses, genuine and %s.</p>" % DANS_9),
    "niche": ("Niche fragrances – Xerjoff, Nishane, Initio, Creed | Qosmi",
              "Online niche perfumery: Xerjoff, Nishane, Initio, Parfums de Marly, Creed, Sospiro and more. Genuine bottles, %s." % DANS_9,
              "<p>The niche creators we love: Xerjoff, Nishane, Initio, Parfums de Marly, Creed, Sospiro and other exceptional houses. Genuine, brand-new and %s.</p>" % DANS_9),
    "parfums-arabes": ("Arabian fragrances – Lattafa, Armaf, Al Haramain, Afnan | Qosmi",
                       "Authentic Arabian fragrances: Lattafa, Armaf, Al Haramain, Afnan, Rasasi, Ajmal and other houses from the Emirates. Oud, amber, spices.",
                       "<p>The great houses of Arabian perfumery: Lattafa, Armaf, Al Haramain, Afnan, Rasasi, Ajmal, Amouage and many more. "
                       "Generous trails of oud, amber, rose and spices that last a long time on the skin. "
                       "Every bottle is genuine and brand-new, %s.</p>" % DANS_9),
    "testeurs": ("Authentic perfume testers, for less | Qosmi",
                 "Perfume testers: the same authentic fragrance as the boxed version, in simple packaging, for less. %s." % DANS_9.capitalize(),
                 "<p>A tester is the same authentic fragrance as the boxed version, with its cap, delivered in simple packaging. Same contents, a gentler price.</p>"),
}

TITRES_NL = {"parfums-arabes": "Arabische parfums"}


def traduire(s, rid, valeurs, locale="nl"):
    tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }",
               {"id": rid})["translatableResource"]
    dig = {x["key"]: x["digest"] for x in (tr or {}).get("translatableContent", [])}
    t = [{"locale": locale, "key": k, "value": v, "translatableContentDigest": dig[k]} for k, v in valeurs.items() if k in dig]
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
    try:
        print("Accueil EN :", traduire(s, shop, {"meta_title": ACCUEIL["en"][0], "meta_description": ACCUEIL["en"][1]}, locale="en"))
    except Exception as e:
        print("Accueil EN : impossible —", str(e)[:200])
    # --- collections
    for h, ((t_fr, m_fr, b_fr), (t_nl, m_nl, b_nl)) in COLLECTIONS.items():
        c = s.gql("query($h: String!) { collectionByIdentifier(identifier: {handle: $h}) { id } }", {"h": h}).get("collectionByIdentifier")
        if not c:
            print("  collection %s introuvable" % h)
            continue
        r = s.gql("""mutation($c: CollectionInput!) { collectionUpdate(input: $c) { collection { id } userErrors { field message } } }""",
                  {"c": {"id": c["id"], "descriptionHtml": b_fr, "seo": {"title": t_fr, "description": m_fr}}})["collectionUpdate"]
        vals = {"body_html": b_nl, "meta_title": t_nl, "meta_description": m_nl}
        if h in TITRES_NL:
            vals["title"] = TITRES_NL[h]
        nl = traduire(s, c["id"], vals)
        en = "—"
        if h in COLLECTIONS_EN:
            t_en, m_en, b_en = COLLECTIONS_EN[h]
            en = traduire(s, c["id"], {"body_html": b_en, "meta_title": t_en, "meta_description": m_en}, locale="en")
        print("  collection %-15s FR : %s · NL : %s · EN : %s" % (h, r["userErrors"] or "ok", nl, en))
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
