#!/usr/bin/env python3
"""Analyse bol.com : pour chaque référence du fournisseur, est-ce rentable de la vendre sur bol, et à quel prix ?

Lecture seule sur bol (rien n'est publié ici). Règle : scripts/bol_regle.py, paramètres : config/bol.json.

Par EAN (API officielle bol, Retailer API v10) :
  - bornes d'étoiles de prix (au-dessus de la borne 2, bol masque l'offre) ;
  - offres « neuf » aux Pays-Bas et en Belgique (qui a le koopblok, à quel prix) ;
  - commission bol au prix visé (requête groupée par 100).
Le relevé de chaque EAN est gardé (base/bol_marche.json) et refait quand il a plus de « rescan_heures » :
le premier passage complet prend plusieurs passages, chacun s'arrête après « duree_max_minutes ».

Sorties (internes, confidentielles : coûts et prix concurrents) :
  base/bol_marche.json      relevés bol par EAN
  base/bol_decisions.json   décision et prix par EAN (sert à la publication)
  rapports/bol_analyse.csv  le tableau complet ; rapports/bol_analyse.txt  le résumé

Usage : python3 scripts/bol_analyse.py [--max N] [--sans-releve]
"""
import csv, datetime as dt, json, os, re, sys, time

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import bol_regle as regle  # noqa: E402

RACINE = os.path.dirname(ICI)
BASE = os.path.join(RACINE, "base")
RAPPORTS = os.path.join(RACINE, "rapports")
CFG = os.path.join(RACINE, "config", "bol.json")
SOURCE = os.path.join(BASE, "soleluna_liste.csv")
MARCHE = os.path.join(BASE, "bol_marche.json")
DECISIONS = os.path.join(BASE, "bol_decisions.json")


def lire_json(chemin, defaut):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return defaut


def ecrire_json(chemin, d):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    tmp = chemin + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, chemin)


def nombre(v):
    try:
        return float(str(v or "").replace(",", ".").strip())
    except ValueError:
        return 0.0


def references():
    """Liste du fournisseur → {ean: ref}. Un EAN présent deux fois : on garde le moins cher en stock."""
    if not os.path.exists(SOURCE):
        import site_synchro
        site_synchro.listes_serveur()
    with open(SOURCE, encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.reader(f.read().replace("\r\n", "\n").replace("\r", "\n").splitlines(), delimiter=";"))
    tete = [h.strip().upper() for h in lignes[0]]
    refs = {}
    for l in lignes[1:]:
        r = dict(zip(tete, [c.strip() for c in l]))
        ean = re.sub(r"\D", "", r.get("EAN") or "")
        if len(ean) not in (8, 12, 13, 14):
            continue
        ean = ean.zfill(13) if len(ean) <= 13 else ean
        achat = nombre(r.get("PRICE"))
        if achat <= 0:
            continue
        ref = {"ean": ean, "achat": achat, "stock": int(nombre(r.get("STOCK"))),
               "testeur": (r.get("TESTER") or "").strip() == "1", "abime": (r.get("DAMAGED") or "").strip() == "1",
               "nom": " ".join(x for x in (r.get("BRAND"), r.get("TITLE"), r.get("TYPE"), r.get("VOLUME")) if x),
               "marque": r.get("BRAND") or ""}
        old = refs.get(ean)
        # 18/11/2026 : une version « boîte abîmée » ne remplace jamais la version normale du même EAN (sinon l'offre bol,
        # vendue « neuve », pouvait renvoyer vers une pièce abîmée). Elle n'est gardée que si c'est la seule.
        if old and ref["abime"] and not old["abime"]:
            continue
        if not old or (old["abime"] and not ref["abime"]) or \
                (ref["stock"] > 0 and (old["stock"] <= 0 or ref["achat"] < old["achat"])):
            refs[ean] = ref
    if lire_json(CFG, {}).get("grossiste_2", True):
        ajouter_grossiste_2(refs)
    if lire_json(CFG, {}).get("rituals"):
        ajouter_rituals(refs)
    return refs


def ajouter_rituals(refs):
    """18/11/2026 (Amine) : tous les produits Rituals de la boutique belge (autorisation de Rituals), achetés au prix
    public belge TTC ramené en HT (facture au nom de Deway). Envoi Rituals : 3,90 € TTC sous 35 € de commande, gratuit
    au-delà. Au moins 7 € net partout, koopblok compris. Même EAN chez SoleLuna : on garde le moins cher des deux."""
    import bol_rituals
    try:
        bol_rituals.main()
    except Exception as e:
        print("Rituals : catalogue non relu (%s)" % str(e)[:120], flush=True)
    d = lire_json(bol_rituals.SORTIE, {}).get("produits") or {}
    cfg = lire_json(CFG, {})
    tva = cfg.get("tva", 0.21)
    ajoutes = 0
    for code, p in d.items():
        nom, prix = p.get("nom") or "", p.get("prix_ttc")
        if cfg.get("rituals_prix_promo") and p.get("prix_actuel_ttc") and 0 < p["prix_actuel_ttc"] < (prix or 1e9):
            prix = p["prix_actuel_ttc"]  # 18/11/2026 (Amine) : on suit la promo ; à la fin de la promo, le coût remonte et nos prix aussi
        if not prix or not p.get("ean") or re.search(r"gift ?card|cadeaukaart|e-gift", nom, re.I):
            continue
        achat = round(prix / (1 + tva), 2)
        stock = 3 if p.get("dispo") == "InStock" else 0
        old = refs.get(p["ean"])
        if old and old["stock"] > 0 and not old.get("abime") and old["achat"] <= achat:
            continue
        envoi_f = 0.0 if prix >= cfg.get("rituals_franco_ttc", 35) else round(cfg.get("rituals_envoi_ttc", 3.90) / (1 + tva), 2)
        refs[p["ean"]] = {"ean": p["ean"], "achat": achat, "stock": stock, "testeur": False, "abime": False,
                          "nom": "Rituals " + nom if not nom.lower().startswith("rituals") else nom, "marque": "Rituals",
                          "nature": nom + " | " + (p.get("cat") or ""), "source": 3,
                          "reglages": {"envoi_fournisseur_eur": envoi_f,
                                       "marge_nette_koopblok_eur": cfg.get("rituals_marge_min_eur", 7)}}
        ajoutes += 1
    print("Rituals : %d référence(s) ajoutée(s) à l'analyse bol" % ajoutes, flush=True)


EXCLUS_BOL_G2 = re.compile(r"\b(tester|testeur|gwp|sample|samples|vial|vials|echantillon|échantillon|not for sale|nfs)\b", re.I)


def ajouter_grossiste_2(refs):
    """17/11/2026 (Amine) : les parfums de la liste « Bons plans » vont aussi sur bol, au délai le plus long.
    18/11/2026 23 h 06 : TOUS les produits Trista, même si SoleLuna a le produit (une offre par EAN : le moins cher des deux). Coût = prix HT + 2 % (comme les Bons plans) ;
    l'envoi fournisseur par pièce est celui de la règle bol (envoi_fournisseur_eur). Testeurs, coffrets, minis exclus."""
    import site_variantes as sv
    if not os.path.exists(sv.TRISTA):
        try:
            import site_synchro
            site_synchro.liste_bons_plans()
        except Exception:
            return
    if not os.path.exists(sv.TRISTA):
        return
    with open(sv.TRISTA, encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    if len(lignes) < 200:
        return
    maj = sv.reglages_bons_plans()["majoration_pct"]
    sel = lire_json(os.path.join(RACINE, "config", "selection.json"), {})
    ajoutes = 0
    for l in lignes:
        ean = re.sub(r"\D", "", l.get("ean") or "")
        if len(ean) not in (8, 12, 13, 14):
            continue
        ean = ean.zfill(13) if len(ean) <= 13 else ean
        nom = " ".join((l.get("product") or "").split())
        achat, stock = nombre(l.get("price")), int(nombre(l.get("stock")))
        # 18/11/2026 (Amine) : « tous les produits Trista aussi sur bol » → plus d'exclusion coffrets / soins / bougies / minis ;
        # seuls restent exclus ce que bol interdit ou qui n'est pas vendable neuf (testeurs, échantillons, cadeaux promo).
        if achat <= 0 or stock <= 0 or EXCLUS_BOL_G2.search(nom):
            continue
        old = refs.get(ean)
        achat_g2 = round(achat * (1 + maj), 2)
        # même EAN chez les deux : une seule offre bol possible → on garde le moins cher des deux (en stock, boîte normale)
        if old and old["stock"] > 0 and not old.get("abime") and old["achat"] <= achat_g2:
            continue
        marque = sv.marque_trista(nom, sel.get("marques", []))[0] or ""
        refs[ean] = {"ean": ean, "achat": achat_g2, "stock": stock, "testeur": False, "abime": False,
                     "nom": nom, "marque": marque, "source": 2}
        ajoutes += 1
    print("grossiste 2 : %d référence(s) ajoutée(s) à l'analyse bol" % ajoutes, flush=True)


def priorite(refs):
    """Ordre de relevé : marques vedettes du site d'abord, puis le reste par prix décroissant."""
    sel = lire_json(os.path.join(RACINE, "config", "selection.json"), {})
    vedettes = {m.lower() for m in sel.get("vedettes", [])}
    return sorted(refs, key=lambda e: (refs[e]["marque"].lower() not in vedettes, -refs[e]["achat"]))


def releve_ean(bol, ean, pays):
    bornes = bol.get("/retailer/products/%s/price-star-boundaries" % ean)
    offres, vu = [], bornes is not None
    for p in pays:
        d = bol.get("/retailer/products/%s/offers" % ean, {"condition": "NEW", "country-code": p})
        if d is None:
            continue
        vu = True
        for o in d.get("offers", []):
            offres.append({"pays": o.get("countryCode") or p, "prix": float(o.get("price") or 0),
                           "koopblok": bool(o.get("bestOffer")), "retailer": str(o.get("retailerId") or ""),
                           "mode": o.get("fulfilmentMethod", ""), "livraison_max": (o.get("maxDeliveryDate") or "")[:10]})
        if not vu:
            break  # inconnu dans le premier pays et sans bornes : inutile de demander l'autre
    return {"t": time.time(), "existe": vu, "offres": offres,
            "bornes": {str(b["level"]): b["boundaryPrice"] for b in (bornes or {}).get("priceStarBoundaryLevels", [])}}


def commissions(bol, demandes):
    """demandes = [(ean, prix)] → {ean: (fixe, pct, prix)} ; requêtes groupées par 100, sinon une par une."""
    res = {}
    for i in range(0, len(demandes), 100):
        lot = demandes[i:i + 100]
        try:
            d = bol.post("/retailer/commission", {"commissionQueries": [
                {"ean": e, "condition": "NEW", "unitPrice": round(p, 2)} for e, p in lot]}) or {}
            for c in d.get("commissions", []):
                res[c["ean"]] = (float(c.get("fixedAmount") or 0), float(c.get("percentage") or 0) / 100,
                                 float(c.get("unitPrice") or 0))
        except RuntimeError:
            pass
        for e, p in lot:
            if e not in res:
                c = bol.get("/retailer/commission/%s" % e, {"condition": "NEW", "unit-price": "%.2f" % p})
                if c:
                    res[e] = (float(c.get("fixedAmount") or 0), float(c.get("percentage") or 0) / 100, p)
    return res


def releve(cfg, refs, marche, maxi=None):
    from bol_api import Bol
    bol = Bol()
    debut = time.time()
    limite = debut + 60 * float(cfg.get("duree_max_minutes", 300))
    vieux = time.time() - 3600 * float(cfg.get("rescan_heures", 24))
    a_faire = [e for e in priorite(refs) if refs[e]["stock"] > 0 and (e not in marche or marche[e]["t"] < vieux)
               and not (refs[e]["testeur"] and not cfg.get("testeurs")) and not refs[e]["abime"]]
    a_faire.sort(key=lambda e: e in marche)  # jamais relevés d'abord
    if maxi:
        a_faire = a_faire[:maxi]
    print("Relevé bol : %d EAN à relever (sur %d)." % (len(a_faire), len(refs)), flush=True)
    fait, lot = 0, []

    def fin_lot():
        demandes = []
        for e in lot:
            m = marche[e]
            if m["existe"]:
                prix = m.get("prix_vise") or regle.plancher(refs[e]["achat"], cfg, 1.0, 0.15) or 50
                demandes.append((e, prix))
        for e, (fixe, pct, p) in commissions(bol, demandes).items():
            marche[e]["comm"] = [fixe, pct]
            marche[e]["comm_prix"] = p
        ecrire_json(MARCHE, marche)
        lot.clear()

    for e in a_faire:
        if time.time() > limite:
            print("Durée maximale atteinte : la suite au prochain passage.", flush=True)
            break
        try:
            ancien = marche.get(e, {})
            marche[e] = releve_ean(bol, e, cfg["pays"])
            if ancien.get("comm"):
                marche[e]["comm"], marche[e]["comm_prix"] = ancien["comm"], ancien.get("comm_prix")
            if ancien.get("prix_vise"):
                marche[e]["prix_vise"] = ancien["prix_vise"]
        except RuntimeError as err:
            print("  %s : %s" % (e, str(err)[:160]), flush=True)
            continue
        lot.append(e)
        fait += 1
        if len(lot) >= 100:
            fin_lot()
        if fait % 250 == 0:
            print("  %d relevés · %d appels · %d pauses bol · %.0f min" % (fait, bol.appels, bol.pauses,
                                                                         (time.time() - debut) / 60), flush=True)
    if lot:
        fin_lot()
    reste = len(a_faire) - fait
    print("Relevé : %d EAN relevés, %d restent · %d appels, %d pauses imposées par bol." % (fait, reste, bol.appels, bol.pauses))
    return bol, fait, reste


def decider_tout(cfg, refs, marche, bol=None):
    decisions, lignes = {}, []
    for e, ref in refs.items():
        m = marche.get(e)
        d = regle.decider(ref, m and {"existe": m["existe"], "offres": m["offres"], "bornes": m["bornes"],
                                      "comm": tuple(m["comm"]) if m.get("comm") else None}, cfg) if m else \
            dict(regle.decider(ref, {"existe": True, "offres": [], "bornes": {}}, cfg), decision="pas encore relevé", prix=None)
        if m and d.get("prix"):
            m["prix_vise"] = d["prix"]
        nl = [o for o in (m or {}).get("offres", []) if o["pays"] == "NL"]
        be = [o for o in (m or {}).get("offres", []) if o["pays"] == "BE"]
        kb = lambda l: min([o["prix"] for o in l if o["koopblok"]] or [None]) if any(o["koopblok"] for o in l) else ""
        decisions[e] = {k: d.get(k) for k in ("prix", "stock", "decision", "net", "etoiles")}
        # pour la publication (08/11/2026) : prix du koopblok le plus bas (NL/BE) et prix de marché connu ou non
        kbs = [x for x in (kb(nl), kb(be)) if x]
        decisions[e]["koopblok"] = min(kbs) if kbs else None
        decisions[e]["marche_connu"] = bool(kbs or (m or {}).get("bornes") or d.get("etoiles"))
        decisions[e]["nom"] = ref["nom"]
        decisions[e]["marque"] = ref.get("marque", "")
        decisions[e]["fournisseur"] = ref.get("source") or 1  # 18/11/2026 : où commander (1 = catalogue, 2 = Bons plans, 3 = boutique de la marque)
        b = (m or {}).get("bornes", {})
        lignes.append({"decision": d["decision"], "ean": e, "nom": ref["nom"], "stock_fournisseur": ref["stock"],
                       "achat": ref["achat"], "cout_total_ht": round(regle.cout_ht(ref["achat"], regle.cfg_pour(ref, cfg)), 2),
                       "comm_fixe": (m or {}).get("comm", ["", ""])[0] if (m or {}).get("comm") else "",
                       "comm_pct": round(m["comm"][1] * 100, 1) if (m or {}).get("comm") else "",
                       "plancher": d.get("plancher") or "", "prix_bol": d.get("prix") or "", "net": d.get("net") or "",
                       "etoiles": d.get("etoiles") or "", "offres_NL": len(nl), "koopblok_NL": kb(nl),
                       "offres_BE": len(be), "koopblok_BE": kb(be), "borne_3": b.get("3", ""), "borne_2": b.get("2", ""),
                       "releve": dt.datetime.fromtimestamp(m["t"]).strftime("%d/%m %H:%M") if m else ""})
    return decisions, lignes


def rapports(lignes, cfg):
    os.makedirs(RAPPORTS, exist_ok=True)
    lignes.sort(key=lambda l: (not l["decision"].startswith("oui"), l["decision"], -(l["net"] or 0)))
    with open(os.path.join(RAPPORTS, "bol_analyse.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(lignes)
    compte = {}
    for l in lignes:
        compte[l["decision"]] = compte.get(l["decision"], 0) + 1
    oui = [l for l in lignes if l["decision"].startswith("oui")]
    txt = ["Analyse bol du %s" % dt.datetime.now().strftime("%d/%m/%Y %H:%M"),
           "Règle : %.0f € net minimum (%.0f € quand on est seul vendeur) ; envoi client compté %.2f € HT ; part colis fournisseur %.2f € ; emballage %.2f € ; "
           "retours %.2f € ; délai %s." % (cfg["marge_nette_eur"], max(cfg["marge_nette_eur"], cfg.get("marge_nette_seul_vendeur_eur", 0)), max(cfg["envoi_client_ht"].values()),
                                          cfg["envoi_fournisseur_eur"], cfg["emballage_eur"],
                                          cfg.get("provision_retours_eur", 0), cfg["delai_livraison"]), ""]
    txt += ["%-45s %6d" % (k, v) for k, v in sorted(compte.items(), key=lambda kv: -kv[1])]
    if oui:
        txt += ["", "À mettre en vente : %d références, gain net moyen %.2f € par vente." %
                (len(oui), sum(l["net"] for l in oui) / len(oui))]
    with open(os.path.join(RAPPORTS, "bol_analyse.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(txt) + "\n")
    print("\n".join(txt))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("```\n" + "\n".join(txt) + "\n```\n")


def main():
    cfg = lire_json(CFG, None)
    if not cfg:
        raise SystemExit("config/bol.json absent ou illisible.")
    maxi = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else None
    refs = references()
    marche = lire_json(MARCHE, {})
    if "--sans-releve" not in sys.argv:
        releve(cfg, refs, marche, maxi)
    decisions, lignes = decider_tout(cfg, refs, marche)
    ecrire_json(MARCHE, marche)
    ecrire_json(DECISIONS, {"date": time.time(), "decisions": decisions})
    rapports(lignes, cfg)


if __name__ == "__main__":
    main()
