#!/usr/bin/env python3
"""Gain net des commandes bol récentes (demande d'Amine du 19/11/2026 : « je gagne combien à chaque commande ? »).

  python3 scripts/bol_commandes_detail.py   → rapports/commandes_detail.csv (confidentiel)

Pour chaque article commandé ces 3 derniers jours : prix payé par le client, coût d'achat, commission bol, frais
(colis fournisseur, emballage, envoi client, provision retours) et gain net, avec la même formule que bol_regle.net.
Le dépôt est public : le journal n'affiche que le nombre de lignes ; le fichier est chiffré par le workflow
(clé publique config/cle_rapports.pem) avant d'en sortir.
"""
import csv
import datetime as dt
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import bol_analyse as ba  # noqa: E402
import bol_regle as regle  # noqa: E402
from bol_api import Bol  # noqa: E402

SORTIE = os.path.join(ba.RACINE, "rapports", "commandes_detail.csv")
SOURCE = {1: "SoleLuna", 2: "Trista", 3: "Rituals"}


def main():
    cfg = ba.lire_json(ba.CFG, {})
    refs = ba.references()
    marche = ba.lire_json(ba.MARCHE, {})
    bol = Bol()
    depuis = (dt.datetime.utcnow() - dt.timedelta(days=3)).strftime("%Y-%m-%d")
    lignes = []
    for statut in ("OPEN", "SHIPPED"):
        d = bol.get("/retailer/orders", {"status": statut, "fulfilment-method": "FBR", "page": 1}) or {}
        for c in d.get("orders") or []:
            if (c.get("orderPlacedDateTime") or "")[:10] < depuis:
                continue
            det = bol.get("/retailer/orders/%s" % c["orderId"]) or {}
            for it in det.get("orderItems") or []:
                ean = str((it.get("product") or {}).get("ean") or "")
                ref = refs.get(ean) or refs.get(ean.zfill(13)) or refs.get(ean.lstrip("0")) or {}
                q = int(it.get("quantity") or 1)
                prix = float(it.get("unitPrice") or 0)
                ligne = {"commande": c["orderId"], "statut": statut, "date": (c.get("orderPlacedDateTime") or "")[:16],
                         "ean": ean, "titre": (it.get("product") or {}).get("title", ""), "quantite": q,
                         "prix_client_ttc": prix, "commission_bol_annoncee": it.get("commission", ""),
                         "source": SOURCE.get(ref.get("source") or 1, "?") if ref else "introuvable"}
                if ref:
                    c2 = regle.cfg_pour(ref, cfg)
                    fixe, pct = (marche.get(ean) or {}).get("comm") or (1.15, 0.13)
                    ligne.update({"achat_ht": ref["achat"], "commission_calculee": round(fixe + pct * prix, 2),
                                  "frais_ht": round(regle.cout_ht(ref["achat"], c2) - ref["achat"], 2),
                                  "net_par_piece": round(regle.net(prix, ref["achat"], c2, fixe, pct), 2)})
                    ligne["net_total"] = round(ligne["net_par_piece"] * q, 2)
                lignes.append(ligne)
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    champs = ["commande", "statut", "date", "ean", "titre", "quantite", "source", "prix_client_ttc", "achat_ht",
              "commission_calculee", "commission_bol_annoncee", "frais_ht", "net_par_piece", "net_total"]
    with open(SORTIE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=champs, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(lignes)
    print("Commandes des 3 derniers jours : %d article(s) (détail chiffré)." % len(lignes))


if __name__ == "__main__":
    main()
