#!/usr/bin/env python3
"""Collection « Bons plans » / « Koopjes » (14/11/2026, demande d'Amine).

Collection automatique : toutes les fiches qui portent l'étiquette « bon-plan », posée par la mise à jour horaire
(scripts/site_synchro.py) quand une fiche a au moins une option « Bon plan » en stock. Texte, SEO et adresse FR + NL.
À lancer une fois (action « bons-plans » du workflow theme), puis action « menu » pour l'entrée de menu.
"""
import json, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

DELAI_FR, DELAI_NL = "5 à 10 jours ouvrables", "5 tot 10 werkdagen"
TEXTE_FR = ("<p>Un peu plus de patience, un meilleur prix. Sur ces parfums, choisis le format marqué « Bon plan » "
            "(ou « Sur commande » pour les parfums qu'on ne garde pas en continu) : on le commande spécialement pour toi "
            "et il part sous %s. Parfums authentiques et neufs.</p>" % DELAI_FR)
TEXTE_NL = ("<p>Iets meer geduld, een betere prijs. Kies bij deze parfums het formaat met „Koopje” "
            "(of „Op bestelling” voor parfums die we niet altijd in voorraad hebben): we bestellen het speciaal voor jou "
            "en het vertrekt binnen %s. Originele, nieuwe parfums.</p>" % DELAI_NL)
SEO_FR = ("Bons plans parfums : des parfums originaux et neufs à prix plus doux, commandés spécialement pour toi. "
          "Livraison partout en Belgique.")
SEO_NL = "Parfumkoopjes: originele, nieuwe parfums aan een zachtere prijs, speciaal voor jou besteld. Levering in heel België."


def main():
    from shopify_api import Shopify
    from seo_boutique import traduire
    from site_theme import publication_boutique
    s = Shopify()
    champs = {"title": "Bons plans", "descriptionHtml": TEXTE_FR, "sortOrder": "BEST_SELLING",
              "seo": {"title": "Bons plans parfums | Qosmi", "description": SEO_FR},
              "ruleSet": {"appliedDisjunctively": False, "rules": [{"column": "TAG", "relation": "EQUALS", "condition": "bon-plan"}]}}
    ex = s.gql("query($h: String!) { collectionByIdentifier(identifier: {handle: $h}) { id } }", {"h": "bons-plans"}).get("collectionByIdentifier")
    if ex:
        r = s.gql("mutation($c: CollectionInput!) { collectionUpdate(input: $c) { collection { id } userErrors { field message } } }",
                  {"c": dict(champs, id=ex["id"])})["collectionUpdate"]
    else:
        r = s.gql("mutation($c: CollectionInput!) { collectionCreate(input: $c) { collection { id } userErrors { field message } } }",
                  {"c": dict(champs, handle="bons-plans")})["collectionCreate"]
    if r["userErrors"]:
        sys.exit("ERREUR : %s" % r["userErrors"])
    cid = r["collection"]["id"]
    pub = publication_boutique(s)
    if pub:
        s.gql("mutation($id: ID!, $p: ID!) { publishablePublish(id: $id, input: [{publicationId: $p}]) { userErrors { message } } }",
              {"id": cid, "p": pub})
    tr = traduire(s, cid, {"title": "Koopjes", "handle": "koopjes", "body_html": TEXTE_NL,
                           "meta_title": "Parfumkoopjes | Qosmi", "meta_description": SEO_NL})
    n = s.gql("query($id: ID!) { collection(id: $id) { productsCount { count } } }", {"id": cid})["collection"]["productsCount"]["count"]
    print("Collection bons-plans OK : %d fiches · NL %s" % (n, tr))


if __name__ == "__main__":
    main()
