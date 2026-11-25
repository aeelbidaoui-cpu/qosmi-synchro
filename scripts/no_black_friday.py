#!/usr/bin/env python3
"""« No Black Friday » (25/11/2026, Amine : « je veux faire comme eux », exemple my-origines.com).
Pas de remise : on affiche que nos prix sont justes toute l'année. La collection reprend les fiches marquées « meilleur-prix »
par la mise à jour horaire (au moins un format en stock nettement moins cher que le prix de référence du marché), triées
par meilleures ventes. Jamais de pourcentage affiché (pas de prix de référence publiable, règle belge des annonces de prix).
Bandeau et diapositive d'accueil : theme_rk/sections/qk-annonces.liquid et theme_rk/snippets/qk-slide-bf.liquid."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HANDLE = "no-black-friday"
FR = ("<p><strong>Chez Qosmi, pas de faux rabais en novembre.</strong> Nos prix sont calculés au plus juste toute l'année : "
      "ils ne montent pas avant Black Friday pour mieux « baisser » ensuite.</p>"
      "<p>Voici les parfums que nous proposons en ce moment à un prix particulièrement doux. La sélection est mise à jour "
      "chaque heure, selon les stocks. Parfums 100 % authentiques et neufs, livrés dans 9 pays ou à retirer à Dilbeek.</p>")
NL = ("<p><strong>Bij Qosmi geen nepkortingen in november.</strong> Onze prijzen zijn het hele jaar zo scherp mogelijk: "
      "ze gaan niet eerst omhoog voor Black Friday om daarna te « zakken ».</p>"
      "<p>Hier vind je de parfums die we nu aan een bijzonder zachte prijs aanbieden. De selectie wordt elk uur bijgewerkt, "
      "volgens de voorraad. 100 % echte en nieuwe parfums, geleverd in 9 landen of af te halen in Dilbeek.</p>")
EN = ("<p><strong>At Qosmi, no fake discounts in November.</strong> Our prices are as fair as we can make them all year round: "
      "they don't go up before Black Friday only to \"drop\" afterwards.</p>"
      "<p>Here are the fragrances we currently offer at a particularly gentle price. The selection is updated every hour, "
      "based on stock. 100% authentic, brand-new fragrances, delivered to 9 countries or collected in Dilbeek.</p>")
SEO = {"fr": ("No Black Friday : des prix justes toute l'année | Qosmi",
              "Pas de faux rabais chez Qosmi : des parfums authentiques à prix justes toute l'année. Sélection mise à jour chaque heure."),
       "nl": ("No Black Friday: eerlijke prijzen, het hele jaar | Qosmi",
              "Geen nepkortingen bij Qosmi: echte parfums aan eerlijke prijzen, het hele jaar door. Selectie elk uur bijgewerkt."),
       "en": ("No Black Friday: fair prices all year round | Qosmi",
              "No fake discounts at Qosmi: authentic fragrances at fair prices all year round. Selection updated every hour.")}


def main():
    from shopify_api import Shopify
    from seo_boutique import traduire
    from site_theme import publication_boutique
    s = Shopify()
    champs = {"title": "No Black Friday", "descriptionHtml": FR, "sortOrder": "BEST_SELLING",
              "seo": {"title": SEO["fr"][0], "description": SEO["fr"][1]},
              "ruleSet": {"appliedDisjunctively": False, "rules": [{"column": "TAG", "relation": "EQUALS", "condition": "meilleur-prix"}]}}
    ex = s.gql("query($h: String!) { collectionByIdentifier(identifier: {handle: $h}) { id } }", {"h": HANDLE}).get("collectionByIdentifier")
    if ex:
        r = s.gql("mutation($c: CollectionInput!) { collectionUpdate(input: $c) { collection { id } userErrors { field message } } }",
                  {"c": dict(champs, id=ex["id"])})["collectionUpdate"]
    else:
        r = s.gql("mutation($c: CollectionInput!) { collectionCreate(input: $c) { collection { id } userErrors { field message } } }",
                  {"c": dict(champs, handle=HANDLE)})["collectionCreate"]
    if r["userErrors"]:
        sys.exit("ERREUR : %s" % r["userErrors"])
    cid = r["collection"]["id"]
    pub = publication_boutique(s)
    if pub:
        s.gql("mutation($id: ID!, $p: ID!) { publishablePublish(id: $id, input: [{publicationId: $p}]) { userErrors { message } } }",
              {"id": cid, "p": pub})
    tr = traduire(s, cid, {"title": "No Black Friday", "handle": "geen-black-friday", "body_html": NL,
                           "meta_title": SEO["nl"][0], "meta_description": SEO["nl"][1]})
    tr += " · EN %s" % traduire(s, cid, {"title": "No Black Friday", "body_html": EN,
                                         "meta_title": SEO["en"][0], "meta_description": SEO["en"][1]}, locale="en")
    n = s.gql("query($id: ID!) { collection(id: $id) { productsCount { count } } }", {"id": cid})["collection"]["productsCount"]["count"]
    print("Collection %s OK : %d fiches · NL %s" % (HANDLE, n, tr))


if __name__ == "__main__":
    main()
