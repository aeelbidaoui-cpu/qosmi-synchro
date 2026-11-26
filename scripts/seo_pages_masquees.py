"""26/11/2026 (audit SEO) : pages utilitaires sans contenu à indexer (favoris, page Instagram) retirées des résultats de
recherche et du sitemap via le champ méta seo.hidden = 1 (méthode Shopify). Les pages restent en ligne et accessibles."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import Shopify

PAGES = ["favoris", "instagram"]

def main():
    s = Shopify()
    for h in PAGES:
        d = s.gql('query($q: String!) { pages(first: 5, query: $q) { nodes { id handle title } } }', {"q": "handle:%s" % h})
        p = next((n for n in d["pages"]["nodes"] if n["handle"] == h), None)
        if not p:
            print("  %-10s introuvable" % h)
            continue
        r = s.gql("""mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) { userErrors { field message } } }""",
                  {"m": [{"ownerId": p["id"], "namespace": "seo", "key": "hidden", "type": "number_integer", "value": "1"}]})
        print("  %-10s masquée des moteurs de recherche : %s" % (h, r["metafieldsSet"]["userErrors"] or "ok"))

if __name__ == "__main__":
    main()
