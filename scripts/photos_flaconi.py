#!/usr/bin/env python3
"""Photos Flaconi en haute définition, par EAN (27/11/2026). Amine a l'autorisation de Flaconi d'utiliser leurs images ;
il a demandé : « vas-y alors, remplace » (les photos de faible qualité du site).

Pour chaque format des fiches affichées sur le site, cherche la photo du flacon chez Flaconi :
  https://cdn.flaconi.net/media/catalog/product/<1er chiffre>/<2e chiffre>/<EAN>_c_live.jpg
et écrit rapports/theme/photos_flaconi.json ({"par_ean": {EAN sans zéros de tête: URL}}), à recopier dans config/.
Ensuite : photos-cadre (recadrage et envoi dans Shopify) puis photos-marques (pose sur les fiches).
Lecture seule sur Shopify."""
import concurrent.futures as cf, json, os, sys, threading, time, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
AGENT = "Mozilla/5.0 (compatible; QosmiPhotos/1.0)"


SUFFIXES = ("_c_live", "-1_c_live", "-1_live", "_live")  # « _c » : flacon détouré ; sinon 1re vue produit


def url(e, suf="_c_live"):
    return "https://cdn.flaconi.net/media/catalog/product/%s/%s/%s%s.jpg" % (e[0], e[1], e, suf)


def existe(u):
    for essai in range(3):
        try:
            req = urllib.request.Request(u + "?w=200&q=50", headers={"User-Agent": AGENT}, method="HEAD")
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status == 200 and "image" in (r.headers.get("Content-Type") or "")
        except urllib.error.HTTPError as e:
            if e.code in (404, 410, 403):
                return False
            time.sleep(2 * (essai + 1))
        except Exception:
            time.sleep(2 * (essai + 1))
    return False


def main():
    import site_synchro as ss
    if os.environ.get("SOLELUNA_EMAIL"):
        ss.listes_serveur()
    produits = ss.sv.preparer(exemples=False)
    sel = ss.selection()
    eans = sorted({v["ean"] for p in produits if ss.visible(p, sel) for v in p["variantes"] if v.get("ean")})
    print("Formats affichés sur le site : %d EAN" % len(eans), flush=True)
    trouves, verrou, n = {}, threading.Lock(), [0]

    def un(e):
        for c in dict.fromkeys([e, e.lstrip("0"), e.zfill(13)]):
            for suf in SUFFIXES:
                if len(c) >= 8 and existe(url(c, suf)):
                    return e, url(c, suf) + "?w=1600&q=90"
        return e, None

    with cf.ThreadPoolExecutor(8) as ex:
        for e, u in ex.map(un, eans):
            with verrou:
                n[0] += 1
                if u:
                    trouves[e.lstrip("0")] = u
                if n[0] % 500 == 0:
                    print("  %d / %d, trouvés %d" % (n[0], len(eans), len(trouves)), flush=True)
    os.makedirs(os.path.join(RACINE, "rapports", "theme"), exist_ok=True)
    json.dump({"source": "Flaconi (autorisation d'Amine du 27/11/2026) : photo du flacon par EAN, 1600 px",
               "maj": time.strftime("%Y-%m-%d"), "par_ean": trouves},
              open(os.path.join(RACINE, "rapports", "theme", "photos_flaconi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("Photos Flaconi trouvées : %d sur %d EAN" % (len(trouves), len(eans)))


if __name__ == "__main__":
    main()
