#!/usr/bin/env python3
"""Refus Google Shopping « Product page unavailable » (26/11/2026, Amine : « commence par les 1900 refus »).

Merchant Center refusait ~1 600 offres parce que leur page renvoie 404 : fiches passées en brouillon ou archivées
(soins mis en pause le 23/11, doublons masqués…) mais toujours publiées sur le canal Google & YouTube. Google garde
alors l'ancienne offre et la signale « page indisponible ».

Lecture seule par défaut : compte les fiches par statut et par canal, liste les « fantômes » (publiées sur Google
mais pas visibles sur la boutique). --appliquer : les retire du canal Google & YouTube seulement (la fiche reste
dans Shopify, rien n'est supprimé ; l'appli Google retire alors l'offre morte). Une fiche remise en ligne plus tard
est republiée sur Google par la synchro (publications_vente) ou par fiches_epuisees.py.
"""
import collections, json, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from shopify_api import Shopify  # noqa: E402

s = Shopify()
pubs = s.gql("{ publications(first: 20) { nodes { id name } } }")["publications"]["nodes"]
G = next(p["id"] for p in pubs if "google" in p["name"].lower())
B = next(p["id"] for p in pubs if p["name"] in ("Online Store", "Boutique en ligne"))

Q = """query($a: String, $g: ID!, $b: ID!) { products(first: 250, after: $a) { pageInfo { hasNextPage endCursor }
  nodes { id handle status productType updatedAt
    google: publishedOnPublication(publicationId: $g) boutique: publishedOnPublication(publicationId: $b) } } }"""

fiches, a = [], None
while True:
    d = s.gql(Q, {"a": a, "g": G, "b": B})["products"]
    fiches += d["nodes"]
    if not d["pageInfo"]["hasNextPage"]:
        break
    a = d["pageInfo"]["endCursor"]

tab = collections.Counter((f["status"], "google" if f["google"] else "-", "boutique" if f["boutique"] else "-") for f in fiches)
print("Fiches : %d" % len(fiches))
for k, n in sorted(tab.items()):
    print("  %-9s %-7s %-9s %5d" % (k + (n,)))

fantomes = [f for f in fiches if f["google"] and not (f["status"] == "ACTIVE" and f["boutique"])]
print("\nFantômes (sur Google, pas visibles sur la boutique) : %d" % len(fantomes))
for k, n in collections.Counter((f["status"], f["productType"] or "?") for f in fantomes).most_common(30):
    print("  %-9s %-35s %5d" % (k + (n,)))
for f in fantomes[:15]:
    print("  ex. %s (%s, %s)" % (f["handle"], f["status"], f["updatedAt"][:10]))
temoin = [f for f in fiches if f["id"].endswith("/15762133287236")]
print("\nTémoin Cartier La Panthère Bon plan (15762133287236) : %s" % json.dumps(temoin, ensure_ascii=False))

if "--appliquer" in sys.argv:
    ok = err = 0
    for f in fantomes:
        r = s.gql("""mutation($id: ID!, $p: ID!) { publishableUnpublish(id: $id, input: [{publicationId: $p}]) {
                     userErrors { message } } }""", {"id": f["id"], "p": G})["publishableUnpublish"]
        if r["userErrors"]:
            err += 1
            print("  erreur %s : %s" % (f["handle"], r["userErrors"]))
        else:
            ok += 1
    print("Retirées du canal Google & YouTube : %d (erreurs %d)" % (ok, err))
