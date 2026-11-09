#!/usr/bin/env python3
"""Robot de publication Qosmi sur Facebook et Instagram (demande d'Amine du 09/11/2026).

Chaque jour, publie UNE publication des lots validés (config/social.json « lots » : social/lot1/lot1.json, social/lot2/lot2.json…) à l'heure exacte choisie (config/social.json,
18 h 30 heure de Bruxelles), sur la page Facebook Qosmi et sur le compte Instagram qosmi.be.

Déroulé (lancé un peu avant l'heure par .github/workflows/social.yml) :
  1. choisit la publication du jour : la plus ancienne non publiée dont la date est passée (rien n'est publié deux fois,
     une seule par jour). Pas de contrôle de stock (décision d'Amine du 09/11 : une rupture n'empêche pas de publier) ;
     on peut le réactiver avec « verifier_stock »: true dans config/social.json ;
  2. envoie ses visuels dans les Fichiers Shopify (adresse publique exigée par Instagram) ;
  3. prépare la publication chez Meta (carrousel si plusieurs visuels) ;
  4. attend l'heure exacte, puis publie sur Instagram et sur Facebook ;
  5. note la publication dans social/publie.json (le workflow le sauvegarde dans le dépôt).

Sans le secret META_TOKEN (jeton de l'utilisateur système « qosmi-robot »), le robot s'arrête proprement.
--essai : montre ce qui serait publié aujourd'hui, sans rien envoyer.
--forcer : publie tout de suite, sans attendre l'heure (en cas de rattrapage manuel).
"""
import datetime as dt, json, os, sys, time, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
CFG = json.load(open(os.path.join(RACINE, "config", "social.json"), encoding="utf-8"))
ETAT = os.path.join(RACINE, "social", "publie.json")
GRAPH = "https://graph.facebook.com/" + CFG.get("graph_version", "v23.0")


def lire_etat():
    try:
        return json.load(open(ETAT, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def ecrire_etat(e):
    with open(ETAT, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=1)


def en_stock(handle):
    """Vrai si au moins une taille est disponible sur qosmi.be (fiche publique)."""
    try:
        with urllib.request.urlopen("https://qosmi.be/products/%s.js" % handle, timeout=30) as r:
            return bool(json.loads(r.read()).get("available"))
    except Exception as ex:
        print("  stock illisible pour %s (%s) : considéré absent" % (handle, ex))
        return False


def choisir(lot, etat, aujourd_hui):
    """Publication du jour : la plus ancienne non publiée et échue, sinon la suivante du calendrier ; tous ses parfums en stock."""
    faites = set(etat)
    attente = [p for p in sorted(lot, key=lambda p: p["iso"]) if p["id"] not in faites]
    echues = [p for p in attente if p["iso"] <= aujourd_hui]
    if not echues:
        return None, []
    sautees = []
    verifier = CFG.get("verifier_stock", False)
    for p in echues + [p for p in attente if p["iso"] > aujourd_hui]:
        absents = [h for h in p.get("produits", []) if not en_stock(h)] if verifier else []
        if not absents:
            return p, sautees
        sautees.append((p["id"], absents))
    return None, sautees


def legende(p):
    """Légende publiée.
    - « langue » = "nl" : texte NL seul + hashtags NL (lot 2 : un jour FR, le lendemain NL) ;
    - « langue » = "fr" : texte FR seul + hashtags ;
    - sans « langue » (lot 1) : texte FR, puis texte NL s'il existe, puis hashtags."""
    langue = p.get("langue")
    if langue == "nl":
        t = p["txt_nl"]
        tags = p.get("tags_nl") or p.get("tags")
        return t + ("\n\n" + tags if tags else "")
    if langue == "fr":
        return p["txt"] + ("\n\n" + p["tags"] if p.get("tags") else "")
    t = p["txt"]
    if p.get("txt_nl") and CFG.get("bilingue", True):
        t += "\n\n— NL —\n\n" + p["txt_nl"]
    if p.get("tags"):
        t += "\n\n" + p["tags"]
    return t


def charger_lots():
    """Tous les lots, chacun avec le dossier de ses visuels."""
    lots = []
    for chemin in CFG.get("lots") or [CFG["lot"]]:
        for p in json.load(open(os.path.join(RACINE, chemin), encoding="utf-8")):
            lots.append(dict(p, _dossier=os.path.join(RACINE, os.path.dirname(chemin))))
    return lots


def graph(methode, chemin, jeton, **params):
    params["access_token"] = jeton
    donnees = urllib.parse.urlencode(params).encode()
    url = GRAPH + chemin
    if methode == "GET":
        url, donnees = url + "?" + donnees.decode(), None
    for essai in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=donnees, method=methode), timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            corps = e.read().decode("utf-8", "replace")
            if e.code >= 500 or '"is_transient":true' in corps:
                time.sleep(10 * (essai + 1))
                continue
            raise RuntimeError("Meta %s %s → %s %s" % (methode, chemin, e.code, corps[:400]))
    raise RuntimeError("Meta %s %s : échec après plusieurs essais" % (methode, chemin))


def page_et_instagram(jeton):
    """Page Facebook Qosmi (jeton de page) et compte Instagram professionnel relié."""
    d = graph("GET", "/me/accounts", jeton, fields="id,name,access_token,instagram_business_account")
    for p in d.get("data", []):
        if p["name"].strip().lower() == CFG.get("page_nom", "Qosmi").lower():
            ig = (p.get("instagram_business_account") or {}).get("id")
            return p["id"], p["access_token"], ig
    raise RuntimeError("Page « %s » introuvable pour ce jeton : vérifier l'utilisateur système" % CFG.get("page_nom"))


def urls_publiques(p):
    """Envoie les visuels dans les Fichiers Shopify (une seule fois) et renvoie leurs adresses publiques."""
    from shopify_api import Shopify
    import photos_adp as pa
    s = Shopify()
    dossier = p.get("_dossier") or os.path.join(RACINE, os.path.dirname(CFG["lot"]))
    out = []
    for n in p["img"]:
        nom = "qosmi-social-%s.jpg" % n
        u = pa.adresse_fichier(s, nom)
        if not u:
            tmp = os.path.join("/tmp", nom)
            with open(os.path.join(dossier, n + ".jpg"), "rb") as src, open(tmp, "wb") as dst:
                dst.write(src.read())
            u = pa.envoyer(s, tmp, alt="Qosmi · " + (p.get("titre_nl") if p.get("langue") == "nl" else None or p["titre"]))
        if not u:
            raise RuntimeError("visuel %s non envoyé dans Shopify" % n)
        out.append(u)
    return out


def attendre_conteneur(cid, jeton):
    for _ in range(60):
        st = graph("GET", "/" + cid, jeton, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError("Instagram a refusé le visuel (%s)" % st)
        time.sleep(5)
    raise RuntimeError("Instagram : préparation trop longue")


def preparer_instagram(ig, jeton, urls, legende):
    if len(urls) == 1:
        c = graph("POST", "/%s/media" % ig, jeton, image_url=urls[0], caption=legende)["id"]
    else:
        enfants = []
        for u in urls[:10]:
            e = graph("POST", "/%s/media" % ig, jeton, image_url=u, is_carousel_item="true")["id"]
            attendre_conteneur(e, jeton)
            enfants.append(e)
        c = graph("POST", "/%s/media" % ig, jeton, media_type="CAROUSEL", children=",".join(enfants), caption=legende)["id"]
    attendre_conteneur(c, jeton)
    return c


def preparer_facebook(page, jeton_page, urls):
    """Photos envoyées sans être publiées ; elles seront rattachées à la publication à l'heure dite."""
    return [graph("POST", "/%s/photos" % page, jeton_page, url=u, published="false")["id"] for u in urls]


def publier_facebook(page, jeton_page, photos, legende):
    pieces = {"attached_media[%d]" % i: json.dumps({"media_fbid": f}) for i, f in enumerate(photos)}
    return graph("POST", "/%s/feed" % page, jeton_page, message=legende, **pieces)["id"]


def main():
    essai, forcer = "--essai" in sys.argv, "--forcer" in sys.argv
    tz = ZoneInfo(CFG.get("fuseau", "Europe/Brussels"))
    maintenant = dt.datetime.now(tz)
    h, m = map(int, CFG.get("heure", "18:30").split(":"))
    cible = maintenant.replace(hour=h, minute=m, second=0, microsecond=0)
    if not CFG.get("actif", True) and not essai:
        print("Robot désactivé (config/social.json « actif »).")
        return
    etat = lire_etat()
    jour = maintenant.date().isoformat()
    if any(v.get("date") == jour for v in etat.values()) and not essai:
        print("Déjà une publication aujourd'hui (%s)." % jour)
        return
    if not (essai or forcer):
        avance = (cible - maintenant).total_seconds() / 60
        if avance > 75:
            print("Trop tôt (%d min avant %s) : le passage suivant s'en charge." % (avance, CFG.get("heure")))
            return
        if avance < -90:
            print("Trop tard pour aujourd'hui (%s dépassé de %d min) : rien publié." % (CFG.get("heure"), -avance))
            return
    lot = charger_lots()
    p, sautees = choisir(lot, etat, jour)
    for pid, absents in sautees:
        print("Sautée pour l'instant (rupture de stock) : %s → %s" % (pid, ", ".join(absents)))
    if not p:
        print("Rien à publier aujourd'hui.")
        return
    print("Publication du jour : n°%s %s — %s (%d visuel(s))" % (p["n"], p["id"], p["titre"], len(p["img"])))
    if essai:
        print(legende(p))
        return
    jeton = os.environ.get("META_TOKEN", "").strip()
    if not jeton:
        print("META_TOKEN absent : accès Meta pas encore créé, rien publié.")
        return
    page, jeton_page, ig = page_et_instagram(jeton)
    urls = urls_publiques(p)
    conteneur = preparer_instagram(ig, jeton, urls, legende(p)) if ig else None
    if not ig:
        print("Aucun compte Instagram relié à la page : Facebook seulement.")
    photos = preparer_facebook(page, jeton_page, urls)
    if not forcer:
        reste = (cible - dt.datetime.now(tz)).total_seconds()
        if reste > 0:
            print("Attente de %s (%d s)…" % (CFG.get("heure"), reste))
            time.sleep(reste)
    resultat = {"date": jour, "n": p["n"], "heure": dt.datetime.now(tz).strftime("%H:%M:%S")}
    erreurs = []
    if conteneur:
        try:
            resultat["instagram"] = graph("POST", "/%s/media_publish" % ig, jeton, creation_id=conteneur)["id"]
        except RuntimeError as ex:
            erreurs.append(str(ex))
    try:
        resultat["facebook"] = publier_facebook(page, jeton_page, photos, legende(p))
    except RuntimeError as ex:
        erreurs.append(str(ex))
    if "instagram" in resultat or "facebook" in resultat:
        etat[p["id"]] = resultat
        ecrire_etat(etat)
    print("Résultat : %s" % json.dumps(resultat, ensure_ascii=False))
    if erreurs:
        raise SystemExit("Erreurs : " + " | ".join(erreurs))


if __name__ == "__main__":
    main()
