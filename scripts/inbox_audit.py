#!/usr/bin/env python3
"""Contrôle (17/11/2026) : ce que le chat Shopify Inbox peut lire sur la boutique publique ne doit révéler ni nos
fournisseurs, ni nos prix d'achat, ni nos marges. On lit ce qui est visible côté vitrine (étiquettes, champs
personnalisés publics, textes des fiches, pages et articles publiés) et on compte les correspondances.
Le dépôt est public : la liste des mots sensibles est construite à partir des secrets (jamais écrite ici) et le
journal n'affiche que des nombres et des noms de champs, jamais les mots trouvés."""
import os, re, sys
from urllib.parse import urlparse

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)


def mots_sensibles():
    m = set()
    for var in ("TRISTA_URL", "SOLELUNA_EMAIL"):
        v = os.environ.get(var, "")
        h = urlparse(v).hostname if "://" in v else v.split("@")[-1]
        if h:
            base = h.replace("www.", "").split(".")[0]
            if len(base) >= 4:
                m.add(base.lower())
    m.update(["prix d'achat", "inkoopprijs", "marge", "fournisseur", "leverancier", "unitcost", "coût d'achat"])
    return m


def main():
    from shopify_api import Shopify
    s = Shopify()
    mots = mots_sensibles()
    rx = re.compile("|".join(re.escape(x) for x in mots), re.I)
    print("Mots contrôlés : %d" % len(mots))
    # 1. champs personnalisés lisibles par la vitrine
    for owner in ("PRODUCT", "PRODUCTVARIANT", "COLLECTION", "PAGE", "SHOP"):
        d = s.gql("""query($o: MetafieldOwnerType!) { metafieldDefinitions(first: 100, ownerType: $o) {
          nodes { namespace key access { storefront } } } }""", {"o": owner})["metafieldDefinitions"]["nodes"]
        pub = ["%s.%s" % (n["namespace"], n["key"]) for n in d if (n["access"] or {}).get("storefront") == "PUBLIC_READ"]
        print("Champs %s lisibles en vitrine : %d %s" % (owner, len(pub), pub[:30]))
    # 2. fiches : étiquettes, textes, fournisseur affiché (vendor), champs publics
    a, n, tags_bad, desc_bad, vendor_bad, mf_bad, tags = None, 0, 0, 0, 0, 0, set()
    q = """query($a: String) { products(first: 100, after: $a, query: "status:active") { pageInfo { hasNextPage endCursor }
      nodes { tags vendor descriptionHtml metafields(first: 30) { nodes { namespace key value } } } } }"""
    while True:
        d = s.gql(q, {"a": a})["products"]
        for p in d["nodes"]:
            n += 1
            tags.update(p["tags"])
            tags_bad += any(rx.search(t) for t in p["tags"])
            desc_bad += bool(rx.search(p["descriptionHtml"] or ""))
            vendor_bad += bool(rx.search(p["vendor"] or ""))
            mf_bad += any(rx.search(m["value"] or "") for m in p["metafields"]["nodes"])
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]
    propres = sorted(t for t in tags if not rx.search(t))
    print("Fiches actives : %d · étiquettes suspectes : %d · textes : %d · marque affichée : %d · champs : %d"
          % (n, tags_bad, desc_bad, vendor_bad, mf_bad))
    print("Étiquettes distinctes : %d (dont %d suspectes) · exemples sans risque : %s"
          % (len(tags), len(tags) - len(propres), propres[:40]))
    # 3. pages et articles publiés
    pg = s.gql('{ pages(first: 250) { nodes { handle isPublished body } } }')["pages"]["nodes"]
    print("Pages publiées : %d · avec mot suspect : %s" % (sum(p["isPublished"] for p in pg),
          [p["handle"] for p in pg if p["isPublished"] and rx.search(p["body"] or "")]))
    print("Pages NON publiées (invisibles du chat) avec mot suspect : %d" % sum(1 for p in pg if not p["isPublished"] and rx.search(p["body"] or "")))
    ar = s.gql('{ articles(first: 250) { nodes { handle isPublished body } } }')["articles"]["nodes"]
    print("Articles publiés avec mot suspect : %s" % [x["handle"] for x in ar if x["isPublished"] and rx.search(x["body"] or "")])


if __name__ == "__main__":
    main()
