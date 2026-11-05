#!/usr/bin/env python3
"""Photos de Riklis Karto (rikliskarto.com) : autorisation donnée par téléphone le 05/11/2026 (mail de
confirmation annoncé). Catalogue public Shopify : /products.json (noms, marques, photos 2048 px), puis
/products/<handle>.js pour l'EAN de chaque contenance. Parfums seulement (Eau de Parfum, Extrait, Parfum).
Écrit config/photos_riklis.json : {"par_ean": {ean: url}, "par_nom": {"marque|nom": url}, "maj": date}.

  python3 scripts/photos_riklis.py
"""
import json, os, re, sys, time, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import photos_marques as pm  # noqa: E402

SORTIE = os.path.join(os.path.dirname(ICI), "config", "photos_riklis.json")
BASE = "https://rikliskarto.com"
TYPES = {"eau de parfum", "extrait de parfum", "parfum", "eau de toilette", "eau de cologne"}
MARQUES = {"montale paris": "Montale", "mancera paris": "Mancera"}
EXCLUS = re.compile(r"discovery|sample|proef|giftbox|gift box|set\b|coffret|refill", re.I)


def lire(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; QosmiPhotos/1.0)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def main():
    produits, page = [], 1
    while page < 20:
        d = lire("%s/products.json?limit=250&page=%d" % (BASE, page))
        if not d.get("products"):
            break
        produits += d["products"]
        page += 1
        time.sleep(0.6)
    print("Riklis Karto : %d fiches" % len(produits), flush=True)
    par_ean, par_nom, n = {}, {}, 0
    for p in produits:
        if (p.get("product_type") or "").lower() not in TYPES or EXCLUS.search(p.get("title", "")) or not p.get("images"):
            continue
        marque = MARQUES.get(p["vendor"].lower(), p["vendor"])
        image = p["images"][0]["src"].split("?")[0]
        n += 1
        par_nom.setdefault(pm.cle_nom(marque, p["title"]), image)
        try:
            d = lire("%s/products/%s.js" % (BASE, p["handle"]))
            for v in d.get("variants", []):
                e = re.sub(r"\D", "", v.get("barcode") or "")
                if len(e) >= 8:
                    par_ean[e.lstrip("0")] = image
        except Exception as e:
            print("  EAN illisibles :", p["handle"], str(e)[:80])
        time.sleep(0.6)
    if n < 10:
        sys.exit("Trop peu de photos lues (%d) : fichier inchangé." % n)
    json.dump({"maj": time.strftime("%Y-%m-%d"), "source": "rikliskarto.com", "par_ean": par_ean, "par_nom": par_nom},
              open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Photos Riklis Karto : %d parfums, %d EAN" % (n, len(par_ean)))


if __name__ == "__main__":
    main()
