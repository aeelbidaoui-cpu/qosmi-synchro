#!/usr/bin/env python3
"""Liste de commande « Bons plans » (15/11/2026, point 8 validé par Amine).

Le grossiste des Bons plans est commandé une fois par semaine, le lundi matin (décision d'Amine du 20/11/2026 ; avant :
lundi et jeudi) ; clôture le dimanche à minuit. Lancé le lundi matin (action « commande-bons-plans » du workflow theme) : relève les commandes payées
passées avant minuit et pas encore expédiées qui contiennent un format Bon plan (références QS-B / QS-C / QS-D),
regroupe les quantités par parfum et écrit la liste dans une page NON PUBLIÉE de l'admin Shopify
(Boutique en ligne → Pages → « Liste interne · commande Bons plans »).

Règle d'Amine : minimum 300 € chez le grossiste. En dessous, on attend une fois ; si une commande a déjà attendu un
passage, Amine complète lui-même la commande.

Le dépôt est public : le journal ne montre que des nombres (parfums, pièces) et la décision, jamais un prix,
un nom de fournisseur ou un nom de client. Le détail reste dans l'admin Shopify.
"""
import csv, datetime, html, json, os, re, sys
from collections import defaultdict
from zoneinfo import ZoneInfo

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

MINIMUM = 300.0
PREFIXES = ("QS-B", "QS-C", "QS-D")
HANDLE = "liste-interne-commande-bons-plans"
BXL = ZoneInfo("Europe/Brussels")

Q_COMMANDES = """query($q: String!, $apres: String) { orders(first: 100, after: $apres, query: $q, sortKey: CREATED_AT) {
  pageInfo { hasNextPage endCursor }
  nodes { id name createdAt cancelledAt displayFinancialStatus
    lineItems(first: 100) { nodes { sku name variantTitle unfulfilledQuantity } } } } }"""


def clotures(maintenant):
    """(dernière clôture, clôture précédente) : minuit à la fin du dimanche, heure de Bruxelles (20/11/2026)."""
    jour = maintenant.replace(hour=0, minute=0, second=0, microsecond=0)
    res = []
    while len(res) < 2:
        if jour.weekday() == 0 and jour <= maintenant:  # lundi 00:00 = fin du dimanche (1 commande par semaine)
            res.append(jour)
        jour -= datetime.timedelta(days=1)
    return res[0], res[1]


def prix_grossiste():
    import site_variantes as sv
    if not os.path.exists(sv.TRISTA):
        return {}
    with open(sv.TRISTA, encoding="utf-8-sig", newline="") as f:
        out = {}
        for l in csv.DictReader(f, delimiter=";"):
            ean = re.sub(r"\D", "", l.get("ean") or "").lstrip("0")
            try:
                out[ean] = (float((l.get("price") or "0").replace(",", ".")), int(float(l.get("stock") or 0)))
            except ValueError:
                pass
        return out


def main():
    from shopify_api import Shopify
    import site_synchro
    site_synchro.liste_bons_plans()
    prix = prix_grossiste()
    s = Shopify()
    maintenant = datetime.datetime.now(BXL)
    cloture, precedente = clotures(maintenant)
    q = "status:open created_at:<'%s'" % cloture.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lignes = defaultdict(lambda: {"qte": 0, "commandes": [], "nom": ""})
    plus_ancienne, apres = None, None
    while True:
        d = s.gql(Q_COMMANDES, {"q": q, "apres": apres})["orders"]
        for o in d["nodes"]:
            if o["cancelledAt"] or o["displayFinancialStatus"] not in ("PAID", "AUTHORIZED", "PARTIALLY_REFUNDED"):
                continue
            for li in o["lineItems"]["nodes"]:
                sku = li.get("sku") or ""
                if not sku.startswith(PREFIXES) or int(li.get("unfulfilledQuantity") or 0) <= 0:
                    continue
                ean = sku[4:].lstrip("0")
                x = lignes[ean]
                x["qte"] += int(li["unfulfilledQuantity"])
                x["commandes"].append(o["name"])
                x["nom"] = li["name"]
                cree = datetime.datetime.fromisoformat(o["createdAt"].replace("Z", "+00:00"))
                plus_ancienne = min(plus_ancienne or cree, cree)
        if not d["pageInfo"]["hasNextPage"]:
            break
        apres = d["pageInfo"]["endCursor"]

    total, manque_stock, rangs = 0.0, 0, []
    for ean, x in sorted(lignes.items(), key=lambda kv: kv[1]["nom"]):
        p, st = prix.get(ean, (None, None))
        sous_total = p * x["qte"] if p is not None else None
        total += sous_total or 0
        alerte = ""
        if st is not None and st < x["qte"]:
            manque_stock += 1
            alerte = " ⚠ stock grossiste : %d" % st
        rangs.append("<tr><td>%s%s</td><td>%s</td><td style='text-align:center'>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            html.escape(x["nom"]), alerte, ean, x["qte"],
            "%.2f €" % p if p is not None else "?", "%.2f €" % sous_total if sous_total is not None else "?",
            html.escape(", ".join(sorted(set(x["commandes"]))))))
    pieces = sum(x["qte"] for x in lignes.values())
    a_attendu = plus_ancienne is not None and plus_ancienne < precedente.astimezone(datetime.timezone.utc)
    if not lignes:
        decision, texte = "rien", "Aucune commande Bons plans à passer pour cette clôture."
    elif total >= MINIMUM:
        decision, texte = "commander", "Minimum atteint (%.2f € pour %.0f €) : commande à passer aujourd'hui." % (total, MINIMUM)
    elif a_attendu:
        decision, texte = "completer", ("Minimum pas atteint (%.2f €, il manque %.2f €) et une commande a déjà attendu un passage : "
                                        "complète la commande jusqu'à %.0f € et commande aujourd'hui." % (total, MINIMUM - total, MINIMUM))
    else:
        decision, texte = "attendre", ("Minimum pas atteint (%.2f €, il manque %.2f €) : on attend la prochaine clôture."
                                       % (total, MINIMUM - total))
    corps = ("<p><strong>Liste interne — ne pas publier.</strong> Mise à jour le %s (commandes passées avant le %s).</p>"
             "<p>%s</p>" % (maintenant.strftime("%d/%m/%Y à %H:%M"), cloture.strftime("%d/%m/%Y à minuit"), html.escape(texte)))
    if rangs:
        corps += ("<table><thead><tr><th>Parfum</th><th>EAN</th><th>Qté</th><th>Prix grossiste HT</th><th>Total</th>"
                  "<th>Commandes</th></tr></thead><tbody>%s</tbody></table><p>Total : <strong>%.2f €</strong> HT · %d pièce(s)</p>"
                  % ("".join(rangs), total, pieces))
    champs = {"title": "Liste interne · commande Bons plans", "handle": HANDLE, "body": corps, "isPublished": False}
    d = s.gql('query($q: String!) { pages(first: 1, query: $q) { nodes { id } } }', {"q": "handle:%s" % HANDLE})["pages"]["nodes"]
    if d:
        r = s.gql("mutation($id: ID!, $p: PageUpdateInput!) { pageUpdate(id: $id, page: $p) { page { id } userErrors { field message } } }",
                  {"id": d[0]["id"], "p": champs})["pageUpdate"]
    else:
        r = s.gql("mutation($p: PageCreateInput!) { pageCreate(page: $p) { page { id } userErrors { field message } } }",
                  {"p": champs})["pageCreate"]
    if r["userErrors"]:
        sys.exit("Page refusée : %s" % json.dumps(r["userErrors"], ensure_ascii=False))
    pid = r["page"]["id"].split("/")[-1]
    # journal public : uniquement des nombres et la décision
    print("OK liste Bons plans : %d parfum(s), %d pièce(s) · décision : %s%s · page admin %s"
          % (len(lignes), pieces, decision, " · %d en stock insuffisant" % manque_stock if manque_stock else "", pid))


if __name__ == "__main__":
    main()
