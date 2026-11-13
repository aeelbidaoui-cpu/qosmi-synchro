#!/usr/bin/env python3
"""Alerte « baisse de prix » sur les favoris (13/11/2026, demande d'Amine). Lancé après chaque mise à jour du site.

Le formulaire de la page Favoris (theme_rk/sections/qk-favoris.liquid) crée un contact Shopify avec les étiquettes
  prix-alerte · langue:fr|nl · prix:<id du format>:<prix en centimes au moment de l'inscription>
Ce script, pour chaque format suivi, compare le prix actuel : s'il a baissé d'au moins 5 % et d'au moins 1 €, et que le
parfum est en vente, il ajoute prix-baisse:<fiche>:<ancien>:<nouveau> + prix-pret et note le nouveau prix de référence.
Shopify Flow (étiquette prix-pret ajoutée) envoie l'e-mail (config/mails/prix_baisse_*.liquid) puis retire prix-pret ;
les étiquettes prix-baisse sont retirées au passage suivant.

  python3 scripts/alertes_prix.py           # traite les alertes
  python3 scripts/alertes_prix.py --essai   # montre ce qui serait fait, sans rien changer
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ESSAI = "--essai" in sys.argv
BAISSE_MIN_TAUX, BAISSE_MIN_CTS = 0.05, 100


def log(*a):
    print(*a, flush=True)


def main():
    from shopify_api import Shopify
    s = Shopify()
    clients, apres = [], None
    while True:
        r = s.gql("""query($a: String) { customers(first: 100, after: $a, query: "tag:prix-alerte") {
            nodes { id tags } pageInfo { hasNextPage endCursor } } }""", {"a": apres})["customers"]
        clients += r["nodes"]
        if not r["pageInfo"]["hasNextPage"]:
            break
        apres = r["pageInfo"]["endCursor"]
    log("Alertes prix : %d clients inscrits" % len(clients))
    suivis = {}
    for c in clients:
        for t in c["tags"]:
            x = t.split(":")
            if x[0] == "prix" and len(x) == 3 and x[1].isdigit() and x[2].isdigit():
                suivis[x[1]] = None
    ids = list(suivis)
    for i in range(0, len(ids), 100):
        r = s.gql("""query($ids: [ID!]!) { nodes(ids: $ids) { ... on ProductVariant { id availableForSale price product { handle status } } } }""",
                  {"ids": ["gid://shopify/ProductVariant/%s" % x for x in ids[i:i + 100]]})
        for n in r["nodes"]:
            if n:
                suivis[n["id"].rsplit("/", 1)[1]] = n
    envoyes = 0
    for c in clients:
        cid = c["id"].rsplit("/", 1)[1]
        if "prix-pret" in c["tags"]:
            log("  client %s : e-mail précédent pas encore parti, on attend" % cid)
            continue
        retirer = [t for t in c["tags"] if t.startswith("prix-baisse:")]
        refs = {}
        for t in c["tags"]:
            x = t.split(":")
            if x[0] == "prix" and len(x) == 3 and x[1].isdigit() and x[2].isdigit():
                refs.setdefault(x[1], []).append(int(x[2]))
        ajout, baisses = [], []
        for vid, prix in refs.items():
            ref = min(prix)
            if len(prix) > 1:  # inscrit plusieurs fois : on garde le prix le plus bas
                retirer += ["prix:%s:%d" % (vid, p) for p in prix if p != ref]
            v = suivis.get(vid)
            if not v:
                continue
            maintenant = round(float(v["price"]) * 100)
            if v["availableForSale"] and v["product"]["status"] == "ACTIVE" and maintenant <= ref - max(BAISSE_MIN_CTS, ref * BAISSE_MIN_TAUX):
                baisses.append("prix-baisse:%s:%d:%d" % (v["product"]["handle"], ref, maintenant))
                retirer.append("prix:%s:%d" % (vid, ref))
                ajout.append("prix:%s:%d" % (vid, maintenant))
        if baisses:
            log("  client %s : %s" % (cid, ", ".join(baisses)))
        if ESSAI:
            continue
        if retirer:
            s.gql("mutation($id: ID!, $t: [String!]!) { tagsRemove(id: $id, tags: $t) { userErrors { message } } }", {"id": c["id"], "t": retirer})
        if baisses:
            s.gql("mutation($id: ID!, $t: [String!]!) { tagsAdd(id: $id, tags: $t) { userErrors { message } } }", {"id": c["id"], "t": ajout + baisses})
            s.gql("mutation($id: ID!, $t: [String!]!) { tagsAdd(id: $id, tags: $t) { userErrors { message } } }", {"id": c["id"], "t": ["prix-pret"]})
            envoyes += 1
    log("Alertes prix : %d e-mail(s) déclenché(s)%s" % (envoyes, " (essai, rien changé)" if ESSAI else ""))


if __name__ == "__main__":
    main()
