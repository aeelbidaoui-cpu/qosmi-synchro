#!/usr/bin/env python3
"""Cherche les photos Notino (accord confirmé par Amine le 08/11/2026) par code-barres, pour :
  - les soins (rayon skincare demandé par Amine le 23/11/2026 : visage, corps, solaires) ;
  - les parfums dont la photo est trop petite (liste config/photos_a_ameliorer.json, handles).

  python3 scripts/photos_notino_sonde.py      → rapports/theme/notino_trouvees.json {ean: [url, largeur, hauteur]}

Adresse Notino : https://cdn.notinoimg.com/detail_main_hq/<marque>/<EAN>_01-o.jpg (ou _01.jpg). Lecture seule, une
image à la fois par fil (6 fils), comme un navigateur. Le fichier sort en artefact ; la fusion dans
config/photos_notino.json se fait ensuite (seulement les photos d'au moins 700 px de haut).
"""
import concurrent.futures as cf
import io
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
RUBRIQUES = {"Soins du visage", "Soins du corps", "Solaires et autobronzants"}
AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"


def slug(m):
    m = unicodedata.normalize("NFKD", m).encode("ascii", "ignore").decode().lower()
    m = m.replace("&", "-").replace("´", "").replace("'", "").replace("’", "").replace(".", "")
    return re.sub(r"[^a-z0-9]+", "-", m).strip("-")


def slugs(m):
    s = slug(m)
    out = [s]
    for v in (s.replace("-", "_"), s.replace("-", ""), re.sub(r"-(paris|parfums?|cosmetics|beauty|laboratoires?)$", "", s)):
        if v and v not in out:
            out.append(v)
    return out


def taille(url):
    from PIL import Image
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": AGENT, "Referer": "https://www.notino.be/"}), timeout=30)
        if r.status != 200 or "image" not in (r.headers.get("Content-Type") or ""):
            return None
        im = Image.open(io.BytesIO(r.read()))
        return im.size
    except Exception:
        return None


def chercher(ean, marque):
    for s in slugs(marque):
        for suf in ("_01-o.jpg", "_01.jpg"):
            u = "https://cdn.notinoimg.com/detail_main_hq/%s/%s%s" % (s, ean, suf)
            t = taille(u)
            time.sleep(0.3)
            if t:
                return ean, u, t
    return ean, None, None


def main():
    import site_synchro as ss
    import site_variantes as sv
    if os.environ.get("SOLELUNA_EMAIL"):
        ss.listes_serveur()
    produits = sv.preparer(exemples=False)
    try:
        a_ameliorer = set(json.load(open(os.path.join(RACINE, "config", "photos_a_ameliorer.json"), encoding="utf-8"))["handles"])
    except FileNotFoundError:
        a_ameliorer = set()
    deja = dict(json.load(open(os.path.join(RACINE, "config", "photos_notino.json"), encoding="utf-8"))["par_ean"])
    try:  # 23/11/2026 : déjà trouvées au premier passage
        deja.update(json.load(open(os.path.join(RACINE, "config", "photos_notino_hd.json"), encoding="utf-8"))["par_ean"])
    except FileNotFoundError:
        pass
    cibles = {}
    for p in produits:
        if p.get("type_fr") in RUBRIQUES or p["handle"] in a_ameliorer:
            for v in p["variantes"]:
                e = str(v.get("ean") or "").strip()
                if e and e.lstrip("0") not in deja and e not in deja:
                    cibles[e] = p["marque"]
    print("codes-barres à chercher chez Notino : %d" % len(cibles))
    trouve = {}
    with cf.ThreadPoolExecutor(6) as ex:
        for i, (ean, u, t) in enumerate(ex.map(lambda kv: chercher(*kv), cibles.items())):
            if u:
                trouve[ean] = [u, t[0], t[1]]
            if i % 200 == 0:
                print("  %d / %d (trouvées : %d)" % (i, len(cibles), len(trouve)), flush=True)
    os.makedirs(os.path.join(RACINE, "rapports", "theme"), exist_ok=True)
    json.dump(trouve, open(os.path.join(RACINE, "rapports", "theme", "notino_trouvees.json"), "w"), ensure_ascii=False)
    hautes = sum(1 for _, w, h in trouve.values() if h >= 700)
    print("OK photos Notino trouvées : %d (dont %d d'au moins 700 px de haut)" % (len(trouve), hautes))


def lot():
    """Photos Notino déjà trouvées pour les fiches de photos_a_ameliorer.json → rapports/theme/notino_par_fiche.json {handle: url}."""
    import site_synchro as ss
    import site_variantes as sv
    if os.environ.get("SOLELUNA_EMAIL"):
        ss.listes_serveur()
    produits = sv.preparer(exemples=False)
    cibles = set(json.load(open(os.path.join(RACINE, "config", "photos_a_ameliorer.json"), encoding="utf-8"))["handles"])
    hd = json.load(open(os.path.join(RACINE, "config", "photos_notino_hd.json"), encoding="utf-8"))["par_ean"]
    out = {}
    for p in produits:
        if p["handle"] in cibles:
            for v in p["variantes"]:
                u = hd.get(str(v.get("ean") or "").lstrip("0"))
                if u and "testeur" not in (v.get("format_fr") or ""):
                    out[p["handle"]] = u
                    break
    os.makedirs(os.path.join(RACINE, "rapports", "theme"), exist_ok=True)
    json.dump(out, open(os.path.join(RACINE, "rapports", "theme", "notino_par_fiche.json"), "w"), ensure_ascii=False)
    print("OK fiches à photo trop petite avec une photo Notino : %d / %d" % (len(out), len(cibles)))


if __name__ == "__main__":
    lot() if "--lot" in sys.argv else main()
