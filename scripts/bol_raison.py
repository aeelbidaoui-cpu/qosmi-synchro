#!/usr/bin/env python3
"""Pourquoi un EAN n'est pas (ou pas visible) en vente sur bol (24/11/2026, demande d'Amine). Sortie publique sans prix :
fournisseur (code source), décision de la règle, nombre de vendeurs, koopblok à nous ou non, offre en ligne ou non et
raisons données par bol. Usage : EANS="868...,871..." python3 scripts/bol_raison.py"""
import json, os, sys
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import bol_analyse as ba  # noqa: E402
import bol_regle as regle  # noqa: E402


def main():
    from bol_api import Bol
    from bol_publier import offres_en_ligne
    eans = [e.strip().lstrip("0") for e in os.environ.get("EANS", "").replace(";", ",").split(",") if e.strip()]
    cfg = ba.lire_json(ba.CFG, {})
    refs = {k.lstrip("0"): v for k, v in ba.references().items()}
    marche = {k.lstrip("0"): v for k, v in ba.lire_json(ba.MARCHE, {}).items()}
    moi = str(cfg.get("mon_retailer_id") or "")
    bol = Bol()
    en_ligne = offres_en_ligne(bol)
    for e in eans:
        print("=" * 60 + "\nEAN %s" % e)
        ref = refs.get(e)
        if not ref:
            print("  absent de nos listes fournisseurs (aucun fournisseur ne le propose en ce moment)")
        else:
            m = marche.get(e)
            print("  %s | source %s | stock fournisseur %s" % (ref.get("nom"), ref.get("source") or 1, ref.get("stock")))
            if m:
                d = regle.decider(ref, {"existe": m["existe"], "offres": m["offres"], "bornes": m["bornes"],
                                        "comm": tuple(m["comm"]) if m.get("comm") else None, "ecart": m.get("ecart", 0)}, cfg)
                vend = {str(o.get("retailer")) for o in m.get("offres") or []}
                kb = [o for o in m.get("offres") or [] if o.get("koopblok")]
                print("  décision : %s" % d.get("decision"))
                print("  fiche bol existante : %s · vendeurs : %d · koopblok : %s · étoiles de prix à notre prix : %s"
                      % ("oui" if m.get("existe") else "non", len(vend - {moi}),
                         "à nous" if kb and all(str(o.get("retailer")) == moi for o in kb) else ("un autre vendeur" if kb else "personne"),
                         d.get("etoiles")))
            else:
                print("  pas encore relevé sur bol")
        o = en_ligne.get(e)
        refus = ba.lire_json(os.path.join(ba.BASE, "bol_refus.json"), {})
        r = refus.get(e.zfill(13)) or refus.get(e)
        if r:
            import time
            print("  création refusée par bol il y a %.1f jours : %s" % ((time.time() - r.get("t", 0)) / 86400, r.get("raison", "")[:300]))
        if e in set((refus.get("_prix_trop_haut") or {}).get("eans", [])) or e.zfill(13) in set((refus.get("_prix_trop_haut") or {}).get("eans", [])):
            print("  retiré : bol a jugé le prix trop haut (règle : on retire, on ne baisse pas)")
        if not o:
            print("  offre Qosmi sur bol : aucune")
        else:
            det = bol.get("/retailer/offers/%s" % o["offerId"]) or {}
            rs = det.get("notPublishableReasons") or []
            print("  offre Qosmi sur bol : oui (stock %s, délai %s) · %s" % (o.get("stock"), o.get("delai"),
                  "VISIBLE" if not rs else "NON visible"))
            for r in rs:
                print("    - %s %s" % (r.get("code"), r.get("description")))


if __name__ == "__main__":
    main()
