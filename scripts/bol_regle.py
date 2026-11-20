#!/usr/bin/env python3
"""Règle de prix et de mise en vente bol.com (décision d'Amine du 08/11/2026).

Pour une référence (EAN), avec :
  cout   = achat + part du colis fournisseur + emballage + envoi au client (le plus cher des pays) + provision retours
  comm   = commission bol = fixe + pourcentage × prix TTC (facturée sans TVA, autoliquidation)
  net    = prix TTC / (1 + TVA) − comm − cout

1. Plancher = plus petit prix (,x9) qui laisse net ≥ marge_nette_eur ; quand personne d'autre ne vend le produit,
   net ≥ marge_nette_seul_vendeur_eur (10 €) tant que ça reste sous la borne 2 étoiles.
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
import re

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


# 18/11/2026 : bpost (étiquettes « pakketzegels via bol ») refuse les liquides inflammables, dont le parfum.
# Ces articles gardent le tarif transporteur classique ; les autres (bougies, crèmes…) prennent l'étiquette bol.
INFLAMMABLE = re.compile(r"parfum|perfume|toilette|cologne|extrait|\bedp\b|\bedt\b|mist|brume|spray|vapo|a[ée]rosol|deo|d[ée]odorant|"
                         r"antiperspirant|anti-transpirant|after ?shave|eau fra[iî]che|nail|vernis|polish|laque|hairspray|alcohol|alcool|"
                         r"diffuser|diffuseur|fragrance oil|huile parfum|interior|interieur|int[ée]rieur|home fragrance|room spray|lighter|briquet|"
                         r"fragrance sticks|geurstokjes|refill|navulling|car perfume|autoparfum|wax melt|geurolie", re.I)


def cfg_pour(ref, cfg):
    """Réglages d'envoi propres à l'article : étiquette bpost via bol si l'article n'est pas inflammable."""
    if ref.get("reglages"):  # réglages propres à la source (ex. boutique de la marque : envoi d'achat, marge minimale)
        cfg = dict(cfg, **ref["reglages"])
    bol_bpost = cfg.get("envoi_client_bol_bpost_ht")
    if not bol_bpost or INFLAMMABLE.search(ref.get("nature") or ref.get("nom") or ""):
        return cfg
    return dict(cfg, envoi_client_ht=bol_bpost)


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
    cfg = cfg_pour(ref, cfg)
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
        # 18/11/2026 (Amine) : pour prendre le koopblok, on accepte de descendre jusqu'à « marge_nette_koopblok_eur »
        # (5 € net, tous frais compris, jamais à perte) ; si même ainsi on ne passe pas sous le koopblok, on reste au plancher normal.
        pl_kb = plancher(ref["achat"], dict(cfg, marge_nette_eur=min(cfg["marge_nette_eur"],
                                                cfg.get("marge_nette_koopblok_eur", cfg["marge_nette_eur"]))), fixe, pct) or pl
        mien = [o["prix"] for o in marche.get("offres", []) if str(o.get("retailer")) == moi and o.get("prix")]
        if a_nous and mien:
            # 20/11/2026 (Amine) : là où on a déjà le koopblok, on ne touche pas au prix (sauf s'il tombait sous
            # 5 € net : jamais à perte).
            prix, motif = max(min(mien), pl_kb), OUI_A_NOUS
        elif cible + 1e-9 >= pl_kb:
            ecart = float(marche.get("ecart") or 0)
            if ecart:  # 20/11/2026 : palier sous le koopblok (voir bol_analyse.decider_tout), jamais sous le plancher à 5 €
                cible = max(down9(ref_prix * (1 - ecart)), pl_kb)
            prix, motif = cible, OUI_GAGNABLE
        else:
            # 20/11/2026 (Amine) : sans le koopblok, on se rapproche au maximum : prix à 5 € net (au lieu de 7 €).
            prix, motif = pl_kb, OUI_PLUS_CHER
        d["koopblok"] = ref_prix
    elif a_nous and [o for o in marche.get("offres", []) if o.get("prix")]:
        # 20/11/2026 (Amine) : seul vendeur avec le koopblok : on ne touche pas au prix (jamais sous le plancher).
        prix, motif = max(min(o["prix"] for o in marche["offres"] if o.get("prix")), pl), OUI_A_NOUS
    else:
        # personne d'autre ne vend ce produit sur bol : plancher relevé à « marge_nette_seul_vendeur_eur » (10 €,
        # décision d'Amine du 09/11/2026), sans jamais dépasser la borne 2 étoiles (sinon on garde le plancher normal).
        pl_seul = plancher(ref["achat"], dict(cfg, marge_nette_eur=max(cfg["marge_nette_eur"],
                                                     cfg.get("marge_nette_seul_vendeur_eur", 0))), fixe, pct) or pl
        if bornes.get(2) and pl_seul > bornes[2] + 1e-9:
            pl_seul = max(pl, down9(bornes[2]))
        borne = bornes.get(int(cfg.get("etoiles_min", 3))) or bornes.get(2)
        prix = max(down9(borne), pl_seul) if borne else pl_seul
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
    m = {"existe": True, "offres": [], "bornes": {}, "comm": (1.0, 0.15)}
    d7 = decider(ref, m, cfg)
    d10 = decider(ref, m, dict(cfg, marge_nette_seul_vendeur_eur=10))
    assert abs(d7["net"] - 7) < 0.15 and abs(d10["net"] - 10) < 0.15 and d10["decision"] == OUI_SEUL, (d7, d10)
    m["bornes"] = {5: 55, 4: 57, 3: 59, 2: 63}
    d = decider(ref, m, dict(cfg, marge_nette_seul_vendeur_eur=10))
    assert d["decision"] == OUI_SEUL and d["prix"] <= 63 and d["net"] >= 7, d
    m = {"existe": True, "offres": [], "bornes": {5: 60, 4: 65, 3: 70, 2: 80}, "comm": (1.0, 0.15)}
    d = decider(ref, m, cfg)
    assert d["decision"] == OUI_SEUL and d["prix"] == 69.99, d
    m = {"existe": True, "offres": [{"pays": "NL", "prix": 59.5, "koopblok": True, "retailer": "9"}],
         "bornes": {5: 55, 4: 58, 3: 62, 2: 70}, "comm": (1.0, 0.15)}
    d7, d5 = decider(ref, m, cfg), decider(ref, m, dict(cfg, marge_nette_koopblok_eur=5))
    assert d7["decision"] == OUI_PLUS_CHER and d5["decision"] == OUI_GAGNABLE and 5 - 1e-9 <= d5["net"] < 7, (d7, d5)
    m["offres"][0]["prix"] = 52.0
    assert decider(ref, m, dict(cfg, marge_nette_koopblok_eur=5))["decision"] == OUI_PLUS_CHER
    d = decider(ref, m, dict(cfg, marge_nette_koopblok_eur=5))
    assert d["decision"] == OUI_PLUS_CHER and abs(d["net"] - 5) < 0.15, d  # 20/11 : sans koopblok → 5 € net
    m2 = {"existe": True, "offres": [{"pays": "NL", "prix": 61.49, "koopblok": True, "retailer": "1"},
                                     {"pays": "NL", "prix": 64.0, "koopblok": False, "retailer": "9"}],
          "bornes": {5: 55, 4: 58, 3: 62, 2: 70}, "comm": (1.0, 0.15)}
    d = decider(ref, m2, dict(cfg, marge_nette_koopblok_eur=5))
    assert d["decision"] == OUI_A_NOUS and d["prix"] == 61.49, d  # 20/11 : koopblok à nous → prix inchangé
    m3 = {"existe": True, "offres": [{"pays": "NL", "prix": 72.0, "koopblok": True, "retailer": "1"}],
          "bornes": {5: 60, 4: 65, 3: 70, 2: 80}, "comm": (1.0, 0.15)}
    d = decider(ref, m3, cfg)
    assert d["decision"] == OUI_A_NOUS and d["prix"] == 72.0, d  # seul vendeur avec koopblok → inchangé
    m4 = {"existe": True, "offres": [{"pays": "NL", "prix": 154.66, "koopblok": True, "retailer": "9"},
                                     {"pays": "NL", "prix": 154.59, "koopblok": False, "retailer": "1"}],
          "bornes": {5: 150, 4: 160, 3: 170, 2: 190}, "comm": (1.15, 0.13), "ecart": 0.03}
    d = decider(dict(ref, achat=82.81), m4, dict(cfg, marge_nette_koopblok_eur=5))
    assert d["decision"] == OUI_GAGNABLE and d["prix"] <= 154.66 * 0.97 and d["net"] >= 5, d
    m4["ecart"] = 0.25
    d = decider(dict(ref, achat=82.81), m4, dict(cfg, marge_nette_koopblok_eur=5))
    assert abs(d["net"] - 5) < 0.15, d  # palier bloqué au plancher 5 € net
    assert decider(ref, {"existe": False}, cfg)["decision"] == NON_ABSENT
    assert decider(dict(ref, testeur=True), m, cfg)["decision"] == NON_TESTEUR
    for a in (5, 20, 80, 200):
        for c in ((0.2, 0.05), (1.15, 0.13), (0.85, 0.15)):
            p = plancher(a, cfg, *c)
            assert net(p, a, cfg, *c) >= 7 - 1e-9 and net(p - 0.10, a, cfg, *c) < 7, (a, c, p)
    print("Règle bol : contrôles ok.")
