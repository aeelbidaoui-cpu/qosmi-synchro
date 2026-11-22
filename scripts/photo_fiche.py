#!/usr/bin/env python3
"""Remplace la photo d'une fiche précise (12/11/2026) : pour les fiches qui ne sont plus dans la liste du grossiste
(épuisées), que la mise à jour des photos ne touche pas. Entrées : PHOTOS_FICHE = handle, PHOTOS_ESSAI = adresse de la photo."""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from shopify_api import Shopify
    if "--lot" in sys.argv:  # 23/11/2026 : config/photos_fiches_lot.json {handle: adresse}, une fiche après l'autre
        lot = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "photos_fiches_lot.json"),
                             encoding="utf-8"))["par_fiche"]
        s, ok = Shopify(), 0
        for h, url in lot.items():
            try:
                remplacer(s, h, url)
                ok += 1
            except SystemExit as e:
                print("  %s : %s" % (h, e))
        print("Lot : %d / %d photos remplacées" % (ok, len(lot)))
        return
    h, url = os.environ.get("PHOTOS_FICHE", ""), os.environ.get("PHOTOS_ESSAI", "")
    if not h or not url.startswith("https://"):
        sys.exit("Indiquer fiche (handle) et essai (adresse https de la photo).")
    remplacer(Shopify(), h, url)


def remplacer(s, h, url):
    p = s.gql("""query($h: String!) { productByIdentifier(identifier: {handle: $h}) { id title
        media(first: 20) { nodes { id } }
        pyramide: metafield(namespace: "qosmi", key: "pyramide_media") { value } } }""", {"h": h})["productByIdentifier"]
    if not p:
        sys.exit("Fiche introuvable : %s" % h)
    pyr = (p.get("pyramide") or {}).get("value")  # 22/11/2026 : la 2e image (pyramide olfactive) reste
    anciens = [m["id"] for m in p["media"]["nodes"] if m["id"] != pyr]
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
    s.gql("""mutation($id: ID!, $m: [MoveInput!]!) { productReorderMedia(id: $id, moves: $m) { job { id } } }""",
          {"id": p["id"], "m": [{"id": nouveau, "newPosition": "0"}]})  # la nouvelle photo en tête, devant la pyramide
    if anciens:
        s.gql("mutation($id: ID!, $m: [ID!]!) { productDeleteMedia(productId: $id, mediaIds: $m) { mediaUserErrors { message } } }",
              {"id": p["id"], "m": anciens})
    print("OK photo remplacée : %s (%d ancienne(s) retirée(s))" % (p["title"], len(anciens)))


if __name__ == "__main__":
    main()
