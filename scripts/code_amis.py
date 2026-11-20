#!/usr/bin/env python3
"""Code DOUNIA (20/11/2026, demande d'Amine) : livraison offerte dès 1 article. Sa sœur Dounia en fait la promotion :
ses abonnés ont la livraison gratuite. (Créé d'abord sous le nom AMISQOSMI, renommé le jour même.)
Utilisable plusieurs fois, sans minimum, sur toutes les livraisons (point relais et domicile), cumulable avec BIENVENUE."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# code → (ancien nom éventuel, titre dans l'admin)
CODES = {"DOUNIA": ("AMISQOSMI", "DOUNIA — livraison offerte dès 1 article (abonnés de Dounia)"),
         "NASSIM": (None, "NASSIM — livraison offerte dès 1 article")}  # 20/11/2026 (Amine) : même avantage que DOUNIA


def creer(s, code, ancien, titre):
    q = 'query($q: String!) { codeDiscountNodeByCode(code: $q) { id } }'
    ex = s.gql(q, {"q": code}).get("codeDiscountNodeByCode") or (ancien and s.gql(q, {"q": ancien}).get("codeDiscountNodeByCode"))
    entree = {"title": titre, "code": code, "startsAt": "2026-11-20T00:00:00Z",
              "customerSelection": {"all": True}, "destination": {"all": True}, "appliesOncePerCustomer": False,
              "combinesWith": {"shippingDiscounts": False, "orderDiscounts": True, "productDiscounts": True}}
    if ex:
        r = s.gql("""mutation($id: ID!, $d: DiscountCodeFreeShippingInput!) { discountCodeFreeShippingUpdate(id: $id, freeShippingCodeDiscount: $d) {
                     codeDiscountNode { id } userErrors { field message } } }""", {"id": ex["id"], "d": entree})["discountCodeFreeShippingUpdate"]
    else:
        r = s.gql("""mutation($d: DiscountCodeFreeShippingInput!) { discountCodeFreeShippingCreate(freeShippingCodeDiscount: $d) {
                     codeDiscountNode { id } userErrors { field message } } }""", {"d": entree})["discountCodeFreeShippingCreate"]
    if r["userErrors"]:
        sys.exit("ERREUR %s : %s" % (code, r["userErrors"]))
    print("Code %s OK : livraison offerte dès 1 article, sans limite d'utilisation" % code)


def main():
    from shopify_api import Shopify
    s = Shopify()
    for code, (ancien, titre) in CODES.items():
        creer(s, code, ancien, titre)


if __name__ == "__main__":
    main()
