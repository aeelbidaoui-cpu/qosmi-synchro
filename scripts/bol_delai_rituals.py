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
    # 24/11/2026 : l'export peut annoncer le nouveau délai alors que l'offre ne l'a pas : on relit chaque offre une à une
    a_changer = {}
    vus = {}
    for e, o in rit.items():
        if not o.get("offerId"):
            continue
        det = bol.get("/retailer/offers/%s" % o["offerId"]) or {}
        dc = (det.get("fulfilment") or {}).get("deliveryCode") or ""
        vus[dc] = vus.get(dc, 0) + 1
        if dc != delai:
            a_changer[e] = dict(o, eo=o.get("eo") or det.get("economicOperatorId") or "")
    print("Délais relus offre par offre : %s" % vus)
    print("Offres en ligne : %d · Rituals : %d · déjà en %s : %d · à changer : %d"
          % (len(en_ligne), len(rit), delai, len(rit) - len(a_changer), len(a_changer)))
    ok = ko = 0
    pids = []
    for e, o in a_changer.items():
        corps = {"onHoldByRetailer": False, "fulfilment": {"method": "FBR", "deliveryCode": delai}}
        if o.get("eo"):
            corps["economicOperatorId"] = o["eo"]
        try:
            r = bol.put("/retailer/offers/%s" % o["offerId"], corps) or {}
            pids.append((e, r.get("processStatusId")))
            ok += 1
        except Exception as ex:
            ko += 1
            print("  refus %s : %s" % (e, str(ex)[:150]))
    # 24/11/2026 : bol traite la modification en différé : on vérifie le résultat réel
    import collections
    res = collections.Counter()
    for e, pid in pids:
        if not pid:
            res["sans suivi"] += 1
            continue
        st = bol.statut(pid, tours=40)
        res[st.get("status") or "?"] += 1
        if st.get("status") != "SUCCESS" and res["_affiches"] < 5:
            res["_affiches"] += 1
            print("  %s : %s %s" % (e, st.get("status"), (st.get("errorMessage") or "")[:200]))
    res.pop("_affiches", None)
    print("OK délai Rituals : %d demandes envoyées (%s), %d refus à l'envoi" % (ok, dict(res), ko))


if __name__ == "__main__":
    main()
