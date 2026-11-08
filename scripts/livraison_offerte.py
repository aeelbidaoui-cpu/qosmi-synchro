#!/usr/bin/env python3
"""Réduction automatique « Livraison offerte dès 2 articles » (décision d'Amine du 08/11/2026).

Tous les produits comptent (parfum, soin, autre) : 2 articles ou plus dans le panier = livraison gratuite.
Ne crée rien si une réduction du même nom existe déjà.
"""
import datetime as dt, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TITRE = "Livraison offerte dès 2 articles"


def main():
    from shopify_api import Shopify
    s = Shopify()
    existe = s.gql("""{ discountNodes(first: 50, query: "title:'%s'") { nodes { id discount { __typename
        ... on DiscountAutomaticFreeShipping { title status } } } } }""" % TITRE)["discountNodes"]["nodes"]
    for n in existe:
        d = n["discount"]
        if d.get("title") == TITRE:
            print("Déjà en place : %s (%s)" % (TITRE, d.get("status")))
            return
    r = s.gql("""mutation($d: DiscountAutomaticFreeShippingInput!) {
        discountAutomaticFreeShippingCreate(freeShippingAutomaticDiscount: $d) {
          automaticDiscountNode { id } userErrors { field code message } } }""",
              {"d": {"title": TITRE,
                     "startsAt": dt.datetime.now(dt.timezone.utc).isoformat(),
                     "minimumRequirement": {"quantity": {"greaterThanOrEqualToQuantity": "2"}},
                     "destination": {"all": True},
                     "combinesWith": {"productDiscounts": True, "orderDiscounts": True}}})
    r = r["discountAutomaticFreeShippingCreate"]
    if r["userErrors"]:
        sys.exit("Refus de Shopify : %s" % json.dumps(r["userErrors"], ensure_ascii=False))
    print("Créée : %s (%s)" % (TITRE, r["automaticDiscountNode"]["id"]))


if __name__ == "__main__":
    main()
