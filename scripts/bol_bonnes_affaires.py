#!/usr/bin/env python3
"""Bonnes affaires Trista (demande d'Amine du 18/11/2026) : les produits du grossiste « Bons plans » dont le prix d'achat
est très en dessous du prix du marché (koopblok et offres bol, déjà relevés par bol_analyse), à avoir en stock.

  python3 scripts/bol_bonnes_affaires.py   → rapports/bonnes_affaires.csv (confidentiel)

Le dépôt est public : le journal n'affiche que des nombres ; le fichier est chiffré par le workflow avant d'en sortir
(clé publique config/cle_rapports.pem), seul Claude a la clé pour le lire.
"""
import csv
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import bol_analyse as ba  # noqa: E402
import bol_regle as regle  # noqa: E402

SORTIE = os.path.join(ba.RACINE, "rapports", "bonnes_affaires.csv")


def main():
    cfg = ba.lire_json(ba.CFG, {})
    refs = ba.references()
    marche = ba.lire_json(ba.MARCHE, {})
    moi = str(cfg.get("mon_retailer_id") or "")
    lignes = []
    for e, ref in refs.items():
        if ref.get("source") != 2 or ref.get("stock", 0) <= 0:
            continue
        m = marche.get(e) or {}
        autres = [o for o in m.get("offres") or [] if str(o.get("retailer")) != moi and o.get("prix")]
        if not autres:
            continue
        kb = [o["prix"] for o in autres if o.get("koopblok")] or [o["prix"] for o in autres]
        prix_marche = min(kb)
        fixe, pct = m.get("comm") or (1.15, 0.13)
        c = regle.cfg_pour(ref, cfg)
        vente = round(prix_marche - 0.01, 2)
        net = regle.net(vente, ref["achat"], c, fixe, pct)
        achat_ttc = ref["achat"] * (1 + cfg.get("tva", 0.21))
        lignes.append({"ean": e, "produit": ref["nom"], "marque": ref.get("marque", ""), "achat_ht": ref["achat"],
                       "stock_grossiste": ref["stock"], "prix_marche_bol_ttc": prix_marche, "vendeurs_bol": len(autres),
                       "ecart_pct": round(100 * (prix_marche / achat_ttc - 1)), "net_par_vente": round(net, 2)})
    lignes.sort(key=lambda r: (-r["net_par_vente"], -r["ecart_pct"]))
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()) if lignes else ["ean"], delimiter=";")
        w.writeheader()
        w.writerows(lignes)
    bons = [r for r in lignes if r["net_par_vente"] >= 20]
    print("Bonnes affaires : %d produits comparés au marché bol, %d à 20 € net ou plus par vente" % (len(lignes), len(bons)))


if __name__ == "__main__":
    main()
