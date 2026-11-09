#!/usr/bin/env python3
"""Version néerlandaise de qosmi.be (demande d'Amine du 09/11/2026 : « go alors la version néerlandaise »).

--audit   : compte, type par type, ce qui est traduit en néerlandais (fiches en ligne, collections, pages, articles,
            menus, boutique, politiques, thème) et liste ce qui manque → rapports/theme/nl_audit.json. Lecture seule.
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


def publier():
    s = Shopify()
    marches = s.gql("{ markets(first:20){ nodes{ id name enabled primary webPresences(first:5){ nodes{ id defaultLocale{ locale } alternateLocales{ locale } } } } } }")["markets"]["nodes"]
    print(json.dumps(marches, ensure_ascii=False))
    wp = [w["id"] for m in marches if m["enabled"] for w in m["webPresences"]["nodes"]]
    r = s.gql('mutation($wp:[ID!]){ shopLocaleUpdate(locale:"nl", shopLocale:{ published:true, marketWebPresenceIds:$wp }){ shopLocale{ locale published marketWebPresences{ id } } userErrors{ field message } } }', {"wp": wp})
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    if "--audit" in sys.argv:
        audit()
    elif "--publier" in sys.argv:
        publier()
    else:
        print(__doc__)
