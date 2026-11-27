#!/usr/bin/env python3
"""Tableau de bord Qosmi dans admin.deway.be (27/11/2026, Amine : « vasy »).

Lancé à la fin de chaque passage horaire (synchro.yml). Rassemble :
  - commandes : commandes site payées et non expédiées, commandes bol ouvertes, avec le fournisseur, le coût et un net estimé ;
  - ventes    : site et bol, par jour, 30 derniers jours ;
  - robots    : dernier passage de chaque workflow (synchro, bol, réseaux sociaux, journal) ;
  - alertes   : ce qui demande une action.
puis dépose le tout dans Supabase (fonction qosmi-tableau, jeton OIDC GitHub : aucun secret partagé).

Le dépôt est public : RIEN n'est imprimé dans le journal à part des nombres. Les montants et les fournisseurs ne partent
que dans le corps de la requête vers Supabase, lu ensuite par les seuls comptes connectés d'admin.deway.be.
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

URL_DEPOT = "https://kvmphxitsaaphkewnyxo.supabase.co/functions/v1/qosmi-tableau"
DEPOT = os.environ.get("GITHUB_REPOSITORY", "aeelbidaoui-cpu/qosmi-synchro")
TVA = 1.21

# Net estimé d'une commande du site (hypothèses écrites ici, une seule fois ; à corriger si les vrais frais diffèrent)
FRAIS_PAIEMENT = (0.019, 0.25)           # Shopify Payments, estimation (pourcentage du TTC, fixe)
EMBALLAGE = 0.60
PORT_FOURNISSEUR = {"SoleLuna": 3.0, "Trista": 2.0, "Stock propre": 0.0}   # part du colis d'achat par article
ENVOI_HT = {"BE": 3.22, "NL": 3.62, "LU": 3.62, "FR": 4.32, "ES": 5.72, "PT": 5.72, "IT": 5.72, "DE": 7.52, "PL": 7.52}
DOMICILE_BE_HT = 5.62                    # autre transporteur, ~6,80 € TTC

ROBOTS = [  # (fichier, nom, intervalle attendu en heures)
    ("synchro.yml", "Mise à jour du site", 1),
    ("bol.yml", "bol.com", 6),
    ("social.yml", "Réseaux sociaux", 8),
    ("blog.yml", "Magazine", 26),
]

maintenant = dt.datetime.now(dt.timezone.utc)
alertes = []


def iso(d):
    return d.astimezone(dt.timezone.utc).isoformat(timespec="seconds")


def fournisseur(sku):
    s = (sku or "").upper()
    if s.startswith("QD-"):
        return "Stock propre"
    if s.startswith(("QS-B", "QS-C", "QS-D")):
        return "Trista"
    if s.startswith("QS-"):
        return "SoleLuna"
    return "?"


# ------------------------------------------------------------------------------------------------ site (Shopify)
Q_COMMANDES = """query($q: String!, $a: String) { orders(first: 100, after: $a, query: $q, sortKey: CREATED_AT, reverse: true) {
  pageInfo { hasNextPage endCursor }
  nodes { id name createdAt cancelledAt test displayFinancialStatus displayFulfillmentStatus
    totalPriceSet { shopMoney { amount } } totalShippingPriceSet { shopMoney { amount } }
    shippingAddress { countryCodeV2 } shippingLine { title }
    lineItems(first: 30) { nodes { title variantTitle sku quantity currentQuantity
      originalUnitPriceSet { shopMoney { amount } }
      variant { inventoryItem { unitCost { amount } } } } } } } }"""


def commandes_shopify():
    from shopify_api import Shopify
    s = Shopify()
    depuis = (maintenant - dt.timedelta(days=30)).strftime("%Y-%m-%d")
    toutes, a = [], None
    while True:
        d = s.gql(Q_COMMANDES, {"q": "created_at:>=%s" % depuis, "a": a})["orders"]
        toutes += d["nodes"]
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]
    return [o for o in toutes if not o.get("test") and not o.get("cancelledAt")]


def detail_site(o):
    pays = (o.get("shippingAddress") or {}).get("countryCodeV2") or "BE"
    mode = ((o.get("shippingLine") or {}).get("title") or "").strip()
    total = float(o["totalPriceSet"]["shopMoney"]["amount"])
    lignes, cout_total, cout_connu = [], 0.0, True
    for li in o["lineItems"]["nodes"]:
        q = int(li.get("currentQuantity") if li.get("currentQuantity") is not None else li.get("quantity") or 0)
        if q <= 0:
            continue
        f = fournisseur(li.get("sku"))
        cout = (((li.get("variant") or {}).get("inventoryItem") or {}).get("unitCost") or {}).get("amount")
        cout = float(cout) if cout not in (None, "") else None
        if cout is None:
            cout_connu = False
        else:
            cout_total += (cout + PORT_FOURNISSEUR.get(f, 3.0)) * q
        lignes.append({"titre": li["title"], "format": li.get("variantTitle") or "", "sku": li.get("sku") or "",
                       "quantite": q, "prix_ttc": float(li["originalUnitPriceSet"]["shopMoney"]["amount"]),
                       "fournisseur": f, "cout_ht": cout})
    nb = sum(l["quantite"] for l in lignes)
    m = mode.lower()
    if "retrait" in m or "pickup" in m or "afhaal" in m:
        envoi = 0.0
    elif pays == "BE" and ("domicile" in m or "thuis" in m or "home" in m):
        envoi = DOMICILE_BE_HT
    else:
        envoi = ENVOI_HT.get(pays, 7.52)
    net = None
    if cout_connu and lignes:
        net = total / TVA - cout_total - (FRAIS_PAIEMENT[0] * total + FRAIS_PAIEMENT[1]) - envoi - EMBALLAGE * (1 if nb else 0)
    return {"source": "site", "numero": o["name"], "date": o["createdAt"], "pays": pays, "livraison": mode,
            "statut": o.get("displayFulfillmentStatus"), "paiement": o.get("displayFinancialStatus"),
            "total_ttc": round(total, 2), "net_estime": round(net, 2) if net is not None else None, "lignes": lignes}


# ------------------------------------------------------------------------------------------------ bol
def commandes_bol():
    import bol_analyse as ba
    import bol_regle as regle
    from bol_api import Bol
    import bol_rituals
    bol_rituals.main = lambda *a, **k: None  # pas de relevé Rituals ici (trop long) : seul le catalogue en cache sert
    cfg = ba.lire_json(ba.CFG, {})
    try:
        refs = ba.references()
    except Exception as e:  # noqa: BLE001
        refs = {}
        alertes.append({"niveau": "info", "texte": "Coûts bol indisponibles ce passage (%s)." % type(e).__name__})
    marche = ba.lire_json(ba.MARCHE, {})
    bol = Bol()
    ouvertes, vendues = [], []
    depuis = (maintenant - dt.timedelta(days=30)).strftime("%Y-%m-%d")
    for statut in ("OPEN", "SHIPPED"):
        for page in range(1, 6):
            d = bol.get("/retailer/orders", {"status": statut, "fulfilment-method": "FBR", "page": page}) or {}
            liste = d.get("orders") or []
            for c in liste:
                date = c.get("orderPlacedDateTime") or ""
                if date[:10] < depuis:
                    continue
                det = bol.get("/retailer/orders/%s" % c["orderId"]) or {}
                pays = ((det.get("shipmentDetails") or {}).get("countryCode") or "")
                lignes, net_total, net_connu, limite = [], 0.0, True, None
                for it in det.get("orderItems") or []:
                    ean = str((it.get("product") or {}).get("ean") or "")
                    ref = refs.get(ean) or refs.get(ean.zfill(13)) or refs.get(ean.lstrip("0")) or {}
                    q = int(it.get("quantity") or 1)
                    prix = float(it.get("unitPrice") or 0)
                    ful = it.get("fulfilment") or {}
                    lim = ful.get("latestDeliveryDate") or ful.get("exactDeliveryDate") or ful.get("expiryDate")
                    if lim and (not limite or lim < limite):
                        limite = lim
                    titre = (it.get("product") or {}).get("title", "")
                    if ref:
                        four = {1: "SoleLuna", 2: "Trista", 3: "Rituals (magasin)", 4: "Fournisseur 4"}.get(ref.get("source") or 1, "?")
                    else:
                        four = "Rituals (magasin)" if "rituals" in titre.lower() else "à chercher"
                    ligne = {"titre": titre, "ean": ean, "quantite": q, "prix_ttc": prix, "fournisseur": four,
                             "cout_ht": ref.get("achat") if ref else None, "annule": bool(it.get("cancellationRequest"))}
                    if ref:
                        c2 = regle.cfg_pour(ref, cfg)
                        fixe, pct = (marche.get(ean) or {}).get("comm") or (1.15, 0.13)
                        n = regle.net(prix, ref["achat"], c2, fixe, pct) * q
                        ligne["net_estime"] = round(n, 2)
                        net_total += n
                    else:
                        net_connu = False
                    lignes.append(ligne)
                cmd = {"source": "bol", "numero": c["orderId"], "date": date, "pays": pays, "statut": statut,
                       "date_limite": limite, "total_ttc": round(sum(l["prix_ttc"] * l["quantite"] for l in lignes), 2),
                       "net_estime": round(net_total, 2) if net_connu and lignes else None, "lignes": lignes}
                (ouvertes if statut == "OPEN" else vendues).append(cmd)
            if len(liste) < 50:
                break
    return ouvertes, vendues


# ------------------------------------------------------------------------------------------------ robots (GitHub)
def gh(chemin):
    req = urllib.request.Request("https://api.github.com/repos/%s/%s" % (DEPOT, chemin),
                                 headers={"Authorization": "Bearer " + os.environ.get("GITHUB_TOKEN", ""),
                                          "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def robots():
    sortie = []
    for fichier, nom, heures in ROBOTS:
        try:
            runs = gh("actions/workflows/%s/runs?per_page=10" % fichier).get("workflow_runs") or []
        except Exception as e:  # noqa: BLE001
            sortie.append({"nom": nom, "fichier": fichier, "etat": "inconnu", "detail": type(e).__name__})
            continue
        fini = next((r for r in runs if r.get("status") == "completed" and r.get("conclusion") != "cancelled"), None)
        ok = next((r for r in runs if r.get("conclusion") == "success"), None)
        en_cours = any(r.get("status") in ("in_progress", "queued") for r in runs)
        etat = "ok"
        if fini and fini.get("conclusion") != "success":
            etat = "echec"
        dernier_ok = ok and dt.datetime.fromisoformat(ok["updated_at"].replace("Z", "+00:00"))
        if not dernier_ok or (maintenant - dernier_ok).total_seconds() > heures * 2 * 3600 + 1800:
            etat = "echec" if etat == "echec" else "retard"
        sortie.append({"nom": nom, "fichier": fichier, "etat": etat, "en_cours": en_cours,
                       "dernier": fini and fini.get("updated_at"), "conclusion": fini and fini.get("conclusion"),
                       "dernier_ok": ok and ok.get("updated_at"), "url": fini and fini.get("html_url"),
                       "intervalle_h": heures})
        if etat == "echec":
            alertes.append({"niveau": "urgent", "texte": "Robot « %s » : le dernier passage a échoué." % nom,
                            "lien": fini and fini.get("html_url")})
        elif etat == "retard":
            alertes.append({"niveau": "attention", "texte": "Robot « %s » : pas de passage réussi depuis plus de %d h." % (nom, heures * 2)})
    return sortie


# ------------------------------------------------------------------------------------------------ dépôt
def jeton_github():
    url, tok = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL"), os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    if not url or not tok:
        raise RuntimeError("jeton OIDC GitHub indisponible (le workflow doit avoir « id-token: write »)")
    req = urllib.request.Request(url + "&audience=qosmi-tableau", headers={"Authorization": "bearer " + tok})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["value"]


def deposer(blocs):
    req = urllib.request.Request(URL_DEPOT, data=json.dumps({"blocs": blocs}, ensure_ascii=False).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + jeton_github(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError("dépôt refusé : %s %s" % (e.code, e.read()[:200].decode("utf-8", "replace")))


def jour_local(iso_date):
    d = dt.datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
    return (d + dt.timedelta(hours=1)).strftime("%Y-%m-%d")  # Bruxelles (hiver)


def main():
    blocs = {"commandes": {"maj": iso(maintenant), "site": [], "bol": []},
             "ventes": {"maj": iso(maintenant), "jours": {}}}
    ventes = blocs["ventes"]["jours"]

    def compter(cmd, canal):
        j = ventes.setdefault(jour_local(cmd["date"]), {"site": {"nb": 0, "ttc": 0, "net": 0}, "bol": {"nb": 0, "ttc": 0, "net": 0}})
        j[canal]["nb"] += 1
        j[canal]["ttc"] = round(j[canal]["ttc"] + cmd["total_ttc"], 2)
        j[canal]["net"] = round(j[canal]["net"] + (cmd.get("net_estime") or 0), 2)

    try:
        for o in commandes_shopify():
            cmd = detail_site(o)
            if o.get("displayFinancialStatus") in ("PAID", "PARTIALLY_REFUNDED", "PARTIALLY_PAID"):
                compter(cmd, "site")
            if o.get("displayFulfillmentStatus") in ("UNFULFILLED", "PARTIALLY_FULFILLED", "IN_PROGRESS", "ON_HOLD", "SCHEDULED") \
                    and o.get("displayFinancialStatus") in ("PAID", "PARTIALLY_PAID", "AUTHORIZED"):
                blocs["commandes"]["site"].append(cmd)
                age = (maintenant - dt.datetime.fromisoformat(cmd["date"].replace("Z", "+00:00"))).days
                if age >= 3:
                    alertes.append({"niveau": "attention", "texte": "Commande site %s non expédiée depuis %d jours." % (cmd["numero"], age)})
                if any(l["fournisseur"] == "Trista" for l in cmd["lignes"]):
                    alertes.append({"niveau": "info", "texte": "Commande site %s : Bon plan Trista, à mettre dans la commande du lundi." % cmd["numero"]})
    except Exception as e:  # noqa: BLE001
        alertes.append({"niveau": "attention", "texte": "Commandes du site illisibles ce passage (%s)." % type(e).__name__})

    if os.environ.get("BOL_CLIENT_ID"):
        try:
            ouvertes, vendues = commandes_bol()
            blocs["commandes"]["bol"] = ouvertes
            for c in ouvertes + vendues:
                compter(c, "bol")
            for c in ouvertes:
                if c.get("date_limite"):
                    reste = (dt.date.fromisoformat(c["date_limite"][:10]) - (maintenant + dt.timedelta(hours=1)).date()).days
                    if reste <= 2:
                        alertes.append({"niveau": "urgent" if reste <= 1 else "attention",
                                        "texte": "Commande bol %s : à livrer au plus tard le %s (%s)." % (
                                            c["numero"], c["date_limite"][:10], "aujourd'hui" if reste <= 0 else "dans %d jour(s)" % reste)})
        except Exception as e:  # noqa: BLE001
            alertes.append({"niveau": "attention", "texte": "Commandes bol illisibles ce passage (%s)." % type(e).__name__})

    blocs["robots"] = {"maj": iso(maintenant), "liste": robots()}
    ordre = {"urgent": 0, "attention": 1, "info": 2}
    blocs["alertes"] = {"maj": iso(maintenant), "liste": sorted(alertes, key=lambda a: ordre.get(a["niveau"], 3))}
    r = deposer(blocs)
    print("Tableau de bord : %d commande(s) site, %d bol, %d alerte(s) — %s" % (
        len(blocs["commandes"]["site"]), len(blocs["commandes"]["bol"]), len(alertes), ",".join(r.get("ok") or [])))


if __name__ == "__main__":
    main()
