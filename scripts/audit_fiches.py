"""Relevé des fiches en ligne (23/11/2026) : date d'arrivée, profil olfactif présent ou non, taille de la photo principale.
→ rapports/theme/audit_fiches.csv (sert aux photos 1200 px, aux étiquettes « Nouveau » et aux fiches sans notes)."""
import csv, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = """query($a: String) { products(first: 100, after: $a, query: "status:active") { pageInfo { hasNextPage endCursor }
  nodes { handle title vendor productType createdAt tags totalInventory
    featuredMedia { ... on MediaImage { image { width height url } } } } } }"""


def main():
    from shopify_api import Shopify
    s = Shopify()
    profils = json.load(open(os.path.join(RACINE, "config", "profils_parfums.json"), encoding="utf-8"))["parfums"]
    desc = json.load(open(os.path.join(RACINE, "config", "descriptions_parfums.json"), encoding="utf-8")).get("parfums") or {}
    lignes, a = [], None
    while True:
        d = s.gql(Q, {"a": a})["products"]
        for p in d["nodes"]:
            im = ((p.get("featuredMedia") or {}).get("image") or {})
            lignes.append({"handle": p["handle"], "titre": p["title"], "marque": p["vendor"], "type": p["productType"],
                           "cree": p["createdAt"][:10], "stock": p.get("totalInventory"),
                           "profil": "oui" if p["handle"] in profils or p["handle"] in desc else "non",
                           "largeur": im.get("width") or 0, "hauteur": im.get("height") or 0, "photo": (im.get("url") or "").split("?")[0]})
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]
    os.makedirs(os.path.join(RACINE, "rapports", "theme"), exist_ok=True)
    with open(os.path.join(RACINE, "rapports", "theme", "audit_fiches.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    parf = [l for l in lignes if (l["type"] or "").startswith(("Parfums", "Testeurs", "Coffrets"))]
    print("Fiches en ligne : %d, dont parfums/testeurs/coffrets : %d" % (len(lignes), len(parf)))
    print("  sans profil olfactif : %d" % sum(1 for l in parf if l["profil"] == "non"))
    print("  photo principale < 1200 px : %d (sans photo : %d)" % (
        sum(1 for l in lignes if 0 < min(l["largeur"], l["hauteur"]) < 1200), sum(1 for l in lignes if not l["largeur"])))


if __name__ == "__main__":
    main()
