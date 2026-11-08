#!/usr/bin/env python3
"""Recadrage uniforme des photos autorisées (demande d'Amine du 07/11/2026 : « mets tout à la même taille »).

Sur les cartes du site, chaque photo arrive avec plus ou moins de blanc autour du flacon : les flacons paraissent
de tailles différentes. Ce script reprend chaque photo autorisée (fichiers config/photos_*.json), repère le flacon
(tout ce qui diffère du fond clair), puis le replace au centre d'une image 4:5 à fond blanc où il occupe toujours
la même part de la hauteur (ou de la largeur pour les flacons larges). Aucun agrandissement : on ajoute seulement du blanc.
Les photos à fond foncé ou coloré sont laissées telles quelles.

Chaque photo recadrée est envoyée dans les Fichiers Shopify (qosmi-c-<empreinte>.jpg) ;
rapports/theme/photos_cadrees.json donne {adresse d'origine: adresse Shopify} (à recopier dans config/).
Limite par passage : variable PHOTOS_MAX (600 par défaut) ; les photos déjà faites sont reprises de config/photos_cadrees.json.
"""
import concurrent.futures as cf, hashlib, io, json, os, sys, threading, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
CONFIG = os.path.join(RACINE, "config")
SOURCES = ("photos_marques.json", "photos_riklis.json", "photos_skins.json", "photos_parfumerie.json", "photos_acquadiparma.json",
           "photos_parfuma.json", "photos_ici.json", "photos_elo.json", "photos_creed.json")
AGENT = "Mozilla/5.0 (compatible; QosmiPhotos/1.0)"
PART_H, PART_L = 0.80, 0.74  # part de la hauteur / de la largeur occupée par le flacon
SEUIL_FOND, ECART = 232, 22
VERSION = "2"  # v2 (08/11/2026) : fonds gris clairs passés au blanc ; nouveau nom de fichier pour ne pas reprendre l'ancien


def toutes_les_photos():
    urls = set()
    for nom in SOURCES:
        chemin = os.path.join(CONFIG, nom)
        if os.path.exists(chemin):
            ph = json.load(open(chemin, encoding="utf-8"))
            urls |= set(ph.get("par_ean", {}).values()) | set(ph.get("par_nom", {}).values()) | set(ph.get("par_fiche", {}).values())
    return sorted(u for u in urls if u)


FOND_GRIS_MIN, FOND_ECART_MAX = 195, 24  # fond uni gris clair (ex. photos Creed) : passé au blanc avant recadrage


def blanchir(im, t0=4.0, t1=46.0):
    """Fond uni gris clair -> blanc, sans détourage destructif (08/11/2026, photos Creed).
    Alpha = écart à la couleur du fond (lissé entre t0 et t1) ; ce qui ressemble au fond glisse vers le blanc,
    le flacon (alpha 1) n'est pas touché ; le verre laisse voir le nouveau fond ; l'ombre douce reste. Aucun rééchantillonnage."""
    import numpy as np
    from PIL import Image
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    coins = np.concatenate([a[:20, :20].reshape(-1, 3), a[:20, -20:].reshape(-1, 3),
                            a[-20:, :20].reshape(-1, 3), a[-20:, -20:].reshape(-1, 3)])
    bg = np.median(coins, axis=0)
    alpha = np.clip((np.abs(a - bg).max(axis=2) - t0) / (t1 - t0), 0, 1)[..., None]
    return Image.fromarray(np.clip(a + (1 - alpha) * (255.0 - bg), 0, 255).round().astype(np.uint8))


def recadrer(donnees):
    """Renvoie le JPEG recadré, ou None si le fond n'est pas clair (photo laissée telle quelle)."""
    from PIL import Image, ImageChops
    im = Image.open(io.BytesIO(donnees))
    im.load()
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        fond = Image.new("RGBA", im.size, (255, 255, 255, 255))
        fond.alpha_composite(im)
        im = fond
    im = im.convert("RGB")
    l, h = im.size
    coins = [im.getpixel(p) for p in ((0, 0), (l - 1, 0), (0, h - 1), (l - 1, h - 1), (l // 2, 0), (l // 2, h - 1))]
    bas, haut = min(min(c) for c in coins), max(max(c) for c in coins)
    ecart = ECART
    if FOND_GRIS_MIN <= bas < SEUIL_FOND and haut - bas <= FOND_ECART_MAX:  # fond gris clair uni : passé au blanc
        im = blanchir(im)
        ecart = 40  # l'ombre portée, devenue gris très clair, ne compte pas dans le cadrage
        coins = [im.getpixel(p) for p in ((0, 0), (l - 1, 0), (0, h - 1), (l - 1, h - 1), (l // 2, 0), (l // 2, h - 1))]
    if min(min(c) for c in coins) < SEUIL_FOND:
        return None
    teinte0 = tuple(sorted(c[i] for c in coins)[len(coins) // 2] for i in range(3))
    gris = ImageChops.difference(im, Image.new("RGB", im.size, teinte0)).convert("L")
    masque = gris.point(lambda v: 255 if v > ecart else 0)
    boite = masque.getbbox()
    if not boite:
        return None
    flacon = im.crop(boite)
    fl, fh = flacon.size
    ch = max(fh / PART_H, (fl / PART_L) * 1.25)
    ch = int(round(ch))
    cl = int(round(ch * 0.8))
    teinte = tuple(sorted(c[i] for c in coins)[len(coins) // 2] for i in range(3))  # couleur du fond d'origine
    toile = Image.new("RGB", (cl, ch), teinte)
    toile.paste(flacon, ((cl - fl) // 2, (ch - fh) // 2))
    out = io.BytesIO()
    toile.save(out, "JPEG", quality=90, optimize=True)
    return out.getvalue()


def lire(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    from shopify_api import Shopify
    import photos_adp as pa
    s = Shopify()
    verrou = threading.Lock()
    chemin_conf = os.path.join(CONFIG, "photos_cadrees.json")
    faites = json.load(open(chemin_conf, encoding="utf-8"))["par_url"] if os.path.exists(chemin_conf) else {}
    a_faire = [u for u in toutes_les_photos() if u not in faites]
    if os.environ.get("SOLELUNA_EMAIL"):  # serveur : seulement les photos des fiches affichées sur le site
        import site_synchro as ss
        ss.listes_serveur()
        produits = ss.sv.preparer(exemples=False)
        sel = ss.selection()
        utiles = {v.get("photo_brute") for p in produits if ss.visible(p, sel) for v in p["variantes"]}
        a_faire = [u for u in a_faire if u in utiles]
    maxi = int(os.environ.get("PHOTOS_MAX") or 600)
    print("Photos autorisées : %d, déjà recadrées : %d, à faire : %d (ce passage : %d)"
          % (len(a_faire) + len(faites), len(faites), len(a_faire), min(maxi, len(a_faire))))
    bilan = {"recadrées": 0, "laissées (fond foncé)": 0, "illisibles": 0, "refus Shopify": 0}
    dossier = os.path.join(RACINE, "rapports", "theme", "cadre")
    os.makedirs(dossier, exist_ok=True)

    def une(u):
        try:
            jpeg = recadrer(lire(u))
        except Exception as e:
            with verrou:
                bilan["illisibles"] += 1
            return u, None, "illisible : %s" % str(e)[:80]
        if jpeg is None:
            with verrou:
                bilan["laissées (fond foncé)"] += 1
            return u, u, None
        nom = "qosmi-c%s-%s.jpg" % (VERSION, hashlib.sha1(u.encode()).hexdigest()[:16])
        chemin = os.path.join(dossier, nom)
        open(chemin, "wb").write(jpeg)
        with verrou:
            existant = pa.adresse_fichier(s, nom)
        cdn = existant or pa.envoyer(s, chemin, alt="")
        os.remove(chemin)
        with verrou:
            bilan["recadrées" if cdn else "refus Shopify"] += 1
        return u, cdn, None

    with cf.ThreadPoolExecutor(4) as ex:
        for i, (u, cdn, erreur) in enumerate(ex.map(une, a_faire[:maxi]), 1):
            if cdn:
                faites[u] = cdn
            elif erreur:
                print("  %s — %s" % (u[:100], erreur))
            if i % 50 == 0:
                print("  %d / %d" % (i, min(maxi, len(a_faire))), flush=True)
    os.makedirs(os.path.join(RACINE, "rapports", "theme"), exist_ok=True)
    json.dump({"source": "photos autorisées recadrées (scripts/photos_cadre.py)", "par_url": faites},
              open(os.path.join(RACINE, "rapports", "theme", "photos_cadrees.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    print("Bilan : %s ; reste à faire : %d" % (bilan, max(0, len(a_faire) - maxi)))


if __name__ == "__main__":
    main()
