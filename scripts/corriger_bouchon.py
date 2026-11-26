#!/usr/bin/env python3
"""26/11/2026 (Amine) : les testeurs arrivent AVEC leur bouchon. Corrige les anciennes descriptions de fiches (FR) et leurs
traductions (NL, EN) qui disaient « souvent sans bouchon » / « vaak zonder dop » / « often without a cap »."""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
REMPL = [
    (r"dans un emballage simple, souvent sans bouchon", "avec son bouchon, dans un emballage simple"),
    (r"dans un emballage simple, parfois sans bouchon", "avec son bouchon, dans un emballage simple"),
    (r",? ?(souvent|parfois) sans (son |leur )?bouchon( décoratif)?", ", avec son bouchon"),
    (r"in een eenvoudige verpakking, vaak zonder dop", "met dop, in een eenvoudige verpakking"),
    (r",? ?(vaak|soms) zonder (sier)?dop(je)?", ", met dop"),
    (r"in simple packaging, often without a cap", "with its cap, in simple packaging"),
    (r",? ?(often|sometimes) without a (decorative )?cap", ", with its cap"),
]
MOTIF = re.compile(r"sans (son |leur )?bouchon|zonder (sier)?dop|without a (decorative )?cap", re.I)


def corriger(t):
    for a, b in REMPL:
        t = re.sub(a, b, t, flags=re.I)
    return t


Q = """query($a: String) { translatableResources(first: 50, resourceType: PRODUCT, after: $a) {
  nodes { resourceId translatableContent { key value digest }
          nl: translations(locale: "nl") { key value } en: translations(locale: "en") { key value } }
  pageInfo { hasNextPage endCursor } } }"""
QR = """query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key value digest } } }"""
MT = """mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { field message } } }"""
MP = """mutation($p: ProductUpdateInput!) { productUpdate(product: $p) { product { id } userErrors { field message } } }"""


def main():
    from shopify_api import Shopify
    s = Shopify()
    apres, lus, fr_ok, tr_ok, reste = None, 0, 0, 0, 0
    while True:
        r = s.gql(Q, {"a": apres})["translatableResources"]
        for nd in r["nodes"]:
            lus += 1
            src = {c["key"]: c for c in nd["translatableContent"]}
            body = (src.get("body_html") or {}).get("value") or ""
            tr = {lg: {c["key"]: c["value"] for c in (nd.get(lg) or [])} for lg in ("nl", "en")}
            besoin_fr = bool(MOTIF.search(body))
            besoin_tr = {lg: [k for k, v in d.items() if v and MOTIF.search(v)] for lg, d in tr.items()}
            if not besoin_fr and not any(besoin_tr.values()):
                continue
            rid = nd["resourceId"]
            if besoin_fr:
                nb = corriger(body)
                e = s.gql(MP, {"p": {"id": rid, "descriptionHtml": nb}})["productUpdate"]["userErrors"]
                if e:
                    print("  ERREUR FR", rid, e); continue
                fr_ok += 1
                # le texte source a changé : les traductions doivent être réenregistrées avec la nouvelle empreinte
                src = {c["key"]: c for c in s.gql(QR, {"id": rid})["translatableResource"]["translatableContent"]}
            for lg, d in tr.items():
                cles = set(besoin_tr[lg]) | ({"body_html"} if besoin_fr and d.get("body_html") else set())
                t = [{"locale": lg, "key": k, "value": corriger(d[k]), "translatableContentDigest": src[k]["digest"]}
                     for k in cles if k in src and d.get(k)]
                if t:
                    e = s.gql(MT, {"id": rid, "t": t})["translationsRegister"]["userErrors"]
                    if e:
                        print("  ERREUR", lg.upper(), rid, e)
                    else:
                        tr_ok += len(t)
            if MOTIF.search(corriger(body)):
                reste += 1
                print("  reste à voir :", rid, re.sub(r"<[^>]+>", " ", body)[:200])
        if not r["pageInfo"]["hasNextPage"]:
            break
        apres = r["pageInfo"]["endCursor"]
        if lus % 5000 == 0:
            print("  … %d fiches lues" % lus, flush=True)
    print("Fiches lues : %d · descriptions FR corrigées : %d · traductions corrigées : %d · à revoir : %d" % (lus, fr_ok, tr_ok, reste))


if __name__ == "__main__":
    main()
