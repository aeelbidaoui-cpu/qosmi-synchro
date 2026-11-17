#!/usr/bin/env python3
"""Shopify Inbox (17/11/2026, « lance A ») : l'agent du chat ne peut conseiller que les fiches publiées sur le canal
Inbox. Ce script y publie toutes les fiches actives qui n'y sont pas encore (les nouvelles fiches y sont ensuite publiées
par la mise à jour horaire, via site_synchro.publications_vente). Le journal n'affiche que des nombres."""
import os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
INBOX_ID = "gid://shopify/Publication/332532842820"
M = "mutation($id: ID!, $p: ID!) { publishablePublish(id: $id, input: [{publicationId: $p}]) { userErrors { message } } }"


def main():
    from shopify_api import Shopify
    s = Shopify()
    pubs = s.gql("{ publications(first: 30) { nodes { id name } } }")["publications"]["nodes"]
    print("Canaux : %s" % ", ".join(p["name"] for p in pubs))
    pub = next((p["id"] for p in pubs if "inbox" in p["name"].lower()), INBOX_ID)
    a, manquants, total = None, [], 0
    q = """query($a: String, $p: ID!) { products(first: 250, after: $a, query: "status:active") {
      pageInfo { hasNextPage endCursor } nodes { id publishedOnPublication(publicationId: $p) } } }"""
    while True:
        d = s.gql(q, {"a": a, "p": pub})["products"]
        total += len(d["nodes"])
        manquants += [n["id"] for n in d["nodes"] if not n["publishedOnPublication"]]
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]
    err = 0
    for pid in manquants:
        if s.gql(M, {"id": pid, "p": pub})["publishablePublish"]["userErrors"]:
            err += 1
    print("OK Inbox : %d fiches actives, %d publiées sur Inbox maintenant, %d erreurs" % (total, len(manquants) - err, err))


if __name__ == "__main__":
    main()
