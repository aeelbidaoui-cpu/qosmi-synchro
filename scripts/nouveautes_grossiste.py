#!/usr/bin/env python3
"""Ce qui bouge dans la liste « Bons plans » (17-18/11/2026, demande d'Amine) : nouveautés, ruptures, retours en stock,
références retirées. Lancé après chaque mise à jour du site.

Compare la liste du 2e grossiste lue à ce passage avec celle des passages précédents et envoie à Amine, en message
Telegram privé :
  - les références jamais vues (dans ses marques : nom, format, stock, et la fiche Qosmi avec son prix si elle est en ligne ;
    hors de ses marques : les noms, pour décider d'en ajouter) ;
  - les références de ses marques revenues en stock.
Jamais de prix d'achat, de marge ni de nom de grossiste dans les messages ; le journal (public) ne montre que des nombres.

État : stocklists/WHOLESALEFRAGRANCES/nouveautes_vues.json (dossier gardé d'un passage à l'autre par le cache GitHub).
Telegram : secret TELEGRAM_TOKEN (mis par Amine lui-même). La conversation d'Amine est trouvée toute seule la première fois
qu'il écrit /start au robot, puis gardée dans un métachamp privé de la boutique (qosmi_prive.telegram_chat).
Sans secret : l'état avance quand même (pas de rafale de vieux messages le jour où Telegram est branché).

  python3 scripts/nouveautes_grossiste.py           # normal
  python3 scripts/nouveautes_grossiste.py --essai   # compte seulement, n'envoie rien, ne change rien
  python3 scripts/nouveautes_grossiste.py --test    # envoie un message d'essai sur Telegram
"""
import csv, datetime as dt, html, json, os, re, sys, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_soleluna as sl  # noqa: E402
import site_variantes as sv  # noqa: E402

ESSAI, TEST = "--essai" in sys.argv, "--test" in sys.argv
ETAT = os.path.join(sl.RACINE, "stocklists", "WHOLESALEFRAGRANCES", "nouveautes_vues.json")
SITE = "https://qosmi.be/products/"
MAX_MESSAGES, MAX_HORS = 6, 40


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ liste
def lire_liste():
    """{ean: {"nom", "stock", "arrivee"}} ou None si la liste manque ou est trop courte."""
    if not os.path.exists(sv.TRISTA):
        return None
    with open(sv.TRISTA, encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    if len(lignes) < 200 or not {"ean", "product", "stock"} <= set(lignes[0]):
        return None
    out = {}
    for l in lignes:
        ean = re.sub(r"\D", "", l.get("ean") or "").lstrip("0")
        if len(ean) < 7:
            continue
        stock = max(0, int(sl.nombre(l.get("stock"))))
        arrive = int(sl.nombre(l.get("incoming")))
        d = out.setdefault(ean, {"nom": sl.propre(l.get("product")), "stock": 0, "arrivee": ""})
        d["stock"] = max(d["stock"], stock)
        if arrive > 0 and (l.get("eta_date") or "").strip():
            d["arrivee"] = (l.get("eta_date") or "").strip()[:10]
    return out


def lire_etat():
    try:
        return json.load(open(ETAT, encoding="utf-8"))
    except Exception:
        return None


def ecrire_etat(liste, avant=None):
    """eans : 1 = en stock, 0 = épuisé ou sorti de la liste ; noms gardés pour annoncer une référence qui disparaît."""
    avant = avant or {}
    eans = {e: 0 for e in avant.get("eans", {})}
    eans.update({e: 1 if d["stock"] > 0 else 0 for e, d in liste.items()})
    noms = dict(avant.get("noms", {}))
    noms.update({e: d["nom"] for e, d in liste.items()})
    os.makedirs(os.path.dirname(ETAT), exist_ok=True)
    json.dump({"maj": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "nb": len(liste), "eans": eans, "noms": noms},
              open(ETAT, "w", encoding="utf-8"), ensure_ascii=False)


# ------------------------------------------------------------------ site
def fiches_site(s, eans):
    """{ean: (titre, format, prix, handle, statut)} pour les formats du site dont le code-barres est dans eans."""
    out, apres = {}, None
    while True:
        r = s.gql("""query($a: String) { productVariants(first: 250, after: $a) {
            nodes { barcode title price inventoryQuantity product { title handle status } }
            pageInfo { hasNextPage endCursor } } }""", {"a": apres})["productVariants"]
        for v in r["nodes"]:
            e = (v.get("barcode") or "").lstrip("0")
            if e in eans and v["product"]["status"] != "ARCHIVED":
                prix = float(v["price"])
                deja = out.get(e)
                if not deja or (v["product"]["status"] == "ACTIVE" and (deja[4] != "ACTIVE" or prix < deja[2])):
                    out[e] = (v["product"]["title"], v["title"], prix, v["product"]["handle"], v["product"]["status"])
        if not r["pageInfo"]["hasNextPage"]:
            return out
        apres = r["pageInfo"]["endCursor"]


# ------------------------------------------------------------------ Telegram
def tg(methode, **params):
    jeton = os.environ.get("TELEGRAM_TOKEN", "").strip()
    req = urllib.request.Request("https://api.telegram.org/bot%s/%s" % (jeton, methode),
                                 data=urllib.parse.urlencode(params).encode())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def conversation(s):
    """Identifiant de la conversation d'Amine : métachamp privé, sinon le premier « /start » reçu par le robot."""
    mf = s.gql('{ shop { id metafield(namespace: "qosmi_prive", key: "telegram_chat") { value } } }')["shop"]
    if mf["metafield"] and mf["metafield"]["value"]:
        return mf["metafield"]["value"], False
    for u in tg("getUpdates", timeout=0).get("result", []):
        m = u.get("message") or {}
        if (m.get("chat") or {}).get("type") == "private" and (m.get("text") or "").startswith("/start"):
            chat = str(m["chat"]["id"])
            r = s.gql("""mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) { userErrors { message } } }""",
                      {"m": [{"ownerId": mf["id"], "namespace": "qosmi_prive", "key": "telegram_chat",
                              "type": "single_line_text_field", "value": chat}]})["metafieldsSet"]
            if r["userErrors"]:
                raise RuntimeError("métachamp : %s" % r["userErrors"][0]["message"])
            return chat, True
    return None, False


def envoyer(chat, blocs):
    """Envoie les blocs (texte HTML) en messages de moins de 4 000 caractères."""
    messages, cur = [], ""
    for b in blocs:
        if len(cur) + len(b) + 1 > 3900 and cur:
            messages.append(cur)
            cur = ""
        cur += b + "\n"
    if cur.strip():
        messages.append(cur)
    if len(messages) > MAX_MESSAGES:
        messages = messages[:MAX_MESSAGES]
        messages[-1] += "\n… la suite est trop longue pour Telegram : demande-la à Claude."
    for m in messages:
        tg("sendMessage", chat_id=chat, text=m, parse_mode="HTML", disable_web_page_preview="true")
    return len(messages)


# ------------------------------------------------------------------ message
def euros(x):
    return ("%.2f €" % x).replace(".", ",")


def date_fr(d):
    try:
        return dt.date.fromisoformat(d).strftime("%d/%m")
    except ValueError:
        return d


def ligne(ean, d, site):
    h = html.escape
    dispo = "%d en stock" % d["stock"] if d["stock"] > 0 else ("arrive le %s" % date_fr(d["arrivee"]) if d["arrivee"] else "pas encore en stock")
    if ean in site:
        titre, fmt, prix, handle, statut = site[ean]
        etat = '<a href="%s%s">%s</a> · %s · %s' % (SITE, handle, h(fmt), euros(prix), "en ligne" if statut == "ACTIVE" else "pas en ligne")
    else:
        etat = "pas sur le site"
    return "• %s\n   %s · %s" % (h(d["nom"]), dispo, etat)


def composer(nouveaux, retours, ruptures, retires, liste, noms, site, marques):
    dans, hors, autres = [], [], 0
    for e in nouveaux:
        d = liste[e]
        if sv.EXCLUS_TRISTA.search(d["nom"]):
            autres += 1
        elif sv.marque_trista(d["nom"], marques)[0]:
            dans.append(e)
        else:
            hors.append(e)
    tri = lambda e: liste[e]["nom"].lower()  # noqa: E731
    blocs = []
    blocs.append("<b>📦 Ce qui bouge dans la liste Bons plans</b> (%s)" % dt.datetime.now().strftime("%d/%m %Hh"))
    if dans:
        blocs.append("\n<b>🆕 Nouveautés dans tes marques (%d)</b>" % len(dans))
        blocs += [ligne(e, liste[e], site) for e in sorted(dans, key=tri)]
    if hors:
        blocs.append("\n<b>🆕 Nouveautés, autres marques (%d)</b>" % len(hors))
        blocs += ["• " + html.escape(liste[e]["nom"]) for e in sorted(hors, key=tri)[:MAX_HORS]]
        if len(hors) > MAX_HORS:
            blocs.append("… et %d autres" % (len(hors) - MAX_HORS))
    if autres:
        blocs.append("\n+ %d coffret(s), testeur(s) ou miniature(s)" % autres)
    if retours:
        blocs.append("\n<b>🔁 De retour en stock (%d)</b>" % len(retours))
        blocs += [ligne(e, liste[e], site) for e in sorted(retours, key=tri)]
    if ruptures:
        blocs.append("\n<b>❌ En rupture (%d)</b> (sur le site, le format Bon plan s'affiche « épuisé »)" % len(ruptures))
        blocs += [ligne(e, liste[e], site) for e in sorted(ruptures, key=tri)]
    if retires:
        blocs.append("\n<b>🚫 Retirés de la liste (%d)</b>" % len(retires))
        for e in sorted(retires, key=lambda e: noms[e].lower()):
            d = {"nom": noms[e], "stock": 0, "arrivee": ""}
            blocs.append(ligne(e, d, site).replace("pas encore en stock", "plus proposé"))
    if len(blocs) == 1:
        return [], 0, 0, 0
    return blocs, len(dans), len(hors), autres


def main():
    from shopify_api import Shopify
    configure = bool(os.environ.get("TELEGRAM_TOKEN", "").strip())
    if TEST:
        if not configure:
            raise SystemExit("TELEGRAM_TOKEN absent")
        s = Shopify()
        chat, neuf = conversation(s)
        if not chat:
            raise SystemExit("Pas encore de conversation : écris /start à ton robot sur Telegram, puis relance.")
        envoyer(chat, ["✅ C'est branché : je t'écrirai ici dès que ça bouge dans la liste Bons plans (nouveautés, ruptures, retours en stock)."])
        log("message d'essai envoyé")
        return
    liste = lire_liste()
    if liste is None:
        log("nouveautés : liste absente ou illisible, rien à comparer")
        return
    etat = lire_etat()
    if not etat:
        if not ESSAI:
            ecrire_etat(liste)
        log("nouveautés : premier passage, %d références mémorisées (rien à signaler)" % len(liste))
        return
    if len(liste) < 0.7 * etat.get("nb", 0):
        log("nouveautés : liste nettement plus courte que la précédente (%d / %d), passage ignoré" % (len(liste), etat["nb"]))
        return
    vus = etat["eans"]
    sel = os.path.join(os.path.dirname(sl.SITE), "selection.json")
    marques = json.load(open(sel, encoding="utf-8"))["marques"] if os.path.exists(sel) else []
    noms = etat.get("noms", {})
    suivie = lambda nom: not sv.EXCLUS_TRISTA.search(nom) and sv.marque_trista(nom, marques)[0]  # noqa: E731
    nouveaux = [e for e in liste if e not in vus]
    retours = [e for e, d in liste.items() if vus.get(e) == 0 and d["stock"] > 0 and suivie(d["nom"])]
    ruptures = [e for e, d in liste.items() if vus.get(e) == 1 and d["stock"] == 0 and suivie(d["nom"])]
    retires = [e for e in vus if vus[e] == 1 and e not in liste and e in noms and suivie(noms[e])]
    log("nouveautés : %d nouvelle(s), %d retour(s), %d rupture(s), %d retirée(s) (marques suivies pour les 3 derniers)"
        % (len(nouveaux), len(retours), len(ruptures), len(retires)))
    if ESSAI:
        return
    envoye = True
    bouge = nouveaux or retours or ruptures or retires
    if bouge and configure:
        from shopify_api import Shopify
        s = Shopify()
        try:
            chat, neuf = conversation(s)
            if not chat:
                log("nouveautés : Telegram configuré mais pas de /start reçu ; messages en attente")
                envoye = False
            else:
                site = fiches_site(s, set(nouveaux) | set(retours) | set(ruptures) | set(retires))
                blocs, nd, nh, na = composer(nouveaux, retours, ruptures, retires, liste, noms, site, marques)
                if neuf:
                    blocs.insert(0, "✅ C'est branché : je t'écrirai ici dès que ça bouge.\n")
                n = envoyer(chat, blocs) if blocs else 0
                log("nouveautés : %d message(s) envoyé(s) (%d dans tes marques, %d autres, %d coffrets/testeurs)" % (n, nd, nh, na))
        except Exception as e:
            log("nouveautés : envoi Telegram impossible (%s)" % type(e).__name__)
            envoye = False
    elif bouge:
        log("nouveautés : Telegram pas encore configuré, rien envoyé")
    if not envoye:
        return  # on garde l'ancien état : ce sera renvoyé au prochain passage
    ecrire_etat(liste, etat)


if __name__ == "__main__":
    main()
