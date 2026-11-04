#!/usr/bin/env python3
"""Qosmi : thème de la boutique (Horizon).

  python3 scripts/site_theme.py --exporter   → copie les fichiers de réglage du thème publié dans rapports/theme/
                                              (lecture seule, rien n'est modifié)
"""
import json, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import site_soleluna as sl  # noqa: E402

Q_THEMES = "{ themes(first: 20) { nodes { id name role themeStoreId processing updatedAt } } }"
Q_FICHIERS = """query($id: ID!, $apres: String) { theme(id: $id) { files(first: 250, after: $apres) {
  nodes { filename size } pageInfo { hasNextPage endCursor } } } }"""
Q_CONTENU = """query($id: ID!, $noms: [String!]) { theme(id: $id) { files(filenames: $noms, first: 50) {
  nodes { filename body { ... on OnlineStoreThemeFileBodyText { content } } } } } }"""


def exporter():
    from shopify_api import Shopify
    s = Shopify()
    themes = s.gql(Q_THEMES)["themes"]["nodes"]
    dossier = os.path.join(sl.RAPPORTS, "theme")
    os.makedirs(dossier, exist_ok=True)
    json.dump(themes, open(os.path.join(dossier, "_themes.json"), "w"), indent=1, ensure_ascii=False)
    main = next(t for t in themes if t["role"] == "MAIN")
    print("Thème publié :", main["name"], main["id"])
    noms, apres = [], None
    while True:
        d = s.gql(Q_FICHIERS, {"id": main["id"], "apres": apres})["theme"]["files"]
        noms += [f["filename"] for f in d["nodes"]]
        if not d["pageInfo"]["hasNextPage"]:
            break
        apres = d["pageInfo"]["endCursor"]
    open(os.path.join(dossier, "_fichiers.txt"), "w").write("\n".join(noms) + "\n")
    voulus = [n for n in noms if n.startswith(("config/", "templates/")) or
              (n.startswith("sections/") and n.endswith(".json")) or n in ("layout/theme.liquid", "locales/fr.json",
                                                                         "locales/nl.json", "locales/en.default.json")]
    for i in range(0, len(voulus), 40):
        d = s.gql(Q_CONTENU, {"id": main["id"], "noms": voulus[i:i + 40]})["theme"]["files"]["nodes"]
        for f in d:
            c = (f.get("body") or {}).get("content")
            if c is None:
                continue
            chemin = os.path.join(dossier, f["filename"])
            os.makedirs(os.path.dirname(chemin), exist_ok=True)
            open(chemin, "w", encoding="utf-8").write(c)
    print("Fichiers exportés : %d sur %d" % (len(voulus), len(noms)))


if __name__ == "__main__":
    if "--exporter" in sys.argv:
        exporter()
    else:
        print(__doc__)
