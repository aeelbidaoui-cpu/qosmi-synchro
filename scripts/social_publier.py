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

18/11/2026 : Meta bloque toujours l'accès développeur, on publie via Zernio (secret ZERNIO_API_KEY, comptes Instagram et
Facebook reliés dans le tableau de bord Zernio). La publication y est programmée à l'heure exacte. Sans aucun des deux
secrets (ZERNIO_API_KEY, META_TOKEN), le robot s'arrête proprement.
--comptes : vérifie quels comptes sont reliés dans Zernio, sans rien publier.
--essai : montre ce qui serait publié aujourd'hui, sans rien envoyer.
--forcer : publie tout de suite, sans attendre l'heure (en cas de rattrapage manuel).
--test : programme tout de suite chez Zernio la prochaine publication du calendrier, à l'heure « test_heure » de
config/social.json (test d'Amine du 18/11/2026 à 14 h), sans attendre sa date.
"""
import datetime as dt, json, os, sys, time, urllib.error, urllib.parse, urllib.request
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


def creneau(p):
    return p.get("heure") or CFG.get("heure", "18:30")


def choisir(lot, etat, aujourd_hui, heure=None):
    """Publication du créneau : la plus ancienne non publiée dont la date et l'heure sont passées (19/11/2026 : deux
    créneaux par jour, champ « heure » de chaque publication, voir scripts/social_planning.py)."""
    faites = set(etat)
    cle = lambda p: (p["iso"], creneau(p))  # noqa: E731
    attente = [p for p in sorted(lot, key=cle) if p["id"] not in faites]
    echues = [p for p in attente if cle(p) <= (aujourd_hui, heure or "99:99")]
    if not echues:
        return None, []
    sautees = []
    verifier = CFG.get("verifier_stock", False)
    for p in echues:
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


def legende_plateforme(p, plateforme):
    """18/11/2026 (Amine) : un lien direct vers le site sous chaque publication.
    Facebook : liens cliquables vers les fiches des parfums. Instagram : liens non cliquables dans les légendes,
    donc renvoi vers le lien de la bio (page qosmi.be/pages/instagram, mise à jour par ce robot)."""
    texte = legende(p)
    nl = p.get("langue") == "nl"
    if plateforme == "facebook":
        prefixe = "https://qosmi.be/nl/products/" if nl else "https://qosmi.be/products/"
        liens = ["👉 " + prefixe + h for h in p.get("produits") or []] or ["👉 https://qosmi.be" + ("/nl" if nl else "")]
        ajout = "\n".join(liens)
    else:
        ajout = "🔗 Link in bio om te bestellen" if nl else "🔗 Lien en bio pour le commander"
    tags = p.get("tags_nl") if nl and p.get("tags_nl") else p.get("tags")
    if tags and texte.endswith(tags):  # avant les hashtags
        return texte[: -len(tags)].rstrip() + "\n\n" + ajout + "\n\n" + tags
    return texte + "\n\n" + ajout


# ---------------------------------------------------------------- page « Vu sur Instagram » (lien de la bio)
PAGE = {"handle": "instagram", "titre": "Vu sur Instagram", "titre_nl": "Gezien op Instagram", "handle_nl": "instagram"}


def fiche_publique(handle, nl=False):
    try:
        with urllib.request.urlopen("https://qosmi.be%s/products/%s.js" % ("/nl" if nl else "", handle), timeout=30) as r:
            d = json.loads(r.read())
        return d.get("title"), d.get("price", 0) / 100, d.get("available")
    except Exception:
        return None, None, None


def corps_page(etat, lots, nl):
    import html
    e = lambda x: html.escape(x or "", quote=True)  # noqa: E731
    par_id = {p["id"]: p for p in lots}
    faites = sorted(((v.get("date", ""), k) for k, v in etat.items() if k in par_id), reverse=True)[:30]
    cartes = []
    for date, pid in faites:
        p, v = par_id[pid], etat[pid]
        titre = (p.get("titre_nl") if nl else None) or p["titre"]
        img = (v.get("img") or [None])[0]
        boutons = []
        for h in p.get("produits") or []:
            nom, prix, dispo = fiche_publique(h, nl)
            if not nom:
                continue
            lib = ("Bekijk" if nl else "Voir") + (" · %s" % ("%.2f €" % prix).replace(".", ",") if prix else "")
            boutons.append('<a class="qk-insta__btn" href="%s/products/%s">%s<br><small>%s</small></a>'
                           % ("/nl" if nl else "", e(h), e(lib), e(nom)))
        if not boutons:
            boutons.append('<a class="qk-insta__btn" href="%s/collections/all">%s</a>'
                           % ("/nl" if nl else "", "Ontdek onze parfums" if nl else "Découvrir nos parfums"))
        cartes.append('<div class="qk-insta__carte">%s<p class="qk-insta__titre">%s</p>%s</div>'
                      % ('<img src="%s" alt="%s" loading="lazy" width="540" height="675">' % (e(img), e(titre)) if img else "",
                         e(titre), "".join(boutons)))
    style = ("<style>.qk-insta{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:24px}"
             ".qk-insta__carte img{width:100%;height:auto;display:block;background:#f4f4f4}"
             ".qk-insta__titre{font-weight:500;margin:10px 0 8px}"
             ".qk-insta__btn{display:block;text-align:center;background:#111;color:#fff;text-decoration:none;padding:10px 12px;"
             "margin-top:6px;text-transform:uppercase;letter-spacing:.06em;font-size:13px}"
             ".qk-insta__btn small{text-transform:none;letter-spacing:0;opacity:.8}</style>")
    intro = ("<p>Les parfums de nos dernières publications Instagram : touche un bouton pour arriver sur la fiche.</p>" if not nl else
             "<p>De parfums uit onze laatste Instagram-posts: tik op een knop om naar de productpagina te gaan.</p>")
    return style + intro + '<div class="qk-insta">%s</div>' % "".join(cartes)


def maj_page(etat, lots):
    """Crée ou met à jour la page qosmi.be/pages/instagram (FR) et sa traduction NL."""
    from shopify_api import Shopify
    s = Shopify()
    fr, nl = corps_page(etat, lots, False), corps_page(etat, lots, True)
    d = s.gql('query($q: String!) { pages(first: 1, query: $q) { nodes { id } } }', {"q": "handle:" + PAGE["handle"]})["pages"]["nodes"]
    champs = {"title": PAGE["titre"], "handle": PAGE["handle"], "body": fr, "isPublished": True}
    if d:
        r = s.gql("mutation($id: ID!, $p: PageUpdateInput!) { pageUpdate(id: $id, page: $p) { page { id } userErrors { message } } }",
                  {"id": d[0]["id"], "p": champs})["pageUpdate"]
    else:
        r = s.gql("mutation($p: PageCreateInput!) { pageCreate(page: $p) { page { id } userErrors { message } } }", {"p": champs})["pageCreate"]
    if r["userErrors"]:
        print("Page Instagram : %s" % r["userErrors"])
        return
    pid = r["page"]["id"]
    tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": pid})
    dig = {x["key"]: x["digest"] for x in tr["translatableResource"]["translatableContent"]}
    t = [{"locale": "nl", "key": k, "value": v, "translatableContentDigest": dig[k]}
         for k, v in (("title", PAGE["titre_nl"]), ("body_html", nl), ("handle", PAGE["handle_nl"]))
         if k in dig and not (k == "handle" and v == PAGE["handle"])]  # même adresse en NL : rien à traduire
    e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) {
                 userErrors { message } } }""", {"id": pid, "t": t})["translationsRegister"]["userErrors"]
    print("Page qosmi.be/pages/instagram à jour (%d publication(s)), NL : %s" % (len(etat), "ok" if not e else e))


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


# ---------------------------------------------------------------- Zernio (18/11/2026, décision d'Amine : Meta bloque toujours)
ZAPI = "https://zernio.com/api/v1"


def zernio(methode, chemin, cle, corps=None):
    req = urllib.request.Request(ZAPI + chemin, method=methode,
                                 data=json.dumps(corps).encode() if corps is not None else None,
                                 headers={"Authorization": "Bearer " + cle, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as ex:
        raise RuntimeError("Zernio %s %s : %s %s" % (methode, chemin, ex.code, ex.read()[:300].decode("utf-8", "replace")))


def comptes_zernio(cle):
    """{"instagram": (accountId, profileId), "facebook": (...)} des comptes reliés dans Zernio."""
    d = zernio("GET", "/accounts", cle)
    liste = d if isinstance(d, list) else (d.get("accounts") or d.get("data") or [])
    out = {}
    for a in liste:
        plat = (a.get("platform") or "").lower()
        prof = a.get("profileId")
        prof = prof.get("_id") if isinstance(prof, dict) else prof
        if plat in ("instagram", "facebook") and plat not in out and a.get("isActive", True) is not False:
            out[plat] = (a.get("_id") or a.get("id"), prof)
    return out


def publier_zernio(cle, p, urls, cible, maintenant):
    comptes = comptes_zernio(cle)
    if not comptes:
        raise SystemExit("Aucun compte Instagram ou Facebook relié dans Zernio : relie-les dans le tableau de bord Zernio.")
    corps = {"content": legende_plateforme(p, "instagram"),
             "platforms": [dict({"platform": k, "accountId": v[0]},
                                **({"customContent": legende_plateforme(p, "facebook")} if k == "facebook" else {}))
                           for k, v in comptes.items()],
             "mediaItems": [{"type": "image", "url": u} for u in urls]}
    prof = next((v[1] for v in comptes.values() if v[1]), None)
    if prof:
        corps["profileId"] = prof
    if cible > maintenant + dt.timedelta(minutes=2):
        corps["scheduledFor"] = cible.isoformat(timespec="seconds")  # avec le décalage horaire : Zernio publie à l'heure exacte
        corps["timezone"] = CFG.get("fuseau", "Europe/Brussels")
    else:
        corps["publishNow"] = True
    r = zernio("POST", "/posts", cle, corps)
    post = r.get("post", r) if isinstance(r, dict) else {}
    return {"zernio": post.get("_id") or post.get("id"), "plateformes": sorted(comptes),
            "programme": corps.get("scheduledFor", "maintenant")}


def main():
    essai, forcer = "--essai" in sys.argv, "--forcer" in sys.argv
    if "--statut" in sys.argv or "--relancer" in sys.argv:  # état (ou relance) de la dernière publication chez Zernio
        cle = os.environ.get("ZERNIO_API_KEY", "").strip()
        etat = lire_etat()
        dern = sorted(((v.get("date", ""), v.get("heure", ""), k, v) for k, v in etat.items() if v.get("zernio")))[-1]
        pid = dern[3]["zernio"]
        r = zernio("POST", "/posts/%s/retry" % pid, cle) if "--relancer" in sys.argv else zernio("GET", "/posts/%s" % pid, cle)
        post = r.get("post", r) if isinstance(r, dict) else {}
        print("Publication %s (%s) : %s %s" % (dern[2], pid, post.get("status"), r.get("message") or r.get("error") or ""))
        for pl in post.get("platforms") or []:
            print("  - %s : %s %s %s" % (pl.get("platform"), pl.get("status"), pl.get("platformPostUrl") or "",
                                         (pl.get("errorMessage") or pl.get("error") or "")))
        return
    if "--comptes" in sys.argv:  # vérifie la connexion Zernio sans rien publier
        cle = os.environ.get("ZERNIO_API_KEY", "").strip()
        if not cle:
            raise SystemExit("ZERNIO_API_KEY absent")
        print("Comptes reliés dans Zernio : %s" % (", ".join(sorted(comptes_zernio(cle))) or "aucun"))
        return
    tz = ZoneInfo(CFG.get("fuseau", "Europe/Brussels"))
    maintenant = dt.datetime.now(tz)
    if "--test" in sys.argv:  # test : la prochaine publication, programmée à « test_heure »
        cle = os.environ.get("ZERNIO_API_KEY", "").strip()
        if not cle:
            raise SystemExit("ZERNIO_API_KEY absent")
        etat, lot = lire_etat(), charger_lots()
        p = next((x for x in sorted(lot, key=lambda x: x["iso"]) if x["id"] not in etat), None)
        if not p:
            raise SystemExit("Rien à publier.")
        cible = dt.datetime.fromisoformat(CFG["test_heure"]).astimezone(tz)
        print("Test : n°%s %s — %s, programmée pour %s" % (p["n"], p["id"], p["titre"], cible.isoformat()))
        urls = urls_publiques(p)
        resultat = dict(publier_zernio(cle, p, urls, cible, dt.datetime.now(tz)), date=cible.date().isoformat(),
                        n=p["n"], heure=cible.strftime("%H:%M:%S"), img=urls[:1], test=True)
        etat[p["id"]] = resultat
        ecrire_etat(etat)
        print("Résultat : %s" % json.dumps(resultat, ensure_ascii=False))
        try:
            maj_page(etat, lot)
        except Exception as ex:
            print("Page Instagram non mise à jour (%s)" % ex)
        return
    if not CFG.get("actif", True) and not essai:
        print("Robot désactivé (config/social.json « actif »).")
        return
    heures = CFG.get("heures") or [CFG.get("heure", "18:30")]
    cle_z = os.environ.get("ZERNIO_API_KEY", "").strip()
    if cle_z and not os.environ.get("META_TOKEN", "").strip() and not essai and not forcer:
        # 20/11/2026 : GitHub lance les passages programmés avec des heures de retard (le 19/11 : entre 20 h et minuit),
        # donc le « créneau proche » n'était jamais trouvé et rien n'est parti les 19 et 20/11. Désormais chaque passage
        # programme d'avance chez Zernio les créneaux libres d'aujourd'hui et des jours suivants : Zernio publie à
        # l'heure exacte, quel que soit le retard de GitHub.
        etat, lot = lire_etat(), charger_lots()
        jours = int(CFG.get("jours_avance", 2))
        programmees = 0
        for d in range(jours + 1):
            jour_c = (maintenant + dt.timedelta(days=d)).date()
            for hm in heures:
                h, m = map(int, hm.split(":"))
                cible = dt.datetime.combine(jour_c, dt.time(h, m), tzinfo=tz)
                if cible < maintenant + dt.timedelta(minutes=10):
                    continue
                jiso = jour_c.isoformat()
                if any(v.get("date") == jiso and v.get("creneau") == hm and not v.get("test") for v in etat.values()):
                    continue
                p, sautees = choisir(lot, etat, jiso, hm)
                if not p:
                    continue
                urls = urls_publiques(p)
                resultat = dict(publier_zernio(cle_z, p, urls, cible, dt.datetime.now(tz)), date=jiso, creneau=hm,
                                n=p["n"], heure=hm + ":00", img=urls[:1])
                etat[p["id"]] = resultat
                ecrire_etat(etat)
                programmees += 1
                print("Programmée chez Zernio : %s %s → n°%s %s — %s" % (jiso, hm, p["n"], p["id"], p["titre"]), flush=True)
        print("%d publication(s) programmée(s) d'avance." % programmees)
        if programmees:
            try:
                maj_page(etat, lot)
            except Exception as ex:
                print("Page Instagram non mise à jour (%s)" % ex)
        return
    # créneaux du jour (19/11/2026 : 12 h 30 et 18 h 30, heure de Bruxelles) : on prend celui qui est proche
    def cible_de(hm):
        h, m = map(int, hm.split(":"))
        return maintenant.replace(hour=h, minute=m, second=0, microsecond=0)
    proches = [hm for hm in heures if -90 <= (cible_de(hm) - maintenant).total_seconds() / 60 <= 75]
    if proches:
        heure = proches[0]
    elif essai or forcer:
        heure = max([hm for hm in heures if cible_de(hm) <= maintenant] or [heures[0]])
    else:
        print("Aucun créneau proche (%s) : rien à faire maintenant." % ", ".join(heures))
        return
    cible = cible_de(heure)
    etat = lire_etat()
    jour = maintenant.date().isoformat()
    if any(v.get("date") == jour and v.get("creneau", CFG.get("heure", "18:30")) == heure and not v.get("test")
           for v in etat.values()) and not essai:
        print("Déjà une publication pour le créneau de %s aujourd'hui (%s)." % (heure, jour))
        return
    lot = charger_lots()
    p, sautees = choisir(lot, etat, jour, heure)
    for pid, absents in sautees:
        print("Sautée pour l'instant (rupture de stock) : %s → %s" % (pid, ", ".join(absents)))
    if not p:
        print("Rien à publier aujourd'hui.")
        return
    print("Publication du jour : n°%s %s — %s (%d visuel(s))" % (p["n"], p["id"], p["titre"], len(p["img"])))
    if essai:
        print("--- Instagram ---\n" + legende_plateforme(p, "instagram"))
        print("--- Facebook ---\n" + legende_plateforme(p, "facebook"))
        return
    cle = os.environ.get("ZERNIO_API_KEY", "").strip()
    jeton = os.environ.get("META_TOKEN", "").strip()
    if cle and not jeton:
        urls = urls_publiques(p)
        resultat = dict(publier_zernio(cle, p, urls, cible if not forcer else maintenant, dt.datetime.now(tz)),
                        date=jour, creneau=heure, n=p["n"], heure=dt.datetime.now(tz).strftime("%H:%M:%S"), img=urls[:1])
        etat[p["id"]] = resultat
        ecrire_etat(etat)
        print("Résultat : %s" % json.dumps(resultat, ensure_ascii=False))
        try:
            maj_page(etat, lot)
        except Exception as ex:
            print("Page Instagram non mise à jour (%s)" % ex)
        return
    if not jeton:
        print("Ni ZERNIO_API_KEY ni META_TOKEN : rien publié.")
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
            print("Attente de %s (%d s)…" % (heure, reste))
            time.sleep(reste)
    resultat = {"date": jour, "creneau": heure, "n": p["n"], "heure": dt.datetime.now(tz).strftime("%H:%M:%S")}
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
