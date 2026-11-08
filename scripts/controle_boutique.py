#!/usr/bin/env python3
"""Contrôle en lecture seule : tarifs de livraison (zones, prix) avant l'ouverture."""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from shopify_api import Shopify
    s = Shopify()
    q = """{ deliveryProfiles(first: 10) { nodes { name default
      profileLocationGroups { locationGroupZones(first: 20) { nodes {
        zone { name countries { code { countryCode } name } }
        methodDefinitions(first: 20) { nodes { name active description
          rateProvider { ... on DeliveryRateDefinition { price { amount currencyCode } } }
          methodConditions { field operator conditionCriteria { ... on MoneyV2 { amount } ... on Weight { value unit } } } } } } } } } } }"""
    for th in s.gql("{ themes(first: 20) { nodes { name role } } }")["themes"]["nodes"]:
        print("thème : %s (%s)" % (th["name"], th["role"]))
    try:
        d = s.gql(q)
        print(json.dumps(d, ensure_ascii=False, indent=1)[:6000])
    except Exception as e:
        print("Livraison : lecture impossible :", str(e)[:300])


if __name__ == "__main__":
    main()
