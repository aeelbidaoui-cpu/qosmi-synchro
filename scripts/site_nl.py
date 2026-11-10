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
CHAMPS = "resourceId translatableContent { key value } translations(locale: \"nl\") { key outdated }"


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
    with open(os.path.join(RAPPORTS, "nl_audit.json"), "w", encoding="utf-8") as f:
        json.dump(detail, f, ensure_ascii=False, indent=1)


# Traductions NL des textes fixes (titres de collections, menus, pages, textes de l'accueil et du thème). Clé = texte FR exact.
NL = {
 "Page d’accueil": "Startpagina", "Parfums": "Parfums", "Parfums femme": "Damesparfums", "Parfums homme": "Herenparfums",
 "Parfums mixtes": "Unisex parfums", "Parfums enfants": "Kinderparfums", "Parfums de niche": "Nicheparfums",
 "Parfums orientaux": "Oosterse parfums", "Testeurs": "Testers", "Coffrets": "Geschenksets", "Soins": "Verzorging",
 "Maquillage": "Make-up", "Contact": "Contact", "Marques": "Merken",
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
 "<p>Qosmi, c'est une parfumerie en ligne belge, simple et honnête : des parfums 100 % authentiques, neufs, au juste prix. On choisit les maisons qu'on aime, des grands classiques aux créateurs de niche, et on te les livre partout en Belgique.</p>":
     "<p>Qosmi is een Belgische onlineparfumerie, eenvoudig en eerlijk: 100 % authentieke, nieuwe parfums aan de juiste prijs. We kiezen de huizen die we graag hebben, van de grote klassiekers tot nichecreateurs, en leveren ze in heel België.</p>",
 "Voir tous les parfums": "Alle parfums bekijken", "<h1>Collections</h1>": "<h1>Collecties</h1>", "Submit": "Verzenden",
 "Livraison offerte dès 2 articles\nLivraison suivie partout en Belgique\nParfums 100 % authentiques et neufs\nPlus de 100 maisons, des grands classiques à la niche\nPaiement sécurisé : Bancontact, carte, Apple Pay\n14 jours pour changer d'avis":
     "Gratis levering vanaf 2 artikelen\nLevering in heel België\n100 % authentieke en nieuwe parfums\nMeer dan 100 huizen, van grote klassiekers tot niche\nVeilig betalen: Bancontact, kaart, Apple Pay\n14 dagen bedenktijd",
}
MARQUES_INTRO = ("<p>Toutes les maisons que nous proposons, des grands classiques aux créateurs de niche.</p>",
                 "<p>Alle huizen die we aanbieden, van de grote klassiekers tot nichecreateurs.</p>")
TYPES_TRAD = ["COLLECTION", "PAGE", "MENU", "LINK", "ONLINE_STORE_THEME_JSON_TEMPLATE", "ONLINE_STORE_THEME_SECTION_GROUP"]


def traduire():
    s = Shopify()
    m = """mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) {
           userErrors { field message } translations { key } } }"""
    ok = err = 0
    for t in TYPES_TRAD:
        apres = None
        while True:
            d = s.gql("query($a:String){ translatableResources(first:100, after:$a, resourceType:%s){ pageInfo{hasNextPage endCursor} "
                      "nodes{ resourceId translatableContent{ key value digest } translations(locale:\"nl\"){ key value outdated } } } }" % t,
                      {"a": apres})["translatableResources"]
            for n in d["nodes"]:
                faites = {x["key"]: x["value"] for x in n["translations"] if not x["outdated"]}
                lot = []
                for c in n["translatableContent"]:
                    v = (c.get("value") or "")
                    if not v.strip():
                        continue
                    nl = NL.get(v.replace("\r\n", "\n").strip()) if c["key"] != "handle" else None
                    if c["key"] == "body_html" and v.startswith(MARQUES_INTRO[0]):
                        nl = v.replace(MARQUES_INTRO[0], MARQUES_INTRO[1], 1)
                    if c["key"] in faites and (nl is None or faites[c["key"]] == nl):
                        continue  # déjà traduit (et identique au dictionnaire)
                    if nl is not None:
                        lot.append({"locale": "nl", "key": c["key"], "value": nl, "translatableContentDigest": c["digest"]})
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
    print("Traductions NL enregistrées : %d textes (%d erreurs)" % (ok, err))


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


if __name__ == "__main__":
    if "--audit" in sys.argv:
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
