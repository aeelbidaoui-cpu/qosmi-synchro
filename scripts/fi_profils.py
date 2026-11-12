#!/usr/bin/env python3
"""Profil des parfums sur les fiches (13/11/2026, demande d'Amine).

config/profils_parfums.json (construit par scripts/fi_construire.py) → métachamp produit qosmi.profil (JSON),
lu par le snippet theme_rk/snippets/qk-profil.liquid : saison, tenue, sillage, occasions, pyramide FR/NL.
Données de saison, tenue, sillage et occasions : Fragrance Index (accord obtenu par Amine le 13/11/2026).

  python3 scripts/fi_profils.py            # pose les métachamps
  python3 scripts/fi_profils.py --essai    # compte seulement
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CHEMIN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "profils_parfums.json")
MUT = "mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) { userErrors { field message } } }"


def main():
    P = json.load(open(CHEMIN, encoding="utf-8"))["parfums"]
    print("profils dans le fichier :", len(P))
    if "--essai" in sys.argv:
        return
    from shopify_api import Shopify
    s = Shopify()
    md = s.gql("""{ metafieldDefinitions(first: 5, ownerType: PRODUCT, namespace: "qosmi", key: "profil") { nodes { id } } }""")["metafieldDefinitions"]["nodes"]
    if not md:
        r = s.gql("""mutation($d: MetafieldDefinitionInput!) { metafieldDefinitionCreate(definition: $d) {
                createdDefinition { id } userErrors { field message code } } }""",
                  {"d": {"name": "Profil du parfum", "namespace": "qosmi", "key": "profil", "ownerType": "PRODUCT",
                         "type": "json", "access": {"storefront": "PUBLIC_READ"}}})["metafieldDefinitionCreate"]
        print("définition qosmi.profil :", r["userErrors"] or "créée")
    ids, apres = {}, None
    while True:
        r = s.gql("query($a: String) { products(first: 250, after: $a) { nodes { id handle } pageInfo { hasNextPage endCursor } } }", {"a": apres})["products"]
        ids.update({p["handle"]: p["id"] for p in r["nodes"]})
        if not r["pageInfo"]["hasNextPage"]:
            break
        apres = r["pageInfo"]["endCursor"]
    lot, faits, absents = [], 0, 0
    def envoyer(l):
        e = s.gql(MUT, {"m": l})["metafieldsSet"]["userErrors"]
        if e:
            print("ERREUR", json.dumps(e, ensure_ascii=False)[:400])
    for h, v in P.items():
        if h not in ids:
            absents += 1
            continue
        lot.append({"ownerId": ids[h], "namespace": "qosmi", "key": "profil", "type": "json",
                    "value": json.dumps(v, ensure_ascii=False, separators=(",", ":"))})
        if len(lot) == 25:
            envoyer(lot); faits += len(lot); lot = []
    if lot:
        envoyer(lot); faits += len(lot)
    print("OK profils posés sur %d fiches (%d absentes de la boutique)" % (faits, absents))


if __name__ == "__main__":
    main()
