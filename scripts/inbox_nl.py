#!/usr/bin/env python3
"""Shopify Inbox (17/11/2026) : message d'accueil du chat en néerlandais pour /nl. Le message FR est réglé dans
l'intégration d'appli du thème ; la version NL est une traduction de ce réglage (ressource traduisible du thème)."""
import os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
FR_DEBUT = "Salut, moi c'est Mimi"
NL = "Hoi, ik ben Mimi! Op zoek naar een parfum of heb je een vraag over je bestelling? Stuur me een bericht, ik antwoord meteen."


def main():
    from shopify_api import Shopify
    s = Shopify()
    m = """mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) {
      userErrors { field message } } }"""
    trouve = 0
    for typ in ("ONLINE_STORE_THEME_APP_EMBED", "ONLINE_STORE_THEME_SETTINGS_DATA_SECTIONS", "ONLINE_STORE_THEME_JSON_TEMPLATE",
                "ONLINE_STORE_THEME_SECTION_GROUP"):
        a = None
        while True:
            try:
                d = s.gql("""query($t: TranslatableResourceType!, $a: String) { translatableResources(first: 50, resourceType: $t, after: $a) {
                  pageInfo { hasNextPage endCursor } nodes { resourceId translatableContent { key value digest } } } }""",
                          {"t": typ, "a": a})["translatableResources"]
            except Exception as e:
                print("%s : non lisible (%s)" % (typ, str(e)[:120]))
                break
            for n in d["nodes"]:
                for c in n["translatableContent"]:
                    if (c["value"] or "").startswith(FR_DEBUT):
                        r = s.gql(m, {"id": n["resourceId"], "t": [{"locale": "nl", "key": c["key"], "value": NL,
                                                                       "translatableContentDigest": c["digest"]}]})["translationsRegister"]
                        print("OK message d'accueil NL (%s, clé %s) %s" % (typ, c["key"], r["userErrors"] or ""))
                        trouve += 1
            if not d["pageInfo"]["hasNextPage"]:
                break
            a = d["pageInfo"]["endCursor"]
    if not trouve:
        print("Message d'accueil FR introuvable dans les ressources traduisibles")


if __name__ == "__main__":
    main()
