#!/usr/bin/env python3
"""Crée ou met à jour une page Shopify affichée par un modèle page.<suffixe> du thème (titre + adresse FR/NL).
13/11/2026 : diagnostic olfactif.

  python3 scripts/page_simple.py diagnostic
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PAGES = {  # suffixe du modèle : (handle FR, titre FR, handle NL, titre NL)
    "diagnostic": ("diagnostic", "Diagnostic olfactif", "geurdiagnose", "Geurdiagnose"),
}


def main(cle):
    from shopify_api import Shopify
    h, t, h_nl, t_nl = PAGES[cle]
    s = Shopify()
    champs = {"title": t, "handle": h, "body": "", "isPublished": True, "templateSuffix": cle}
    d = s.gql('query($q: String!) { pages(first: 1, query: $q) { nodes { id } } }', {"q": "handle:%s" % h})["pages"]["nodes"]
    if d:
        r = s.gql("mutation($id: ID!, $p: PageUpdateInput!) { pageUpdate(id: $id, page: $p) { page { id } userErrors { field message } } }",
                  {"id": d[0]["id"], "p": champs})["pageUpdate"]
    else:
        r = s.gql("mutation($p: PageCreateInput!) { pageCreate(page: $p) { page { id } userErrors { field message } } }", {"p": champs})["pageCreate"]
    if r["userErrors"]:
        sys.exit("Refus : %s" % json.dumps(r["userErrors"], ensure_ascii=False))
    pid = r["page"]["id"]
    tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": pid})
    dig = {x["key"]: x["digest"] for x in (tr["translatableResource"] or {}).get("translatableContent", [])}
    tt = [{"locale": "nl", "key": k, "value": v, "translatableContentDigest": dig[k]} for k, v in (("title", t_nl), ("handle", h_nl)) if k in dig]
    e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
              {"id": pid, "t": tt})["translationsRegister"]["userErrors"]
    print("Page %s OK : %s, NL : %s" % (t, pid, e or "ok"))


if __name__ == "__main__":
    main(sys.argv[1])
