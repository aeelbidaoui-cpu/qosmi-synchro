#!/usr/bin/env python3
"""Textes des images (alt) en néerlandais (préparé le 10/11/2026, à lancer en décembre : action theme « seo-alt-nl »).

Sur /nl/products/…, la galerie de la fiche affichait l'alt français des photos (« … pour homme »).
Pour chaque photo d'une fiche active, on enregistre la traduction NL de son alt = le titre NL de la fiche
(déjà traduit par la synchro). Relançable : les traductions à jour ne sont pas renvoyées.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

Q = """query($c: String) { products(first: 50, after: $c, query: "status:active") { pageInfo { hasNextPage endCursor }
      nodes { title translations(locale: "nl") { key value } media(first: 10) { nodes { id ... on MediaImage { alt } } } } } }"""
QT = """query($ids: [ID!]!) { translatableResourcesByIds(resourceIds: $ids, first: 250) { nodes { resourceId
      translatableContent { key value digest } translations(locale: "nl") { key value outdated } } } }"""
M = """mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { field message } } }"""


def main(essai=False):
    from shopify_api import Shopify
    s = Shopify()
    c, faits, deja, err = None, 0, 0, 0
    while True:
        d = s.gql(Q, {"c": c})["products"]
        voulu = {}
        for p in d["nodes"]:
            t_nl = next((x["value"] for x in p["translations"] if x["key"] == "title" and x["value"]), None)
            if not t_nl:
                continue
            for m in p["media"]["nodes"]:
                if m.get("alt"):
                    voulu[m["id"]] = t_nl
        if voulu:
            res = s.gql(QT, {"ids": list(voulu)})["translatableResourcesByIds"]["nodes"]
            for r in res:
                alt = next((x for x in r["translatableContent"] if x["key"] == "alt"), None)
                if not alt:
                    continue
                ok = next((x for x in r["translations"] if x["key"] == "alt" and not x["outdated"]), None)
                if ok and ok["value"] == voulu[r["resourceId"]]:
                    deja += 1
                    continue
                if essai:
                    faits += 1
                    continue
                e = s.gql(M, {"id": r["resourceId"], "t": [{"locale": "nl", "key": "alt", "value": voulu[r["resourceId"]],
                                                              "translatableContentDigest": alt["digest"]}]})["translationsRegister"]["userErrors"]
                if e:
                    err += 1
                    if err <= 3:
                        print("  erreur :", e)
                else:
                    faits += 1
        if not d["pageInfo"]["hasNextPage"]:
            break
        c = d["pageInfo"]["endCursor"]
    print("Alt NL : %d %s, %d déjà bons, %d erreurs" % (faits, "à faire" if essai else "enregistrés", deja, err))


if __name__ == "__main__":
    main(essai="--essai" in sys.argv)
