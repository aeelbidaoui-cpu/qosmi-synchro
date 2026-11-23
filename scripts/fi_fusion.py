#!/usr/bin/env python3
"""Ajoute les profils d'un relevé (Fragrance Index ou Fragrantica) sans toucher aux profils existants (23/11/2026).

  python3 scripts/fi_fusion.py <relevé.json> [<relevé2.json> …]

Chaque relevé est une liste au format qosmi-fi-*.json ({"h": [handle], "ok": 2, "d": {...}}). Le calcul est fait par
scripts/fi_construire.py dans une copie temporaire du dépôt ; seules les fiches absentes de config/profils_parfums.json
et config/notes_fi.json y sont ajoutées. Les fiches du relevé restées sans résultat (ok = 0) vont dans
config/notes_introuvables.json, pour ne pas les rechercher chaque semaine.
"""
import datetime, json, os, shutil, subprocess, sys, tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(fichiers):
    tmp = tempfile.mkdtemp()
    try:
        shutil.copytree(os.path.join(RACINE, "scripts"), os.path.join(tmp, "scripts"))
        shutil.copytree(os.path.join(RACINE, "config"), os.path.join(tmp, "config"))
        rel = os.path.join(tmp, "releves")
        os.makedirs(rel)
        vides = []
        for i, f in enumerate(fichiers):
            R = json.load(open(f, encoding="utf-8"))
            vides += [r["h"][0] for r in R if not r.get("d") or r.get("ok") not in (1, 2)]
            json.dump([r for r in R if r.get("d")], open(os.path.join(rel, "qosmi-fi-%04d.json" % i), "w", encoding="utf-8"),
                      ensure_ascii=False)
        subprocess.run([sys.executable, "-I", os.path.join(tmp, "scripts", "fi_construire.py"), rel, "-"], check=True)
        for nom in ("profils_parfums.json", "notes_fi.json"):
            vrai = os.path.join(RACINE, "config", nom)
            ancien = json.load(open(vrai, encoding="utf-8"))
            neuf = json.load(open(os.path.join(tmp, "config", nom), encoding="utf-8"))
            ajout = {k: v for k, v in neuf["parfums"].items() if k not in ancien["parfums"]}
            ancien["parfums"].update(ajout)
            json.dump(ancien, open(vrai, "w", encoding="utf-8"), ensure_ascii=False)
            print("%s : %d fiches ajoutées" % (nom, len(ajout)))
        prof = json.load(open(os.path.join(RACINE, "config", "profils_parfums.json"), encoding="utf-8"))["parfums"]
        chemin = os.path.join(RACINE, "config", "notes_introuvables.json")
        try:
            jm = json.load(open(chemin, encoding="utf-8"))
        except FileNotFoundError:
            jm = {"_note": "Parfums cherchés sans succès (Fragrance Index, Fragrantica) : pas recherchés à nouveau chaque semaine.",
                  "parfums": {}}
        jour = datetime.date.today().isoformat()
        n = 0
        for h in vides:
            if h not in prof and h not in jm["parfums"]:
                jm["parfums"][h] = jour
                n += 1
        json.dump(jm, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("introuvables ajoutés : %d" % n)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1:])
