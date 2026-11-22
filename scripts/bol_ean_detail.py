#!/usr/bin/env python3
"""Détail bol d'un ou plusieurs EAN (22/11/2026, Amine : « on gagne combien sur ce produit, je veux avoir le koopblok »).
Relevé en direct des offres NL/BE (prix, koopblok, mode d'expédition, date de livraison max), coût tout compris,
commission bol, bénéfice net à notre prix actuel, au prix du koopblok et juste en dessous, prix minimum à 3/5/7 € net.
Sortie : rapports/ean_detail.txt (CONFIDENTIEL, chiffré par le workflow). Usage : EANS="871...,..." python3 scripts/bol_ean_detail.py"""
import os, sys
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import bol_analyse as ba  # noqa: E402
import bol_regle as regle  # noqa: E402
from bol_api import Bol  # noqa: E402


def main():
    eans = [e.strip().zfill(13) for e in os.environ.get("EANS", "").replace(";", ",").split(",") if e.strip()]
    cfg = ba.lire_json(ba.CFG, {})
    refs = ba.references()
    bol = Bol()
    moi = str(cfg.get("mon_retailer_id") or "")
    out = []
    for e in eans:
        ref = refs.get(e) or refs.get(e.lstrip("0"))
        out.append("=" * 70 + "\nEAN %s" % e)
        if not ref:
            out.append("  introuvable dans nos listes fournisseurs")
            continue
        c = regle.cfg_pour(ref, cfg)
        out.append("  %s | source %s | stock fournisseur %s" % (ref.get("nom"), ref.get("source") or 1, ref.get("stock")))
        out.append("  Achat HT %.2f + part colis fournisseur %.2f + emballage %.2f + envoi client %.2f + retours %.2f = coût %.2f HT"
                   % (ref["achat"], c["envoi_fournisseur_eur"], c["emballage_eur"], max(c["envoi_client_ht"].values()),
                      c.get("provision_retours_eur", 0), regle.cout_ht(ref["achat"], c)))
        m = ba.releve_ean(bol, e, cfg.get("pays", ["NL", "BE"]))
        offres = sorted(m["offres"], key=lambda o: o["prix"])
        out.append("  Bornes étoiles : %s" % m["bornes"])
        for o in offres:
            out.append("  %s %-8s %7.2f €  %s  %s  livraison max %s" % (o["pays"], "NOUS" if o["retailer"] == moi else o["retailer"],
                       o["prix"], "KOOPBLOK" if o["koopblok"] else "        ", o["mode"], o["livraison_max"]))
        mien = [o["prix"] for o in offres if o["retailer"] == moi]
        kb = [o["prix"] for o in offres if o["koopblok"] and o["retailer"] != moi]
        prix_test = sorted({round(p, 2) for p in mien + kb + [round(x - 0.01, 2) for x in kb] + [round(x - 0.50, 2) for x in kb]
                            + [round(x - 1, 2) for x in kb] if p > 0})
        com = ba.commissions(bol, [(e, p) for p in prix_test][:1]) if prix_test else {}
        fixe, pct = (com.get(e) or (0.0, 0.15, 0))[:2]
        out.append("  Commission bol : %.2f € + %.1f %% du prix TTC" % (fixe, pct * 100))
        for p in prix_test:
            lab = []
            if p in mien: lab.append("notre prix actuel")
            if p in kb: lab.append("prix du koopblok")
            out.append("  à %7.2f € TTC : bénéfice net %6.2f €  %s" % (p, regle.net(p, ref["achat"], c, fixe, pct), " / ".join(lab)))
        for mn in (3, 5, 7, 10):
            out.append("  prix minimum pour %2d € net : %.2f €" % (mn, regle.plancher(ref["achat"], dict(c, marge_nette_eur=mn), fixe, pct)))
        d = regle.decider(ref, {"existe": m["existe"], "offres": m["offres"], "bornes": m["bornes"], "comm": (fixe, pct),
                                "ecart": 0}, cfg)
        out.append("  Décision de la règle aujourd'hui : %s à %s € (net %s €)" % (d["decision"], d.get("prix"), d.get("net")))
    os.makedirs(ba.RAPPORTS, exist_ok=True)
    open(os.path.join(ba.RAPPORTS, "ean_detail.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("Détail écrit pour %d EAN" % len(eans))


if __name__ == "__main__":
    main()
