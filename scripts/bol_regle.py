#!/usr/bin/env python3
"""Règle de prix et de mise en vente bol.com (décision d'Amine du 08/11/2026).

Pour une référence (EAN), avec :
  cout   = achat + part du colis fournisseur + emballage + envoi au client (le plus cher des pays) + provision retours
  comm   = commission bol = fixe + pourcentage × prix TTC (facturée sans TVA, autoliquidation)
  net    = prix TTC / (1 + TVA) − comm − cout

1. Plancher = plus petit prix (,x9) qui laisse net ≥ marge_nette_eur.
2. Prix visé :
   - des concurrents vendent ce produit sur bol : juste sous le koopblok (le plus bas des deux pays),
     jamais sous le plancher (si le plancher est plus haut, on liste quand même au plancher) ;
   - personne ne le vend mais bol donne des bornes d'étoiles : le prix le plus haut qui garde
     « etoiles_min » étoiles, jamais sous le plancher ;
   - aucune donnée de marché : le plancher.
3. Mise en vente seulement si :
   - le produit existe sur bol ;
   - le prix reste ≤ la borne 2 étoiles (au-dessus, bol masque l'offre) ;
   - ce n'est ni un testeur (sauf si autorisé), ni un article abîmé, ni un EAN exclu.
"""
import math

NON_ABSENT = "non : absent de bol"
NON_MASQUE = "non : trop cher pour bol (masqué, 1 étoile)"
NON_TESTEUR = "non : testeur"
NON_ABIME = "non : article abîmé"
NON_EXCLU = "non : EAN exclu"
NON_STOCK = "non : plus en stock"
OUI_SEUL = "oui : seul vendeur"
OUI_GAGNABLE = "oui : koopblok gagnable"
OUI_PLUS_CHER = "oui : plus cher que le koopblok"
OUI_A_NOUS = "oui : koopblok à nous"


def up9(p):
    """Arrondi vers le haut à ,x9."""
    return round(math.ceil(round((p + 0.01) * 10, 6)) / 10 - 0.01, 2)


def down9(p):
    """Arrondi vers le bas à ,x9."""
    return round(math.floor(round((p + 0.01) * 10, 6)) / 10 - 0.01, 2)


def cout_ht(achat, cfg):
    return (achat + cfg["envoi_fournisseur_eur"] + cfg["emballage_eur"] + max(cfg["envoi_client_ht"].values())
            + cfg.get("provision_retours_eur", 0))


def net(prix, achat, cfg, fixe, pct):
    return prix / (1 + cfg["tva"]) - fixe - pct * prix - cout_ht(achat, cfg)


def plancher(achat, cfg, fixe, pct):
    k = 1 / (1 + cfg["tva"]) - pct
    if k <= 0:
        return None
    return up9((cout_ht(achat, cfg) + cfg["marge_nette_eur"] + fixe) / k)


def etoiles(prix, bornes):
    """bornes = {niveau: prix max pour ce niveau} ; 5 = le moins cher. Au-dessus de la borne 2 : 1 étoile (masqué)."""
    if not bornes:
        return None
    for niv in sorted(bornes, reverse=True):
        if niv >= 2 and prix <= bornes[niv] + 1e-9:
            return niv
    return 1


def decider(ref, marche, cfg):
    """ref = {ean, achat, stock, testeur, abime} ; marche = {existe, offres: [{pays, prix, koopblok, retailer}],
    bornes: {niveau: prix}, comm: (fixe, pct)} → dict de décision."""
    d = {"ean": ref["ean"], "prix": None, "plancher": None, "net": None, "etoiles": None, "decision": ""}
    if ref["ean"] in cfg.get("ean_exclus", []):
        d["decision"] = NON_EXCLU
        return d
    if ref.get("abime"):
        d["decision"] = NON_ABIME
        return d
    if ref.get("testeur") and not cfg.get("testeurs"):
        d["decision"] = NON_TESTEUR
        return d
    if ref.get("stock", 0) <= 0:
        d["decision"] = NON_STOCK
        return d
    if not marche or not marche.get("existe"):
        d["decision"] = NON_ABSENT
        return d
    fixe, pct = marche.get("comm") or (0.0, 0.15)
    pl = plancher(ref["achat"], cfg, fixe, pct)
    d["plancher"] = pl
    bornes = {int(k): float(v) for k, v in (marche.get("bornes") or {}).items()}
    moi = str(cfg.get("mon_retailer_id") or "")
    autres = [o for o in marche.get("offres", []) if str(o.get("retailer")) != moi]
    gagnants = [o for o in marche.get("offres", []) if o.get("koopblok")]
    a_nous = bool(gagnants) and all(str(o.get("retailer")) == moi for o in gagnants)
    if autres:
        kb = [o["prix"] for o in gagnants if str(o.get("retailer")) != moi] or [o["prix"] for o in autres]
        ref_prix = min(kb)
        cible = down9(ref_prix - 0.001)
        if cible >= ref_prix:
            cible = round(cible - 0.10, 2)
        prix = max(cible, pl)
        motif = OUI_GAGNABLE if prix <= cible + 1e-9 else OUI_PLUS_CHER
        d["koopblok"] = ref_prix
    elif bornes:
        borne = bornes.get(int(cfg.get("etoiles_min", 3))) or bornes.get(2)
        prix = max(down9(borne), pl) if borne else pl
        motif = OUI_A_NOUS if a_nous else OUI_SEUL
    else:
        prix = pl
        motif = OUI_A_NOUS if a_nous else OUI_SEUL
    if bornes.get(2) and prix > bornes[2] + 1e-9:
        d.update(prix=None, decision=NON_MASQUE, etoiles=1)
        return d
    if a_nous and motif != OUI_PLUS_CHER:
        motif = OUI_A_NOUS
    d.update(prix=prix, net=round(net(prix, ref["achat"], cfg, fixe, pct), 2), etoiles=etoiles(prix, bornes),
             decision=motif, stock=min(int(ref["stock"]), int(cfg.get("stock_max", 3))))
    return d


if __name__ == "__main__":  # petits contrôles de la règle
    cfg = {"tva": 0.21, "marge_nette_eur": 7, "envoi_fournisseur_eur": 3, "emballage_eur": 0.6,
           "envoi_client_ht": {"BE": 6.02, "NL": 8.5}, "provision_retours_eur": 1, "etoiles_min": 3,
           "stock_max": 3, "mon_retailer_id": "1"}
    ref = {"ean": "1", "achat": 20.0, "stock": 10}
    m = {"existe": True, "offres": [{"pays": "NL", "prix": 66.0, "koopblok": True, "retailer": "9"}],
         "bornes": {5: 60, 4: 64, 3: 68, 2: 75}, "comm": (1.0, 0.15)}
    d = decider(ref, m, cfg)
    assert d["decision"] == OUI_GAGNABLE and d["prix"] == 65.99 and d["net"] >= 7, d
    m["offres"][0]["prix"] = 40.0
    d = decider(ref, m, cfg)
    assert d["decision"] == OUI_PLUS_CHER and d["prix"] == d["plancher"] and abs(d["net"] - 7) < 0.15, d
    m["bornes"] = {5: 45, 4: 50, 3: 55, 2: 58}
    assert decider(ref, m, cfg)["decision"] == NON_MASQUE
    m = {"existe": True, "offres": [], "bornes": {5: 60, 4: 65, 3: 70, 2: 80}, "comm": (1.0, 0.15)}
    d = decider(ref, m, cfg)
    assert d["decision"] == OUI_SEUL and d["prix"] == 69.99, d
    assert decider(ref, {"existe": False}, cfg)["decision"] == NON_ABSENT
    assert decider(dict(ref, testeur=True), m, cfg)["decision"] == NON_TESTEUR
    for a in (5, 20, 80, 200):
        for c in ((0.2, 0.05), (1.15, 0.13), (0.85, 0.15)):
            p = plancher(a, cfg, *c)
            assert net(p, a, cfg, *c) >= 7 - 1e-9 and net(p - 0.10, a, cfg, *c) < 7, (a, c, p)
    print("Règle bol : contrôles ok.")
