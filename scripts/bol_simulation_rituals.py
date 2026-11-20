#!/usr/bin/env python3
"""Simulation (20/11/2026, question d'Amine) : produits Rituals sur bol, minimum 7 € net (actuel) contre 5 € net.
Lecture seule : ne publie rien. Le dépôt est public : le journal n'affiche que des nombres."""
import collections
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import bol_analyse as ba  # noqa: E402
import bol_regle as regle  # noqa: E402


def main():
    cfg = ba.lire_json(ba.CFG, {})
    refs = ba.references()
    if hasattr(ba, "ajouter_rituals"):
        ba.ajouter_rituals(refs)
    marche = ba.lire_json(ba.MARCHE, {})
    trans, nets7, nets5 = collections.Counter(), [], []
    for e, ref in refs.items():
        if ref.get("source") != 3 or not marche.get(e):
            continue
        m = marche[e]
        mm = {"existe": m["existe"], "offres": m["offres"], "bornes": m["bornes"], "comm": tuple(m["comm"]) if m.get("comm") else None}
        d7 = regle.decider(ref, mm, cfg)
        r5 = dict(ref, reglages=dict(ref.get("reglages") or {}, marge_nette_koopblok_eur=5, marge_nette_eur=5))
        d5 = regle.decider(r5, mm, cfg)
        trans["%s  →  %s" % (d7["decision"], d5["decision"])] += 1
        if d5["decision"] != d7["decision"] and d5.get("net"):
            nets5.append(d5["net"])
    print("Rituals relevés : %d" % sum(trans.values()))
    for k, n in trans.most_common():
        print("  %4d × %s" % (n, k))
    if nets5:
        print("Gain net moyen sur les produits qui changent (à 5 €) : %.2f €" % (sum(nets5) / len(nets5)))


if __name__ == "__main__":
    main()
