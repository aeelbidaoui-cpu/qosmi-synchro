#!/usr/bin/env python3
"""Code de bienvenue (15/11/2026, décision d'Amine) : BIENVENUE = 3 € de réduction sur la commande, une fois par client,
cumulable avec la livraison offerte. 3 € au plus : chaque parfum garde au moins 5 € net (règle de prix), donc jamais de perte.
Le montant n'est pas écrit dans l'e-mail de bienvenue (« un petit cadeau »)."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CODE, MONTANT = "BIENVENUE", "3.00"


def main():
    from shopify_api import Shopify
    s = Shopify()
    ex = s.gql('query($q: String!) { codeDiscountNodeByCode(code: $q) { id } }', {"q": CODE}).get("codeDiscountNodeByCode")
    entree = {"title": "Bienvenue (inscription newsletter)", "code": CODE, "startsAt": "2026-11-15T00:00:00Z",
              "customerSelection": {"all": True}, "appliesOncePerCustomer": True,
              "combinesWith": {"shippingDiscounts": True, "orderDiscounts": False, "productDiscounts": False},
              "customerGets": {"items": {"all": True}, "value": {"discountAmount": {"amount": MONTANT, "appliesOnEachItem": False}}}}
    if ex:
        r = s.gql("""mutation($id: ID!, $d: DiscountCodeBasicInput!) { discountCodeBasicUpdate(id: $id, basicCodeDiscount: $d) {
                     codeDiscountNode { id } userErrors { field message } } }""", {"id": ex["id"], "d": entree})["discountCodeBasicUpdate"]
    else:
        r = s.gql("""mutation($d: DiscountCodeBasicInput!) { discountCodeBasicCreate(basicCodeDiscount: $d) {
                     codeDiscountNode { id } userErrors { field message } } }""", {"d": entree})["discountCodeBasicCreate"]
    if r["userErrors"]:
        sys.exit("ERREUR : %s" % r["userErrors"])
    print("Code %s OK : %s € sur la commande, une fois par client, cumulable avec la livraison offerte" % (CODE, MONTANT))


if __name__ == "__main__":
    main()
