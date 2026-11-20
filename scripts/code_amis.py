#!/usr/bin/env python3
"""Code « amis » (20/11/2026, demande d'Amine) : livraison offerte dès 1 article, pour les gens qu'il connaît.
Utilisable plusieurs fois, sans minimum, sur toutes les livraisons (point relais et domicile), cumulable avec BIENVENUE."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CODE = "AMISQOSMI"


def main():
    from shopify_api import Shopify
    s = Shopify()
    ex = s.gql('query($q: String!) { codeDiscountNodeByCode(code: $q) { id } }', {"q": CODE}).get("codeDiscountNodeByCode")
    entree = {"title": "Amis — livraison offerte dès 1 article", "code": CODE, "startsAt": "2026-11-20T00:00:00Z",
              "customerSelection": {"all": True}, "destination": {"all": True}, "appliesOncePerCustomer": False,
              "combinesWith": {"shippingDiscounts": False, "orderDiscounts": True, "productDiscounts": True}}
    if ex:
        r = s.gql("""mutation($id: ID!, $d: DiscountCodeFreeShippingInput!) { discountCodeFreeShippingUpdate(id: $id, freeShippingCodeDiscount: $d) {
                     codeDiscountNode { id } userErrors { field message } } }""", {"id": ex["id"], "d": entree})["discountCodeFreeShippingUpdate"]
    else:
        r = s.gql("""mutation($d: DiscountCodeFreeShippingInput!) { discountCodeFreeShippingCreate(freeShippingCodeDiscount: $d) {
                     codeDiscountNode { id } userErrors { field message } } }""", {"d": entree})["discountCodeFreeShippingCreate"]
    if r["userErrors"]:
        sys.exit("ERREUR : %s" % r["userErrors"])
    print("Code %s OK : livraison offerte dès 1 article, sans limite d'utilisation" % CODE)


if __name__ == "__main__":
    main()
