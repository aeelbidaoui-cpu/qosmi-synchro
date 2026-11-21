#!/usr/bin/env python3
"""Stories Instagram Qosmi (demande d'Amine du 20/11/2026 : « 2 story, une à 11 h et une à 18 h », « toute sorte de story,
pas que le parfum du jour »).

Chaque jour, deux stories (11 h et 18 h, heure de Bruxelles) sont fabriquées puis programmées d'avance chez Zernio
(même compte que les publications, secret ZERNIO_API_KEY), sur Instagram uniquement. Un jour en français, le lendemain en
néerlandais (comme les publications). Jamais de prix de parfum sur une story (choix d'Amine).

Sortes de stories (elles tournent) :
  - 11 h : le parfum du jour · un Bon plan · « lequel choisis-tu ? » (duel) · une nouveauté ;
  - 18 h : une famille d'odeurs (3 parfums) · une info Qosmi (livraison, testeurs, authenticité…) · le parfum du soir.
Données : la boutique publique (qosmi.be/products.json : parfums en stock avec photo) et les notes de config/notes_fi.json.
Visuel 1080 × 1920 au style des publications (police Jost, fond gris clair). Un parfum n'est pas repris avant 30 jours.

Usage :
  python3 scripts/social_stories.py              → programme chez Zernio les créneaux libres d'aujourd'hui et des 2 jours suivants
  python3 scripts/social_stories.py --maintenant → publie tout de suite une story (rattrapage du jour)
  python3 scripts/social_stories.py --apercu N   → fabrique les N prochaines stories dans rapports/stories/ sans rien envoyer
Historique : social/stories.json (le workflow le sauvegarde dans le dépôt).
"""
import datetime as dt, hashlib, io, json, os, random, sys, textwrap, urllib.request
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont, ImageOps

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)
ETAT = os.path.join(RACINE, "social", "stories.json")
POLICE = os.path.join(RACINE, "social", "polices", "Jost.ttf")
SORTIE = os.path.join(RACINE, "rapports", "stories")
TZ = ZoneInfo("Europe/Brussels")
CRENEAUX = ["11:00", "18:00"]
JOURS_AVANCE = 2
W, H = 1080, 1920
NOIR, GRIS, DOUX, BLANC = (17, 17, 17), (244, 244, 244), (107, 107, 107), (255, 255, 255)
UA = {"User-Agent": "Mozilla/5.0 (qosmi-robot stories)"}

T = {
    "fr": {"du_jour": "Le parfum du jour", "soir": "Le parfum du soir", "bon_plan": "Bon plan", "nouveau": "Nouveau sur Qosmi",
           "duel": "Lequel choisis-tu ?", "duel_bas": "Réponds-nous en message", "famille": "Envie de %s ?",
           "famille_bas": "3 parfums à découvrir sur Qosmi", "tete": "Tête", "coeur": "Cœur", "fond": "Fond", "cta": "qosmi.be · lien en bio", "ou": "ou",
           "bp_txt": "Le même parfum, un prix plus doux,\nlivré chez toi en 3 à 8 jours ouvrables.",
           "nv_txt": "Il vient d'arriver dans la boutique."},
    "nl": {"du_jour": "Parfum van de dag", "soir": "Parfum van de avond", "bon_plan": "Koopje", "nouveau": "Nieuw bij Qosmi",
           "duel": "Welke kies jij?", "duel_bas": "Stuur ons een bericht", "famille": "Zin in %s?",
           "famille_bas": "3 parfums om te ontdekken bij Qosmi", "tete": "Top", "coeur": "Hart", "fond": "Basis", "cta": "qosmi.be · link in bio", "ou": "of",
           "bp_txt": "Hetzelfde parfum, een zachtere prijs,\nbij jou geleverd in 3 tot 8 werkdagen.",
           "nv_txt": "Net binnen in de winkel."},
}

# Familles d'odeurs : (mot cherché dans les notes, libellé FR, libellé NL)
FAMILLES = [("vanille", "vanille", "vanille"), ("rose", "rose", "roos"), ("oud", "oud", "oud"), ("ambre", "ambré", "amber"),
            ("cuir", "cuir", "leer"), ("musc", "musc", "musk"), ("santal", "santal", "sandelhout"), ("jasmin", "jasmin", "jasmijn"),
            ("bergamote", "frais", "fris"), ("patchouli", "patchouli", "patchoeli"), ("tabac", "tabac", "tabak"),
            ("iris", "iris", "iris"), ("café", "café", "koffie"), ("lavande", "lavande", "lavendel")]

# Infos Qosmi (texte seul) : vérifiées sur le site au 20/11/2026
INFOS = [
    {"fr": ("Livraison offerte", "dès 2 articles, en point relais.\n1 article : 2,95 €."),
     "nl": ("Gratis levering", "vanaf 2 artikelen, in een afhaalpunt.\n1 artikel: € 2,95.")},
    {"fr": ("C'est quoi un testeur ?", "Le même parfum, dans la même contenance.\nCe n'est pas un échantillon :\njuste un emballage plus simple."),
     "nl": ("Wat is een tester?", "Hetzelfde parfum, dezelfde inhoud.\nGeen staaltje:\nalleen een eenvoudigere verpakking.")},
    {"fr": ("100 % authentiques", "Tous nos parfums sont neufs\net authentiques."),
     "nl": ("100 % authentiek", "Al onze parfums zijn nieuw\nen authentiek.")},
    {"fr": ("Le bon geste", "Vaporise sur les poignets et le cou,\nsans frotter : le parfum garde\nses notes plus longtemps."),
     "nl": ("De juiste reflex", "Spray op polsen en hals,\nzonder te wrijven: het parfum houdt\nzijn noten langer vast.")},
    {"fr": ("Bons plans", "Sur certains parfums, une option\nmoins chère, livrée en 3 à 8 jours.\nCherche l'étiquette « Bon plan »."),
     "nl": ("Koopjes", "Bij sommige parfums een goedkopere\noptie, geleverd in 3 tot 8 dagen.\nZoek het label « Koopje ».")},
]

ORDRE = {"11:00": ["du_jour", "bon_plan", "duel", "du_jour", "nouveau"], "18:00": ["famille", "info", "soir", "famille", "info"]}


def police(taille, poids="Regular"):
    f = ImageFont.truetype(POLICE, taille)
    try:
        f.set_variation_by_name(poids)
    except Exception:
        pass
    return f


def lire_etat():
    try:
        return json.load(open(ETAT, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def ecrire_etat(e):
    with open(ETAT, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=1)


def get(url, binaire=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        d = r.read()
    return d if binaire else json.loads(d)


_CATALOGUE = {}


def catalogue(langue):
    """Parfums actifs EN STOCK avec photo, depuis la boutique publique (titres dans la langue de la story)."""
    if langue in _CATALOGUE:
        return _CATALOGUE[langue]
    base = "https://qosmi.be/nl" if langue == "nl" else "https://qosmi.be"
    out, page = [], 1
    while page <= 60:
        d = get("%s/products.json?limit=250&page=%d" % (base, page)).get("products") or []
        if not d:
            break
        for p in d:
            tags = [t.lower() for t in p.get("tags") or []]
            if not p.get("images") or "coffret" in (p.get("product_type") or "").lower() or any(
                    m in p["title"].lower() for m in ("refill", "recharge", "navulling", "miniature", "coffret", " set", "sample")):
                continue
            if not any(v.get("available") for v in p.get("variants") or []):
                continue
            out.append({"handle": p["handle"], "titre": p["title"], "marque": p.get("vendor") or "",
                        "photo": p["images"][0]["src"], "bon_plan": "bon-plan" in tags,
                        "testeur_seul": all("testeur" in (v.get("title") or "").lower() for v in p["variants"]),
                        "cree": p.get("created_at") or ""})
        page += 1
    _CATALOGUE[langue] = out
    return out


NOTES = json.load(open(os.path.join(RACINE, "config", "notes_fi.json"), encoding="utf-8")).get("parfums") or {}


def notes(handle, langue):
    n = (NOTES.get(handle) or {}).get("notes_" + langue) or {}
    return {k: n.get(k) or [] for k in ("tete", "coeur", "fond")}


def nom_court(p):
    """Nom du parfum sans la marque ni « eau de parfum pour femme »… : « Delina », « Erba Pura »."""
    t = p["titre"].split(" — ")[0].split(" – ")[0]
    if p["marque"] and t.lower().startswith(p["marque"].lower()):
        t = t[len(p["marque"]):].strip(" -–")
    for coupe in (" Eau de Parfum", " Eau de Toilette", " Extrait", " Parfum ", " Eau Fraîche", " Cologne", " Eau de Cologne", " Elixir"):
        i = t.lower().find(coupe.lower())
        if i > 1:
            t = t[:i]
            break
    return t.strip() or p["titre"]


def photo(url, cote):
    im = Image.open(io.BytesIO(get(url + ("&" if "?" in url else "?") + "width=1200", binaire=True))).convert("RGB")
    im = ImageOps.contain(im, (cote, cote), Image.LANCZOS)
    carre = Image.new("RGB", (cote, cote), BLANC)
    carre.paste(im, ((cote - im.width) // 2, (cote - im.height) // 2))
    return carre


def texte_centre(d, y, txt, f, couleur=NOIR, espacement=0, largeur=920):
    """Écrit un texte centré (retour à la ligne automatique) ; renvoie le y suivant."""
    lignes = []
    for para in txt.split("\n"):
        mots, cur = para.split(), ""
        for m in mots:
            essai = (cur + " " + m).strip()
            if d.textlength(essai, font=f) + espacement * len(essai) <= largeur:
                cur = essai
            else:
                lignes.append(cur)
                cur = m
        lignes.append(cur)
    hauteur = int(f.size * 1.22)
    for l in lignes:
        if espacement:
            larg = d.textlength(l, font=f) + espacement * (len(l) - 1)
            x = (W - larg) / 2
            for c in l:
                d.text((x, y), c, font=f, fill=couleur)
                x += d.textlength(c, font=f) + espacement
        else:
            d.text(((W - d.textlength(l, font=f)) / 2, y), l, font=f, fill=couleur)
        y += hauteur
    return y


def cadre(fond=GRIS):
    im = Image.new("RGB", (W, H), fond)
    d = ImageDraw.Draw(im)
    coul = BLANC if fond == NOIR else NOIR
    texte_centre(d, 250, "QOSMI", police(40, "Medium"), coul, espacement=16)
    return im, d


def bas(d, langue, fond=GRIS):
    texte_centre(d, H - 290, T[langue]["cta"].upper(), police(32, "Medium"), BLANC if fond == NOIR else DOUX, espacement=5)


def puce(d, y, txt, fond=NOIR, couleur=BLANC):
    f = police(30, "Medium")
    txt = txt.upper()
    larg = d.textlength(txt, font=f) + 4 * len(txt)
    x = (W - larg) / 2
    d.rectangle([x - 26, y - 14, x + larg + 22, y + 50], fill=fond)
    texte_centre(d, y, txt, f, couleur, espacement=4)
    return y + 100


def bloc_notes(d, y, n, langue, nmax=3):
    f_t, f_n = police(26, "Medium"), police(38, "Light")
    for k in ("tete", "coeur", "fond"):
        if not n[k]:
            continue
        texte_centre(d, y, T[langue][k].upper(), f_t, DOUX, espacement=5)
        y = texte_centre(d, y + 36, " · ".join(n[k][:nmax]), f_n) + 14
    return y


# ------------------------------------------------------------------ modèles
def v_parfum(p, langue, sur, chip=False, texte=None):
    im, d = cadre()
    y = 360
    y = puce(d, y, sur) if chip else texte_centre(d, y, sur.upper(), police(34, "Medium"), DOUX, espacement=6) + 40
    im.paste(photo(p["photo"], 620), (230, y))
    y += 655
    texte_centre(d, y, p["marque"].upper(), police(30, "Medium"), DOUX, espacement=6)
    y = texte_centre(d, y + 50, nom_court(p).upper(), police(68, "Medium"), largeur=940) + 16
    if texte:
        texte_centre(d, y + 20, texte, police(40, "Light"))
    else:
        bloc_notes(d, y + 10, notes(p["handle"], langue), langue, 3 if y < 1180 else 2)  # nom sur 2 lignes : notes plus courtes
    bas(d, langue)
    return im


def v_duel(a, b, langue):
    im, d = cadre()
    texte_centre(d, 420, T[langue]["duel"].upper(), police(68, "Medium"))
    for i, p in enumerate((a, b)):
        x = 60 + i * 500
        im.paste(photo(p["photo"], 460), (x, 620))
        texte_centre_col(d, x + 230, 1110, p["marque"].upper(), police(26, "Medium"), DOUX)
        texte_centre_col(d, x + 230, 1152, nom_court(p).upper(), police(42, "Medium"))
    f = police(40, "Medium")
    d.ellipse([540 - 50, 800, 540 + 50, 900], fill=NOIR)
    d.text((540 - d.textlength(T[langue]["ou"], font=f) / 2, 822), T[langue]["ou"], font=f, fill=BLANC)
    texte_centre(d, 1420, T[langue]["duel_bas"], police(42, "Light"))
    bas(d, langue)
    return im


def texte_centre_col(d, cx, y, txt, f, couleur=NOIR, largeur=440):
    mots, cur, lignes = txt.split(), "", []
    for m in mots:
        e = (cur + " " + m).strip()
        if d.textlength(e, font=f) <= largeur:
            cur = e
        else:
            lignes.append(cur)
            cur = m
    lignes.append(cur)
    for l in lignes[:3]:
        d.text((cx - d.textlength(l, font=f) / 2, y), l, font=f, fill=couleur)
        y += int(f.size * 1.2)
    return y


# Photos d'ambiance Pexels choisies à la main (config/images_ambiance.json, 21/11/2026) : clé de note par famille
AMBIANCE = json.load(open(os.path.join(RACINE, "config", "images_ambiance.json"), encoding="utf-8")).get("notes", {}) \
    if os.path.exists(os.path.join(RACINE, "config", "images_ambiance.json")) else {}
CLE_AMBIANCE = {"vanille": "vanille", "rose": "rose", "oud": "oud", "ambre": "ambre", "cuir": "cuir", "musc": "musc",
                "jasmin": "jasmin", "bergamote": "agrumes", "patchouli": "patchouli", "tabac": "tabac", "iris": "iris",
                "café": "cafe", "lavande": "lavande"}


def fond_ambiance(cle, larg, haut):
    """Photo d'ambiance recadrée (larg × haut), assombrie pour que le texte blanc se lise ; None si pas de photo."""
    a = AMBIANCE.get(cle)
    if not a:
        return None
    try:
        im = Image.open(io.BytesIO(get(a["url"] + "?auto=compress&cs=tinysrgb&w=1600", binaire=True))).convert("RGB")
    except Exception:
        return None
    im = ImageOps.fit(im, (larg, haut), Image.LANCZOS)
    voile = Image.new("RGB", (larg, haut), (0, 0, 0))
    return Image.blend(im, voile, 0.38)


def titre_famille(mot, langue):
    t = T[langue]["famille"] % mot
    return t.replace("de a", "d'a").replace("de e", "d'e").replace("de i", "d'i").replace("de o", "d'o").replace("de u", "d'u") \
        if langue == "fr" else t


def v_famille(ps, mot, langue, cle=None):
    im, d = cadre()
    fond = fond_ambiance(cle, W, 860) if cle else None
    if fond:  # photo d'ambiance en haut, titre en blanc dessus
        im.paste(fond, (0, 0))
        texte_centre(d, 250, "QOSMI", police(40, "Medium"), BLANC, espacement=16)
        texte_centre(d, 600, titre_famille(mot, langue).upper(), police(80, "Medium"), BLANC, largeur=960)
        y0 = 930
    else:
        texte_centre(d, 440, titre_famille(mot, langue).upper(), police(76, "Medium"), largeur=960)
        y0 = 700
    for i, p in enumerate(ps):
        x = 40 + i * 340
        im.paste(photo(p["photo"], 320), (x, y0))
        texte_centre_col(d, x + 160, y0 + 350, p["marque"].upper(), police(24, "Medium"), DOUX, largeur=310)
        texte_centre_col(d, x + 160, y0 + 390, nom_court(p).upper(), police(34, "Medium"), largeur=310)
    texte_centre(d, 1470 if fond else 1420, T[langue]["famille_bas"], police(42, "Light"))
    bas(d, langue)
    return im


def v_info(info, langue):
    im, d = cadre(NOIR)
    titre, txt = info[langue]
    y = texte_centre(d, 780, titre.upper(), police(84, "Medium"), BLANC, largeur=960) + 60
    texte_centre(d, y, txt, police(46, "Light"), BLANC)
    bas(d, langue, NOIR)
    return im


# ------------------------------------------------------------------ choix
def deja_vus(etat, jour, jours=30):
    lim = (jour - dt.timedelta(days=jours)).isoformat()
    return {h for v in etat.values() if v.get("date", "") >= lim for h in v.get("parfums", [])}


def fabriquer(jour, creneau, etat):
    """Renvoie (image, description) de la story du créneau."""
    langue = "fr" if jour.toordinal() % 2 == 0 else "nl"
    rang = (jour.toordinal() + (0 if creneau == "11:00" else 1)) % len(ORDRE[creneau])
    sorte = ORDRE[creneau][rang]
    graine = int(hashlib.md5(("%s %s" % (jour, creneau)).encode()).hexdigest(), 16)
    rnd = random.Random(graine)
    vus = deja_vus(etat, jour)
    cat = [p for p in catalogue(langue) if p["handle"] not in vus and not p["testeur_seul"]]
    avec_notes = [p for p in cat if any(notes(p["handle"], langue).values())]
    if sorte == "info":
        info = INFOS[(jour.toordinal() // 2) % len(INFOS)]
        return v_info(info, langue), {"sorte": sorte, "langue": langue, "titre": info[langue][0], "parfums": []}
    if sorte == "bon_plan":
        bp = [p for p in avec_notes if p["bon_plan"]] or [p for p in cat if p["bon_plan"]]
        if bp:
            p = rnd.choice(bp)
            return (v_parfum(p, langue, T[langue]["bon_plan"], chip=True, texte=T[langue]["bp_txt"]),
                    {"sorte": sorte, "langue": langue, "titre": p["titre"], "parfums": [p["handle"]]})
        sorte = "du_jour"
    if sorte == "nouveau":
        recents = sorted(avec_notes, key=lambda p: p["cree"], reverse=True)[:40]
        if recents:
            p = rnd.choice(recents)
            return (v_parfum(p, langue, T[langue]["nouveau"], chip=True),
                    {"sorte": sorte, "langue": langue, "titre": p["titre"], "parfums": [p["handle"]]})
        sorte = "du_jour"
    if sorte == "duel":
        a, b = rnd.sample(avec_notes, 2)
        return v_duel(a, b, langue), {"sorte": sorte, "langue": langue, "titre": a["titre"] + " / " + b["titre"],
                                      "parfums": [a["handle"], b["handle"]]}
    if sorte == "famille":
        fams = FAMILLES[:]
        rnd.shuffle(fams)
        for mot, fr, nl in fams:
            ps = [p for p in avec_notes if any(mot in x.lower() for x in sum(NOTES.get(p["handle"], {}).get("notes_fr", {}).values(), []))]
            if len(ps) >= 3:
                ps = rnd.sample(ps, 3)
                lib = fr if langue == "fr" else nl
                return v_famille(ps, lib, langue, CLE_AMBIANCE.get(mot)), {"sorte": sorte, "langue": langue, "titre": lib,
                                                    "parfums": [p["handle"] for p in ps]}
        sorte = "du_jour"
    p = rnd.choice(avec_notes or cat)
    sur = T[langue]["soir"] if sorte == "soir" else T[langue]["du_jour"]
    return v_parfum(p, langue, sur), {"sorte": sorte, "langue": langue, "titre": p["titre"], "parfums": [p["handle"]]}


# ------------------------------------------------------------------ envoi
def envoyer_image(im, nom):
    """Visuel dans les Fichiers Shopify (adresse publique pour Instagram)."""
    from shopify_api import Shopify
    import photos_adp as pa
    s = Shopify()
    u = pa.adresse_fichier(s, nom)
    if u:
        return u
    tmp = os.path.join("/tmp", nom)
    im.save(tmp, "JPEG", quality=92)
    u = pa.envoyer(s, tmp, alt="Qosmi · story")
    if not u:
        raise RuntimeError("visuel %s non envoyé dans Shopify" % nom)
    return u


def programmer(cle, url, cible, maintenant):
    import social_publier as sp
    comptes = sp.comptes_zernio(cle)
    if "instagram" not in comptes:
        raise SystemExit("Aucun compte Instagram relié dans Zernio.")
    acc, prof = comptes["instagram"]
    corps = {"content": "", "platforms": [{"platform": "instagram", "accountId": acc, "platformSpecificData": {"contentType": "story"}}],
             "mediaItems": [{"type": "image", "url": url}]}
    if prof:
        corps["profileId"] = prof
    if cible and cible > maintenant + dt.timedelta(minutes=2):
        corps["scheduledFor"] = cible.isoformat(timespec="seconds")
        corps["timezone"] = "Europe/Brussels"
    else:
        corps["publishNow"] = True
    r = sp.zernio("POST", "/posts", cle, corps)
    post = r.get("post", r) if isinstance(r, dict) else {}
    return post.get("_id") or post.get("id"), corps.get("scheduledFor", "maintenant")


def main():
    maintenant = dt.datetime.now(TZ)
    etat = lire_etat()
    if "--apercu" in sys.argv:
        n = int(sys.argv[sys.argv.index("--apercu") + 1]) if len(sys.argv) > sys.argv.index("--apercu") + 1 else 4
        os.makedirs(SORTIE, exist_ok=True)
        jour, faits, essai_etat = maintenant.date(), 0, dict(etat)
        while faits < n:
            for hm in CRENEAUX:
                if faits >= n:
                    break
                im, meta = fabriquer(jour, hm, essai_etat)
                nom = "story-%s-%s.jpg" % (jour.isoformat(), hm.replace(":", "h"))
                im.save(os.path.join(SORTIE, nom), "JPEG", quality=90)
                essai_etat["%s %s" % (jour, hm)] = dict(meta, date=jour.isoformat())
                print("%s %s : %s (%s) — %s" % (jour, hm, meta["sorte"], meta["langue"], meta["titre"]))
                faits += 1
            jour += dt.timedelta(days=1)
        return
    cle = os.environ.get("ZERNIO_API_KEY", "").strip()
    if not cle:
        print("ZERNIO_API_KEY absent : aucune story.")
        return
    if "--maintenant" in sys.argv:
        jour = maintenant.date()
        cle_e = "%s rattrapage-%s" % (jour, maintenant.strftime("%H%M"))
        im, meta = fabriquer(jour, "11:00", etat)  # un parfum (plus parlant qu'une info pour la toute première)
        url = envoyer_image(im, "qosmi-story-%s-%s.jpg" % (jour.isoformat(), maintenant.strftime("%H%M")))
        pid, quand = programmer(cle, url, None, maintenant)
        etat[cle_e] = dict(meta, date=jour.isoformat(), creneau="maintenant", zernio=pid, programme=quand, img=url)
        ecrire_etat(etat)
        print("Story publiée maintenant : %s (%s) — %s" % (meta["sorte"], meta["langue"], meta["titre"]))
        return
    n = 0
    for k in range(JOURS_AVANCE + 1):
        jour = (maintenant + dt.timedelta(days=k)).date()
        for hm in CRENEAUX:
            h, m = map(int, hm.split(":"))
            cible = dt.datetime.combine(jour, dt.time(h, m), tzinfo=TZ)
            cle_e = "%s %s" % (jour, hm)
            if cible < maintenant + dt.timedelta(minutes=10) or cle_e in etat:
                continue
            im, meta = fabriquer(jour, hm, etat)
            url = envoyer_image(im, "qosmi-story-%s-%s.jpg" % (jour.isoformat(), hm.replace(":", "h")))
            pid, quand = programmer(cle, url, cible, maintenant)
            etat[cle_e] = dict(meta, date=jour.isoformat(), creneau=hm, zernio=pid, programme=quand, img=url)
            ecrire_etat(etat)
            n += 1
            print("Story programmée : %s %s → %s (%s) — %s" % (jour, hm, meta["sorte"], meta["langue"], meta["titre"]), flush=True)
    print("%d story(s) programmée(s) d'avance." % n)


if __name__ == "__main__":
    main()
