#!/usr/bin/env python3
"""Deloox comme fournisseur pour bol (demande d'Amine du 20/11/2026).

Deloox (Pays-Bas) vend à Deway sans TVA (livraison intracommunautaire, numéro de TVA de Deway) : coût = prix affiché ÷ 1,21.
Port offert dès 30 €, « voor 20:00 besteld, morgen in huis ».

  --candidats    : EAN à relever chez Deloox = tout ce que bol connaît dans notre relevé de marché (bol_marche.json),
                   les plus chers d'abord → rapports/deloox_candidats.csv (chiffré par le workflow : prix bol)
  --opportunites : avec config/deloox.json (relevé Deloox) et le marché bol : les produits revendables sur bol avec au moins
                   5 € net en achetant chez Deloox → rapports/deloox_opportunites.csv (chiffré) + comptes dans le journal.
Le dépôt est public : le journal n'affiche que des nombres."""
import collections
import csv
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import bol_analyse as ba  # noqa: E402
import bol_regle as regle  # noqa: E402

VENDABLES = (regle.OUI_SEUL, regle.OUI_GAGNABLE, regle.OUI_PLUS_CHER, regle.OUI_A_NOUS)
RAP = os.path.join(ba.RACINE, "rapports")


def prix_bol(m):
    p = [o["prix"] for o in m.get("offres") or [] if o.get("prix")]
    b = m.get("bornes") or {}
    return max(p + [float(x) for x in b.values()] or [0])


def candidats():
    marche = ba.lire_json(ba.MARCHE, {})
    lignes = sorted(((e, prix_bol(m)) for e, m in marche.items() if m.get("existe")), key=lambda x: -x[1])
    lignes = [(e, p) for e, p in lignes if p >= 25]  # sous 25 € sur bol, 5 € net est hors d'atteinte avec les frais
    os.makedirs(RAP, exist_ok=True)
    with open(os.path.join(RAP, "deloox_candidats.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ean", "prix_bol_max"])
        w.writerows(lignes)
    print("Candidats Deloox : %d EAN connus de bol (sur %d relevés), à 25 € ou plus" % (len(lignes), len(marche)))


def opportunites():
    cfg = ba.lire_json(ba.CFG, {})
    tva = cfg.get("tva", 0.21)
    refs = ba.references()
    for f in ("ajouter_rituals", "ajouter_grossiste_2"):
        try:
            getattr(ba, f)(refs)
        except Exception as ex:
            print("%s : %s" % (f, ex))
    marche = ba.lire_json(ba.MARCHE, {})
    dl = json.load(open(os.path.join(ba.RACINE, "config", "deloox.json"), encoding="utf-8")).get("par_ean", {})
    # 22/11/2026 (Amine : « et si on descend notre bénéfice à 3 € ? ») : simulation avec --marge <euros> (défaut 5)
    marge = float(sys.argv[sys.argv.index("--marge") + 1]) if "--marge" in sys.argv else 5
    print("Bénéfice net minimum simulé : %.2f €" % marge)
    stats, lignes = collections.Counter(), []
    for e, v in dl.items():
        prix, dispo = (float(v[0]), v[1]) if isinstance(v, list) else (float(v), "InStock")
        e13 = e.zfill(13)
        m = marche.get(e13) or marche.get(e)
        if not m:
            stats["pas de relevé bol"] += 1
            continue
        if dispo != "InStock":
            stats["pas en stock chez Deloox"] += 1
            continue
        mm = {"existe": m["existe"], "offres": m["offres"], "bornes": m["bornes"], "comm": tuple(m["comm"]) if m.get("comm") else None,
              "ecart": m.get("ecart", 0)}
        ref = {"ean": e13, "achat": round(prix / (1 + tva), 2), "stock": 3, "testeur": False, "abime": False, "nom": "",
               "source": 4, "reglages": {"envoi_fournisseur_eur": 0.0 if prix >= 30 else 4.95, "marge_nette_koopblok_eur": marge,
                                         "marge_nette_eur": marge}}
        d = regle.decider(ref, mm, cfg)
        actu = refs.get(e13) or refs.get(e)
        da = regle.decider(actu, mm, cfg) if actu and actu.get("stock", 0) > 0 else {"decision": "aucune source en stock", "net": None}
        if d["decision"] not in VENDABLES:
            stats["Deloox : " + d["decision"]] += 1
            continue
        if da["decision"] not in VENDABLES:
            etat = "nouveau"
        elif (d.get("net") or 0) > (da.get("net") or 0) + 1:
            etat = "mieux que la source actuelle"
        else:
            etat = "source actuelle meilleure"
        stats["%s · %s" % (etat, d["decision"])] += 1
        kb = [o["prix"] for o in m["offres"] if o.get("koopblok")]
        lignes.append({"ean": e13, "etat": etat, "decision": d["decision"], "prix_bol_vise": d["prix"], "net_deloox": d["net"],
                       "achat_deloox_ht": ref["achat"], "prix_deloox_ttc": prix, "koopblok_bol": min(kb) if kb else "",
                       "decision_source_actuelle": da["decision"], "net_source_actuelle": da.get("net"),
                       "source_actuelle": (actu or {}).get("source", "")})
    lignes.sort(key=lambda r: (r["etat"] != "nouveau", -(r["net_deloox"] or 0)))
    os.makedirs(RAP, exist_ok=True)
    with open(os.path.join(RAP, "deloox_opportunites.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()) if lignes else ["ean"], delimiter=";")
        w.writeheader()
        w.writerows(lignes)
    print("Deloox : %d EAN relevés chez Deloox" % len(dl))
    for k, n in stats.most_common():
        print("  %5d × %s" % (n, k))
    nv = [r["net_deloox"] for r in lignes if r["etat"] == "nouveau"]
    if nv:
        print("Nouveaux produits vendables sur bol via Deloox : %d (gain net moyen %.2f €)" % (len(nv), sum(nv) / len(nv)))


if __name__ == "__main__":
    candidats() if "--candidats" in sys.argv else opportunites()
