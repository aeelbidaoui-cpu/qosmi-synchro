#!/usr/bin/env python3
"""Photos officielles des marques qui ont autorisé Qosmi à utiliser les images de leur site (04/11/2026) :
Mancera et Montale (même groupe). Lit le plan du site (sitemap) puis, sur chaque fiche, les données produit
(schema.org) : nom, photo, EAN de chaque contenance. Écrit config/photos_marques.json :
  {"par_ean": {ean: url}, "par_nom": {"marque|nom": url}, "maj": date}

  python3 scripts/photos_marques.py
"""
import html, json, os, re, sys, time, unicodedata, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(os.path.dirname(ICI), "config", "photos_marques.json")
AGENT = "Mozilla/5.0 (compatible; QosmiPhotos/1.0)"
SITES = {"Mancera": "https://www.manceraparfums.com", "Montale": "https://www.montaleparfums.com"}


def cle_nom(marque, nom):
    n = unicodedata.normalize("NFKD", html.unescape(nom or "")).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"\b(eau de parfum|edp|intense edp|parfum|extrait|\d+\s*ml)\b", " ", n)
    return marque.lower() + "|" + " ".join(re.findall(r"[a-z0-9]+", n))


def lire(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def produits_du_site(base):
    plan = lire(base + "/1_fr_0_sitemap.xml")
    urls = [u for u in re.findall(r"<loc><!\[CDATA\[(.*?)\]\]></loc>", plan) + re.findall(r"<loc>([^<]+)</loc>", plan)
            if re.search(r"/\d+-[^/]+\.html$", u)]
    return sorted(set(urls))


def fiche(url):
    t = lire(url)
    for bloc in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            d = json.loads(bloc.strip())
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("@type") == "Product":
            image = d.get("image")
            if isinstance(image, list):
                image = image[0] if image else None
            offres = d.get("offers") or []
            if isinstance(offres, dict):
                offres = [offres]
            eans = [re.sub(r"\D", "", str(o.get("gtin13") or o.get("gtin") or "")) for o in offres]
            return d.get("name"), image, [e for e in eans if len(e) >= 8]
    return None, None, []


def main():
    par_ean, par_nom, n = {}, {}, 0
    for marque, base in SITES.items():
        try:
            urls = produits_du_site(base)
        except Exception as e:
            print("%s : plan du site illisible (%s)" % (marque, e))
            continue
        print("%s : %d fiches" % (marque, len(urls)))
        for u in urls:
            try:
                nom, image, eans = fiche(u)
            except Exception as e:
                print("  illisible :", u, e)
                continue
            time.sleep(0.5)  # rythme raisonnable pour leur site
            if not (nom and image and image.startswith("http") and "default-large" not in image):
                continue
            n += 1
            par_nom.setdefault(cle_nom(marque, nom), image)
            for e in eans:
                par_ean[e.lstrip("0")] = image
    if n < 10:
        sys.exit("Trop peu de photos lues (%d) : fichier inchangé." % n)
    json.dump({"maj": time.strftime("%Y-%m-%d"), "marques": list(SITES), "par_ean": par_ean, "par_nom": par_nom},
              open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Photos officielles : %d parfums, %d EAN" % (len(par_nom), len(par_ean)))


if __name__ == "__main__":
    main()
