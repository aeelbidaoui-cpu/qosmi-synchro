#!/usr/bin/env python3
"""Catalogue Rituals (boutique belge rituals.com/nl-be) pour bol — demande d'Amine du 18/11/2026 :
publier sur bol les produits Rituals (autorisation de Rituals), achetés au prix public belge, avec au moins 7 € net.

  python3 scripts/bol_rituals.py            → base/rituals_catalogue.json (gardé 20 h)

Pour chaque fiche produit du plan du site nl-be : code article, nom, catégorie, prix public BE TTC (prix « consumer »,
jamais le prix promo, pour ne pas vendre à perte quand une promo se termine) et disponibilité.
EAN = 8719134 + 5 derniers chiffres du code article + chiffre de contrôle (vérifié sur les paires code/EAN de leurs pages).
Le journal n'affiche que des nombres (dépôt public) : aucun prix ni nom de produit.
"""
import concurrent.futures as cf
import json
import os
import re
import sys
import time
import urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "base", "rituals_catalogue.json")
SITE = "https://www.rituals.com"
AGENT = "Mozilla/5.0 (compatible; Qosmi-catalogue/1.0; +https://qosmi.be)"
FRAIS_HEURES = 20


def lire(url, essais=3):
    for i in range(essais):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept-Language": "nl-BE,nl;q=0.9"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            time.sleep(2 + 3 * i)
    return None


def ean_de(code):
    s = "8719134" + code[-5:]
    t = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(s))
    return s + str((10 - t % 10) % 10)


def fiche(url):
    code = (re.search(r"-(\d{6,8})\.html$", url) or [None, None])[1]
    h = lire(url)
    if not h or not code:
        return code, None, []
    u = h.replace('\\"', '"')
    lds = []
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>([\s\S]*?)</script>', h):
        try:
            lds.append(json.loads(m.group(1)))
        except Exception:
            pass
    p = next((x for x in lds if isinstance(x, dict) and x.get("@type") == "Product"), {})
    bc = next((x for x in lds if isinstance(x, dict) and x.get("@type") == "BreadcrumbList"), None)
    cat = " > ".join(i["item"]["name"] for i in bc["itemListElement"][1:-1]) if bc else ""
    m = re.search(r'"prices":\[\{"country":"BE"[^\]]*?"priceInclVAT":"([\d.]+)"[^\]]*?"type":"consumer"', u)
    off = p.get("offers") or {}
    paires = re.findall(r'"tradeCode":"(\d{7})"[\s\S]{0,700}?"eanCode":"(\d{13})"', u)
    return code, {"nom": p.get("name") or "", "cat": cat, "prix_ttc": float(m.group(1)) if m else None,
                  "dispo": str(off.get("availability", "")).rsplit("/", 1)[-1]}, paires


def main():
    force = "--force" in sys.argv
    if not force and os.path.exists(SORTIE) and time.time() - os.path.getmtime(SORTIE) < FRAIS_HEURES * 3600:
        print("Rituals : catalogue encore frais, rien à relire", flush=True)
        return
    plan = lire(SITE + "/nl-be/sitemap-nl-be.xml") or ""
    urls = sorted(set(u for u in re.findall(r"<loc>([^<]+)</loc>", plan) if re.search(r"/nl-be/.+-\d{6,8}\.html$", u)))
    if len(urls) < 200:
        print("Rituals : plan du site illisible (%d fiches) : catalogue précédent gardé" % len(urls), flush=True)
        return
    cat, paires, erreurs = {}, {}, 0
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for code, d, pr in ex.map(fiche, urls):
            if not d:
                erreurs += 1
                continue
            paires.update(pr)
            if d["prix_ttc"]:
                cat[code] = d
    ok = sum(1 for c, e in paires.items() if ean_de(c) == e)
    for code, d in cat.items():
        d["ean"] = paires.get(code) or ean_de(code)
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as f:
        json.dump({"date": time.time(), "produits": cat}, f, ensure_ascii=False)
    print("Rituals : %d fiches lues, %d avec prix, %d en stock, %d erreurs ; règle EAN vérifiée sur %d/%d paires"
          % (len(urls), len(cat), sum(1 for d in cat.values() if d["dispo"] == "InStock"), erreurs, ok, len(paires)), flush=True)


if __name__ == "__main__":
    main()
