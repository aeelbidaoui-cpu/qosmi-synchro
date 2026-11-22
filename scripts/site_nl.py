#!/usr/bin/env python3
"""Version néerlandaise de qosmi.be (demande d'Amine du 09/11/2026 : « go alors la version néerlandaise »).

--audit   : compte, type par type, ce qui est traduit en néerlandais (fiches en ligne, collections, pages, articles,
            menus, boutique, politiques, thème) et liste ce qui manque → rapports/theme/nl_audit.json. Lecture seule.
--traduire : enregistre les traductions NL des textes fixes (dictionnaire NL ci-dessous).
--publier : publie le néerlandais sur le marché Belgique (qosmi.be/nl). Réversible (published: false).
"""
import json, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from shopify_api import Shopify, RACINE  # noqa: E402

RAPPORTS = os.path.join(RACINE, "rapports", "theme")
TYPES = ["COLLECTION", "PAGE", "ARTICLE", "BLOG", "MENU", "LINK", "SHOP", "SHOP_POLICY",
         "ONLINE_STORE_THEME", "ONLINE_STORE_THEME_JSON_TEMPLATE", "ONLINE_STORE_THEME_SECTION_GROUP",
         "ONLINE_STORE_THEME_SETTINGS_DATA_SECTIONS", "ONLINE_STORE_THEME_LOCALE_CONTENT", "METAOBJECT"]
LANGUE = os.environ.get("LANGUE", "nl")  # 22/11/2026 : « en » pour la version anglaise (même audit)
CHAMPS = "resourceId translatableContent { key value } translations(locale: \"%s\") { key outdated }" % LANGUE


def bilan(noeuds, detail, nom):
    tot = trad = obso = 0
    manquants = []
    for n in noeuds:
        cles = {c["key"]: c["value"] for c in n["translatableContent"] if (c.get("value") or "").strip()}
        faites = {t["key"]: t["outdated"] for t in n["translations"]}
        for k, v in cles.items():
            tot += 1
            if k in faites:
                trad += 1
                obso += 1 if faites[k] else 0
            elif len(manquants) < 400 and k != "handle" and not k.startswith("shopify."):
                manquants.append({"id": n["resourceId"], "cle": k, "fr": v if not nom.startswith("PRODUCT") else (v or "")[:120]})
    detail[nom] = {"textes": tot, "traduits": trad, "perimes": obso, "manquants": len(
        [1 for n in noeuds for c in n["translatableContent"] if (c.get("value") or "").strip()
         and c["key"] not in {t["key"] for t in n["translations"]}]), "exemples": manquants}
    print("%-48s %6d textes · %6d traduits · %5d périmés" % (nom, tot, trad, obso))


def audit():
    s = Shopify()
    print(json.dumps(s.gql("{ shopLocales { locale primary published marketWebPresences { id } } }")["shopLocales"]))
    detail = {}
    # fiches en ligne (ACTIVE) seulement
    ids, apres = [], None
    while True:
        d = s.gql("query($a:String){ products(first:250, after:$a, query:\"status:active\"){ pageInfo{hasNextPage endCursor} nodes{ id } } }", {"a": apres})["products"]
        ids += [n["id"] for n in d["nodes"]]
        if not d["pageInfo"]["hasNextPage"]:
            break
        apres = d["pageInfo"]["endCursor"]
    noeuds = []
    for i in range(0, len(ids), 250):
        d = s.gql("query($ids:[ID!]!){ translatableResourcesByIds(first:250, resourceIds:$ids){ nodes{ %s } } }" % CHAMPS, {"ids": ids[i:i + 250]})
        noeuds += d["translatableResourcesByIds"]["nodes"]
    bilan(noeuds, detail, "PRODUCT (en ligne : %d)" % len(ids))
    for t in TYPES:
        noeuds, apres = [], None
        while True:
            try:
                d = s.gql("query($a:String){ translatableResources(first:100, after:$a, resourceType:%s){ pageInfo{hasNextPage endCursor} nodes{ %s } } }" % (t, CHAMPS), {"a": apres})["translatableResources"]
            except Exception as ex:
                print("%s : %s" % (t, str(ex)[:120]))
                break
            noeuds += d["nodes"]
            if not d["pageInfo"]["hasNextPage"]:
                break
            apres = d["pageInfo"]["endCursor"]
        bilan(noeuds, detail, t)
    os.makedirs(RAPPORTS, exist_ok=True)
    with open(os.path.join(RAPPORTS, "%s_audit.json" % LANGUE), "w", encoding="utf-8") as f:
        json.dump(detail, f, ensure_ascii=False, indent=1)


# Traductions NL des textes fixes (titres de collections, menus, pages, textes de l'accueil et du thème). Clé = texte FR exact.
NL = {
 "Page d’accueil": "Startpagina", "Parfums": "Parfums", "Parfums femme": "Damesparfums", "Parfums homme": "Herenparfums",
 "Parfums mixtes": "Unisex parfums", "Parfums enfants": "Kinderparfums", "Parfums de niche": "Nicheparfums",
 "Parfums orientaux": "Oosterse parfums", "Testeurs": "Testers", "Coffrets": "Geschenksets", "Nouveautés": "Nieuw", "Black Friday": "Black Friday", "Soins": "Verzorging",
 "Maquillage": "Make-up", "Contact": "Contact", "Marques": "Merken", "Par odeurs": "Op geur", "Trouve ton parfum": "Vind je parfum",
 "Menu principal": "Hoofdmenu", "Menu du pied de page": "Footermenu", "Menu principal du compte client": "Hoofdmenu klantaccount",
 "Rechercher": "Zoeken", "Commandes": "Bestellingen", "Profil": "Profiel", "Femme": "Dames", "Homme": "Heren",
 "Mixte": "Unisex", "Niche": "Niche", "Parfums arabes": "Arabische parfums", "Journal": "Magazine", "Magazine": "Magazine", "Arabes": "Arabisch",
 "Conditions générales de vente": "Algemene verkoopsvoorwaarden", "Livraison": "Levering",
 "Retours et remboursements": "Retourneren en terugbetalen", "Politique de confidentialité": "Privacybeleid",
 "Mentions légales": "Wettelijke vermeldingen", "Conditions d'utilisation": "Gebruiksvoorwaarden",
 "Politique de cookies": "Cookiebeleid", "Déclaration d'accessibilité": "Toegankelijkheidsverklaring",
 "<h1>Page not found</h1>": "<h1>Pagina niet gevonden</h1>",
 "<p>The link may be incorrect, or the page has been removed. </p>": "<p>De link klopt misschien niet, of de pagina werd verwijderd.</p>",
 "Continue shopping": "Verder winkelen", "<p>Discover something new</p>": "<p>Ontdek iets nieuws</p>",
 "Panier": "Winkelmandje", "Tu aimeras aussi": "Misschien vind je dit ook mooi",
 "<h3>Tu aimeras aussi</h3>": "<h3>Misschien vind je dit ook mooi</h3>",
 "Ton parfum,": "Jouw parfum,", "au juste prix.": "aan de juiste prijs.",
 "Parfums de marque et de niche, 100 % authentiques.": "Merkparfums en nicheparfums, 100 % authentiek.",
 "Découvrir": "Ontdekken", "Le parfum du jour": "Parfum van de dag", "Prochain parfum dans": "Volgende parfum over",
 "Favoris": "Favorieten",
 "Idées cadeaux": "Cadeau-ideeën", "Bons plans": "Koopjes", "Parfums d'hiver": "Winterparfums", "Parfums de printemps": "Lenteparfums",
 "Parfums d'été": "Zomerparfums", "Parfums d'automne": "Herfstparfums",
 "Les parfums qu'on nous demande le plus. Une sélection de grandes maisons et de niche, choisie avec soin.":
     "De parfums waar we het vaakst naar gevraagd worden. Een zorgvuldige selectie van grote huizen en niche.",
 "Les incontournables": "Onmisbaar", "Voir la niche": "Ontdek de niche",
 "Parfums de Marly Layton, Maison Francis Kurkdjian Baccarat Rouge 540, Xerjoff Erba Pura, Nishane Hundred Silent Ways et Creed Aventus":
     "Parfums de Marly Layton, Maison Francis Kurkdjian Baccarat Rouge 540, Xerjoff Erba Pura, Nishane Hundred Silent Ways en Creed Aventus",
 "Xerjoff, Nishane, Initio, Parfums de Marly et plus": "Xerjoff, Nishane, Initio, Parfums de Marly en meer",
 "Dior, Chanel, Tom Ford et plus": "Dior, Chanel, Tom Ford en meer", "À porter par tout le monde": "Voor iedereen",
 "Chanel, Dior, Guerlain et plus": "Chanel, Dior, Guerlain en meer",
 "Des parfums originaux et neufs, des grandes maisons aux créateurs de niche.": "Originele, nieuwe parfums, van de grote huizen tot nichecreateurs.",
 "À propos": "Over ons", "Qosmi": "Qosmi",
 "<p>Qosmi, c'est une parfumerie en ligne belge, simple et honnête : des parfums 100 % authentiques, neufs, au juste prix. On choisit les maisons qu'on aime, des grands classiques aux créateurs de niche, et on te les livre en Belgique et dans 8 autres pays d'Europe.</p>":
     "<p>Qosmi is een Belgische onlineparfumerie, eenvoudig en eerlijk: 100 % authentieke, nieuwe parfums aan de juiste prijs. We kiezen de huizen die we graag hebben, van de grote klassiekers tot nichecreateurs, en leveren ze in België en 8 andere Europese landen.</p>",
 "Voir tous les parfums": "Alle parfums bekijken", "<h1>Collections</h1>": "<h1>Collecties</h1>", "Submit": "Verzenden",
 "Livraison offerte dès 2 articles (BE · NL · LU)\nLivraison suivie dans 9 pays d'Europe\nParfums 100 % authentiques et neufs\nPlus de 100 maisons, des grands classiques à la niche\nPaiement sécurisé : Bancontact, carte, Apple Pay\n14 jours pour changer d'avis":
     "Gratis levering vanaf 2 artikelen (BE · NL · LU)\nGevolgde levering in 9 Europese landen\n100 % authentieke en nieuwe parfums\nMeer dan 100 huizen, van grote klassiekers tot niche\nVeilig betalen: Bancontact, kaart, Apple Pay\n14 dagen bedenktijd",
}
MARQUES_INTRO = ("<p>Toutes les maisons que nous proposons, des grands classiques aux créateurs de niche.</p>",
                 "<p>Alle huizen die we aanbieden, van de grote klassiekers tot nichecreateurs.</p>")

# 22/11/2026 (Amine : « fait ça », version anglaise) : mêmes textes fixes en anglais. Clé = texte FR exact.
EN = {
 "Page d’accueil": "Home page", "Parfums": "Fragrances", "Parfums femme": "Women's fragrances", "Parfums homme": "Men's fragrances",
 "Parfums mixtes": "Unisex fragrances", "Parfums enfants": "Kids' fragrances", "Parfums de niche": "Niche fragrances",
 "Parfums orientaux": "Oriental fragrances", "Testeurs": "Testers", "Coffrets": "Gift sets", "Nouveautés": "New in", "Black Friday": "Black Friday", "Soins": "Skincare",
 "Maquillage": "Make-up", "Contact": "Contact", "Marques": "Brands", "Par odeurs": "By scent", "Trouve ton parfum": "Find your fragrance",
 "Menu principal": "Main menu", "Menu du pied de page": "Footer menu", "Menu principal du compte client": "Customer account main menu",
 "Rechercher": "Search", "Commandes": "Orders", "Profil": "Profile", "Femme": "Women", "Homme": "Men",
 "Mixte": "Unisex", "Niche": "Niche", "Parfums arabes": "Arabian fragrances", "Journal": "Magazine", "Magazine": "Magazine", "Arabes": "Arabian",
 "Conditions générales de vente": "Terms and conditions of sale", "Livraison": "Shipping",
 "Retours et remboursements": "Returns and refunds", "Politique de confidentialité": "Privacy policy",
 "Mentions légales": "Legal notice", "Conditions d'utilisation": "Terms of use",
 "Politique de cookies": "Cookie policy", "Déclaration d'accessibilité": "Accessibility statement",
 "<h1>Page not found</h1>": "<h1>Page not found</h1>",
 "<p>The link may be incorrect, or the page has been removed. </p>": "<p>The link may be incorrect, or the page has been removed.</p>",
 "Continue shopping": "Continue shopping", "<p>Discover something new</p>": "<p>Discover something new</p>",
 "Panier": "Cart", "Tu aimeras aussi": "You may also like",
 "<h3>Tu aimeras aussi</h3>": "<h3>You may also like</h3>",
 "Ton parfum,": "Your fragrance,", "au juste prix.": "at the right price.",
 "Parfums de marque et de niche, 100 % authentiques.": "Designer and niche fragrances, 100% authentic.",
 "Découvrir": "Discover", "Le parfum du jour": "Fragrance of the day", "Prochain parfum dans": "Next fragrance in",
 "Favoris": "Favourites",
 "Idées cadeaux": "Gift ideas", "Bons plans": "Deals", "Parfums d'hiver": "Winter fragrances", "Parfums de printemps": "Spring fragrances",
 "Parfums d'été": "Summer fragrances", "Parfums d'automne": "Autumn fragrances",
 "Les parfums qu'on nous demande le plus. Une sélection de grandes maisons et de niche, choisie avec soin.":
     "The fragrances we're asked for most. A carefully chosen selection of great houses and niche brands.",
 "Les incontournables": "The essentials", "Voir la niche": "Explore niche",
 "Parfums de Marly Layton, Maison Francis Kurkdjian Baccarat Rouge 540, Xerjoff Erba Pura, Nishane Hundred Silent Ways et Creed Aventus":
     "Parfums de Marly Layton, Maison Francis Kurkdjian Baccarat Rouge 540, Xerjoff Erba Pura, Nishane Hundred Silent Ways and Creed Aventus",
 "Xerjoff, Nishane, Initio, Parfums de Marly et plus": "Xerjoff, Nishane, Initio, Parfums de Marly and more",
 "Dior, Chanel, Tom Ford et plus": "Dior, Chanel, Tom Ford and more", "À porter par tout le monde": "For everyone",
 "Chanel, Dior, Guerlain et plus": "Chanel, Dior, Guerlain and more",
 "Des parfums originaux et neufs, des grandes maisons aux créateurs de niche.": "Genuine, brand-new fragrances, from the great houses to niche creators.",
 "À propos": "About us", "Qosmi": "Qosmi",
 "<p>Qosmi, c'est une parfumerie en ligne belge, simple et honnête : des parfums 100 % authentiques, neufs, au juste prix. On choisit les maisons qu'on aime, des grands classiques aux créateurs de niche, et on te les livre en Belgique et dans 8 autres pays d'Europe.</p>":
     "<p>Qosmi is a Belgian online perfumery, simple and honest: 100% authentic, brand-new fragrances at the right price. We pick the houses we love, from the great classics to niche creators, and deliver them across Europe.</p>",
 "Voir tous les parfums": "View all fragrances", "<h1>Collections</h1>": "<h1>Collections</h1>", "Submit": "Submit",
 "Livraison offerte dès 2 articles (BE · NL · LU)\nLivraison suivie dans 9 pays d'Europe\nParfums 100 % authentiques et neufs\nPlus de 100 maisons, des grands classiques à la niche\nPaiement sécurisé : Bancontact, carte, Apple Pay\n14 jours pour changer d'avis":
     "Free pick-up point delivery from 2 items (Belgium, Netherlands, Luxembourg)\nTracked delivery in 9 European countries\n100% authentic, brand-new fragrances\nOver 100 houses, from great classics to niche\nSecure payment: Bancontact, card, Apple Pay\n14 days to change your mind",
}

EN.update({
 # 22/11/2026 : textes des blocs « ambiance » du thème, titres de pages
 "Flacon de parfum posé sur une surface couverte de gouttes": "Perfume bottle on a surface covered in droplets",
 "Perdu ?": "Lost?", "<p>Parcours nos parfums ou nos marques.</p>": "<p>Browse our fragrances or our brands.</p>",
 "Retrouve ton parfum": "Find your fragrance", "Pivoine blanche dans un petit flacon de verre": "White peony in a small glass bottle",
 "Idées de parfums": "Fragrance ideas", "Un cadeau ?": "A gift?",
 "<p>La livraison en point relais est offerte dès 2 articles en Belgique, aux Pays-Bas et au Luxembourg.</p>": "<p>Pick-up point delivery is free from 2 items in Belgium, the Netherlands and Luxembourg.</p>",
 "Offre un parfum": "Give a fragrance", "Flacons de parfum alignés, en lumière douce": "Perfume bottles lined up in soft light",
 "Voir les marques": "See the brands", "Toutes nos marques": "All our brands",
 "<p>Des grands classiques aux créateurs de niche, retrouve chaque maison sur sa page.</p>": "<p>From the great classics to niche creators, every house has its own page.</p>",
 "Plus de 100 maisons": "Over 100 houses", "Flacons de parfum dorés dans la lumière": "Golden perfume bottles in the light",
 "<p>Oud, ambre, vanille, rose : Lattafa, Armaf, Al Haramain, Afnan et bien d'autres maisons des Émirats.</p>": "<p>Oud, amber, vanilla, rose: Lattafa, Armaf, Al Haramain, Afnan and many more houses from the Emirates.</p>",
 "L'Orient en flacon": "The Orient in a bottle", "Main qui vaporise un parfum": "Hand spraying a fragrance",
 "Lire le Magazine": "Read the Magazine", "Le Magazine": "The Magazine",
 "<p>Conseils pour bien porter ton parfum, matières premières, portraits de parfumeurs : tout ce qu'il faut savoir avant de choisir.</p>": "<p>Tips on wearing your fragrance, raw materials, perfumer portraits: everything to know before you choose.</p>",
 "Le bon geste": "The right touch", "Coffret cadeau en carton, papier de soie et anis étoilé": "Cardboard gift box, tissue paper and star anise",
 "Voir le guide cadeaux": "See the gift guide",
 "<p>Des coffrets, des parfums pour tous les budgets et de l'aide pour choisir celui qui lui ressemble. Tu peux aussi ajouter un petit mot au moment de commander.</p>":
     "<p>Gift sets, fragrances for every budget and help choosing the one that suits them. You can also add a short note when you order.</p>", "Noël": "Christmas", "Idées cadeaux parfum": "Fragrance gift ideas",
 "Flacons de parfum sur une console en marbre, pétales séchés et branche d'olivier": "Perfume bottles on a marble console, dried petals and an olive branch",
 "Toutes les marques": "All brands", "Flacon de parfum sur une fourrure blanche": "Perfume bottle on white fur",
 "Nos marques": "Our brands",
 "<p>Chaque parfum est neuf et d'origine. Livraison dans 9 pays d'Europe, offerte en point relais dès 2 articles en Belgique, aux Pays-Bas et au Luxembourg.</p>": "<p>Every fragrance is brand-new and genuine. Delivered across 9 European countries, free pick-up point delivery from 2 items in Belgium, the Netherlands and Luxembourg.</p>",
 "100 % authentique": "100% authentic", "Reflets dorés d'un flacon de parfum": "Golden reflections of a perfume bottle",
 "Besoin d'idées ?": "Need ideas?", "<p>Guides, conseils et parfums du jour pour t'aider à trouver le tien.</p>": "<p>Guides, tips and fragrances of the day to help you find yours.</p>",
 "Diagnostic olfactif": "Scent profile", "Idées cadeaux de Noël": "Christmas gift ideas", "Lexique du parfum": "Fragrance glossary",
 "Mes favoris": "My favourites", "Questions fréquentes": "FAQ", "Quiz : trouve ton parfum": "Quiz: find your fragrance",
 "Trouve ton parfum par ses odeurs": "Find your fragrance by scent", "Vu sur Instagram": "Seen on Instagram",
})
MARQUES_INTRO_EN = "<p>All the houses we carry, from the great classics to niche creators.</p>"
TYPES_TRAD = ["COLLECTION", "PAGE", "MENU", "LINK", "ONLINE_STORE_THEME_JSON_TEMPLATE", "ONLINE_STORE_THEME_SECTION_GROUP"]


def traduire():
    s = Shopify()
    m = """mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) {
           userErrors { field message } translations { key } } }"""
    ok = err = 0
    manque = set()
    for t in TYPES_TRAD:
        apres = None
        while True:
            d = s.gql("query($a:String){ translatableResources(first:100, after:$a, resourceType:%s){ pageInfo{hasNextPage endCursor} "
                      "nodes{ resourceId translatableContent{ key value digest } translations(locale:\"%s\"){ key value outdated } } } }" % (t, LANGUE),
                      {"a": apres})["translatableResources"]
            for n in d["nodes"]:
                faites = {x["key"]: x["value"] for x in n["translations"] if not x["outdated"]}
                lot = []
                for c in n["translatableContent"]:
                    v = (c.get("value") or "")
                    if not v.strip():
                        continue
                    dico = EN if LANGUE == "en" else NL
                    nl = dico.get(v.replace("\r\n", "\n").strip()) if c["key"] != "handle" else None
                    if c["key"] == "body_html" and v.startswith(MARQUES_INTRO[0]):
                        nl = v.replace(MARQUES_INTRO[0], MARQUES_INTRO_EN if LANGUE == "en" else MARQUES_INTRO[1], 1)
                    if nl is None and c["key"] not in faites and c["key"] != "handle" and len(v) < 300 and t != "COLLECTION":
                        manque.add((t, c["key"], v.replace("\n", " ⏎ ")[:200]))
                    if c["key"] in faites and (nl is None or faites[c["key"]] == nl):
                        continue  # déjà traduit (et identique au dictionnaire)
                    if nl is not None:
                        lot.append({"locale": LANGUE, "key": c["key"], "value": nl, "translatableContentDigest": c["digest"]})
                if lot:
                    r = s.gql(m, {"id": n["resourceId"], "t": lot})["translationsRegister"]
                    if r["userErrors"]:
                        err += 1
                        print("  %s : %s" % (n["resourceId"], r["userErrors"][:2]))
                    else:
                        ok += len(lot)
            if not d["pageInfo"]["hasNextPage"]:
                break
            apres = d["pageInfo"]["endCursor"]
    print("Traductions %s enregistrées : %d textes (%d erreurs)" % (LANGUE.upper(), ok, err))
    print("Textes sans traduction %s (hors collections) : %d" % (LANGUE.upper(), len(manque)))
    for m_ in sorted(manque):
        print("  MANQUE %s | %s | %s" % m_)


def emails():
    """Copie des modèles d'e-mail (FR et NL existant) → rapports/theme/emails/ : base de la traduction NL."""
    s = Shopify()
    dossier = os.path.join(RAPPORTS, "emails")
    os.makedirs(dossier, exist_ok=True)
    apres, n = None, 0
    while True:
        d = s.gql("query($a:String){ translatableResources(first:50, after:$a, resourceType:EMAIL_TEMPLATE){ pageInfo{hasNextPage endCursor} "
                  "nodes{ resourceId translatableContent{ key value digest } translations(locale:\"nl\"){ key value outdated } } } }",
                  {"a": apres})["translatableResources"]
        for nd in d["nodes"]:
            n += 1
            with open(os.path.join(dossier, nd["resourceId"].split("/")[-1] + ".json"), "w", encoding="utf-8") as f:
                json.dump(nd, f, ensure_ascii=False, indent=1)
        if not d["pageInfo"]["hasNextPage"]:
            break
        apres = d["pageInfo"]["endCursor"]
    print("Modèles d'e-mail copiés : %d" % n)


def emails_envoyer():
    """Enregistre la version NL des 7 e-mails clients personnalisés (config/emails_nl/*.json) : même mise en forme que
    le FR (code de confirmation au lieu du n° de commande, sans bouton Shop ni lien « Bezoek onze winkel », mode clair)."""
    import glob
    s = Shopify()
    m = """mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) {
           userErrors { field message } translations { key } } }"""
    for f in sorted(glob.glob(os.path.join(RACINE, "config", "emails_nl", "*.json"))):
        e = json.load(open(f, encoding="utf-8"))
        d = s.gql("query($ids:[ID!]!){ translatableResourcesByIds(first:1, resourceIds:$ids){ nodes{ translatableContent{ key digest } } } }",
                  {"ids": [e["id"]]})["translatableResourcesByIds"]["nodes"]
        dig = {c["key"]: c["digest"] for c in d[0]["translatableContent"]}
        t = [{"locale": "nl", "key": k, "value": e[k], "translatableContentDigest": dig[k]} for k in ("title", "body_html")]
        r = s.gql(m, {"id": e["id"], "t": t})["translationsRegister"]
        print("%s « %s » : %s" % (e["id"].split("/")[-1], e["title"], r["userErrors"] or "ok"))


def publier():
    s = Shopify()
    marches = s.gql("{ markets(first:20){ nodes{ id name enabled primary webPresences(first:5){ nodes{ id defaultLocale{ locale } alternateLocales{ locale } } } } } }")["markets"]["nodes"]
    print(json.dumps(marches, ensure_ascii=False))
    wp = [w["id"] for m in marches if m["enabled"] for w in m["webPresences"]["nodes"]]
    if not wp:  # présences web rattachées à la boutique (celles du français)
        loc = s.gql("{ shopLocales { locale primary marketWebPresences { id } } }")["shopLocales"]
        wp = [w["id"] for l in loc if l["primary"] for w in l["marketWebPresences"]]
    print("Présences web visées : %s" % wp)
    r = s.gql('mutation($wp:[ID!]){ shopLocaleUpdate(locale:"nl", shopLocale:{ published:true, marketWebPresenceIds:$wp }){ shopLocale{ locale published marketWebPresences{ id } } userErrors{ field message } } }', {"wp": wp})
    print(json.dumps(r, ensure_ascii=False))


def ajouter():
    """Ajoute la langue LANGUE à la boutique, NON publiée (invisible pour les clients)."""
    s = Shopify()
    r = s.gql('mutation($l:String!){ shopLocaleEnable(locale:$l){ shopLocale{ locale published } userErrors{ field message } } }', {"l": LANGUE})
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    if "--ajouter" in sys.argv:
        ajouter()
    elif "--audit" in sys.argv:
        audit()
    elif "--emails-envoyer" in sys.argv:
        emails_envoyer()
    elif "--emails" in sys.argv:
        emails()
    elif "--traduire" in sys.argv:
        traduire()
    elif "--publier" in sys.argv:
        publier()
    else:
        print(__doc__)
