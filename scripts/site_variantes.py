#!/usr/bin/env python3
"""Qosmi : une seule fiche par parfum, avec ses formats en variantes (30 ml / 50 ml / 100 ml / 100 ml – testeur…).

Demande d'Amine du 04/11/2026. Remplace les fiches SoleLuna « un format = une fiche » créées le 03/11.

  python3 scripts/site_variantes.py --preparer   → construit base/site_produits.json + base/site_catalogue.csv
                                                   (une ligne par variante), sans rien envoyer à Shopify
  python3 scripts/site_variantes.py --basculer   → préparer, confirmation « OUI », envoi (lanceur 28)

Regroupement : même marque + même nom + même type (Eau de Parfum, Shampooing…) + même genre.
  - option « Format » / « Inhoud » : contenance, + « testeur », + « boîte abîmée » ;
  - option « Teinte » / « Kleur » quand le produit en a (maquillage, colorations) ;
  - les coffrets restent chacun sur leur fiche ;
  - deux lignes identiques (même format, même teinte) : on garde la moins chère.
Sur Shopify, chaque fiche groupée REPREND une fiche existante du 03/11 (pas de doublon) ; les autres fiches
du 03/11 devenues inutiles sont ARCHIVÉES (récupérables). Tout reste en BROUILLON. Prix PROVISOIRES par variante.
Les fiches du dépôt ne sont pas touchées.
"""
import csv, html, json, os, re, sys, time
from collections import defaultdict

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import site_soleluna as sl  # noqa: E402

PRODUITS = os.path.join(sl.BASE, "site_produits.json")
V1 = os.path.join(sl.BASE, "site_catalogue_soleluna_v1.csv")  # fiches « un format = une fiche » du 03/11
COLONNES = sl.COLONNES + ["groupe", "format_fr", "format_nl", "teinte"]

sl.SOINS.update({
    "day cream": ("Crème de jour", "Dagcrème"), "night skin cream": ("Crème de nuit", "Nachtcrème"),
    "skin serum": ("Sérum", "Serum"), "makeup": ("Fond de teint", "Foundation"), "face mask": ("Masque visage", "Gezichtsmasker"),
    "hair color": ("Coloration", "Haarkleuring"), "sun body lotion": ("Lait solaire", "Zonnemelk"),
    "facial lotion and spray": ("Lotion visage", "Gezichtslotion"), "face sun care": ("Protection solaire visage", "Zonnebescherming gezicht"),
    "hair spray": ("Laque", "Haarlak"), "eye cream": ("Crème contour des yeux", "Oogcrème"),
    "leave-in hair care": ("Soin sans rinçage", "Leave-in verzorging"), "toothpaste": ("Dentifrice", "Tandpasta"),
    "hair serum": ("Sérum capillaire", "Haarserum"), "eye shadow": ("Fard à paupières", "Oogschaduw"),
    "dry shampoo": ("Shampooing sec", "Droogshampoo"), "lip balm": ("Baume à lèvres", "Lippenbalsem"),
    "hair oils and serum": ("Huile capillaire", "Haarolie"), "cleansing gel": ("Gel nettoyant", "Reinigingsgel"),
    "for definition and hair styling": ("Coiffant", "Styling"), "hair gel": ("Gel coiffant", "Haargel"),
    "antiperspirant": ("Anti-transpirant", "Anti-transpirant"), "hair volume": ("Soin volume", "Volumeverzorging"),
    "aftershave water": ("Après-rasage", "Aftershave"), "aftershave balm": ("Baume après-rasage", "Aftershave balsem"),
})

GROUPE_RE = re.compile(r"[^a-z0-9]+")


def cle_groupe(l):
    if sl.propre(l.get("SET")):  # un coffret = sa propre fiche
        return ("coffret", sl.propre(l.get("ID")))
    return (sl.nom_marque(l.get("BRAND")).lower(), GROUPE_RE.sub(" ", sl.propre(l.get("TITLE")).lower()).strip(),
            sl.propre(l.get("TYPE")).lower(), (l.get("SEX") or "").upper())


def ml(v):
    m = re.match(r"^(\d+(?:[.,]\d+)?)", sl.propre(v))
    return float(m.group(1).replace(",", ".")) if m else 0.0


def format_de(l):
    vol = sl.contenance(l.get("VOLUME")) or ""
    fr, nl = (vol or "Taille unique"), (vol or "Standaard")
    if (l.get("TESTER") or "").strip() == "1":
        fr += " – testeur"
        nl += " – tester"
    if sl.propre(l.get("DAMAGED")):
        fr += " – boîte abîmée"
        nl += " – beschadigde doos"
    return fr, nl


def joli_liste(xs, et):
    xs = list(dict.fromkeys(xs))
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " " + et + " " + xs[-1]


def produit(lignes, r, photos):
    """Une fiche Qosmi (titre, description, catégorie…) + ses variantes, à partir des lignes SoleLuna d'un groupe."""
    base = sl.fiche(lignes[0], r, photos)  # catégorie, marque… (fiche d'un format, réutilisée)
    l0 = lignes[0]
    marque = sl.nom_marque(l0.get("BRAND"))
    titre = sl.propre(l0.get("TITLE"))
    if titre.lower().startswith(marque.lower() + " "):
        titre = titre[len(marque) + 1:]
    t = sl.propre(l0.get("TYPE"))
    parfum = sl.PARFUMS.get(t.lower())
    type_fr, type_nl = parfum or sl.SOINS.get(t.lower(), (t, t))
    g_fr, g_nl, g_cle = sl.GENRES.get((l0.get("SEX") or "").upper(), ("", "", ""))
    coffret = bool(sl.propre(l0.get("SET")))
    testeurs = any((l.get("TESTER") or "").strip() == "1" for l in lignes)
    abimes = any(sl.propre(l.get("DAMAGED")) for l in lignes)
    teintes = any(sl.propre(l.get("SHADE")) for l in lignes)
    # variantes, triées : contenance, puis normal < testeur < boîte abîmée, puis teinte
    lignes = sorted(lignes, key=lambda l: (ml(l.get("VOLUME")), (l.get("TESTER") or "") == "1",
                                           bool(sl.propre(l.get("DAMAGED"))), sl.propre(l.get("SHADE"))))
    if coffret:
        t_fr, t_nl = base["titre_fr"], base["titre_nl"]
    elif parfum:
        t_fr = "%s %s — %s %s" % (marque, titre, type_fr, g_fr)
        t_nl = "%s %s — %s %s" % (marque, titre, type_nl, g_nl)
    else:
        t_fr = "%s %s — %s" % (marque, titre, type_fr)
        t_nl = "%s %s — %s" % (marque, titre, type_nl)
    vols = [sl.contenance(l.get("VOLUME")) for l in lignes if sl.contenance(l.get("VOLUME"))]
    if coffret:
        d_fr, d_nl = base["desc_fr"], base["desc_nl"]
    else:
        if parfum:
            d_fr = "%s %s de %s, %s." % (type_fr, titre, marque, "un parfum mixte" if g_cle == "mixte" else g_fr)
            d_nl = "%s %s van %s, %s." % (type_nl, titre, marque, "een unisex geur" if g_cle == "mixte" else g_nl)
        else:
            d_fr = "%s %s de %s." % (type_fr, titre, marque)
            d_nl = "%s %s van %s." % (type_nl, titre, marque)
        if len(set(vols)) > 1:
            d_fr += " Disponible en %s." % joli_liste(vols, "et")
            d_nl += " Verkrijgbaar in %s." % joli_liste(vols, "en")
        elif vols and parfum:
            d_fr += " Flacon de %s." % vols[0]
            d_nl += " Flacon van %s." % vols[0]
        if teintes:
            d_fr += " Plusieurs teintes au choix."
            d_nl += " Verschillende kleuren beschikbaar."
        if testeurs:
            d_fr += (" Format « testeur » : le même produit que la version vendue en boutique, dans un emballage simple,"
                     " souvent sans bouchon.")
            d_nl += " Formaat „tester”: hetzelfde product als in de winkel, in een eenvoudige verpakking, vaak zonder dop."
        if abimes:
            d_fr += " Format « boîte abîmée » : boîte d'origine abîmée, le produit lui-même est neuf et intact."
            d_nl += " Formaat „beschadigde doos”: originele doos beschadigd, het product zelf is nieuw en onbeschadigd."
        d_fr += " Produit authentique, neuf. Livraison partout en Belgique en %s." % r["delai_fr"]
        d_nl += " Origineel en nieuw product. Levering in heel België binnen %s." % r["delai_nl"]
        d_fr = "<p>%s</p>" % html.escape(d_fr.strip(), quote=False)
        d_nl = "<p>%s</p>" % html.escape(d_nl.strip(), quote=False)
    t_fr, t_nl = re.sub(r"\s+", " ", t_fr).strip(), re.sub(r"\s+", " ", t_nl).strip()
    cat_fr, cat_nl = base["type_fr"], base["type_nl"]
    if cat_fr == "Testeurs":  # la catégorie suit le genre ; « testeur » devient une variante + une étiquette
        cat_fr, cat_nl = {"femme": ("Parfums femme", "Damesparfums"), "homme": ("Parfums homme", "Herenparfums"),
                          "mixte": ("Parfums mixtes", "Unisex parfums"),
                          "enfant": ("Parfums enfants", "Kinderparfums")}.get(g_cle, ("Parfums", "Parfums"))
    tags = [cat_fr, marque] + (["Testeurs"] if testeurs else []) + (["boite-abimee"] if abimes else [])
    variantes, vus = [], {}
    for l in lignes:
        f_fr, f_nl = format_de(l)
        teinte = sl.propre(l.get("SHADE")) or ("—" if teintes else "")
        cle = (f_fr, teinte)
        if cle in vus:  # même format, même teinte : on garde la moins chère
            if sl.nombre(l.get("PRICE")) >= sl.nombre(vus[cle]["_achat"]):
                continue
            variantes.remove(vus[cle])
        v = sl.fiche(l, r, photos)
        v.update({"format_fr": f_fr, "format_nl": f_nl, "teinte": teinte, "_achat": l.get("PRICE")})
        vus[cle] = v
        variantes.append(v)
    seo = seo_textes(t_fr, t_nl, r)
    return {"handle": sl.slug(t_fr)[:200], "titre_fr": t_fr, "titre_nl": t_nl, "desc_fr": d_fr, "desc_nl": d_nl,
            "marque": marque, "type_fr": cat_fr, "type_nl": cat_nl, "tags": ", ".join(tags),
            "teintes": teintes, "variantes": variantes, **seo}


def seo_textes(t_fr, t_nl, r):
    """Titre (≤ 70 caractères) et méta-description (≤ 160) pour Google, FR + NL (08/11/2026)."""
    def titre(t):
        t = t.replace(" — ", " ")
        return t + " | Qosmi" if len(t) + 8 <= 70 else (t if len(t) <= 70 else t[:71].rsplit(" ", 1)[0])

    def coupe(d):
        return d if len(d) <= 160 else d[:157].rsplit(" ", 1)[0] + "…"
    n_fr, n_nl = t_fr.replace(" — ", ", ").replace("— ", ""), t_nl.replace(" — ", ", ").replace("— ", "")
    return {"seo_titre_fr": titre(t_fr), "seo_titre_nl": titre(t_nl),
            "seo_desc_fr": coupe("%s, 100 %% authentique et neuf. Livraison en Belgique en %s. Paiement Bancontact." % (n_fr, r["delai_fr"])),
            "seo_desc_nl": coupe("%s, 100%% origineel en nieuw. Levering in België binnen %s. Betalen met Bancontact." % (n_nl, r["delai_nl"]))}


def photos_officielles(produits):
    """Photos autorisées, prioritaires sur celles de Wholesale-Fragrances :
    - sites des marques (config/photos_marques.json : Mancera, Montale, Xerjoff ; config/photos_acquadiparma.json, 2400 px, 05/11/2026) ;
    - revendeurs qui ont donné leur accord : Parfumerie.be (config/photos_parfumerie.json, 2000 px, 05/11/2026),
      Parfuma (config/photos_parfuma.json, 1000 px, 05/11/2026), Riklis Karto (config/photos_riklis.json, 2048 px, 05/11/2026) et Skins (config/photos_skins.json, 1200 px, 05/11/2026).
    Correspondance par EAN d'abord, sinon par nom du parfum (testeurs compris) ; à égalité, la plus grande photo."""
    import photos_marques as pm
    dossier = os.path.dirname(sl.SITE)
    sources = []  # (qualité, par_ean, par_nom, marques limitées ou None)
    for nom, qualite in (("photos_elo.json", 4), ("photos_creed.json", 4), ("photos_ch.json", 4), ("photos_puig.json", 3.5), ("photos_notino.json", 3), ("photos_dg.json", 4), ("photos_jm.json", 3.5), ("photos_mm.json", 3.5), ("photos_tfi.json", 3.5), ("photos_ck.json", 3.5), ("photos_tt.json", 3.5), ("photos_lvmh.json", 3.5), ("photos_ici.json", 2.5), ("photos_bijenkorf.json", 2.5), ("photos_acquadiparma.json", 4), ("photos_parfuma.json", 1.5), ("photos_parfumerie.json", 3), ("photos_riklis.json", 3), ("photos_skins.json", 2), ("photos_marques.json", None)):
        chemin = os.path.join(dossier, nom)
        if not os.path.exists(chemin):
            continue
        ph = json.load(open(chemin, encoding="utf-8"))
        marques = {m.lower() for m in ph["marques"]} if "marques" in ph else None
        sources.append((qualite, ph.get("par_ean", {}), ph.get("par_nom", {}), marques, ph.get("par_fiche", {})))
    if not sources:
        return 0
    # photos recadrées (même taille de flacon sur toutes les cartes, 07/11/2026) : config/photos_cadrees.json
    chemin = os.path.join(dossier, "photos_cadrees.json")
    cadrees = json.load(open(chemin, encoding="utf-8"))["par_url"] if os.path.exists(chemin) else {}
    n = 0
    for p in produits:
        m = p["marque"].lower()
        titre = p["titre_fr"].split(" — ")[0][len(p["marque"]) + 1:]
        cle = pm.cle_nom(p["marque"], titre)
        for v in p["variantes"]:
            choix = []
            for qualite, par_ean, par_nom, marques, par_fiche in sources:
                if marques is not None and m not in marques:
                    continue
                q = qualite if qualite is not None else (1 if m == "xerjoff" else 2)  # photos du site Xerjoff : 590 px
                u = par_ean.get(v["ean"].lstrip("0"))
                if u:
                    choix.append((2, q, u))
                u = par_nom.get(cle) or par_fiche.get(p["handle"])  # par_fiche : même parfum vérifié nom + type
                if u:
                    choix.append((1, q, u))
            if choix:
                v["photo_brute"] = max(choix)[2]
                v["photo_source"] = cadrees.get(v["photo_brute"], v["photo_brute"])
                v["_photo_autorisee"] = True
                n += 1
        # même parfum dans une autre contenance : les formats sans photo autorisée reprennent celle de la fiche
        reprise = next((v["photo_source"] for v in p["variantes"] if v.get("_photo_autorisee")), None)
        p["photo_ok"] = bool(reprise)  # sans photo autorisée (photo du grossiste, 220-350 px, ou aucune) : fiche masquée
        for v in p["variantes"]:
            if not v.pop("_photo_autorisee", False) and reprise and not p["teintes"]:
                v["photo_source"] = reprise
                n += 1
    return n


def preparer(exemples=True):
    if not os.path.exists(sl.SOURCE):
        sys.exit("Liste SoleLuna brute absente (base/soleluna_liste.csv) : lance d'abord « telecharger.py PERFUMEWHOLESALE ».")
    r = sl.reglages()
    lignes = sl.lire_source(sl.SOURCE)
    depot = []  # 04/11/2026 : Qosmi vend uniquement SoleLuna (les fiches du dépôt sont retirées du site)
    eans_depot = {l["ean"].lstrip("0") for l in depot}
    photos = sl.photos_wf()
    groupes, ecart = defaultdict(list), defaultdict(int)
    suspens = json.load(open(sl.SITE, encoding="utf-8")).get("testeurs_en_suspens") if os.path.exists(sl.SITE) else False
    for l in lignes:
        ean = re.sub(r"\D", "", l.get("EAN") or "")
        if suspens and (l.get("TESTER") or "").strip() == "1":  # 08/11/2026 : testeurs en suspens (config/site.json)
            ecart["testeur (en suspens)"] += 1
        elif len(ean) < 8:
            ecart["sans EAN"] += 1
        elif sl.nombre(l.get("PRICE")) <= 0:
            ecart["prix nul"] += 1
        elif ean.lstrip("0") in eans_depot:
            ecart["déjà en stock au dépôt"] += 1
        else:
            groupes[cle_groupe(l)].append(l)
    produits = [produit(g, r, photos) for g in groupes.values()]
    n_off = photos_officielles(produits)
    # handles uniques
    vus = set()
    for p in sorted(produits, key=lambda p: p["titre_fr"].lower()):
        h, i = p["handle"], 2
        while p["handle"] in vus:
            p["handle"] = "%s-%d" % (h, i)
            i += 1
        vus.add(p["handle"])
    # confidentialité
    garde = []
    for p in produits:
        texte = " ".join([p["handle"], p["titre_fr"], p["titre_nl"], p["desc_fr"], p["desc_nl"], p["tags"]] +
                         [v["format_fr"] + " " + v["teinte"] for v in p["variantes"]]).lower()
        if any(m in texte and m not in p["marque"].lower() for m in sl.INTERDITS):
            ecart["mot interdit dans la fiche"] += 1
        else:
            garde.append(p)
    produits = sorted(garde, key=lambda p: (p["marque"].lower(), p["titre_fr"].lower()))
    # sauvegarde des fiches du 03/11 (une seule fois)
    if os.path.exists(sl.CATALOGUE) and not os.path.exists(V1):
        with open(sl.CATALOGUE, encoding="utf-8") as f:
            if "groupe" not in f.readline():
                import shutil
                shutil.copy2(sl.CATALOGUE, V1)
    with open(PRODUITS, "w", encoding="utf-8") as f:
        json.dump(produits, f, ensure_ascii=False)
    with open(sl.CATALOGUE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(depot)
        for p in produits:
            for v in p["variantes"]:
                w.writerow({**v, "groupe": p["handle"]})
    nv = sum(len(p["variantes"]) for p in produits)
    multi = [p for p in produits if len(p["variantes"]) > 1]
    print("Liste SoleLuna lue : %d lignes." % len(lignes))
    print("Fiches SoleLuna : %d (au lieu de %d formats séparés), dont %d avec plusieurs formats ou teintes."
          % (len(produits), nv, len(multi)))
    print("  %d fiches avec photo, dont %d formats avec la photo officielle de la marque." % (
        sum(1 for p in produits if any(v["photo_source"] for v in p["variantes"])), n_off))
    if ecart:
        print("  écartées : " + ", ".join("%s %d" % (k, v) for k, v in ecart.items()))
    for p in (sorted(multi, key=lambda p: -len(p["variantes"]))[:3] + multi[:3]) if exemples else []:
        print("  exemple :", p["titre_fr"], "→", " | ".join(
            v["format_fr"] + (" " + v["teinte"] if v["teinte"] and v["teinte"] != "—" else "") for v in p["variantes"][:6]))
    return produits


# ------------------------------------------------------------------ Shopify
def entree(p, lieu_id, ident):
    options = [{"name": "Format", "values": []}] + ([{"name": "Teinte", "values": []}] if p["teintes"] else [])
    fichiers, variantes = {}, []
    for v in p["variantes"]:
        if v["format_fr"] not in [x["name"] for x in options[0]["values"]]:
            options[0]["values"].append({"name": v["format_fr"]})
        ov = [{"optionName": "Format", "name": v["format_fr"]}]
        if p["teintes"]:
            if v["teinte"] not in [x["name"] for x in options[1]["values"]]:
                options[1]["values"].append({"name": v["teinte"]})
            ov.append({"optionName": "Teinte", "name": v["teinte"]})
        var = {"optionValues": ov, "price": v["prix"], "sku": v["sku"], "barcode": v["ean"],
               "inventoryPolicy": "DENY", "taxable": True,
               "inventoryItem": {"tracked": True, "requiresShipping": True, "cost": v["cout_ht"]},
               "inventoryQuantities": [{"locationId": lieu_id, "name": "available", "quantity": int(v["stock"])}]}
        src = (v.get("photo_source") or "").split("?")[0]
        ext = os.path.splitext(src)[1]
        sans_ext = bool(src) and not ext and re.search(r"reference=[^&]*?\.(?:jpe?g|png|webp)", v["photo_source"], re.I)
        if src and (ext or sans_ext):
            if v["photo_source"] not in fichiers:
                f = {"originalSource": v["photo_source"], "contentType": "IMAGE", "alt": p["titre_fr"]}
                if ext:  # sans extension dans l'adresse (De Bijenkorf), Shopify nomme le fichier lui-même
                    f["filename"] = "%s-%d%s" % (p["handle"][:110], len(fichiers) + 1, ext)
                fichiers[v["photo_source"]] = f
            var["file"] = fichiers[v["photo_source"]]
        variantes.append(var)
    inp = {"handle": p["handle"], "title": p["titre_fr"], "descriptionHtml": p["desc_fr"], "vendor": p["marque"],
           "productType": p["type_fr"], "tags": [t.strip() for t in p["tags"].split(",") if t.strip()],
           "status": "DRAFT", "productOptions": options, "variants": variantes, "files": list(fichiers.values())}
    return {"input": inp, "identifier": ident}


def lire_fiches_shopify(s, sc):
    d = s.gql("""mutation($q: String!) { bulkOperationRunQuery(query: $q) { bulkOperation { id } userErrors { message } } }""",
              {"q": "{ products { edges { node { id handle status } } } }"})["bulkOperationRunQuery"]
    if d["userErrors"]:
        sys.exit("Lecture des fiches Shopify refusée : %s" % d["userErrors"])
    b = sc.attendre(s, d["bulkOperation"]["id"], "lecture-fiches")
    if not b.get("url"):
        sys.exit("Lecture des fiches Shopify impossible (%s)." % b.get("errorCode"))
    import urllib.request
    chemin = os.path.join(sl.RAPPORTS, "site_fiches_shopify.jsonl")
    urllib.request.urlretrieve(b["url"], chemin)
    return {x["handle"]: x for x in (json.loads(l) for l in open(chemin, encoding="utf-8")) if x.get("handle")}


def envoyer(produits):
    from shopify_api import Shopify
    import site_charger as sc
    os.makedirs(sl.RAPPORTS, exist_ok=True)
    s = Shopify()
    lieu_id = sc.lieu(s)
    existantes = lire_fiches_shopify(s, sc)
    ancien_par_sku = {}
    if os.path.exists(V1):
        with open(V1, encoding="utf-8") as f:
            ancien_par_sku = {l["sku"]: l["handle"] for l in csv.DictReader(f, delimiter=";") if l["sku"].startswith("QS-")}
    reprises, envoi = set(), os.path.join(sl.RAPPORTS, "site_variantes_envoi.jsonl")
    with open(envoi, "w", encoding="utf-8") as f:
        for p in produits:
            ident = None
            if p["handle"] in existantes:  # relance : la fiche groupée existe déjà
                ident = {"id": existantes[p["handle"]]["id"]}
            else:  # reprendre la fiche du 03/11 d'un de ses formats
                for v in p["variantes"]:
                    h = ancien_par_sku.get(v["sku"])
                    if h in existantes and h not in reprises:
                        ident = {"id": existantes[h]["id"]}
                        reprises.add(h)
                        break
            f.write(json.dumps(entree(p, lieu_id, ident or {"handle": p["handle"]}), ensure_ascii=False) + "\n")
    sc.journal("Fiches groupées préparées : %d (dont %d reprennent une fiche du 03/11)" % (len(produits), len(reprises)))
    op = sc.lancer_mutation(s, sc.M_SET, envoi, "variantes")
    b = sc.attendre(s, op, "variantes")
    sc.bilan_resultats(b, "variantes")
    if b["status"] != "COMPLETED":
        sys.exit("Envoi interrompu : les fiches du 03/11 ne sont pas archivées.")
    # archiver les fiches du 03/11 devenues inutiles
    nouveaux = {p["handle"] for p in produits}
    a_archiver = [existantes[h]["id"] for h in set(ancien_par_sku.values())
                  if h in existantes and h not in reprises and h not in nouveaux and existantes[h]["status"] != "ARCHIVED"]
    sc.journal("Fiches du 03/11 à archiver : %d" % len(a_archiver))
    if a_archiver:
        chemin = os.path.join(sl.RAPPORTS, "site_archivage_v1_envoi.jsonl")
        with open(chemin, "w", encoding="utf-8") as f:
            for pid in a_archiver:
                f.write(json.dumps({"product": {"id": pid, "status": "ARCHIVED"}}) + "\n")
        with open(os.path.join(sl.RAPPORTS, "site_archivage_v1_ids_%s.txt" % time.strftime("%Y-%m-%d_%Hh%M")), "w") as f:
            f.write("\n".join(a_archiver) + "\n")
        op = sc.lancer_mutation(s, sc.M_MAJ, chemin, "archivage-v1")
        sc.bilan_resultats(sc.attendre(s, op, "archivage-v1"), "archivage-v1")
    try:
        traduire(s, sc, produits)
    except Exception as e:  # les fiches sont en place ; seules les traductions sont à refaire
        sc.journal("Traductions NL non terminées (%s : %s) — relancer le lanceur 28 plus tard." % (type(e).__name__, str(e)[:200]))


TRAD_OPTIONS = [("Format", "Inhoud"), ("Teinte", "Kleur")]


def valeur_nl(v):
    return (v.replace("Taille unique", "Standaard").replace(" – testeur", " – tester")
             .replace(" – boîte abîmée", " – beschadigde doos"))


def traduire(s, sc, produits):
    """NL : titre, description, type de chaque fiche ; noms et valeurs des options (Format → Inhoud…)."""
    import urllib.request
    par_handle = {p["handle"]: p for p in produits}
    sortie = os.path.join(sl.RAPPORTS, "site_variantes_traductions_envoi.jsonl")
    n = 0
    with open(sortie, "w", encoding="utf-8") as f:
        for type_res in ("PRODUCT", "PRODUCT_OPTION", "PRODUCT_OPTION_VALUE"):
            q = ("{ translatableResources(resourceType: %s) { edges { node { resourceId "
                 "translatableContent { key value digest locale } } } } }" % type_res)
            d = s.gql("""mutation($q: String!) { bulkOperationRunQuery(query: $q) { bulkOperation { id } userErrors { message } } }""",
                      {"q": q})["bulkOperationRunQuery"]
            if d["userErrors"]:
                sc.journal("Lecture %s refusée : %s" % (type_res, d["userErrors"]))
                continue
            b = sc.attendre(s, d["bulkOperation"]["id"], "lecture-" + type_res.lower())
            if not b.get("url"):
                continue
            chemin = os.path.join(sl.RAPPORTS, "site_traduisibles_%s.jsonl" % type_res.lower())
            urllib.request.urlretrieve(b["url"], chemin)
            for l in open(chemin, encoding="utf-8"):
                x = json.loads(l)
                c = {k["key"]: k for k in x.get("translatableContent", [])}
                t = []
                if type_res == "PRODUCT":
                    p = par_handle.get((c.get("handle") or {}).get("value"))
                    if not p:
                        continue
                    for cle, val in (("title", p["titre_nl"]), ("body_html", p["desc_nl"]), ("product_type", p["type_nl"]),
                                     ("meta_title", p.get("seo_titre_nl")), ("meta_description", p.get("seo_desc_nl"))):
                        if cle in c and val:
                            t.append({"locale": "nl", "key": cle, "value": val, "translatableContentDigest": c[cle]["digest"]})
                else:
                    nom = c.get("name")
                    if not nom:
                        continue
                    nl = dict(TRAD_OPTIONS).get(nom["value"]) if type_res == "PRODUCT_OPTION" else valeur_nl(nom["value"])
                    if nl and nl != nom["value"]:
                        t.append({"locale": "nl", "key": "name", "value": nl, "translatableContentDigest": nom["digest"]})
                if t:
                    f.write(json.dumps({"resourceId": x["resourceId"], "translations": t}, ensure_ascii=False) + "\n")
                    n += 1
    sc.journal("Traductions NL préparées : %d éléments" % n)
    if n:
        op = sc.lancer_mutation(s, sc.M_TRAD, sortie, "traductions-variantes")
        sc.bilan_resultats(sc.attendre(s, op, "traductions-variantes"), "traductions-variantes")


def basculer():
    produits = preparer()
    print()
    print("Étapes suivantes sur Shopify :")
    print("  1. %d fiches groupées en BROUILLON ; chacune reprend une fiche du 03/11 quand c'est possible ;" % len(produits))
    print("  2. les fiches du 03/11 devenues inutiles passent en ARCHIVÉ (récupérables) ;")
    print("  3. traductions NL (titres, descriptions, « Format » → « Inhoud », « testeur » → « tester »…).")
    print("  Les fiches du dépôt ne sont pas touchées.")
    if input("Tape OUI pour lancer : ").strip() != "OUI":
        print("Annulé : rien n'a été envoyé à Shopify.")
        return
    envoyer(produits)


if __name__ == "__main__":
    if "--preparer" in sys.argv:
        preparer()
    elif "--basculer" in sys.argv:
        basculer()
    else:
        print(__doc__)
