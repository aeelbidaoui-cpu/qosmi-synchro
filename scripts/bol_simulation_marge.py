#!/usr/bin/env python3
"""Simulation (22/11/2026, Amine : « si on descendait notre bénéfice à 3 €, on gagnerait combien de produits en plus ? »).
Toutes les sources, tous les EAN relevés : décisions avec les planchers actuels, puis avec un plancher unique de
--marge euros (défaut 3) partout (général, koopblok, seul vendeur, sources à réglages propres). Compare les sélections de
publication. Lecture seule : ne publie rien. Le dépôt est public : le journal n'affiche que des nombres."""
import collections
import copy
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import bol_analyse as ba  # noqa: E402
import bol_publier as bp  # noqa: E402

CLES = ("marge_nette_eur", "marge_nette_koopblok_eur", "marge_nette_seul_vendeur_eur")


def main():
    marge = float(sys.argv[sys.argv.index("--marge") + 1]) if "--marge" in sys.argv else 3.0
    cfg = ba.lire_json(ba.CFG, {})
    refs = ba.references()
    marche = ba.lire_json(ba.MARCHE, {})
    dec_a, _ = ba.decider_tout(cfg, refs, copy.deepcopy(marche))
    cfg_b = dict(cfg, **{k: marge for k in CLES}, rituals_marge_min_eur=marge, deloox_marge_min_eur=marge)
    refs_b = copy.deepcopy(refs)
    for r in refs_b.values():
        if r.get("reglages"):
            r["reglages"] = dict(r["reglages"], **{k: marge for k in CLES if k in r["reglages"]})
    dec_b, _ = ba.decider_tout(cfg_b, refs_b, copy.deepcopy(marche))
    sel_a, sel_b = bp.selection(dec_a, cfg), bp.selection(dec_b, cfg_b)
    gagnes = [e for e in sel_b if e not in sel_a]
    perdus = [e for e in sel_a if e not in sel_b]
    communs = [e for e in sel_a if e in sel_b]
    print("Simulation plancher %.2f € net partout (actuel : %.0f € général, %.0f € koopblok, %.0f € seul vendeur)" % (
        marge, cfg["marge_nette_eur"], cfg.get("marge_nette_koopblok_eur", 0), cfg.get("marge_nette_seul_vendeur_eur", 0)))
    print("Sélection actuelle : %d références · avec %.2f € : %d (+%d gagnées, -%d perdues)" % (
        len(sel_a), marge, len(sel_b), len(gagnes), len(perdus)))
    par = collections.Counter((dec_b[e].get("fournisseur") or 1, dec_b[e]["decision"].split(" (")[0]) for e in gagnes)
    for (src, d), n in sorted(par.items()):
        print("  + %4d × source %s · %s" % (n, src, d))
    nets = [dec_b[e]["net"] for e in gagnes if dec_b[e].get("net")]
    if nets:
        print("Gain net moyen des références gagnées : %.2f € (min %.2f €)" % (sum(nets) / len(nets), min(nets)))
    # koopblok : combien passeraient de « plus cher » à « koopblok gagnable »
    kb = sum(1 for e in communs if not dec_a[e]["decision"].startswith("oui : koopblok") and dec_b[e]["decision"].startswith("oui : koopblok"))
    print("Déjà sélectionnées qui pourraient prendre le koopblok en plus : %d" % kb)
    baisse = [(dec_a[e]["net"] or 0) - (dec_b[e]["net"] or 0) for e in communs if dec_a[e].get("prix") and dec_b[e].get("prix")
              and dec_b[e]["prix"] < dec_a[e]["prix"] - 0.005]
    if baisse:
        print("Déjà sélectionnées dont le prix baisserait : %d (gain net en moins par vente : %.2f € en moyenne)" % (
            len(baisse), sum(baisse) / len(baisse)))
    n_seul = sum(1 for e in communs if dec_a[e]["decision"].startswith("oui : seul vendeur") and dec_b[e].get("prix")
                 and dec_b[e]["prix"] < dec_a[e]["prix"] - 0.005)
    print("  dont « seul vendeur » (prix plus bas alors que personne d'autre ne vend) : %d" % n_seul)


if __name__ == "__main__":
    main()
