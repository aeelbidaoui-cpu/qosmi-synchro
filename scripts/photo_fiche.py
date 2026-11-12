#!/usr/bin/env python3
"""Remplace la photo d'une fiche précise (12/11/2026) : pour les fiches qui ne sont plus dans la liste du grossiste
(épuisées), que la mise à jour des photos ne touche pas. Entrées : PHOTOS_FICHE = handle, PHOTOS_ESSAI = adresse de la photo."""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from shopify_api import Shopify
    h, url = os.environ.get("PHOTOS_FICHE", ""), os.environ.get("PHOTOS_ESSAI", "")
    if not h or not url.startswith("https://"):
        sys.exit("Indiquer fiche (handle) et essai (adresse https de la photo).")
    s = Shopify()
    p = s.gql("""query($h: String!) { productByIdentifier(identifier: {handle: $h}) { id title
        media(first: 20) { nodes { id } } } }""", {"h": h})["productByIdentifier"]
    if not p:
        sys.exit("Fiche introuvable : %s" % h)
    anciens = [m["id"] for m in p["media"]["nodes"]]
    r = s.gql("""mutation($id: ID!, $m: [CreateMediaInput!]!) { productCreateMedia(productId: $id, media: $m) {
        media { id status } mediaUserErrors { field message } } }""",
              {"id": p["id"], "m": [{"originalSource": url, "mediaContentType": "IMAGE", "alt": p["title"]}]})["productCreateMedia"]
    if r["mediaUserErrors"]:
        sys.exit("Refus : %s" % r["mediaUserErrors"])
    nouveau = r["media"][0]["id"]
    for _ in range(30):
        time.sleep(4)
        st = s.gql("query($id: ID!) { node(id: $id) { ... on MediaImage { status mediaErrors { message } } } }", {"id": nouveau})["node"]
        if st["status"] in ("READY", "FAILED"):
            break
    if st["status"] != "READY":
        sys.exit("Photo non traitée : %s" % st)
    if anciens:
        s.gql("mutation($id: ID!, $m: [ID!]!) { productDeleteMedia(productId: $id, mediaIds: $m) { mediaUserErrors { message } } }",
              {"id": p["id"], "m": anciens})
    print("OK photo remplacée : %s (%d ancienne(s) retirée(s))" % (p["title"], len(anciens)))


if __name__ == "__main__":
    main()
