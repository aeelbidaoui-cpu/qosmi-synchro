"""Étiquettes « Tendance » et « Best-seller » sur les fiches (23/11/2026, demande d'Amine) → métachamp qosmi.etiquette.
« Nouveau » se calcule dans le thème (snippet qk-etiquette : fiche créée il y a moins de 3 jours).
Liste : config/etiquettes.json (nom exact du parfum, coffrets exclus). Une fiche qui sort de la liste perd son étiquette.

    python3 scripts/etiquettes.py [--essai]
"""
import json, os, re, sys, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = """query($a: String) { products(first: 250, after: $a, query: "status:active") { pageInfo { hasNextPage endCursor }
  nodes { id title vendor productType etiquette: metafield(namespace: "qosmi", key: "etiquette") { id value } } } }"""
M_SET = "mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) { userErrors { message } } }"
M_DEL = "mutation($m: [MetafieldIdentifierInput!]!) { metafieldsDelete(metafields: $m) { userErrors { message } } }"


def norm(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s.replace("´", "").replace("'", "").replace("’", "")).strip()


def nom(titre, marque):
    t = titre.split(" — ")[0]
    return t[len(marque):].strip() if marque and t.lower().startswith(marque.lower()) else t


def cible(p, regles):
    if (p.get("productType") or "") == "Coffrets" or "coffret" in (p.get("title") or "").lower():
        return None
    n, m = norm(nom(p["title"], p["vendor"])), norm(p["vendor"])
    for etiquette in ("tendance", "best-seller"):
        for marque, parfum in regles[etiquette]:
            if norm(parfum) == n and (m.startswith(norm(marque)[:6]) or norm(marque).startswith(m[:6])):
                return etiquette
    return None


def main(essai=False):
    from shopify_api import Shopify
    s = Shopify()
    regles = json.load(open(os.path.join(RACINE, "config", "etiquettes.json"), encoding="utf-8"))
    poser, retirer, compte, a = [], [], {}, None
    while True:
        d = s.gql(Q, {"a": a})["products"]
        for p in d["nodes"]:
            e = cible(p, regles)
            actuel = (p.get("etiquette") or {}).get("value")
            if e:
                compte[e] = compte.get(e, 0) + 1
                if e != actuel:
                    poser.append({"ownerId": p["id"], "namespace": "qosmi", "key": "etiquette", "type": "single_line_text_field", "value": e})
                    print("  %s : %s" % (e, p["title"]))
            elif actuel:
                retirer.append({"ownerId": p["id"], "namespace": "qosmi", "key": "etiquette"})
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]
    if not essai:
        for i in range(0, len(poser), 25):
            s.gql(M_SET, {"m": poser[i:i + 25]})
        for i in range(0, len(retirer), 25):
            s.gql(M_DEL, {"m": retirer[i:i + 25]})
    print("Étiquettes : %s ; posées %d, retirées %d%s" % (compte, len(poser), len(retirer), " (essai, rien écrit)" if essai else ""))


if __name__ == "__main__":
    main("--essai" in sys.argv)
