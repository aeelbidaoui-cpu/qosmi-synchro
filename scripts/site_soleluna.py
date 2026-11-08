#!/usr/bin/env python3
"""Qosmi : remplace le catalogue Wholesale-Fragrances du site Shopify par le catalogue SoleLuna.

Décision d'Amine du 03/11/2026 : « Remplacer par SoleLuna » (le site Maison Sillage est abandonné).

  python3 scripts/site_soleluna.py --preparer   → construit base/site_catalogue.csv à partir de la liste SoleLuna
                                                  (stock du dépôt conservé), sans rien envoyer à Shopify
  python3 scripts/site_soleluna.py --archiver   → archive sur Shopify les fiches Wholesale-Fragrances
                                                  (ARCHIVÉES, pas supprimées : récupérables d'un clic)
  python3 scripts/site_soleluna.py --basculer   → préparer, puis confirmation, archiver, charger SoleLuna (lanceur 27)

Source : base/soleluna_liste.csv, la liste brute du compte wholesale-perfumes.eu, écrite par
« telecharger.py PERFUMEWHOLESALE ». Photos : Wholesale-Fragrances par EAN (autorisées pour le site Qosmi le 30/10/2026).
Les fiches partent en BROUILLON. Les PRIX SONT PROVISOIRES (à discuter avec Amine) : (achat + envoi + bénéfice) × 1,21,
arrondi au ,90 supérieur, paramètres dans config/site.json.
Rien sur Shopify ne porte le nom du fournisseur, son code interne ou un coût (le coût va dans « coût par article »,
visible seulement dans l'admin).
"""
import csv, glob, html, json, math, os, re, shutil, sys, time, unicodedata

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
BASE = os.path.join(RACINE, "base")
SOURCE = os.path.join(BASE, "soleluna_liste.csv")
CATALOGUE = os.path.join(BASE, "site_catalogue.csv")
ANCIEN = os.path.join(BASE, "site_catalogue_wholesalefragrances.csv")  # sauvegarde du catalogue d'avant
SITE = os.path.join(RACINE, "config", "site.json")
RAPPORTS = os.path.join(RACINE, "rapports")

COLONNES = ["handle", "sku", "ean", "source", "titre_fr", "titre_nl", "desc_fr", "desc_nl", "marque",
            "type_fr", "type_nl", "tags", "prix", "stock", "cout_ht", "photo_source"]
INTERDITS = ["soleluna", "wholesale", "perfume wholesale", "prodejparfemu", "premierproducts", "grossiste",
             "fournisseur", "trista", "brasty", "stockperfume"]

GENRES = {"W": ("pour femme", "voor dames", "femme"), "M": ("pour homme", "voor heren", "homme"),
          "UNI": ("mixte", "unisex", "mixte"), "K": ("pour enfant", "voor kinderen", "enfant")}
PARFUMS = {  # TYPE SoleLuna → (FR, NL)
    "eau de parfum": ("Eau de Parfum", "Eau de Parfum"), "eau de toilette": ("Eau de Toilette", "Eau de Toilette"),
    "eau de cologne": ("Eau de Cologne", "Eau de Cologne"), "perfume": ("Parfum", "Parfum"),
    "perfume extract": ("Extrait de Parfum", "Extrait de Parfum"), "extrait de parfum": ("Extrait de Parfum", "Extrait de Parfum"),
    "eau fraîche": ("Eau Fraîche", "Eau Fraîche"), "eau fraiche": ("Eau Fraîche", "Eau Fraîche"),
}
SOINS = {  # TYPE SoleLuna → (FR, NL) ; les types inconnus restent tels quels
    "shampoo": ("Shampooing", "Shampoo"), "conditioner": ("Après-shampooing", "Conditioner"),
    "hair mask": ("Masque capillaire", "Haarmasker"), "hair mist": ("Parfum pour cheveux", "Haarparfum"),
    "body lotion": ("Lait corporel", "Bodylotion"), "body milk": ("Lait corporel", "Bodymilk"),
    "body balm": ("Baume corporel", "Bodybalsem"), "body cream": ("Crème corporelle", "Bodycrème"),
    "body spray": ("Brume parfumée", "Bodymist"), "body mist": ("Brume parfumée", "Bodymist"),
    "shower gel": ("Gel douche", "Douchegel"), "soap": ("Savon", "Zeep"), "deodorant": ("Déodorant", "Deodorant"),
    "aftershave": ("Après-rasage", "Aftershave"), "after shave": ("Après-rasage", "Aftershave"),
    "hand cream": ("Crème pour les mains", "Handcrème"), "face cream": ("Crème visage", "Gezichtscrème"),
    "cream": ("Crème", "Crème"), "serum": ("Sérum", "Serum"), "lipstick": ("Rouge à lèvres", "Lippenstift"),
    "mascara": ("Mascara", "Mascara"), "candle": ("Bougie parfumée", "Geurkaars"),
}
CATEGORIES = [  # (mots dans le TYPE, FR, NL) — le premier qui correspond l'emporte
    (r"hair|shampoo|conditioner", "Cheveux", "Haarverzorging"),
    (r"deodorant|deo\b", "Déodorants", "Deodorants"),
    (r"after ?shave|shaving|beard", "Homme", "Heren"),
    (r"lip|eye|brow|mascara|make|foundation|powder|blush|nail|pallet|palette|concealer|primer|liner", "Maquillage", "Make-up"),
    (r"face|serum|mask|cleans|toner|eye cream", "Soins du visage", "Gezichtsverzorging"),
    (r"body|shower|bath|soap|hand|lotion|balm|scrub|oil", "Soins du corps", "Lichaamsverzorging"),
    (r"sun|tan|bronz", "Solaires et autobronzants", "Zon en zelfbruiners"),
    (r"candle|diffuser|home|car", "Maison", "Wonen"),
]
SIGLES = {"DKNY", "NARS", "MAC", "CK", "BVLGARI", "YSL", "MFK", "HFC", "DSQUARED2", "KKW", "AHC", "TIRTIR", "COSRX"}


def reglages():
    try:
        with open(SITE, encoding="utf-8") as f:
            s = json.load(f)
    except FileNotFoundError:
        s = {}
    p = s.get("prix_provisoires") or {}
    return {"envoi_eur": float(p.get("envoi_eur", 2)), "marge_eur": float(p.get("marge_eur", 5)),
            "emballage_eur": float(p.get("emballage_eur", 0)), "marge_sans_concurrent_eur": float(p.get("marge_sans_concurrent_eur", p.get("marge_eur", 5))),
            "marge_max_concurrent_eur": float(p.get("marge_max_concurrent_eur", 0)),
            "concurrent": concurrent(),
            "paiement_pct": float(p.get("paiement_pct", 0)), "paiement_fixe": float(p.get("paiement_fixe", 0)),
            "tva": float(p.get("tva", 0.21)), "delai_fr": s.get("delai_dropship_fr", "4 à 7 jours ouvrables"),
            "delai_nl": s.get("delai_dropship_nl", "4 tot 7 werkdagen")}


def nombre(v):
    try:
        return float(str(v or "").replace(",", ".").strip())
    except ValueError:
        return 0.0


def propre(s):
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()


def nom_marque(b):
    m = propre(b)
    if m != m.upper() or m in SIGLES or len(m) <= 3:
        return m
    return re.sub(r"(^|[\s\-&'.])(\w)", lambda x: x.group(1) + x.group(2).upper(), m.lower())


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def contenance(v):
    v = propre(v)
    m = re.match(r"^(\d+(?:[.,]\d+)?)\s*(ml|g|pcs|ks)$", v, re.I)
    if not m:
        return v
    n = ("%g" % float(m.group(1).replace(",", "."))).replace(".", ",")
    return n + " " + {"ks": "pcs"}.get(m.group(2).lower(), m.group(2).lower())


def concurrent():
    """Prix relevés chez le concurrent de référence (config/deloox.json, {EAN sans zéros de tête: [prix TTC, dispo, date]}).
    Fichier interne : il ne sort jamais du dépôt (ni Shopify, ni Google)."""
    chemin = os.path.join(RACINE, "config", "deloox.json")
    try:
        d = json.load(open(chemin, encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}
    return {k: v for k, v in (d.get("par_ean") or {}).items() if v and v[0] and v[1] == "InStock"}


def arrondi_90_haut(ttc):
    cents = math.ceil(ttc * 100 - 1e-6)
    euros = cents // 100
    if euros * 100 + 90 < cents:
        euros += 1
    return euros + 0.90


def prix_provisoire(achat, r, ean=""):
    """Règle d'Amine du 08/11/2026 (livraison client 2,95 € ; colis SoleLuna de 15 € pour ~5 parfums, soit envoi_eur 3 €) :
    - coût = achat + envoi + emballage ; les frais de paiement (% du TTC + fixe) sont inclus pour que le bénéfice reste entier ;
    - plancher = coût + frais + marge_eur (5 € net minimum), × 1,21, arrondi au ,90 supérieur ;
    - si le concurrent de référence vend ce même EAN (en stock) : le prix en ,90 juste sous le sien, jamais sous le plancher,
      et (choix d'Amine du 08/11/2026) jamais au-dessus du prix à marge_max_concurrent_eur (10 €) : si on est déjà nettement
      moins cher que lui, on le reste ;
    - sinon : coût + frais + marge_sans_concurrent_eur (7 €)."""
    k = 1 / (1 + r["tva"]) - r.get("paiement_pct", 0)
    base = achat + r["envoi_eur"] + r.get("emballage_eur", 0) + r.get("paiement_fixe", 0)
    plancher = arrondi_90_haut((base + r["marge_eur"]) / k)
    ref = (r.get("concurrent") or {}).get((ean or "").lstrip("0"))
    if ref:
        d = float(ref[0])
        cible = math.floor(d - 0.90 + 1e-9) + 0.90
        if cible >= d - 1e-9:
            cible -= 1
        if r.get("marge_max_concurrent_eur"):
            cible = min(cible, arrondi_90_haut((base + r["marge_max_concurrent_eur"]) / k))
        return max(round(cible, 2), plancher)
    return arrondi_90_haut((base + r.get("marge_sans_concurrent_eur", r["marge_eur"])) / k)


def photos_wf():
    """EAN (sans zéros de tête) → photo Wholesale-Fragrances, d'après sa dernière liste."""
    ph = {}
    wf = sorted(glob.glob(os.path.join(RACINE, "stocklists", "WHOLESALEFRAGRANCES", "*.csv")))
    if wf:
        with open(wf[-1], encoding="utf-8") as f:
            for l in csv.DictReader(f, delimiter=";"):
                for k in ("EAN", "EAN2"):
                    e = re.sub(r"\D", "", l.get(k) or "").lstrip("0")
                    img = (l.get("IMAGE") or "").strip()
                    if e and img and os.path.splitext(img.split("?")[0])[1]:
                        ph.setdefault(e, img)
    # le catalogue d'avant garde aussi les photos déjà validées
    for chemin in (ANCIEN, CATALOGUE):
        if os.path.exists(chemin):
            with open(chemin, encoding="utf-8") as f:
                for l in csv.DictReader(f, delimiter=";"):
                    e = (l.get("ean") or "").lstrip("0")
                    if e and l.get("photo_source"):
                        ph.setdefault(e, l["photo_source"])
            break
    return ph


def lire_source(chemin):
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        texte = f.read()
    lignes = list(csv.reader(texte.replace("\r\n", "\n").replace("\r", "\n").splitlines(), delimiter=";"))
    tete = [h.strip().upper() for h in lignes[0]]
    return [dict(zip(tete, [c.strip() for c in l])) for l in lignes[1:] if len(l) >= len(tete) - 1]


def fiche(l, r, photos):
    marque = nom_marque(l.get("BRAND"))
    titre = propre(l.get("TITLE"))
    if titre.lower().startswith(marque.lower() + " "):
        titre = titre[len(marque) + 1:]
    t = propre(l.get("TYPE"))
    cont = contenance(l.get("VOLUME"))
    g_fr, g_nl, g_cle = GENRES.get((l.get("SEX") or "").upper(), ("", "", ""))
    coffret = bool(propre(l.get("SET")))
    contenu = propre(l.get("SET"))
    testeur = (l.get("TESTER") or "").strip() == "1"
    abime = bool(propre(l.get("DAMAGED")))
    teinte = propre(l.get("SHADE"))
    parfum = PARFUMS.get(t.lower())
    if parfum:
        type_fr, type_nl = parfum
    else:
        type_fr, type_nl = SOINS.get(t.lower(), (t, t))
    # titres
    if coffret:
        t_fr = "%s %s — coffret" % (marque, titre)
        t_nl = "%s %s — geschenkset" % (marque, titre)
    elif parfum:
        t_fr = "%s %s — %s %s%s" % (marque, titre, type_fr, g_fr, (" " + cont) if cont else "")
        t_nl = "%s %s — %s %s%s" % (marque, titre, type_nl, g_nl, (" " + cont) if cont else "")
    else:
        t_fr = "%s %s — %s%s" % (marque, titre, type_fr, (" " + cont) if cont else "")
        t_nl = "%s %s — %s%s" % (marque, titre, type_nl, (" " + cont) if cont else "")
    if teinte:
        t_fr += " — teinte %s" % teinte
        t_nl += " — kleur %s" % teinte
    if testeur:
        t_fr += " (testeur)"
        t_nl += " (tester)"
    if abime:
        t_fr += " (boîte abîmée)"
        t_nl += " (beschadigde doos)"
    # catégorie
    if coffret:
        cat_fr, cat_nl = "Coffrets", "Geschenksets"
    elif testeur and parfum:
        cat_fr, cat_nl = "Testeurs", "Testers"
    elif parfum:
        cat_fr, cat_nl = {"femme": ("Parfums femme", "Damesparfums"), "homme": ("Parfums homme", "Herenparfums"),
                          "mixte": ("Parfums mixtes", "Unisex parfums"),
                          "enfant": ("Parfums enfants", "Kinderparfums")}.get(g_cle, ("Parfums", "Parfums"))
    else:
        cat_fr, cat_nl = next(((fr, nl) for m, fr, nl in CATEGORIES if re.search(m, t, re.I)),
                              ("Soins et beauté", "Verzorging"))
    # descriptions (rédigées par Qosmi, aucun texte du fournisseur)
    if coffret:
        d_fr = "Coffret %s de %s. Contenu : %s. " % (titre, marque, contenu)
        d_nl = "Geschenkset %s van %s. Inhoud: %s. " % (titre, marque, contenu)
    elif parfum:
        d_fr = "%s %s de %s, %s%s. " % (type_fr, titre, marque, "un parfum mixte" if g_cle == "mixte" else g_fr,
                                        (", flacon de " + cont) if cont else "")
        d_nl = "%s %s van %s, %s%s. " % (type_nl, titre, marque, "een unisex geur" if g_cle == "mixte" else g_nl,
                                         (", flacon van " + cont) if cont else "")
    else:
        d_fr = "%s %s de %s%s. " % (type_fr, titre, marque, (", " + cont) if cont else "")
        d_nl = "%s %s van %s%s. " % (type_nl, titre, marque, (", " + cont) if cont else "")
    if teinte:
        d_fr += "Teinte : %s. " % teinte
        d_nl += "Kleur: %s. " % teinte
    if testeur:
        d_fr += "Testeur : le même produit que la version vendue en boutique, dans un emballage simple, souvent sans bouchon. "
        d_nl += "Tester: hetzelfde product als in de winkel, in een eenvoudige verpakking, vaak zonder dop. "
    if abime:
        d_fr += "Boîte d'origine abîmée : le produit lui-même est neuf et intact. "
        d_nl += "Originele doos beschadigd: het product zelf is nieuw en onbeschadigd. "
    d_fr += "Produit authentique, neuf. Livraison partout en Belgique en %s." % r["delai_fr"]
    d_nl += "Origineel en nieuw product. Levering in heel België binnen %s." % r["delai_nl"]
    t_fr, t_nl = re.sub(r"\s+", " ", t_fr).replace(" ,", ","), re.sub(r"\s+", " ", t_nl)
    achat = nombre(l.get("PRICE"))
    ean = re.sub(r"\D", "", l.get("EAN") or "")
    tags = [cat_fr, marque] + (["boite-abimee"] if abime else [])
    return {"handle": "%s-%s" % (slug(t_fr)[:200], ean), "sku": "QS-%s" % re.sub(r"\D", "", l.get("ID") or ""),
            "ean": ean, "source": "dropship", "titre_fr": t_fr, "titre_nl": t_nl,
            "desc_fr": "<p>%s</p>" % html.escape(d_fr.strip(), quote=False),
            "desc_nl": "<p>%s</p>" % html.escape(d_nl.strip(), quote=False),
            "marque": marque, "type_fr": cat_fr, "type_nl": cat_nl, "tags": ", ".join(tags),
            "prix": "%.2f" % prix_provisoire(achat, r, ean), "stock": str(max(0, int(nombre(l.get("STOCK"))))),
            "cout_ht": "%.2f" % (achat + r["envoi_eur"] + r.get("emballage_eur", 0)), "photo_source": photos.get(ean.lstrip("0"), "")}


def preparer(source=SOURCE, sortie=CATALOGUE):
    if not os.path.exists(source):
        sys.exit("Liste SoleLuna brute absente (base/soleluna_liste.csv) : lance d'abord « telecharger.py PERFUMEWHOLESALE ».")
    age_h = (time.time() - os.path.getmtime(source)) / 3600
    r = reglages()
    lignes = lire_source(source)
    if "EAN" not in (lignes[0] if lignes else {}):
        sys.exit("Format de la liste SoleLuna inattendu.")
    if os.path.exists(CATALOGUE) and not os.path.exists(ANCIEN) and sortie == CATALOGUE:
        shutil.copy2(CATALOGUE, ANCIEN)  # une seule fois : le catalogue Wholesale-Fragrances d'origine
    depot = []
    if os.path.exists(ANCIEN):
        with open(ANCIEN, encoding="utf-8") as f:
            depot = [l for l in csv.DictReader(f, delimiter=";") if l["source"] == "depot"]
    eans_depot = {l["ean"].lstrip("0") for l in depot}
    photos = photos_wf()
    garde, ecart = {}, {"sans EAN": 0, "prix nul": 0, "déjà en stock au dépôt": 0, "doublon plus cher": 0}
    for l in lignes:
        ean = re.sub(r"\D", "", l.get("EAN") or "")
        if len(ean) < 8:
            ecart["sans EAN"] += 1
            continue
        if nombre(l.get("PRICE")) <= 0:
            ecart["prix nul"] += 1
            continue
        if ean.lstrip("0") in eans_depot:
            ecart["déjà en stock au dépôt"] += 1
            continue
        cle = (ean, (l.get("TESTER") or "").strip() == "1", bool(propre(l.get("DAMAGED"))))
        if cle in garde and nombre(garde[cle]["PRICE"]) <= nombre(l.get("PRICE")):
            ecart["doublon plus cher"] += 1
            continue
        garde[cle] = l
    fiches = [fiche(l, r, photos) for l in garde.values()]
    vus = set()
    for x in fiches:  # handles uniques
        h, i = x["handle"], 2
        while x["handle"] in vus:
            x["handle"] = "%s-%d" % (h, i)
            i += 1
        vus.add(x["handle"])
    # contrôle de confidentialité : rien de ce qui part sur Shopify ne nomme un fournisseur
    for x in fiches:
        texte = " ".join(x[c] for c in ("handle", "titre_fr", "titre_nl", "desc_fr", "desc_nl", "marque", "tags")).lower()
        for m in INTERDITS:
            if m in texte and m not in x["marque"].lower():
                sys.exit("ARRÊT : « %s » apparaît dans la fiche %s — rien n'a été écrit." % (m, x["sku"]))
    tout = depot + sorted(fiches, key=lambda x: (x["marque"].lower(), x["titre_fr"].lower()))
    with open(sortie, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(tout)
    n_ph = sum(1 for x in fiches if x["photo_source"])
    print("Liste SoleLuna lue : %d lignes (téléchargée il y a %.1f h)." % (len(lignes), age_h))
    print("Catalogue Qosmi préparé : %d fiches = %d du dépôt (inchangées) + %d SoleLuna." % (len(tout), len(depot), len(fiches)))
    print("  dont %d avec photo, %d testeurs, %d boîtes abîmées, %d coffrets, %d en stock chez le fournisseur."
          % (n_ph, sum("(testeur)" in x["titre_fr"] for x in fiches), sum("boite-abimee" in x["tags"] for x in fiches),
             sum(x["type_fr"] == "Coffrets" for x in fiches), sum(int(x["stock"]) > 0 for x in fiches)))
    print("  écartées : " + ", ".join("%s %d" % (k, v) for k, v in ecart.items()))
    print("  PRIX PROVISOIRES : (achat + %.2f € envoi + %.2f €) × %.2f, arrondi au ,90." % (r["envoi_eur"], r["marge_eur"], 1 + r["tva"]))
    return len(depot), fiches


def archiver():
    """Passe en ARCHIVÉ sur Shopify les fiches du catalogue Wholesale-Fragrances qui ne sont plus au catalogue."""
    import json as _j
    import urllib.request
    from shopify_api import Shopify
    import site_charger as sc
    if not os.path.exists(ANCIEN):
        sys.exit("Sauvegarde du catalogue Wholesale-Fragrances absente : lance d'abord --preparer.")
    with open(ANCIEN, encoding="utf-8") as f:
        anciens = {l["handle"] for l in csv.DictReader(f, delimiter=";") if l["source"] == "dropship"}
    with open(CATALOGUE, encoding="utf-8") as f:
        nouveaux = {l["handle"] for l in csv.DictReader(f, delimiter=";")}
    a_archiver_h = anciens - nouveaux
    s = Shopify()
    d = s.gql("""mutation($q: String!) { bulkOperationRunQuery(query: $q) { bulkOperation { id status } userErrors { message } } }""",
              {"q": "{ products { edges { node { id handle status } } } }"})["bulkOperationRunQuery"]
    if d["userErrors"]:
        sys.exit("Lecture des fiches Shopify refusée : %s" % d["userErrors"])
    b = sc.attendre(s, d["bulkOperation"]["id"], "lecture-fiches")
    if not b.get("url"):
        sys.exit("Lecture des fiches Shopify impossible (%s)." % b.get("errorCode"))
    os.makedirs(RAPPORTS, exist_ok=True)
    chemin = os.path.join(RAPPORTS, "site_fiches_shopify.jsonl")
    urllib.request.urlretrieve(b["url"], chemin)
    cibles = []
    for l in open(chemin, encoding="utf-8"):
        p = _j.loads(l)
        if p.get("handle") in a_archiver_h and p.get("status") != "ARCHIVED":
            cibles.append(p["id"])
    sc.journal("Fiches Wholesale-Fragrances à archiver : %d" % len(cibles))
    if not cibles:
        return
    envoi = os.path.join(RAPPORTS, "site_archivage_envoi.jsonl")
    with open(envoi, "w", encoding="utf-8") as f:
        for pid in cibles:
            f.write(_j.dumps({"product": {"id": pid, "status": "ARCHIVED"}}) + "\n")
    with open(os.path.join(RAPPORTS, "site_archivage_ids_%s.txt" % time.strftime("%Y-%m-%d_%Hh%M")), "w") as f:
        f.write("\n".join(cibles) + "\n")  # pour les remettre en brouillon si besoin
    op = sc.lancer_mutation(s, sc.M_MAJ, envoi, "archivage")
    sc.bilan_resultats(sc.attendre(s, op, "archivage"), "archivage")


def basculer():
    n_depot, fiches = preparer()
    print()
    print("Étapes suivantes sur Shopify :")
    print("  1. les fiches Wholesale-Fragrances passent en ARCHIVÉ (pas supprimées, récupérables) ;")
    print("  2. les %d fiches SoleLuna sont créées en BROUILLON (invisibles des clients), puis traduites en NL ;" % len(fiches))
    print("  3. les %d fiches du dépôt sont renvoyées telles quelles." % n_depot)
    rep = input("Tape OUI pour lancer : ").strip()
    if rep != "OUI":
        print("Annulé : rien n'a été envoyé à Shopify (le catalogue préparé reste dans base/site_catalogue.csv).")
        return
    archiver()
    import site_charger
    site_charger.charger()


if __name__ == "__main__":
    if "--preparer" in sys.argv:
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        preparer(*(args[:2]))
    elif "--archiver" in sys.argv:
        archiver()
    elif "--basculer" in sys.argv:
        basculer()
    else:
        print(__doc__)
