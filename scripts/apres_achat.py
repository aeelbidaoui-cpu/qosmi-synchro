#!/usr/bin/env python3
"""E-mails après l'achat (13/11/2026, demande d'Amine). Lancé après chaque mise à jour du site.

Shopify Flow « Qosmi · Après achat » (commande expédiée) : 3 jours plus tard, étiquette achat:<fiche> + e-mail « merci et
conseils » (config/mails/merci_*.liquid) ; 57 jours plus tard encore, étiquette suivi-demande.
Ce script, pour chaque client suivi-demande : 3 parfums en stock aux notes proches de son dernier achat → étiquettes
suggere:<fiche> + suivi-pret (anciennes suggere: retirées). Flow (étiquette suivi-pret ajoutée) envoie l'e-mail
« 3 parfums pour toi » (config/mails/suivi_*.liquid) puis retire suivi-pret.

  python3 scripts/apres_achat.py           # traite les clients
  python3 scripts/apres_achat.py --essai   # montre ce qui serait fait
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ESSAI = "--essai" in sys.argv


def main():
    from shopify_api import Shopify
    import alertes_stock
    s = Shopify()
    clients, apres = [], None
    while True:
        r = s.gql("""query($a: String) { customers(first: 100, after: $a, query: "tag:suivi-demande") {
            nodes { id tags } pageInfo { hasNextPage endCursor } } }""", {"a": apres})["customers"]
        clients += r["nodes"]
        if not r["pageInfo"]["hasNextPage"]:
            break
        apres = r["pageInfo"]["endCursor"]
    print("Après achat : %d client(s) à relancer" % len(clients), flush=True)
    cache = {}

    def disponible(h):
        if h not in cache:
            p = s.gql("query($h: String!) { productByIdentifier(identifier: {handle: $h}) { status "
                      "variants(first: 10) { nodes { availableForSale } } } }", {"h": h})["productByIdentifier"]
            cache[h] = bool(p and p["status"] == "ACTIVE" and any(v["availableForSale"] for v in p["variants"]["nodes"]))
        return cache[h]

    for c in clients:
        cid = c["id"].rsplit("/", 1)[1]
        achats = [t.split(":", 1)[1] for t in c["tags"] if t.startswith("achat:")]
        choix = []
        for h in reversed(achats):  # dernier achat d'abord, puis les précédents si besoin
            for k in alertes_stock.proches(h, disponible, 3):
                if k not in choix and k not in achats:
                    choix.append(k)
            if len(choix) >= 3:
                break
        choix = choix[:3]
        print("  client %s : achats %s → %s" % (cid, achats, choix or "aucune suggestion"), flush=True)
        if ESSAI:
            continue
        retirer = ["suivi-demande"] + [t for t in c["tags"] if t.startswith("suggere:")]
        s.gql("mutation($id: ID!, $t: [String!]!) { tagsRemove(id: $id, tags: $t) { userErrors { message } } }", {"id": c["id"], "t": retirer})
        if choix:
            s.gql("mutation($id: ID!, $t: [String!]!) { tagsAdd(id: $id, tags: $t) { userErrors { message } } }",
                  {"id": c["id"], "t": ["suggere:" + k for k in choix]})
            s.gql("mutation($id: ID!, $t: [String!]!) { tagsAdd(id: $id, tags: $t) { userErrors { message } } }", {"id": c["id"], "t": ["suivi-pret"]})


if __name__ == "__main__":
    main()
