#!/usr/bin/env python3
"""ICI Paris XL : envoi des photos (accord d'ICI Paris XL du 07/11/2026) dans les Fichiers Shopify.

media.iciparisxl.be refuse que Shopify vienne chercher les photos lui-même. Les photos ont été téléchargées
dans le navigateur d'Amine le 07/11/2026 et sont dans assets/photos_ici/, nommées qosmi-ici-<EAN>.jpg.
Ce script les envoie dans les Fichiers Shopify (un fichier déjà présent est repris tel quel)
et écrit rapports/theme/photos_ici.json : {"par_ean": {EAN: adresse Shopify}}, à recopier dans config/.
"""
import json, os, re, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
DOSSIER = os.path.join(RACINE, "assets", "photos_ici")


def main():
    from shopify_api import Shopify
    import photos_adp as pa
    s = Shopify()
    par_ean, echecs = {}, []
    for nom in sorted(os.listdir(DOSSIER)):
        m = re.fullmatch(r"qosmi-ici-(\d{8,14})\.jpg", nom)
        if not m:
            continue
        u = pa.adresse_fichier(s, nom) or pa.envoyer(s, os.path.join(DOSSIER, nom), alt="")
        print("  %s → %s" % (nom, u or "échec"))
        if u:
            par_ean[m.group(1)] = u
        else:
            echecs.append(nom)
    os.makedirs(os.path.join(RACINE, "rapports", "theme"), exist_ok=True)
    json.dump({"source": "ICI Paris XL (accord du 07/11/2026), photos envoyées dans les Fichiers Shopify",
               "par_ean": par_ean}, open(os.path.join(RACINE, "rapports", "theme", "photos_ici.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    print("Photos ICI Paris XL dans les Fichiers Shopify : %d (échecs : %d)" % (len(par_ean), len(echecs)))


if __name__ == "__main__":
    main()
