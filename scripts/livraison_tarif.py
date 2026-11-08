#!/usr/bin/env python3
"""Change le prix des tarifs de livraison Shopify (décision d'Amine du 08/11/2026 : 6,95 € → 2,95 € en Belgique).

  python3 scripts/livraison_tarif.py 6.95 2.95      (ancien prix, nouveau prix ; tous les profils, toutes les zones)

Ne touche qu'aux tarifs dont le prix est exactement l'ancien prix. Affiche ce qui a été changé.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LIRE = """{ deliveryProfiles(first: 10) { nodes { id name
  profileLocationGroups { locationGroup { id } locationGroupZones(first: 50) { nodes {
    zone { id name }
    methodDefinitions(first: 50) { nodes { id name active
      rateProvider { ... on DeliveryRateDefinition { id price { amount currencyCode } } } } } } } } } } }"""

ECRIRE = """mutation($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile) { profile { id } userErrors { field message } } }"""


def main(ancien, nouveau):
    from shopify_api import Shopify
    s = Shopify()
    changes = 0
    for p in s.gql(LIRE)["deliveryProfiles"]["nodes"]:
        groupes = []
        for g in p["profileLocationGroups"]:
            zones = []
            for z in g["locationGroupZones"]["nodes"]:
                defs = []
                for m in z["methodDefinitions"]["nodes"]:
                    rp = m.get("rateProvider") or {}
                    prix = (rp.get("price") or {})
                    if rp.get("id") and abs(float(prix.get("amount", -1)) - ancien) < 0.001:
                        defs.append({"id": m["id"], "rateDefinition": {"id": rp["id"],
                                     "price": {"amount": "%.2f" % nouveau, "currencyCode": prix["currencyCode"]}}})
                        print("  %s / %s / %s : %.2f → %.2f %s" % (p["name"], z["zone"]["name"], m["name"], ancien, nouveau, prix["currencyCode"]))
                if defs:
                    zones.append({"id": z["zone"]["id"], "methodDefinitionsToUpdate": defs})
            if zones:
                groupes.append({"id": g["locationGroup"]["id"], "zonesToUpdate": zones})
        if groupes:
            r = s.gql(ECRIRE, {"id": p["id"], "profile": {"locationGroupsToUpdate": groupes}})["deliveryProfileUpdate"]
            if r["userErrors"]:
                sys.exit("Refus de Shopify : %s" % json.dumps(r["userErrors"], ensure_ascii=False))
            changes += sum(len(z["methodDefinitionsToUpdate"]) for g in groupes for z in g["zonesToUpdate"])
    print("Tarifs de livraison changés : %d" % changes)


if __name__ == "__main__":
    main(float(sys.argv[1]), float(sys.argv[2]))
