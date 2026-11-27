#!/usr/bin/env python3
"""Fiches du stock propre de Qosmi (achats hors grossiste branché), 27/11/2026.
Demande d'Amine du 27/11/2026 : Bois Impérial en stock propre, en vente à 90 €.
Le coût d'achat n'est PAS dans ce fichier (dépôt public) : il est saisi à part dans l'admin Shopify.
SKU « QD-<EAN> » : la synchro ne touche qu'aux SKU « QS- », et l'étiquette garder-en-ligne protège la fiche.
Usage : --essai (défaut) affiche ; --appliquer crée ou met à jour (prix, stock, coût, textes)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import Shopify  # noqa: E402

FICHES = [{
    "handle": "essential-parfums-bois-imperial-eau-de-parfum-mixte",
    "vendor": "Essential Parfums", "type": "Parfums mixtes",
    "tags": ["Essential Parfums", "Parfums mixtes", "garder-en-ligne", "stock-propre"],
    "ean": "3770010614630", "format": "100 ml", "prix": "90.00", "stock": 9,
    "titre": {"fr": "Essential Parfums Bois Impérial — Eau de Parfum mixte",
              "nl": "Essential Parfums Bois Impérial — Eau de Parfum unisex",
              "en": "Essential Parfums Bois Impérial — Eau de Parfum unisex"},
    "desc": {
        "fr": "<p>Bois Impérial est une eau de parfum mixte d'Essential Parfums, sortie en 2020 et signée par Quentin Bisch. "
              "Un boisé aromatique, porté par la fraîcheur épicée du poivre de Timut et le boisé de l'akigalawood.</p>"
              "<p>Flacon de 100 ml rechargeable. Produit authentique, neuf. En stock chez nous en Belgique.</p>"
              "<div class=\"qk-desc-profil\"><h3>Notes olfactives</h3>"
              "<p><strong>Notes de tête :</strong> Basilic, Poivre de Timut<br><strong>Notes de cœur :</strong> Vétiver, Notes boisées<br>"
              "<strong>Notes de fond :</strong> Akigalawood, Patchouli, Ambrofix</p>"
              "<p>Famille olfactive : boisé, aromatique. Sorti en 2020. Parfumeur : Quentin Bisch.</p></div>",
        "nl": "<p>Bois Impérial is een unisex eau de parfum van Essential Parfums, uitgebracht in 2020 en gecreëerd door Quentin Bisch. "
              "Een aromatisch houtgeurtje, gedragen door de pittige frisheid van Timutpeper en de houtige toets van akigalawood.</p>"
              "<p>Navulbare fles van 100 ml. Authentiek, nieuw product. Bij ons op voorraad in België.</p>"
              "<div class=\"qk-desc-profil\"><h3>Geurnoten</h3>"
              "<p><strong>Topnoten:</strong> Basilicum, Timutpeper<br><strong>Hartnoten:</strong> Vetiver, Houtige noten<br>"
              "<strong>Basisnoten:</strong> Akigalawood, Patchoeli, Ambrofix</p>"
              "<p>Geurfamilie: houtig, aromatisch. Uitgebracht in 2020. Parfumeur: Quentin Bisch.</p></div>",
        "en": "<p>Bois Impérial is a unisex eau de parfum by Essential Parfums, released in 2020 and created by Quentin Bisch. "
              "An aromatic woody scent, carried by the spicy freshness of Timut pepper and the woodiness of akigalawood.</p>"
              "<p>Refillable 100 ml bottle. Authentic, new product. In stock with us in Belgium.</p>"
              "<div class=\"qk-desc-profil\"><h3>Fragrance notes</h3>"
              "<p><strong>Top notes:</strong> Basil, Timut pepper<br><strong>Heart notes:</strong> Vetiver, Woody notes<br>"
              "<strong>Base notes:</strong> Akigalawood, Patchouli, Ambrofix</p>"
              "<p>Olfactory family: woody, aromatic. Released in 2020. Perfumer: Quentin Bisch.</p></div>"},
}]

M_SET = """mutation($p: ProductSetInput!) { productSet(synchronous: true, input: $p) {
  product { id handle status variants(first: 5) { nodes { id sku inventoryItem { id } } } } userErrors { field message } } }"""
M_PUB = "mutation($id: ID!, $i: [PublicationInput!]!) { publishablePublish(id: $id, input: $i) { userErrors { message } } }"
Q_TR = "query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key value digest locale } } }"
M_TR = "mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { field message } } }"


def main():
    import site_charger as sc
    from site_synchro import publications_vente
    s = Shopify()
    lieu = sc.lieu(s)
    ok = "--appliquer" in sys.argv
    for f in FICHES:
        ex = s.gql('query($q: String!) { products(first: 3, query: $q) { nodes { id handle status } } }',
                   {"q": "handle:" + f["handle"]})["products"]["nodes"]
        ex = next((p for p in ex if p["handle"] == f["handle"]), None)
        print("%s : %s · %s € · stock %d · EAN %s" % (f["handle"], "existe (%s)" % ex["status"] if ex else "nouvelle",
                                                         f["prix"], f["stock"], f["ean"]))
        if not ok:
            continue
        p = {"handle": f["handle"], "title": f["titre"]["fr"], "descriptionHtml": f["desc"]["fr"], "vendor": f["vendor"],
             "productType": f["type"], "tags": f["tags"], "status": "ACTIVE",
             "productOptions": [{"name": "Format", "values": [{"name": f["format"]}]}],
             "variants": [{"optionValues": [{"optionName": "Format", "name": f["format"]}], "price": f["prix"],
                           "sku": "QD-" + f["ean"], "barcode": f["ean"], "inventoryPolicy": "DENY", "taxable": True,
                           "inventoryItem": {"tracked": True, "requiresShipping": True},
                           "inventoryQuantities": [{"locationId": lieu, "name": "available", "quantity": f["stock"]}]}]}
        if ex:
            p["id"] = ex["id"]
        r = s.gql(M_SET, {"p": p})["productSet"]
        if r["userErrors"]:
            print("  ERREUR %s" % r["userErrors"])
            continue
        pid = r["product"]["id"]
        print("  → %s %s" % (r["product"]["status"], pid))
        e = s.gql(M_PUB, {"id": pid, "i": [{"publicationId": x} for x in publications_vente(s)]})["publishablePublish"]["userErrors"]
        print("  canaux de vente : %s" % (e or "ok"))
        dig = {c["key"]: c["digest"] for c in s.gql(Q_TR, {"id": pid})["translatableResource"]["translatableContent"]}
        for loc in ("nl", "en"):
            t = [{"locale": loc, "key": "title", "value": f["titre"][loc], "translatableContentDigest": dig["title"]},
                 {"locale": loc, "key": "body_html", "value": f["desc"][loc], "translatableContentDigest": dig["body_html"]}]
            e = s.gql(M_TR, {"id": pid, "t": t})["translationsRegister"]["userErrors"]
            print("  traduction %s : %s" % (loc, e or "ok"))
        print("  https://qosmi.be/products/%s" % f["handle"])


if __name__ == "__main__":
    main()
