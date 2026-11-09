#!/usr/bin/env python3
"""SEO et Google Shopping, compléments du 09/11/2026.

--collections-vides : retire de la boutique en ligne (donc du sitemap) les collections sans aucun produit visible
                      (pages « Aucun produit trouvé » que Google traite comme des pages vides). Réversible : la collection
                      reste dans l'admin et se republie d'un clic.
--prix-unitaire     : prix au litre sur chaque variante dont le format est en ml (ex. « 100 ml »). Google Merchant Center le
                      demande en Europe (« Missing unit pricing measure ») et l'affiche à côté du prix.
"""
import os, re, sys, time

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

VIDES_CANDIDATES = ["soins", "maquillage", "coffrets", "testeurs", "frontpage", "all"]


def collections_vides(s):
    from site_theme import publication_boutique
    pub = publication_boutique(s)
    for h in VIDES_CANDIDATES:
        c = s.gql("""query($h: String!) { collectionByIdentifier(identifier: {handle: $h}) { id title
                     products(first: 50) { nodes { status onlineStoreUrl } } } }""", {"h": h}).get("collectionByIdentifier")
        if not c:
            print("  %-12s introuvable" % h)
            continue
        visibles = [p for p in c["products"]["nodes"] if p["status"] == "ACTIVE" and p["onlineStoreUrl"]]
        if visibles:
            print("  %-12s garde (%d produits visibles)" % (h, len(visibles)))
            continue
        if h == "all":  # page système de Shopify : on ne la touche pas
            continue
        r = s.gql("""mutation($id: ID!, $p: ID!) { publishableUnpublish(id: $id, input: [{publicationId: $p}]) { userErrors { message } } }""",
                  {"id": c["id"], "p": pub})["publishableUnpublish"]
        print("  %-12s retirée de la boutique en ligne %s" % (h, r["userErrors"] or "ok"))


def ml(valeur):
    m = re.fullmatch(r"\s*(\d+(?:[.,]\d+)?)\s*ml\s*", valeur or "", flags=re.I)
    return float(m.group(1).replace(",", ".")) if m else None


def prix_unitaire(s):
    q = """query($c: String) { products(first: 100, after: $c, query: "status:active") { pageInfo { hasNextPage endCursor }
           nodes { id variants(first: 50) { nodes { id selectedOptions { value } unitPriceMeasurement { quantityValue quantityUnit } } } } } }"""
    m = """mutation($p: ID!, $v: [ProductVariantsBulkInput!]!) { productVariantsBulkUpdate(productId: $p, variants: $v) {
           userErrors { field message } } }"""
    c, faits, deja, sans, err = None, 0, 0, 0, 0
    while True:
        d = s.gql(q, {"c": c})["products"]
        for p in d["nodes"]:
            maj = []
            for v in p["variants"]["nodes"]:
                vol = next((ml(o["value"]) for o in v["selectedOptions"] if ml(o["value"])), None)
                if not vol:
                    sans += 1
                    continue
                u = v.get("unitPriceMeasurement") or {}
                if u.get("quantityUnit") == "ML" and abs((u.get("quantityValue") or 0) - vol) < 0.01:
                    deja += 1
                    continue
                maj.append({"id": v["id"], "showUnitPrice": True,
                            "unitPriceMeasurement": {"quantityValue": vol, "quantityUnit": "ML", "referenceValue": 1, "referenceUnit": "L"}})
            if maj:
                e = s.gql(m, {"p": p["id"], "v": maj})["productVariantsBulkUpdate"]["userErrors"]
                if e:
                    err += 1
                    if err <= 3:
                        print("  erreur :", e)
                else:
                    faits += len(maj)
        if not d["pageInfo"]["hasNextPage"]:
            break
        c = d["pageInfo"]["endCursor"]
    print("Prix au litre : %d variantes mises à jour, %d déjà bonnes, %d sans format en ml, %d erreurs" % (faits, deja, sans, err))


if __name__ == "__main__":
    from shopify_api import Shopify
    s = Shopify()
    if "--collections-vides" in sys.argv:
        collections_vides(s)
    if "--prix-unitaire" in sys.argv:
        prix_unitaire(s)
