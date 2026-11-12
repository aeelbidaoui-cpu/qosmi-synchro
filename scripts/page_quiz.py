#!/usr/bin/env python3
"""Crée (ou met à jour) la page « Quiz : trouve ton parfum » (/pages/quiz), affichée par le modèle page.quiz (12/11/2026, quiz parfum)."""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from shopify_api import Shopify
    s = Shopify()
    champs = {"title": "Quiz : trouve ton parfum", "handle": "quiz", "body": "", "isPublished": True, "templateSuffix": "quiz"}
    d = s.gql('query($q: String!) { pages(first: 1, query: $q) { nodes { id } } }', {"q": "handle:quiz"})["pages"]["nodes"]
    if d:
        r = s.gql("mutation($id: ID!, $p: PageUpdateInput!) { pageUpdate(id: $id, page: $p) { page { id } userErrors { field message } } }",
                  {"id": d[0]["id"], "p": champs})["pageUpdate"]
    else:
        r = s.gql("mutation($p: PageCreateInput!) { pageCreate(page: $p) { page { id } userErrors { field message } } }",
                  {"p": champs})["pageCreate"]
    if r["userErrors"]:
        sys.exit("Refus : %s" % json.dumps(r["userErrors"], ensure_ascii=False))
    pid = r["page"]["id"]
    tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": pid})
    dig = {x["key"]: x["digest"] for x in (tr["translatableResource"] or {}).get("translatableContent", [])}
    if "title" in dig:
        s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
              {"id": pid, "t": [{"locale": "nl", "key": "title", "value": "Quiz: vind je parfum", "translatableContentDigest": dig["title"]}]})
    print("Page Quiz : trouve ton parfum OK :", pid)


if __name__ == "__main__":
    main()
