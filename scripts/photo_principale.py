#!/usr/bin/env python3
"""Choisit la photo principale d'une fiche parmi ses photos existantes (18/11/2026 : la fiche Scandal pour femme montrait
le flacon Scandal pour homme en premier). Liste : config/photos_principales.json {handle: rang de la bonne photo (0 = 1re)}.
Rien n'est supprimé : la bonne photo passe simplement en tête."""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    from shopify_api import Shopify
    s = Shopify()
    liste = json.load(open(os.path.join(RACINE, "config", "photos_principales.json"), encoding="utf-8"))
    for h, rang in liste.items():
        if h.startswith("_"):
            continue
        p = s.gql("""query($h: String!) { productByIdentifier(identifier: {handle: $h}) { id title
            media(first: 20) { nodes { id } } } }""", {"h": h})["productByIdentifier"]
        if not p:
            print("Fiche introuvable : %s" % h)
            continue
        ids = [m["id"] for m in p["media"]["nodes"]]
        if rang == 0 or rang >= len(ids):
            print("%s : rien à faire (%d photos)" % (p["title"], len(ids)))
            continue
        r = s.gql("""mutation($id: ID!, $m: [MoveInput!]!) { productReorderMedia(id: $id, moves: $m) {
            job { id } mediaUserErrors { field message } } }""",
                  {"id": p["id"], "m": [{"id": ids[rang], "newPosition": "0"}]})["productReorderMedia"]
        print("%s : %s" % (p["title"], "photo n°%d passée en tête" % (rang + 1) if not r["mediaUserErrors"] else r["mediaUserErrors"]))


if __name__ == "__main__":
    main()
