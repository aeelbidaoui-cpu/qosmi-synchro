#!/usr/bin/env python3
"""24/11/2026 (Amine, urgent : « mets tout le Rituals sur 3-5 jours ») : passe tout de suite TOUTES les offres Rituals
en ligne sur bol au délai de config/bol.json « rituals_delai_livraison », sans attendre la mise à jour bol complète.
Offres Rituals = EAN du catalogue Rituals (base/rituals_catalogue.json s'il est là) ou préfixe GS1 Rituals 8719134."""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    from bol_api import Bol
    from bol_publier import offres_en_ligne
    cfg = json.load(open(os.path.join(RACINE, "config", "bol.json"), encoding="utf-8"))
    delai = cfg.get("rituals_delai_livraison") or "3-5d"
    cat = set()
    try:
        c = json.load(open(os.path.join(RACINE, "base", "rituals_catalogue.json"), encoding="utf-8"))
        items = c.values() if isinstance(c, dict) else c
        for v in items:
            if isinstance(v, dict):
                for k in ("ean", "gtin", "EAN"):
                    if v.get(k):
                        cat.add(str(v[k]).lstrip("0"))
            elif isinstance(v, list):
                for x in v:
                    if isinstance(x, dict) and x.get("ean"):
                        cat.add(str(x["ean"]).lstrip("0"))
    except (FileNotFoundError, ValueError):
        pass
    bol = Bol()
    en_ligne = offres_en_ligne(bol)
    rit = {e: o for e, o in en_ligne.items() if e.startswith("8719134") or e in cat}
    a_changer = {e: o for e, o in rit.items() if o.get("delai") != delai and o.get("offerId")}
    print("Offres en ligne : %d · Rituals : %d · déjà en %s : %d · à changer : %d"
          % (len(en_ligne), len(rit), delai, len(rit) - len(a_changer), len(a_changer)))
    ok = ko = 0
    for e, o in a_changer.items():
        corps = {"onHoldByRetailer": False, "fulfilment": {"method": "FBR", "deliveryCode": delai}}
        if o.get("eo"):
            corps["economicOperatorId"] = o["eo"]
        try:
            bol.put("/retailer/offers/%s" % o["offerId"], corps)
            ok += 1
        except Exception as ex:
            ko += 1
            print("  refus %s : %s" % (e, str(ex)[:150]))
    print("OK délai Rituals : %d offres passées en %s, %d refus" % (ok, delai, ko))


if __name__ == "__main__":
    main()
