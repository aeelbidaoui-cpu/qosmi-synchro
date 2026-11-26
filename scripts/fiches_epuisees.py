#!/usr/bin/env python3
"""Remet en ligne des fiches archivées (ou en brouillon), en « épuisé » (demande d'Amine du 26/11/2026 : « désarchive-les
et mets-les simplement en épuisé au lieu de les archiver »).

Pour chaque fiche : statut ACTIVE, visible sur la boutique en ligne, stock 0 sur tous les formats (pas de vente sans
stock), étiquette « garder-en-ligne » : la synchro ne la remasque plus et ne l'archive plus (scripts/site_synchro.py).
Si le grossiste a de nouveau du stock sur un de ses formats, la synchro le remet en vente normalement.

Usage :
  python3 scripts/fiches_epuisees.py              → état des fiches, sans rien changer
  python3 scripts/fiches_epuisees.py --appliquer  → remise en ligne en « épuisé »
Fiches : variable FICHES (adresses séparées par des virgules), sinon la liste ci-dessous.
"""
import os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from shopify_api import Shopify  # noqa: E402

ETIQUETTE = "garder-en-ligne"
FICHES = [
    "chanel-chance-eau-de-parfum-pour-femme",
    "giorgio-armani-my-way-eau-de-parfum-pour-femme",
    "guerlain-mon-guerlain-eau-de-parfum-pour-femme",
    "guerlain-shalimar-eau-de-parfum-pour-femme",
    "xerjoff-xj-1861-naxos-eau-de-parfum-mixte",
    "nishane-tero-extrait-de-parfum-mixte",
]

Q = """query($q: String!) { products(first: 3, query: $q) { nodes {
  id handle title status tags onlineStoreUrl totalInventory
  media(first: 1) { nodes { status } }
  variants(first: 30) { nodes { id sku title inventoryPolicy inventoryQuantity
    inventoryItem { id tracked inventoryLevels(first: 5) { nodes { location { id } } } } } } } } }"""


def fiche(s, h):
    d = s.gql(Q, {"q": "handle:" + h})["products"]["nodes"]
    return next((p for p in d if p["handle"] == h), None)


def erreurs(r):
    e = r.get("userErrors") or []
    return "; ".join(x.get("message", "") for x in e)


def appliquer(s, p, lieu, pub):
    msgs = []
    tags = sorted(set(p["tags"]) | {ETIQUETTE})
    r = s.gql("""mutation($p: ProductInput!) { productUpdate(input: $p) { product { status } userErrors { message } } }""",
              {"p": {"id": p["id"], "status": "ACTIVE", "tags": tags}})["productUpdate"]
    msgs.append("statut " + (erreurs(r) or r["product"]["status"]))
    r = s.gql("mutation($id: ID!, $p: ID!) { publishablePublish(id: $id, input: [{publicationId: $p}]) { userErrors { message } } }",
              {"id": p["id"], "p": pub})["publishablePublish"]
    msgs.append("boutique en ligne " + (erreurs(r) or "ok"))
    variantes = p["variants"]["nodes"]
    pol = [{"id": v["id"], "inventoryPolicy": "DENY"} for v in variantes if v["inventoryPolicy"] != "DENY"]
    if pol:
        r = s.gql("""mutation($p: ID!, $v: [ProductVariantsBulkInput!]!) { productVariantsBulkUpdate(productId: $p, variants: $v) {
                     userErrors { message } } }""", {"p": p["id"], "v": pol})["productVariantsBulkUpdate"]
        msgs.append("vente sans stock coupée " + (erreurs(r) or "ok"))
    for v in variantes:
        it = v["inventoryItem"]
        if not it["tracked"]:
            s.gql("mutation($id: ID!) { inventoryItemUpdate(id: $id, input: {tracked: true}) { userErrors { message } } }", {"id": it["id"]})
        if lieu not in [n["location"]["id"] for n in it["inventoryLevels"]["nodes"]]:
            r = s.gql("""mutation($i: ID!, $l: ID!) { inventoryActivate(inventoryItemId: $i, locationId: $l, available: 0) {
                         userErrors { message } } }""", {"i": it["id"], "l": lieu})["inventoryActivate"]
            if erreurs(r):
                msgs.append("stock %s : %s" % (v["sku"], erreurs(r)))
            continue
        q = int(v["inventoryQuantity"] or 0)
        if q != 0:
            r = s.gql("""mutation($in: InventorySetQuantitiesInput!) { inventorySetQuantities(input: $in) { userErrors { message } } }""",
                      {"in": {"name": "available", "reason": "correction",
                              "quantities": [{"inventoryItemId": it["id"], "locationId": lieu, "quantity": 0, "changeFromQuantity": q}]}}
                      )["inventorySetQuantities"]
            msgs.append("stock %s %d → 0 %s" % (v["sku"], q, erreurs(r) or "ok"))
    return " · ".join(msgs)


def main():
    import site_charger as sc
    from site_theme import publication_boutique
    s = Shopify()
    lieu, pub = sc.lieu(s), publication_boutique(s)
    ok = "--appliquer" in sys.argv
    liste = [h.strip() for h in (os.environ.get("FICHES") or "").split(",") if h.strip()] or FICHES
    for h in liste:
        p = fiche(s, h)
        if not p:
            print("INTROUVABLE %s" % h)
            continue
        photo = (p["media"]["nodes"] or [{}])[0].get("status")
        autres = s.gql('query($q: String!) { products(first: 10, query: $q) { nodes { handle title status } } }',
                       {"q": 'title:"%s"' % p["title"].replace('"', '')})["products"]["nodes"]
        autres = ["%s (%s)" % (a["handle"], a["status"]) for a in autres if a["handle"] != h and a["title"].lower() == p["title"].lower()]
        print("%s — %s · %s · %s · photo %s · stock %s · formats %d · étiquettes %s · autres fiches du même nom : %s"
              % (h, p["title"], p["status"], "en ligne" if p["onlineStoreUrl"] else "pas en ligne", photo, p["totalInventory"],
                 len(p["variants"]["nodes"]), ",".join(p["tags"])[:120], ", ".join(autres) or "aucune"))
        if ok:
            print("  → " + appliquer(s, p, lieu, pub))
            p2 = fiche(s, h)
            print("  → maintenant : %s · %s · stock %s" % (p2["status"], p2["onlineStoreUrl"] or "pas en ligne", p2["totalInventory"]))


if __name__ == "__main__":
    main()
