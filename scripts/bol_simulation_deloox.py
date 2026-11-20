#!/usr/bin/env python3
"""Simulation (20/11/2026, idée d'Amine) : acheter chez Deloox hors TVA (livraison intracommunautaire, numéro de TVA de
Deway : prix affiché ÷ 1,21), livré le lendemain, port offert dès 30 €. Pour chaque EAN dont on connaît le prix Deloox
(config/deloox.json, « InStock ») et le marché bol, on compare la décision bol avec la source actuelle et avec Deloox.
Lecture seule : ne publie rien. Le dépôt est public : le journal n'affiche que des nombres."""
import collections
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import bol_analyse as ba  # noqa: E402
import bol_regle as regle  # noqa: E402

VENDABLES = (regle.OUI_SEUL, regle.OUI_GAGNABLE, regle.OUI_PLUS_CHER, regle.OUI_A_NOUS)


def main():
    cfg = ba.lire_json(ba.CFG, {})
    tva = cfg.get("tva", 0.21)
    refs = ba.references()
    for f in ("ajouter_rituals", "ajouter_grossiste_2"):
        if hasattr(ba, f):
            try:
                getattr(ba, f)(refs)
            except Exception as ex:
                print("%s : %s" % (f, ex))
    marche = ba.lire_json(ba.MARCHE, {})
    dl = json.load(open(os.path.join(ba.RACINE, "config", "deloox.json"), encoding="utf-8")).get("par_ean", {})
    t, gains_nouveaux, gains_mieux = collections.Counter(), [], []
    for e, v in dl.items():
        prix, dispo = (v[0], v[1]) if isinstance(v, list) else (v, "InStock")
        e13 = e.zfill(13)
        m = marche.get(e13) or marche.get(e)
        if not m or dispo != "InStock" or not prix:
            t["sans marché bol ou pas en stock chez Deloox"] += 1
            continue
        mm = {"existe": m["existe"], "offres": m["offres"], "bornes": m["bornes"], "comm": tuple(m["comm"]) if m.get("comm") else None}
        ref_d = {"ean": e13, "achat": round(float(prix) / (1 + tva), 2), "stock": 3, "testeur": False, "abime": False,
                 "nom": "", "source": 4, "reglages": {"envoi_fournisseur_eur": 0.0 if float(prix) >= 30 else 4.95,
                                                      "marge_nette_koopblok_eur": 5}}
        dd = regle.decider(ref_d, mm, cfg)
        actu = refs.get(e13) or refs.get(e)
        da = regle.decider(actu, mm, cfg) if actu and actu.get("stock", 0) > 0 else {"decision": "pas de source en stock", "net": None}
        if dd["decision"] not in VENDABLES:
            t["Deloox : pas vendable (%s)" % dd["decision"]] += 1
            continue
        if da["decision"] not in VENDABLES:
            t["NOUVEAU grâce à Deloox : %s" % dd["decision"]] += 1
            gains_nouveaux.append(dd["net"])
        elif (dd.get("net") or 0) > (da.get("net") or 0) + 1:
            t["Deloox moins cher que la source actuelle : %s" % dd["decision"]] += 1
            gains_mieux.append(dd["net"] - da["net"])
        else:
            t["source actuelle meilleure ou égale"] += 1
    print("Deloox : %d EAN avec prix Deloox" % len(dl))
    for k, n in t.most_common():
        print("  %4d × %s" % (n, k))
    if gains_nouveaux:
        print("Gain net moyen sur les produits NOUVEAUX : %.2f €" % (sum(gains_nouveaux) / len(gains_nouveaux)))
    if gains_mieux:
        print("Gain net supplémentaire moyen quand Deloox est moins cher : %.2f €" % (sum(gains_mieux) / len(gains_mieux)))


if __name__ == "__main__":
    main()
