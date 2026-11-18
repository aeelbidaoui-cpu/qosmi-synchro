#!/usr/bin/env python3
"""Deux modes de livraison en Belgique (décision d'Amine du 18/11/2026) :
  - Point relais Mondial Relay : 2,95 € (le tarif « Standard » existant, renommé), offert dès 2 articles ;
  - Livraison à domicile : 6,95 € (nouveau ; un envoi à domicile coûte ~6,80 € TTC), jamais offerte.
La réduction automatique « Livraison offerte dès 2 articles » est limitée aux tarifs de 3 € maximum, donc au point relais.
Noms et descriptions traduits en néerlandais. Relançable sans effet.

  python3 scripts/livraison_modes.py --essai   # montre l'état actuel et ce qui changerait
  python3 scripts/livraison_modes.py
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ESSAI = "--essai" in sys.argv

RELAIS = {"fr": "Point relais Mondial Relay", "nl": "Mondial Relay-afhaalpunt", "prix": "2.95",
          "desc_fr": "Au point relais le plus proche de ton adresse · offert dès 2 articles",
          "desc_nl": "In het afhaalpunt het dichtst bij je adres · gratis vanaf 2 artikelen"}
DOMICILE = {"fr": "Livraison à domicile", "nl": "Levering aan huis", "prix": "6.95",
            "desc_fr": "Livré à ta porte", "desc_nl": "Geleverd aan je deur"}
REDUC = "Livraison offerte dès 2 articles"
REDUC_NOUVEAU = "Livraison offerte en point relais dès 2 articles"

LIRE = """{ deliveryProfiles(first: 10) { nodes { id name
  profileLocationGroups { locationGroup { id } locationGroupZones(first: 50) { nodes {
    zone { id name countries { code { countryCode } } }
    methodDefinitions(first: 50) { nodes { id name description active
      rateProvider { ... on DeliveryRateDefinition { id price { amount currencyCode } } } } } } } } } } }"""
ECRIRE = """mutation($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile) { profile { id } userErrors { field message } } }"""


def traduire(s, rid, valeurs):
    tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": rid})
    res = tr.get("translatableResource") or {}
    dig = {x["key"]: x["digest"] for x in res.get("translatableContent") or []}
    t = [{"locale": "nl", "key": k, "value": v, "translatableContentDigest": dig[k]} for k, v in valeurs.items() if k in dig]
    if not t:
        return "rien à traduire (%s)" % ", ".join(dig) if dig else "ressource non traduisible"
    e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) {
                 userErrors { message } } }""", {"id": rid, "t": t})["translationsRegister"]["userErrors"]
    return "ok" if not e else e


def main():
    from shopify_api import Shopify
    s = Shopify()
    for p in s.gql(LIRE)["deliveryProfiles"]["nodes"]:
        for g in p["profileLocationGroups"]:
            for z in g["locationGroupZones"]["nodes"]:
                pays = [c["code"].get("countryCode") for c in z["zone"]["countries"]]
                defs = z["methodDefinitions"]["nodes"]
                print("Profil %s / zone %s (%s) :" % (p["name"], z["zone"]["name"], ",".join(filter(None, pays))))
                for m in defs:
                    pr = ((m.get("rateProvider") or {}).get("price") or {}).get("amount")
                    print("   - %s : %s € %s" % (m["name"], pr, "" if m["active"] else "(inactif)"))
                if "BE" not in pays:
                    continue
                relais = next((m for m in defs if m["name"] in ("Standard", RELAIS["fr"])), None)
                domicile = next((m for m in defs if m["name"] == DOMICILE["fr"]), None)
                maj, cree = [], []
                if relais and (relais["name"] != RELAIS["fr"] or (relais.get("description") or "") != RELAIS["desc_fr"]):
                    rp = relais["rateProvider"]
                    maj.append({"id": relais["id"], "name": RELAIS["fr"], "description": RELAIS["desc_fr"],
                                "rateDefinition": {"id": rp["id"], "price": {"amount": RELAIS["prix"], "currencyCode": "EUR"}}})
                if not domicile:
                    cree.append({"name": DOMICILE["fr"], "description": DOMICILE["desc_fr"], "active": True,
                                 "rateDefinition": {"price": {"amount": DOMICILE["prix"], "currencyCode": "EUR"}}})
                print("   → à faire : %d renommage(s), %d création(s)" % (len(maj), len(cree)))
                if ESSAI or not (maj or cree):
                    continue
                zone = {"id": z["zone"]["id"]}
                if maj:
                    zone["methodDefinitionsToUpdate"] = maj
                if cree:
                    zone["methodDefinitionsToCreate"] = cree
                r = s.gql(ECRIRE, {"id": p["id"], "profile": {"locationGroupsToUpdate": [
                    {"id": g["locationGroup"]["id"], "zonesToUpdate": [zone]}]}})["deliveryProfileUpdate"]
                if r["userErrors"]:
                    sys.exit("Refus de Shopify : %s" % json.dumps(r["userErrors"], ensure_ascii=False))
                print("   modes de livraison mis à jour")
    if ESSAI:
        return
    # traductions NL des deux modes
    for p in s.gql(LIRE)["deliveryProfiles"]["nodes"]:
        for g in p["profileLocationGroups"]:
            for z in g["locationGroupZones"]["nodes"]:
                for m in z["methodDefinitions"]["nodes"]:
                    for mode in (RELAIS, DOMICILE):
                        if m["name"] == mode["fr"]:
                            print("Traduction NL « %s » : %s" % (mode["fr"], traduire(s, m["id"], {"name": mode["nl"], "description": mode["desc_nl"]})))
    # réduction « livraison offerte » : seulement les tarifs de 3 € maximum (le point relais)
    noeuds = s.gql("""{ discountNodes(first: 50, query: "type:free_shipping") { nodes { id discount { __typename
        ... on DiscountAutomaticFreeShipping { title status maximumShippingPrice { amount } } } } } }""")["discountNodes"]["nodes"]
    for n in noeuds:
        d = n["discount"]
        if d.get("title") not in (REDUC, REDUC_NOUVEAU):
            continue
        r = s.gql("""mutation($id: ID!, $d: DiscountAutomaticFreeShippingInput!) {
            discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $d) {
              automaticDiscountNode { id } userErrors { field message } } }""",
                  {"id": n["id"], "d": {"title": REDUC_NOUVEAU, "maximumShippingPrice": "3.00"}})["discountAutomaticFreeShippingUpdate"]
        print("Réduction « %s » : %s" % (REDUC_NOUVEAU, "limitée au point relais (tarifs ≤ 3 €)" if not r["userErrors"] else r["userErrors"]))


if __name__ == "__main__":
    main()
