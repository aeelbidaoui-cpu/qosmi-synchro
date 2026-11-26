#!/usr/bin/env python3
"""26/11/2026 (Amine) : les testeurs arrivent AVEC leur bouchon. Recherche, en lecture seule, de toute phrase qui dit le
contraire (FR, NL, EN) : fiches, pages, articles, collections, politiques, et leurs traductions."""
import json, os, re, sys, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MOTIF = re.compile(r"(sans (son |leur |de |le )?(bouchon|capuchon)|parfois sans|bouchon (manquant|absent)|"
                   r"zonder (sier)?(dop|dopje|kapje)|geen dop|soms zonder|"
                   r"without (a |its |their |the )?(decorative )?cap|no cap|missing cap|sometimes without)", re.I)


def trouve(nom, *textes):
    for t in textes:
        for m in MOTIF.finditer(re.sub(r"<[^>]+>", " ", t or "")):
            a = max(0, m.start() - 80)
            print("  %s :: %s" % (nom, " ".join(re.sub(r"<[^>]+>", " ", t)[a:m.end() + 60].split())))


def main():
    from shopify_api import Shopify
    s = Shopify()
    q = """{ products { edges { node { id handle descriptionHtml } } } }"""
    op = s.gql("""mutation($q: String!) { bulkOperationRunQuery(query: $q) { bulkOperation { id } userErrors { message } } }""", {"q": q})["bulkOperationRunQuery"]["bulkOperation"]["id"]
    while True:
        b = s.gql("query($id: ID!) { bulkOperation(id: $id) { status url } }", {"id": op})["bulkOperation"]
        if b["status"] in ("COMPLETED", "FAILED", "CANCELED", "EXPIRED"):
            break
        time.sleep(5)
    n = 0
    for l in urllib.request.urlopen(b["url"]).read().decode().splitlines() if b.get("url") else []:
        x = json.loads(l); n += 1
        trouve("fiche " + x["handle"], x.get("descriptionHtml"))
    print("Fiches lues :", n)
    for typ in ("PRODUCT", "PAGE", "ARTICLE", "COLLECTION", "SHOP_POLICY", "ONLINE_STORE_THEME", "METAOBJECT"):
        apres, vus = None, 0
        while True:
            try:
                r = s.gql("""query($t: TranslatableResourceType!, $a: String) { translatableResources(first: 100, resourceType: $t, after: $a) {
                    nodes { resourceId translatableContent { key value }
                            nl: translations(locale: "nl") { key value } en: translations(locale: "en") { key value } }
                    pageInfo { hasNextPage endCursor } } }""", {"t": typ, "a": apres})["translatableResources"]
            except Exception as e:
                print("  %s : %s" % (typ, str(e)[:150])); break
            for nd in r["nodes"]:
                vus += 1
                for c in nd["translatableContent"]:
                    trouve("%s %s %s FR" % (typ, nd["resourceId"].split("/")[-1], c["key"]), c.get("value"))
                for lg in ("nl", "en"):
                    for c in nd.get(lg) or []:
                        trouve("%s %s %s %s" % (typ, nd["resourceId"].split("/")[-1], c["key"], lg.upper()), c.get("value"))
            if not r["pageInfo"]["hasNextPage"] or typ == "PRODUCT" and vus >= 20000:
                break
            apres = r["pageInfo"]["endCursor"]
        print("%s : %d ressources lues" % (typ, vus))


if __name__ == "__main__":
    main()
