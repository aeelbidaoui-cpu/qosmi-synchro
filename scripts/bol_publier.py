#!/usr/bin/env python3
"""Publication des offres Qosmi sur bol.com (demande d'Amine du 08/11/2026).

Part des décisions de l'analyse (base/bol_decisions.json, scripts/bol_analyse.py) et ne met en vente que la sélection
choisie par Amine (config/bol.json, « selection ») :
  - koopblok gagnable ou déjà à nous ;
  - seul vendeur quand le prix de marché est connu (étoiles / bornes) ;
  - plus cher que le koopblok d'au plus « plus_cher_ecart_max » (10 %).
Chaque prix garde au moins marge_nette_eur (7 €) net : c'est déjà vérifié par la règle (scripts/bol_regle.py).

À chaque passage :
  1. liste les offres déjà en ligne (export bol) ;
  2. crée les offres manquantes. bol vérifie les droits de vente (verkooprechten) à la création : une offre refusée est
     notée avec la raison donnée par bol (base/bol_refus.json) et n'est retentée qu'après 7 jours ;
  3. met à jour prix et stock des offres existantes ;
  4. met à 0 le stock des offres qui ne sont plus rentables ou plus dans la sélection (rien n'est supprimé) ;
  5. liste les commandes bol ouvertes à passer chez le fournisseur (rapports/bol_commandes.txt).

Rien n'est écrit sur bol si config/bol.json « publication_active » vaut false (ou avec --essai).
Rapports internes et confidentiels : rapports/bol_publication.csv / .txt, rapports/bol_commandes.txt.
"""
import csv, io, json, os, sys, time, urllib.request
import datetime as dt

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
BASE = os.path.join(RACINE, "base")
RAPPORTS = os.path.join(RACINE, "rapports")
CFG = os.path.join(RACINE, "config", "bol.json")
DECISIONS = os.path.join(BASE, "bol_decisions.json")
REFUS = os.path.join(BASE, "bol_refus.json")
REESSAI_REFUS_JOURS = 7


def lire(chemin, defaut):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return defaut


def ecrire(chemin, d):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=0)


def selection(decisions, cfg):
    """{ean: décision} à mettre en vente selon le choix d'Amine."""
    sel = cfg.get("selection", {})
    ecart = float(sel.get("plus_cher_ecart_max", 0.10))
    out = {}
    for e, d in decisions.items():
        if e in set(cfg.get("ean_exclus", [])) or not d.get("prix") or not d.get("stock"):
            continue
        dec = d.get("decision") or ""
        if not dec.startswith("oui"):
            continue
        if (dec.startswith("oui : koopblok") and sel.get("koopblok", True)) or \
           (dec.startswith("oui : seul vendeur") and sel.get("seul_vendeur_avec_marche", True) and d.get("marche_connu")) or \
           (dec.startswith("oui : plus cher") and d.get("koopblok") and d["prix"] <= d["koopblok"] * (1 + ecart)):
            out[e] = d
    return out


def offres_en_ligne(bol):
    """{ean: {offerId, prix, stock}} d'après l'export des offres bol (source de vérité)."""
    r = bol.post("/retailer/offers/export", {"format": "CSV"})
    pid = (r or {}).get("processStatusId")
    st = bol.statut(pid, tours=200) if pid else {}
    if st.get("status") != "SUCCESS":
        raise RuntimeError("Export des offres bol impossible : %s" % (st.get("errorMessage") or st.get("status")))
    rep = st.get("entityId")
    req = urllib.request.Request("https://api.bol.com/retailer/offers/export/%s" % rep,
                                 headers={"Authorization": "Bearer " + bol._jeton(),
                                          "Accept": "application/vnd.retailer.v10+csv"})
    with urllib.request.urlopen(req, timeout=60) as f:
        texte = f.read().decode("utf-8-sig", "replace")
    out = {}
    for l in csv.DictReader(io.StringIO(texte)):
        ean = (l.get("ean") or "").lstrip("0")
        if not ean:
            continue
        prix = l.get("bundlePricesPrice") or l.get("price") or ""
        stock = l.get("stockAmount") or l.get("correctedStock") or "0"
        out[ean] = {"offerId": l.get("offerId"), "prix": float(prix.replace(",", ".") or 0), "stock": int(float(stock or 0))}
    return out


def corps_offre(ean, d, cfg):
    return {"ean": ean, "condition": {"name": "NEW"}, "reference": "QOSMI", "onHoldByRetailer": False,
            "pricing": {"bundlePrices": [{"quantity": 1, "unitPrice": round(d["prix"], 2)}]},
            "stock": {"amount": int(d["stock"]), "managedByRetailer": False},
            "fulfilment": {"method": "FBR", "deliveryCode": cfg.get("delai_livraison", "1-8d")}}


def commandes_ouvertes(bol):
    lignes = []
    page = 1
    while page <= 20:
        d = bol.get("/retailer/orders", {"status": "OPEN", "fulfilment-method": "FBR", "page": page}) or {}
        cmds = d.get("orders") or []
        for c in cmds:
            det = bol.get("/retailer/orders/%s" % c["orderId"]) or {}
            for it in det.get("orderItems") or c.get("orderItems") or []:
                lignes.append({"commande": c["orderId"], "date": (c.get("orderPlacedDateTime") or "")[:16],
                               "ean": (it.get("product") or {}).get("ean") or it.get("ean"),
                               "titre": (it.get("product") or {}).get("title", ""), "quantite": it.get("quantity"),
                               "pays": ((det.get("shipmentDetails") or {}).get("countryCode") or "")})
        if len(cmds) < 50:
            break
        page += 1
    return lignes


def main():
    essai = "--essai" in sys.argv
    cfg = lire(CFG, None) or sys.exit("config/bol.json absent.")
    if not cfg.get("publication_active") and not essai:
        print("Publication bol désactivée (config/bol.json « publication_active » = false) : rien n'est envoyé.")
        return
    dec = lire(DECISIONS, {}).get("decisions") or sys.exit("Pas de décisions : lancer d'abord l'analyse bol.")
    voulues = selection(dec, cfg)
    from bol_api import Bol
    bol = Bol()
    en_ligne = offres_en_ligne(bol)
    refus = lire(REFUS, {})
    maintenant = time.time()
    maxi = int(cfg.get("publication_max_creations", 300))
    journal, a_suivre = [], []

    # 1. créations
    creations = [e for e in voulues if e.lstrip("0") not in en_ligne and
                 maintenant - refus.get(e, {}).get("t", 0) > REESSAI_REFUS_JOURS * 86400]
    for e in creations[:maxi]:
        d = voulues[e]
        if essai:
            journal.append(("à créer (essai)", e, d, "")); continue
        try:
            r = bol.post("/retailer/offers", corps_offre(e, d, cfg))
            a_suivre.append((e, (r or {}).get("processStatusId")))
        except RuntimeError as err:
            refus[e] = {"t": maintenant, "raison": str(err)[:300]}
            journal.append(("refusée", e, d, str(err)[:200]))
    for e, pid in a_suivre:
        st = bol.statut(pid, tours=40) if pid else {"status": "FAILURE", "errorMessage": "pas de suivi"}
        if st.get("status") == "SUCCESS":
            journal.append(("créée", e, voulues[e], st.get("entityId", "")))
            refus.pop(e, None)
        else:
            raison = st.get("errorMessage") or st.get("status") or "inconnue"
            refus[e] = {"t": maintenant, "raison": raison[:300]}
            journal.append(("refusée par bol", e, voulues[e], raison[:200]))

    # 2. mises à jour et retraits
    par_court = {e.lstrip("0"): e for e in voulues}
    dec_court = {e.lstrip("0"): v for e, v in dec.items()}
    for ec, o in en_ligne.items():
        e = par_court.get(ec, ec)
        d = voulues.get(e)
        if d:
            if abs(o["prix"] - d["prix"]) > 0.004:
                if not essai:
                    bol.put("/retailer/offers/%s/price" % o["offerId"],
                            {"pricing": {"bundlePrices": [{"quantity": 1, "unitPrice": round(d["prix"], 2)}]}})
                journal.append(("prix mis à jour", e, d, "%.2f → %.2f" % (o["prix"], d["prix"])))
            if o["stock"] != int(d["stock"]):
                if not essai:
                    bol.put("/retailer/offers/%s/stock" % o["offerId"], {"amount": int(d["stock"]), "managedByRetailer": False})
                journal.append(("stock mis à jour", e, d, "%d → %d" % (o["stock"], int(d["stock"]))))
        elif o["stock"] > 0:
            if not essai:
                bol.put("/retailer/offers/%s/stock" % o["offerId"], {"amount": 0, "managedByRetailer": False})
            journal.append(("retirée (stock 0)", e, dec_court.get(ec, {}), (dec_court.get(ec) or {}).get("decision", "hors sélection")))
    ecrire(REFUS, refus)

    # 2 bis. visibilité réelle sur bol : une offre acceptée peut rester invisible (droits de vente, contenu) ;
    # bol donne alors des « notPublishableReasons » (vérifié à chaque passage, 08/11/2026)
    invisibles = {}
    if not essai:
        ids = {e: o["offerId"] for e, o in en_ligne.items()}
        ids.update({e.lstrip("0"): det for action, e, d, det in journal if action == "créée" and det})
        for ec, oid in ids.items():
            o = bol.get("/retailer/offers/%s" % oid) or {}
            for r in o.get("notPublishableReasons") or []:
                cle = "%s %s" % (r.get("code", ""), (r.get("description") or "")[:80])
                invisibles.setdefault(cle, []).append(ec)

    # 3. rapports internes
    os.makedirs(RAPPORTS, exist_ok=True)
    with open(os.path.join(RAPPORTS, "bol_publication.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["action", "ean", "nom", "prix", "stock", "net", "decision", "detail"])
        for action, e, d, det in journal:
            w.writerow([action, e, d.get("nom", ""), d.get("prix", ""), d.get("stock", ""), d.get("net", ""), d.get("decision", ""), det])
    compte = {}
    for action, *_ in journal:
        compte[action] = compte.get(action, 0) + 1
    raisons = {}
    for action, e, d, det in journal:
        if action.startswith("refusée"):
            raisons[det[:90]] = raisons.get(det[:90], 0) + 1
    nets = [d["net"] for d in voulues.values() if d.get("net")]
    txt = ["Publication bol du %s%s" % (dt.datetime.now().strftime("%d/%m/%Y %H:%M"), " (ESSAI, rien envoyé)" if essai else ""),
           "Sélection : %d références (gain net moyen %.2f €, minimum %.2f €). Déjà en ligne avant ce passage : %d offres."
           % (len(voulues), sum(nets) / len(nets) if nets else 0, min(nets) if nets else 0, len(en_ligne)), ""]
    txt += ["%-25s %5d" % kv for kv in sorted(compte.items(), key=lambda kv: -kv[1])]
    if raisons:
        txt += ["", "Raisons des refus bol :"] + ["  %3d × %s" % (n, r) for r, n in sorted(raisons.items(), key=lambda kv: -kv[1])]
    if invisibles:
        txt += ["", "Offres en ligne mais NON visibles sur bol (raison donnée par bol) :"] + \
               ["  %3d × %s" % (len(v), k) for k, v in sorted(invisibles.items(), key=lambda kv: -len(kv[1]))]
        ecrire(os.path.join(RAPPORTS, "bol_invisibles.json"), invisibles)
    elif not essai:
        txt += ["", "Toutes les offres en ligne sont publiables (aucune raison de blocage donnée par bol)."]
    if len(creations) > maxi:
        txt += ["", "%d créations reportées au prochain passage (limite %d par passage)." % (len(creations) - maxi, maxi)]
    # 4. commandes ouvertes à passer chez le fournisseur
    try:
        cmd = commandes_ouvertes(bol)
    except RuntimeError as err:
        cmd, txt = [], txt + ["", "Commandes bol : lecture impossible (%s)" % str(err)[:120]]
    lc = ["Commandes bol ouvertes (%s) : %d article(s) à commander chez le fournisseur" % (dt.datetime.now().strftime("%d/%m %H:%M"), len(cmd))]
    lc += ["  %s  commande %s  %s × %s  %s  (%s)" % (c["date"], c["commande"], c["quantite"], c["ean"], c["titre"][:60], c["pays"]) for c in cmd]
    with open(os.path.join(RAPPORTS, "bol_commandes.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lc) + "\n")
    txt += [""] + lc
    with open(os.path.join(RAPPORTS, "bol_publication.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(txt) + "\n")
    print("\n".join(txt))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("```\n" + "\n".join(txt) + "\n```\n")


if __name__ == "__main__":
    main()
