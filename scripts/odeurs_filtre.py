#!/usr/bin/env python3
"""Filtre « Odeurs » dans les collections (12/11/2026, recherche par odeurs, demande d'Amine).

1. Une fiche « odeur » par odeur (métaobjet qosmi_odeur, nom FR + traduction NL), tirées de scripts/odeurs.py.
2. Métachamp produit qosmi.odeurs = liste des odeurs du parfum (parfums de config/descriptions_parfums.json).
3. Le filtre lui-même s'ajoute une fois dans l'app Search & Discovery (Filtres → Ajouter → « Odeurs »).
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import odeurs

TYPE = "odeur"


def erreurs(r, cle):
    e = (r.get(cle) or {}).get("userErrors") or []
    if e:
        raise SystemExit("%s : %s" % (cle, json.dumps(e, ensure_ascii=False)[:600]))
    return r[cle]


def main():
    from shopify_api import Shopify
    s = Shopify()
    # 1. définition du métaobjet
    global TYPE
    d = None
    for t in ("odeur", "$app:odeur"):  # 12/11/2026 : « qosmi_odeur » refusé (« réservé à une autre application »)
        TYPE = t
        d = s.gql("query($t: String!) { metaobjectDefinitionByType(type: $t) { id } }", {"t": TYPE})["metaobjectDefinitionByType"]
        if d:
            break
        r = s.gql("""mutation($d: MetaobjectDefinitionCreateInput!) { metaobjectDefinitionCreate(definition: $d) {
                metaobjectDefinition { id } userErrors { field message code } } }""",
                  {"d": {"type": TYPE, "name": "Odeur", "displayNameKey": "nom",
                         "access": {"storefront": "PUBLIC_READ"},
                         "capabilities": {"translatable": {"enabled": True}},
                         "fieldDefinitions": [{"key": "nom", "name": "Nom", "type": "single_line_text_field", "required": True}]}})["metaobjectDefinitionCreate"]
        print("type %s : %s" % (t, r["userErrors"] or "créé"))
        if not r["userErrors"]:
            d = r["metaobjectDefinition"]
            break
    if not d:
        raise SystemExit("Aucun type de métaobjet accepté")
    def_id = d["id"]

    # 2. une fiche par odeur précise (pas les « toute la famille »)
    idx, _ = odeurs.construire_index()
    gid = {}
    for o in idx["odeurs"]:
        oid, fam, fr, nl = o
        if oid.startswith("tout_"):
            continue
        r = erreurs(s.gql("""mutation($h: MetaobjectHandleInput!, $m: MetaobjectUpsertInput!) { metaobjectUpsert(handle: $h, metaobject: $m) {
                metaobject { id } userErrors { field message code } } }""",
                          {"h": {"type": TYPE, "handle": oid.replace("_", "-")},
                           "m": {"fields": [{"key": "nom", "value": fr}]}}), "metaobjectUpsert")
        gid[oid] = r["metaobject"]["id"]
        tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": gid[oid]})
        dig = {x["key"]: x["digest"] for x in (tr["translatableResource"] or {}).get("translatableContent", [])}
        if "nom" in dig:
            s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
                  {"id": gid[oid], "t": [{"locale": "nl", "key": "nom", "value": nl, "translatableContentDigest": dig["nom"]}]})
    print("Odeurs : %d fiches (FR + NL)" % len(gid))

    # 3. définition du métachamp produit
    md = s.gql("""{ metafieldDefinitions(first: 5, ownerType: PRODUCT, namespace: "qosmi", key: "odeurs") { nodes { id } } }""")["metafieldDefinitions"]["nodes"]
    if not md:
        erreurs(s.gql("""mutation($d: MetafieldDefinitionInput!) { metafieldDefinitionCreate(definition: $d) {
                createdDefinition { id } userErrors { field message code } } }""",
                      {"d": {"name": "Odeurs", "namespace": "qosmi", "key": "odeurs", "ownerType": "PRODUCT",
                             "type": "list.metaobject_reference", "access": {"storefront": "PUBLIC_READ"},
                             "validations": [{"name": "metaobject_definition_id", "value": def_id}]}}), "metafieldDefinitionCreate")
        print("Métachamp produit qosmi.odeurs créé")

    # 4. identifiants des produits par handle
    ids, apres = {}, None
    while True:
        r = s.gql("query($a: String) { products(first: 250, after: $a) { nodes { id handle } pageInfo { hasNextPage endCursor } } }", {"a": apres})["products"]
        ids.update({p["handle"]: p["id"] for p in r["nodes"]})
        if not r["pageInfo"]["hasNextPage"]:
            break
        apres = r["pageInfo"]["endCursor"]
    rang = {o[0]: i for i, o in enumerate(idx["odeurs"])}
    inv = {i: o[0] for o, i in ((o, rang[o[0]]) for o in idx["odeurs"])}
    lot, faits, absents = [], 0, 0
    for h, v in idx["parfums"].items():
        if h not in ids:
            absents += 1
            continue
        liste = [gid[inv[int(i)]] for i in v.split("|")[0].split(",") if i and inv[int(i)] in gid]
        if not liste:
            continue
        lot.append({"ownerId": ids[h], "namespace": "qosmi", "key": "odeurs", "type": "list.metaobject_reference", "value": json.dumps(liste)})
        if len(lot) == 25:
            erreurs(s.gql("mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) { userErrors { field message } } }", {"m": lot}), "metafieldsSet")
            faits += len(lot); lot = []
    if lot:
        erreurs(s.gql("mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) { userErrors { field message } } }", {"m": lot}), "metafieldsSet")
        faits += len(lot)
    print("OK odeurs posées sur %d parfums (%d parfums de la liste absents de la boutique)" % (faits, absents))


def libelle_nl():
    """Titre du filtre Search & Discovery en néerlandais : « Odeurs » → « Geuren »."""
    from shopify_api import Shopify
    s = Shopify()
    r = s.gql("""{ translatableResources(first: 50, resourceType: FILTER) { nodes { resourceId translatableContent { key value digest locale } } } }""")
    n = 0
    for res in r["translatableResources"]["nodes"]:
        for c in res["translatableContent"]:
            if c["value"] == "Odeurs":
                e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
                          {"id": res["resourceId"], "t": [{"locale": "nl", "key": c["key"], "value": "Geuren", "translatableContentDigest": c["digest"]}]})
                print("Libellé NL :", res["resourceId"], e["translationsRegister"]["userErrors"] or "Geuren")
                n += 1
    print("OK libellés traduits :", n)


if __name__ == "__main__":
    if "--libelle" in sys.argv:
        libelle_nl()
    else:
        main()
