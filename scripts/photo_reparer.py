#!/usr/bin/env python3
"""Remet la photo du flacon sur une fiche qui n'a plus que l'image « pyramide » des notes (27/11/2026, Amine :
« pourquoi y a pas de photo ? y a que les notes », Tom Ford Ombré Leather). Cherche, par EAN des formats de la fiche,
une autre fiche (active, brouillon ou archivée) qui a une vraie photo, et l'ajoute en première position.
FICHES : adresses séparées par des virgules. --appliquer pour modifier, sinon lecture seule."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import Shopify  # noqa: E402

Q_P = """query($q: String!) { products(first: 3, query: $q) { nodes { id handle title status
  media(first: 20) { nodes { id ... on MediaImage { image { url } } } } variants(first: 20) { nodes { barcode } } } } }"""
Q_V = """query($q: String!) { productVariants(first: 20, query: $q) { nodes { product { id handle title status
  media(first: 10) { nodes { ... on MediaImage { image { url } } } } } } } }"""
M_ADD = """mutation($id: ID!, $m: [CreateMediaInput!]!) { productCreateMedia(productId: $id, media: $m) {
  media { id status } mediaUserErrors { message } } }"""
M_ORD = """mutation($id: ID!, $m: [MoveInput!]!) { productReorderMedia(id: $id, moves: $m) { userErrors { message } } }"""


def vraie(url):
    return url and "/pyramide-" not in url


def main():
    s = Shopify()
    ok = "--appliquer" in sys.argv
    for h in [x.strip() for x in (os.environ.get("FICHES") or "").split(",") if x.strip()]:
        p = next((x for x in s.gql(Q_P, {"q": "handle:" + h})["products"]["nodes"] if x["handle"] == h), None)
        if not p:
            print("INTROUVABLE %s" % h)
            continue
        imgs = [m["image"]["url"] for m in p["media"]["nodes"] if m.get("image")]
        print("%s : %d image(s), dont vraies %d" % (h, len(imgs), sum(1 for u in imgs if vraie(u))))
        remplacer = "--remplacer" in sys.argv and os.environ.get("PHOTO")  # 27/11/2026 : photo Flaconi (accord d'Amine) en HD
        anciennes = [m["id"] for m in p["media"]["nodes"] if m.get("image") and vraie(m["image"]["url"])] if remplacer else []
        if any(vraie(u) for u in imgs) and not remplacer:
            continue
        donneur = None
        if os.environ.get("PHOTO"):  # 27/11/2026 : photo fournie (URL), pour une fiche sans autre fiche de même EAN
            donneur = ({"handle": "photo fournie", "status": "-"}, os.environ["PHOTO"])
        for ean in [] if donneur else {v["barcode"] for v in p["variants"]["nodes"] if v["barcode"]}:
            for v in s.gql(Q_V, {"q": "barcode:%s" % ean})["productVariants"]["nodes"]:
                q = v["product"]
                if q["id"] == p["id"]:
                    continue
                u = next((m["image"]["url"] for m in q["media"]["nodes"] if m.get("image") and vraie(m["image"]["url"])), None)
                if u:
                    donneur = (q, u)
                    break
            if donneur:
                break
        if not donneur:
            print("  aucune photo trouvée sur une autre fiche de même EAN")
            continue
        print("  photo de %s (%s) : %s" % (donneur[0]["handle"], donneur[0]["status"], donneur[1][:110]))
        if not ok:
            continue
        r = s.gql(M_ADD, {"id": p["id"], "m": [{"originalSource": donneur[1].split("?")[0], "mediaContentType": "IMAGE",
                                                "alt": p["title"]}]})["productCreateMedia"]
        if r["mediaUserErrors"]:
            print("  ERREUR %s" % r["mediaUserErrors"])
            continue
        mid = r["media"][0]["id"]
        e = s.gql(M_ORD, {"id": p["id"], "m": [{"id": mid, "newPosition": "0"}]})["productReorderMedia"]["userErrors"]
        print("  → photo ajoutée en 1re position %s" % (e or "ok"))
        if anciennes:
            e = s.gql("mutation($id: ID!, $m: [ID!]!) { productDeleteMedia(productId: $id, mediaIds: $m) { mediaUserErrors { message } } }",
                      {"id": p["id"], "m": anciennes})["productDeleteMedia"]["mediaUserErrors"]
            print("  → %d ancienne(s) photo(s) du flacon retirée(s) %s" % (len(anciennes), e or "ok"))


if __name__ == "__main__":
    main()
