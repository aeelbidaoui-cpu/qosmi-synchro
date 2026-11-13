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


SAISONS = [("printemps", "Printemps", "Lente"), ("ete", "Été", "Zomer"), ("automne", "Automne", "Herfst"), ("hiver", "Hiver", "Winter")]
OCCASIONS = [("quotidien", "Tous les jours", "Elke dag"), ("bureau", "Bureau", "Kantoor"), ("rdv", "Rendez-vous", "Een date"),
             ("diner", "Dîner", "Etentje"), ("soiree", "Soirée", "Uitgaan"), ("mariage", "Mariage", "Bruiloft"), ("sport", "Sport", "Sport"),
             ("vacances", "Vacances", "Vakantie"), ("chic", "Événement chic", "Chique gelegenheid"), ("detente", "Détente", "Ontspannen")]


def filtres(s, type_, nom, valeurs):
    """Type de métaobjet + une fiche par valeur (FR, traduction NL) + définition du métachamp produit liste. Renvoie {id: gid}."""
    d = s.gql("query($t: String!) { metaobjectDefinitionByType(type: $t) { id } }", {"t": type_})["metaobjectDefinitionByType"]
    if not d:
        r = s.gql("""mutation($d: MetaobjectDefinitionCreateInput!) { metaobjectDefinitionCreate(definition: $d) {
                metaobjectDefinition { id } userErrors { field message code } } }""",
                  {"d": {"type": type_, "name": nom, "displayNameKey": "nom", "access": {"storefront": "PUBLIC_READ"},
                         "capabilities": {"translatable": {"enabled": True}},
                         "fieldDefinitions": [{"key": "nom", "name": "Nom", "type": "single_line_text_field", "required": True}]}})["metaobjectDefinitionCreate"]
        if r["userErrors"]:
            raise SystemExit("%s : %s" % (type_, r["userErrors"]))
        d = r["metaobjectDefinition"]
    gid = {}
    for k, fr, nl in valeurs:
        r = s.gql("""mutation($h: MetaobjectHandleInput!, $m: MetaobjectUpsertInput!) { metaobjectUpsert(handle: $h, metaobject: $m) {
                metaobject { id } userErrors { field message } } }""", {"h": {"type": type_, "handle": k}, "m": {"fields": [{"key": "nom", "value": fr}]}})["metaobjectUpsert"]
        gid[k] = r["metaobject"]["id"]
        tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": gid[k]})
        dig = {x["key"]: x["digest"] for x in (tr["translatableResource"] or {}).get("translatableContent", [])}
        if "nom" in dig:
            s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
                  {"id": gid[k], "t": [{"locale": "nl", "key": "nom", "value": nl, "translatableContentDigest": dig["nom"]}]})
    cle = {"saison": "saisons", "occasion": "occasions"}[type_]
    md = s.gql("""query($k: String!) { metafieldDefinitions(first: 5, ownerType: PRODUCT, namespace: "qosmi", key: $k) { nodes { id } } }""", {"k": cle})["metafieldDefinitions"]["nodes"]
    if not md:
        r = s.gql("""mutation($d: MetafieldDefinitionInput!) { metafieldDefinitionCreate(definition: $d) { createdDefinition { id } userErrors { field message } } }""",
                  {"d": {"name": nom + "s", "namespace": "qosmi", "key": cle, "ownerType": "PRODUCT", "type": "list.metaobject_reference",
                         "access": {"storefront": "PUBLIC_READ"}, "validations": [{"name": "metaobject_definition_id", "value": d["id"]}]}})["metafieldDefinitionCreate"]
        print("définition qosmi.%s :" % cle, r["userErrors"] or "créée")
    return gid


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
    # filtres de collection (Search & Discovery) : métaobjets « saison » et « occasion » (nom FR + NL), listes sur le produit
    refs = {"s": filtres(s, "saison", "Saison", SAISONS), "o": filtres(s, "occasion", "Occasion", OCCASIONS)}
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
        for k, cle in (("s", "saisons"), ("o", "occasions")):
            g = [refs[k][x] for x in v.get(k, []) if x in refs[k]]
            if g:
                lot.append({"ownerId": ids[h], "namespace": "qosmi", "key": cle, "type": "list.metaobject_reference", "value": json.dumps(g)})
        if len(lot) >= 22:
            envoyer(lot); faits += len(lot); lot = []
    if lot:
        envoyer(lot); faits += len(lot)
    print("OK %d métachamps posés (%d fiches absentes de la boutique)" % (faits, absents))


if __name__ == "__main__":
    main()
