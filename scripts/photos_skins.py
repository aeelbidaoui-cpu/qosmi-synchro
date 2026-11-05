#!/usr/bin/env python3
"""Photos de Skins (skins.nl) pour les marques que Qosmi vend : autorisation de Skins du 05/11/2026
(« toutes les marques qu'on possède »). Lit le plan du site, garde les fiches des marques présentes dans le
catalogue Qosmi, puis lit sur chaque fiche les données produit (schema.org) : nom, EAN (gtin), photo d'origine.
Écrit config/photos_skins.json : {"par_ean": {ean: url}, "par_nom": {"marque|nom": url}, "maj": date}.
Reprend là où il s'est arrêté (fichier d'avancement), une page par seconde au plus.

  python3 scripts/photos_skins.py [chemin/site_produits.json]
"""
import gzip, json, os, re, sys, time, unicodedata, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import photos_marques as pm  # noqa: E402

RACINE = os.path.dirname(ICI)
SORTIE = os.path.join(RACINE, "config", "photos_skins.json")
AVANCE = os.path.join(RACINE, "base", "photos_skins_avancement.json")
BASE = "https://www.skins.nl"
ALIAS = {"by-kilian": "kilian-paris", "le-labo": "le-labo-fragrances"}
EXCLUS = re.compile(r"sample|proef|staal|gift ?set|giftset|coffret|discovery|refill|navulling|candle|kaars|"
                    r"body|shower|douche|hair|haar|soap|zeep|deodorant|lotion|cream|creme|crème|diffuser|"
                    r"home ?spray|room ?spray|travel ?set|miniature", re.I)


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def lire(url, brut=False):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; QosmiPhotos/1.0)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = r.read()
    return d if brut else d.decode("utf-8", "replace")


def main():
    catalogue = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RACINE, "base", "site_produits.json")
    marques = {ALIAS.get(slug(p["marque"]), slug(p["marque"])): p["marque"] for p in json.load(open(catalogue, encoding="utf-8"))}
    index = lire(BASE + "/sitemap.xml")
    urls = []
    for plan in re.findall(r"<loc>([^<]+)</loc>", index):
        t = lire(plan, brut=True)
        t = (gzip.decompress(t) if plan.endswith(".gz") else t).decode("utf-8", "replace")
        urls += [u for u in re.findall(r"<loc>([^<]+)</loc>", t) if re.search(r"skins\.nl/[^/]+/[^/]+/\d+/$", u)]
    urls = [u for u in urls if u.split("/")[3] in marques and not EXCLUS.search(u.split("/")[4])]
    print("Fiches Skins à lire : %d (%d marques en commun)" % (len(urls), len({u.split('/')[3] for u in urls})), flush=True)
    os.makedirs(os.path.dirname(AVANCE), exist_ok=True)
    fait = json.load(open(AVANCE)) if os.path.exists(AVANCE) else {}
    for i, u in enumerate(urls):
        if u in fait:
            continue
        try:
            t = lire(u)
            info = None
            for bloc in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
                try:
                    d = json.loads(bloc.strip())
                except ValueError:
                    continue
                for x in (d if isinstance(d, list) else [d]):
                    if isinstance(x, dict) and x.get("@type") == "Product":
                        img = x.get("image")
                        img = img[0] if isinstance(img, list) else img
                        info = {"nom": x.get("name"), "gtin": re.sub(r"\D", "", str(x.get("gtin") or x.get("gtin13") or "")),
                                "image": (img or "").split("?")[0], "marque": marques[u.split("/")[3]]}
            fait[u] = info
        except Exception as e:
            fait[u] = {"erreur": str(e)[:100]}
        if i % 50 == 0:
            json.dump(fait, open(AVANCE, "w"))
            print("  %d / %d" % (i, len(urls)), flush=True)
        time.sleep(0.6)
    json.dump(fait, open(AVANCE, "w"))
    par_ean, par_nom = {}, {}
    for u, x in fait.items():
        if not x or not x.get("image") or "erreur" in x or EXCLUS.search(x.get("nom") or ""):
            continue
        if len(x["gtin"]) >= 8:
            par_ean[x["gtin"].lstrip("0")] = x["image"]
        par_nom.setdefault(pm.cle_nom(x["marque"], x["nom"]), x["image"])
    json.dump({"maj": time.strftime("%Y-%m-%d"), "source": "skins.nl", "par_ean": par_ean, "par_nom": par_nom},
              open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Photos Skins : %d EAN, %d noms" % (len(par_ean), len(par_nom)))


if __name__ == "__main__":
    main()
