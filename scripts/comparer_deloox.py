#!/usr/bin/env python3
"""Qosmi face à Deloox : combien de nos formats sont moins chers, au même prix ou plus chers que chez Deloox (même EAN).

Demande d'Amine (21/11/2026) : « quand tu compares nos prix avec ceux de deloox on est concurrentiel ? »
Le dépôt est public : le journal n'affiche QUE des nombres et des pourcentages (aucun prix, aucun nom de parfum).
Lecture seule : rien n'est modifié dans la boutique.

Formats comparés : formats « normaux » actifs (pas Bon plan, pas Sur commande, pas testeur), avec un EAN que Deloox
vend en stock (config/deloox.json). « Bloqué par le plancher » = notre prix est au plancher des 5 € net (achat + frais),
on ne peut donc pas descendre plus bas.
"""
import json, os, statistics, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from shopify_api import Shopify  # noqa: E402
import site_soleluna as sl  # noqa: E402

Q = """query($a: String) { productVariants(first: 250, after: $a, query: "product_status:active") {
  pageInfo { hasNextPage endCursor }
  nodes { sku barcode price title inventoryItem { unitCost { amount } } } } }"""


def main():
    r = sl.reglages()
    k = 1 / (1 + r["tva"]) - r.get("paiement_pct", 0)
    concurrent = sl.concurrent()
    s = Shopify()
    a, vs = None, []
    while True:
        d = s.gql(Q, {"a": a})["productVariants"]
        vs += d["nodes"]
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]
    normaux = [v for v in vs if not (v.get("sku") or "").startswith(("QS-B", "QS-C", "QS-D"))
               and "testeur" not in (v.get("title") or "").lower() and "bon plan" not in (v.get("title") or "").lower()]
    moins, egal, plus, plancher, ecarts_moins, ecarts_plus, pct_plus = 0, 0, 0, 0, [], [], []
    for v in normaux:
        e = (v.get("barcode") or "").strip().lstrip("0")
        c = concurrent.get(e)
        if not e or not c:
            continue
        nous, eux = float(v["price"]), float(c[0])
        diff = nous - eux
        if abs(diff) < 0.10:
            egal += 1
        elif diff < 0:
            moins += 1
            ecarts_moins.append(-diff)
        else:
            plus += 1
            ecarts_plus.append(diff)
            pct_plus.append(diff / eux * 100)
            cout = float(((v.get("inventoryItem") or {}).get("unitCost") or {}).get("amount") or 0)
            if cout and nous <= (cout + r.get("paiement_fixe", 0) + 5) / k + 1.0:
                plancher += 1
    n = moins + egal + plus
    print("Formats actifs : %d, dont %d formats normaux." % (len(vs), len(normaux)))
    print("Formats normaux aussi vendus en stock chez Deloox (même EAN) : %d" % n)
    if not n:
        return
    f = lambda x: "%d (%.0f %%)" % (x, x / n * 100)
    print("  Qosmi moins cher : %s — écart moyen %.2f €, médian %.2f €" % (
        f(moins), statistics.mean(ecarts_moins) if ecarts_moins else 0, statistics.median(ecarts_moins) if ecarts_moins else 0))
    print("  Même prix (±0,10 €) : %s" % f(egal))
    print("  Qosmi plus cher : %s — écart médian %.2f € (%.1f %%), moyen %.2f €" % (
        f(plus), statistics.median(ecarts_plus) if ecarts_plus else 0, statistics.median(pct_plus) if pct_plus else 0,
        statistics.mean(ecarts_plus) if ecarts_plus else 0))
    if plus:
        print("    dont bloqués par le plancher des 5 € net (achat + frais trop hauts pour suivre) : %d (%.0f %% des plus chers)"
              % (plancher, plancher / plus * 100))
        for seuil in (1, 3, 5, 10):
            print("    plus cher de moins de %d € : %d" % (seuil, sum(1 for x in ecarts_plus if x < seuil)))


if __name__ == "__main__":
    main()
