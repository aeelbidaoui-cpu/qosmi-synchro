#!/usr/bin/env python3
"""Envoie dans les Fichiers Shopify les photos d'un dossier assets/photos_<nom>/ (fichiers qosmi-<nom>-<EAN>.jpg|png),
téléchargées dans le navigateur d'Amine quand le site de la marque refuse les téléchargements automatiques.
Écrit rapports/theme/photos_<nom>.json : {"par_ean": {EAN: adresse Shopify}}, à recopier dans config/.

  python3 scripts/photos_dossier.py jm      (Jo Malone, accord de la marque du 08/11/2026)
"""
import json, os, re, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)


def main(nom):
    from shopify_api import Shopify
    import photos_adp as pa
    s = Shopify()
    dossier = os.path.join(RACINE, "assets", "photos_%s" % nom)
    par_ean, echecs = {}, []
    for f in sorted(os.listdir(dossier)):
        m = re.fullmatch(r"qosmi-%s-(\d{8,14})\.(jpg|png)" % re.escape(nom), f)
        if not m:
            continue
        u = pa.adresse_fichier(s, f) or pa.envoyer(s, os.path.join(dossier, f), alt="")
        print("  %s → %s" % (f, u or "échec"))
        if u:
            par_ean[m.group(1).lstrip("0")] = u
        else:
            echecs.append(f)
    os.makedirs(os.path.join(RACINE, "rapports", "theme"), exist_ok=True)
    json.dump({"par_ean": par_ean}, open(os.path.join(RACINE, "rapports", "theme", "photos_%s.json" % nom), "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    print("Photos %s dans les Fichiers Shopify : %d (échecs : %d)" % (nom, len(par_ean), len(echecs)))


if __name__ == "__main__":
    main(sys.argv[1])
