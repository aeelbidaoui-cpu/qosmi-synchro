#!/usr/bin/env python3
"""Redirections des pages introuvables (404) signalées par Google Search Console.

Demande d'Amine (21/11/2026, « vasy fait 1 et 2 ») : les 40 pages en 404 de la Search Console.
Pour chaque fiche produit introuvable (fiche passée en brouillon, archivée ou fusionnée), une redirection est créée,
en français et en néerlandais, vers :
  1. la fiche active du même parfum (même nom, ex. « …-2 » fusionnée) ;
  2. sinon la page de la marque (collection de la marque, métachamp boutique qosmi.marques) ;
  3. sinon la page « Parfums ».
Shopify n'applique une redirection QUE si l'adresse n'existe pas : si la fiche revient en ligne, elle s'affiche
normalement. Les adresses techniques de Shopify (/wpm, /cdn, /challenge…) sont ignorées.

  python3 scripts/redirections_404.py --essai   → affiche ce qui serait fait
  python3 scripts/redirections_404.py           → crée les redirections
"""
import json, os, re, sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)
from shopify_api import Shopify  # noqa: E402

LISTE = os.path.join(RACINE, "config", "redirections_404.json")
PAR_DEFAUT = "/collections/parfums"


def cle_nom(titre):
    t = (titre or "").lower().split(" — ")[0]
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def main():
    essai = "--essai" in sys.argv
    cfg = json.load(open(LISTE, encoding="utf-8"))
    s = Shopify()
    marques = {}
    try:
        mf = s.gql('{ shop { metafield(namespace: "qosmi", key: "marques") { value } } }')["shop"]["metafield"]
        marques = json.loads(mf["value"]) if mf else {}
    except Exception as e:
        print("Marques non lues :", str(e)[:120])
    Q = 'query($q: String!) { products(first: 10, query: $q) { nodes { handle title vendor status } } }'
    existantes = set()
    try:
        a = None
        while True:
            d = s.gql('query($a: String) { urlRedirects(first: 250, after: $a) { pageInfo { hasNextPage endCursor } nodes { path } } }', {"a": a})["urlRedirects"]
            existantes |= {n["path"] for n in d["nodes"]}
            if not d["pageInfo"]["hasNextPage"]:
                break
            a = d["pageInfo"]["endCursor"]
    except Exception as e:
        print("Redirections existantes non lues :", str(e)[:120])
    faites, ignorees = 0, 0
    M = "mutation($r: UrlRedirectInput!) { urlRedirectCreate(urlRedirect: $r) { userErrors { field message } } }"
    for handle in cfg.get("fiches", []):
        p = (s.gql(Q, {"q": "handle:%s" % handle})["products"]["nodes"] or [None])[0]
        if p and p["status"] == "ACTIVE":
            print("déjà en ligne :", handle)
            ignorees += 1
            continue
        cible = None
        if p:  # même parfum, fiche active
            cands = s.gql(Q, {"q": 'title:"%s" status:active' % p["title"].split(" — ")[0].replace('"', "")})["products"]["nodes"]
            cands = [c for c in cands if c["status"] == "ACTIVE" and cle_nom(c["title"]) == cle_nom(p["title"])]
            if cands:
                cible = "/products/" + cands[0]["handle"]
            elif marques.get(p["vendor"]):
                cible = "/collections/" + marques[p["vendor"]]
        cible = cible or PAR_DEFAUT
        for pre in ("", "/nl"):
            chemin = "%s/products/%s" % (pre, handle)
            if chemin in existantes:
                continue
            print(("ESSAI " if essai else "") + "%s → %s%s" % (chemin, pre, cible))
            if not essai:
                r = s.gql(M, {"r": {"path": chemin, "target": pre + cible}})["urlRedirectCreate"]["userErrors"]
                if r:
                    print("   erreur :", r)
                else:
                    faites += 1
    for chemin, cible in (cfg.get("autres") or {}).items():
        for pre in ("", "/nl"):
            if pre + chemin in existantes:
                continue
            print(("ESSAI " if essai else "") + "%s → %s%s" % (pre + chemin, pre, cible))
            if not essai:
                r = s.gql(M, {"r": {"path": pre + chemin, "target": pre + cible}})["urlRedirectCreate"]["userErrors"]
                faites += 0 if r else 1
                if r:
                    print("   erreur :", r)
    print("Redirections créées : %d · fiches déjà en ligne : %d" % (faites, ignorees))


if __name__ == "__main__":
    main()
