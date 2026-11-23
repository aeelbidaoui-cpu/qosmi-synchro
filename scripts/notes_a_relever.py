#!/usr/bin/env python3
"""Parfums en ligne sans profil olfactif (notes, accords…) → liste à relever dans le navigateur (23/11/2026, demande
d'Amine : « quand tu rajoutes de nouveaux parfums, il faut aussi les notes »).

  python3 scripts/notes_a_relever.py rapports/theme/audit_fiches.csv > /tmp/fiQ.json

audit_fiches.csv vient de l'action theme « audit-fiches » (artefact du run). Sortie : [[handle, marque, nom, conc, genre]]
pour scripts/navigateur/fi_releve.js (window.fiQ). Les parfums déjà cherchés sans succès (config/notes_introuvables.json)
sont laissés de côté.
"""
import csv, json, os, re, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONC = [("extrait", "Extrait"), ("eau de parfum", "EDP"), ("eau de toilette", "EDT"), ("eau de cologne", "EDC"),
        ("parfum", "Parfum")]


def main(chemin):
    profils = json.load(open(os.path.join(RACINE, "config", "profils_parfums.json"), encoding="utf-8"))["parfums"]
    try:
        jamais = json.load(open(os.path.join(RACINE, "config", "notes_introuvables.json"), encoding="utf-8"))["parfums"]
    except FileNotFoundError:
        jamais = {}
    out = []
    for l in csv.DictReader(open(chemin, encoding="utf-8")):
        if not (l["type"] or "").startswith(("Parfums", "Testeurs")) or l["profil"] == "oui":
            continue
        h = l["handle"]
        if h in profils or h in jamais:
            continue
        titre, marque = l["titre"], l["marque"] or ""
        nom, _, reste = titre.partition(" — ")
        if nom.lower().startswith(marque.lower() + " "):
            nom = nom[len(marque) + 1:]
        r = reste.lower()
        conc = next((c for k, c in CONC if k in r), "")
        g = "f" if "femme" in r else "m" if "homme" in r else "u"
        out.append([h, marque, nom.strip(), conc, g])
    json.dump(out, sys.stdout, ensure_ascii=False)
    print(file=sys.stderr)
    print("parfums sans profil à relever : %d" % len(out), file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1])
