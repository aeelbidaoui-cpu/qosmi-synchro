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
import csv, html, json, math, os, re, sys, time
from collections import defaultdict

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import site_soleluna as sl  # noqa: E402

PRODUITS = os.path.join(sl.BASE, "site_produits.json")
BILAN_BONS_PLANS = None
BILAN_SUR_COMMANDE = None
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


def ajouter_normaux_attente(variantes):
    """22/11/2026 (Amine) : à côté d'un testeur sans flacon normal de même contenance, ajoute ce flacon normal « épuisé »
    (stock 0, prix indicatif = prix du testeur + 15 %, arrondi au ,90). Code : QS-N + code du testeur."""
    normaux_vus = {(v["format_fr"], v["teinte"]) for v in variantes if " – " not in v["format_fr"]}
    for v in list(variantes):
        if not v["format_fr"].endswith(" – testeur"):
            continue
        f_fr, f_nl = v["format_fr"][:-len(" – testeur")], v["format_nl"].rsplit(" – ", 1)[0]
        if (f_fr, v["teinte"]) in normaux_vus:
            continue
        n = dict(v)
        n.update({"format_fr": f_fr, "format_nl": f_nl, "sku": PREFIXE_ATTENTE + v["sku"][3:], "ean": "",
                  "stock": "0", "prix": "%.2f" % sl.arrondi_90_haut(float(v.get("prix") or 0) * 1.15), "attente": True})
        variantes.insert(variantes.index(v), n)
        normaux_vus.add((f_fr, v["teinte"]))


def produit(lignes, r, photos, normaux_attente_auto=True):
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
        d_fr += " Produit authentique, neuf. Livraison en Belgique et dans 8 autres pays d'Europe."
        d_nl += " Origineel en nieuw product. Levering in België en 8 andere Europese landen."
        d_fr = "<p>%s</p>" % html.escape(d_fr.strip(), quote=False)
        d_nl = "<p>%s</p>" % html.escape(d_nl.strip(), quote=False)
    t_fr, t_nl = re.sub(r"\s+", " ", t_fr).strip(), re.sub(r"\s+", " ", t_nl).strip()
    cat_fr, cat_nl = base["type_fr"], base["type_nl"]
    if cat_fr == "Testeurs":  # la catégorie suit le genre ; « testeur » devient une variante + une étiquette
        cat_fr, cat_nl = {"femme": ("Parfums femme", "Damesparfums"), "homme": ("Parfums homme", "Herenparfums"),
                          "mixte": ("Parfums mixtes", "Unisex parfums"),
                          "enfant": ("Parfums enfants", "Kinderparfums")}.get(g_cle, ("Parfums", "Parfums"))
    # 19/11/2026 (Amine, condition des marques) : aucune rubrique ni badge « testeur » : le testeur n'est qu'une option de la fiche
    tags = [cat_fr, marque] + (["boite-abimee"] if abimes else [])
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
    # 18/11/2026 (Amine, testeurs autorisés par les marques) : le testeur est une option de la fiche du parfum, au même
    # calcul de prix que les autres formats ; s'il ne revient pas moins cher que le flacon normal de même contenance,
    # il n'a pas d'intérêt pour le client et n'est pas proposé.
    normaux = {}
    for v in variantes:
        if " – " not in v["format_fr"]:
            normaux[(v["format_fr"], v["teinte"])] = float(v.get("prix") or 0)
    for v in list(variantes):
        if v["format_fr"].endswith(" – testeur"):
            ref = normaux.get((v["format_fr"][:-len(" – testeur")], v["teinte"]))
            if ref and float(v.get("prix") or 0) >= ref and len(variantes) > 1:
                variantes.remove(v)
    # 22/11/2026 (Amine) : jamais une fiche avec le testeur seul : la version normale (en boîte) est toujours parmi les options.
    # Si le grossiste ne la propose pas, on l'ajoute « épuisée » (stock 0) avec un prix indicatif (prix du testeur + 15 %,
    # arrondi au ,90). Le jour où le grossiste la propose, la vraie variante (son propre code) prend sa place automatiquement
    # au passage horaire (même format → l'ancienne est remplacée, voir entree_complete) avec le vrai prix et le stock.
    if normaux_attente_auto:
        ajouter_normaux_attente(variantes)
    if testeurs and any(" – testeur" not in v["format_fr"] for v in variantes):
        tags = [x for x in tags if x != "Testeurs"]  # pas de rubrique ni de badge « testeur » quand la fiche a aussi des flacons normaux
    seo = seo_textes(t_fr, t_nl, r, vols)
    riche = descriptions_riches().get(sl.slug(t_fr)[:200])
    if riche:  # 10/11/2026 : vraie description (notes, famille, occasions) rédigée et vérifiée, FR + NL
        d_fr, d_nl = riche["fr"] + "<p>" + d_fr + "</p>", riche["nl"] + "<p>" + d_nl + "</p>"
        notes = [n for k in ("tete", "coeur", "fond", "cle") for n in (riche.get("notes_fr") or {}).get(k) or []][:3]
        notes_nl = [n for k in ("tete", "coeur", "fond", "cle") for n in (riche.get("notes_nl") or {}).get(k) or []][:3]
        if notes:
            seo["seo_desc_fr"] = coupe155("%s. Notes : %s. 100 %% authentique, livré partout en Belgique."
                                          % (t_fr.replace(" — ", ", "), ", ".join(n.lower() for n in notes)))
        if notes_nl:
            seo["seo_desc_nl"] = coupe155("%s. Geurnoten: %s. 100%% origineel, geleverd in heel België."
                                          % (t_nl.replace(" — ", ", "), ", ".join(n.lower() for n in notes_nl)))
    elif not coffret and parfum:  # 17/11/2026 : profil Fragrance Index (notes, accords, saison…) écrit dans la description,
        prof = profil_fi(sl.slug(t_fr)[:200])  # pour que les clients ET l'assistante du chat (Mimi) le trouvent
        if prof:
            d_fr, d_nl = d_fr + texte_profil(prof, False), d_nl + texte_profil(prof, True)
            nf = [n for k in ("t", "c", "f", "n") for n in (prof.get("nf") or {}).get(k) or []][:3]
            nn = [n for k in ("t", "c", "f", "n") for n in (prof.get("nn") or {}).get(k) or []][:3]
            if nf:
                seo["seo_desc_fr"] = coupe155("%s. Notes : %s. 100 %% authentique, livré partout en Belgique."
                                              % (t_fr.replace(" — ", ", "), ", ".join(n.lower() for n in nf)))
            if nn:
                seo["seo_desc_nl"] = coupe155("%s. Geurnoten: %s. 100%% origineel, geleverd in heel België."
                                              % (t_nl.replace(" — ", ", "), ", ".join(n.lower() for n in nn)))
    return {"handle": sl.slug(t_fr)[:200], "titre_fr": t_fr, "titre_nl": t_nl, "desc_fr": d_fr, "desc_nl": d_nl,
            "marque": marque, "type_fr": cat_fr, "type_nl": cat_nl, "tags": ", ".join(tags),
            "teintes": teintes, "variantes": variantes, **seo}


# ------------------------------------------------------------------ « Bons plans » (14/11/2026, décision d'Amine)
# Pour un format donné, une 2e variante « 100 ml · Bon plan » commandée chez un 2e grossiste les lundis et jeudis
# (minimum de commande, port fixe par commande) : un peu plus de délai, prix plus bas pour le client.
# Affichée dès 1 pièce chez ce grossiste et seulement si elle fait gagner au moins gain_min_eur au client ;
# à 0 pièce (ou sortie de sa liste) elle passe à stock 0 et le thème la cache. Mise à jour au même passage que SoleLuna.
# Liste : base/trista_liste.csv (secret TRISTA_URL sur le serveur), colonnes ean;product;stock;incoming;eta_date;price (HT).
TRISTA = os.path.join(sl.BASE, "trista_liste.csv")
BON_PLAN_FR, BON_PLAN_NL = " · Bon plan", " · Koopje"
PREFIXE_BON_PLAN = "QS-B"


def reglages_bons_plans():
    d = (json.load(open(sl.SITE, encoding="utf-8")) if os.path.exists(sl.SITE) else {}).get("bons_plans") or {}
    return {"actif": bool(d.get("actif", True)), "en_ligne": bool(d.get("en_ligne", False)), "port_commande_eur": float(d.get("port_commande_eur", 13)),
            "minimum_commande_eur": float(d.get("minimum_commande_eur", 300)), "gain_min_eur": float(d.get("gain_min_eur", 3)),
            "stock_min": int(d.get("stock_min", 1)), "majoration_pct": float(d.get("majoration_pct", 0.02)),
            "envoi_eur": float(d.get("envoi_eur", 3)), "benefice_eur": float(d.get("benefice_eur", 10)),
            "benefice_min_eur": float(d.get("benefice_min_eur", 5))}


def liste_trista(chemin=TRISTA):
    """{EAN sans zéros de tête: (prix d'achat HT, stock)} ; None si la liste est absente ou illisible."""
    if not os.path.exists(chemin):
        return None
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    if len(lignes) < 200 or not {"ean", "stock", "price"} <= set(lignes[0]):
        return None
    t = {}
    for l in lignes:
        ean = re.sub(r"\D", "", l.get("ean") or "").lstrip("0")
        achat, stock = sl.nombre(l.get("price")), int(sl.nombre(l.get("stock")))
        if len(ean) >= 7 and achat > 0 and (ean not in t or achat < t[ean][0]):
            t[ean] = (achat, max(0, stock))
    return t


def ajouter_bons_plans(produits, r):
    """Ajoute les variantes « Bon plan » aux fiches. Renvoie un bilan, ou None si la liste n'a pas pu être lue
    (les variantes « Bon plan » déjà sur le site sont alors laissées telles quelles)."""
    rb = reglages_bons_plans()
    t = liste_trista() if rb["actif"] else {}
    if t is None:
        return None
    bilan = {"bons_plans": 0, "fiches": 0, "trop_proches": 0, "sans_stock": 0, "gains": []}
    for p in produits:
        if p["teintes"]:
            continue
        nouvelles = []
        for v in p["variantes"]:
            if " – " in v["format_fr"] or v.get("sur_commande"):  # pas de bon plan sur un testeur, une boîte abîmée, un « sur commande »
                nouvelles.append(v)
                continue
            nouvelles.append(v)
            x = t.get((v.get("ean") or "").lstrip("0"))
            if not x:
                continue
            achat, stock = x
            if stock < rb["stock_min"]:
                bilan["sans_stock"] += 1
                continue
            # Règle d'Amine du 14/11/2026 : (prix + 2 %) + 3 € d'envoi + 10 € de bénéfice (plus d'argent bloqué), + 21 % TVA,
            # arrondi au ,90 supérieur. Pas d'alignement sur le concurrent pour cette option.
            # Règle d'Amine du 14/11/2026 : (prix + 2 %) + 3 € d'envoi + frais Shopify Payments + 10 € de bénéfice, + 21 % TVA,
            # arrondi au ,90 supérieur. Si l'écart avec la livraison normale est alors < gain_min_eur (3 €), on descend jusqu'à
            # 3 € sous le prix normal, sans passer sous benefice_min_eur (5 € net). Pas d'alignement sur le concurrent.
            # 20/11/2026 (Amine) : + emballage (0,60 €) + part d'envoi client Mondial Relay (1,75 €), pour garder 5 € net
            port = rb["envoi_eur"] + r.get("emballage_eur", 0) + r.get("envoi_client_eur", 0)
            k = 1 / (1 + r["tva"]) - r.get("paiement_pct", 0)
            base = achat * (1 + rb["majoration_pct"]) + port + r.get("paiement_fixe", 0)
            normal = float(v["prix"])
            prix = sl.arrondi_90_haut((base + rb["benefice_eur"]) / k)
            if prix > normal - rb["gain_min_eur"] + 1e-6:
                cible = math.floor(normal - rb["gain_min_eur"] - 0.90 + 1e-9) + 0.90  # le ,90 juste sous normal - 3 €
                prix = max(cible, sl.arrondi_90_haut((base + rb["benefice_min_eur"]) / k))
                # 19/11/2026 (Amine, Naxos) : si le format normal est épuisé chez SoleLuna, l'option Trista est quand même
                # proposée (sinon le parfum n'est plus achetable du tout), au prix de la règle avec au moins 5 € net
                if prix > normal - 1 + 1e-6 and int(sl.nombre(v.get("stock") or 0)) > 0:  # même à 5 € net, pas 1 € moins cher : pas d'option
                    bilan["trop_proches"] += 1
                    continue
                bilan["normal_epuise"] = bilan.get("normal_epuise", 0) + (int(sl.nombre(v.get("stock") or 0)) <= 0)
                bilan["benefice_reduit"] = bilan.get("benefice_reduit", 0) + 1
            b = dict(v, sku=PREFIXE_BON_PLAN + v["ean"].lstrip("0"), format_fr=v["format_fr"] + BON_PLAN_FR,
                     format_nl=v["format_nl"] + BON_PLAN_NL, prix="%.2f" % prix, stock=str(stock),
                     cout_ht="%.2f" % (achat * (1 + rb["majoration_pct"]) + port), bon_plan=True,
                     _net="%.2f" % (prix * k - base), _achat=str(achat))
            nouvelles.append(b)
            bilan["bons_plans"] += 1
            bilan["gains"].append((float(v["prix"]) - prix, p["titre_fr"], v["format_fr"], float(v["prix"]), prix))
        if len(nouvelles) > len(p["variantes"]):
            p["variantes"] = nouvelles
            p["tags"] = ", ".join([x for x in p["tags"].split(", ") if x and x != "bon-plan"] + ["bon-plan"])
            bilan["fiches"] += 1
    return bilan


# ------------------------------------------------------------------ « Sur commande » (14/11/2026, décision d'Amine)
# Parfums que seul le 2e grossiste propose (absents de la liste SoleLuna) : fiche créée avec des formats « · Sur commande »,
# au prix de la règle « Bon plan » à 10 € net (pas de prix normal à battre), même délai, même mise à jour horaire ; la fiche
# se masque quand plus aucun format n'est en stock. Seulement les marques de config/selection.json, parfums uniquement
# (pas de coffrets, miniatures, recharges, soins ; testeurs acceptés depuis le 18/11/2026, en option « – testeur »).
SUR_COMMANDE_FR, SUR_COMMANDE_NL = " · Sur commande", " · Op bestelling"
PREFIXE_SUR_COMMANDE = "QS-C"
PREFIXE_ATTENTE = "QS-N"  # 22/11/2026 : version normale ajoutée « épuisée » à côté d'un testeur seul (voir produit())
PREFIXE_SUR_COMMANDE_FUSION = "QS-D"  # format du 2e grossiste ajouté à une fiche SoleLuna du même parfum (genre différent)
ALIAS_MARQUES = {"jpg": "Jean Paul Gaultier", "ysl": "Yves Saint Laurent", "d&g": "Dolce&Gabbana", "ck": "Calvin Klein",
                 "armani": "Giorgio Armani", "lancome": "Lancôme", "etat libre d orange": "Etat Libre d´Orange",
                 "etat libre d'orange": "Etat Libre d´Orange", "spirit of dubai": "The Spirit of Dubai",
                 "marc antoine barrois": "Marc-Antoine Barrois", "maison margiela": "Maison Margiela Paris",
                 "mfk": "Maison Francis Kurkdjian", "penhaligons": "Penhaligon´s", "penhaligon's": "Penhaligon´s",
                 "kilian": "By Kilian", "dolce & gabbana": "Dolce&Gabbana", "dolce gabbana": "Dolce&Gabbana",
                 "boss": "Hugo Boss", "viktor&rolf": "Viktor & Rolf", "viktor and rolf": "Viktor & Rolf"}
TYPES_TRISTA = [(r"\bextrait(?: de parfum)?\b", "extrait de parfum"), (r"\bedp\b|\beau de parfum\b", "eau de parfum"),
                (r"\bedt\b|\beau de toilette\b", "eau de toilette"), (r"\bedc\b|\bcologne\b", "eau de cologne"),
                (r"\bparfum\b", "perfume")]
EXCLUS_TRISTA = re.compile(r"\b(set|tester|gwp|refill|recharge|travel|mini|miniature|sample|vial|deo|deodorant|body|hair|"
                           r"lotion|shower|cream|balm|soap|candle|mist|oil|gel)\b", re.I)


# 15/11/2026 (point 3) : les noms du 2e grossiste arrivent sans accents ni apostrophes (« L Eau D Hiver », « Blanche Bete »).
# Corrections mot à mot qui ne changent pas l'adresse de la fiche (même suite de mots une fois les accents retirés),
# sauf les quelques noms entiers de NOMS_ENTIERS.
ACCENTS_TRISTA = {"bete": "Bête", "vole": "Volé", "therese": "Thérèse", "mediterranee": "Méditerranée",
                  "concentree": "Concentrée", "geranium": "Géranium", "haiti": "Haïti", "neroli": "Néroli",
                  "fraiche": "Fraîche", "idole": "Idôle", "vip": "VIP", "intensly": "Intensely"}
MINUSCULES_TRISTA = {"de", "des", "du", "au", "aux", "et", "est", "di"}  # au milieu du nom seulement
NOMS_ENTIERS = {"men's terre d' intense": "Terre d'Hermès Intense", 'casamorati 1888 "1888"': "Casamorati 1888 « 1888 »",
                "acqua di gio": "Acqua di Giò", "j adore l or": "J'adore L'Or", "j adore": "J'adore"}


def nom_propre(titre):
    """Nom de parfum du 2e grossiste remis en forme : accents, apostrophes (« L'Eau d'Hiver »), petits mots en minuscules."""
    t = re.sub(r"\s+", " ", (titre or "").replace("´", "'")).strip()
    if t.lower() in NOMS_ENTIERS:
        return NOMS_ENTIERS[t.lower()]
    for cle, val in NOMS_ENTIERS.items():
        if t.lower().startswith(cle + " ") and cle.startswith("j adore"):
            t = val + t[len(cle):]
    mots = t.split(" ")
    sortie = []
    i = 0
    while i < len(mots):
        m = mots[i]
        bas = m.lower()
        suivant = mots[i + 1] if i + 1 < len(mots) else ""
        if bas in ("l", "d") and suivant[:1].isalpha():  # « L Eau » → « L'Eau », « D Hiver » → « d'Hiver »
            elision = ("L'" if bas == "l" else ("D'" if not sortie else "d'"))
            mot = ACCENTS_TRISTA.get(suivant.lower(), suivant)
            if bas == "l" and suivant.lower() == "elixir":
                mot = "Élixir"
            sortie.append(elision + mot[:1].upper() + mot[1:])
            i += 2
            continue
        if bas == "a" and suivant.lower() == "la" and sortie:  # « Neroli a la Cardamome » → « à la »
            sortie.append("à la")
            i += 2
            continue
        elif bas == "the" and sortie and sortie[-1].lower() == "au":  # « au The Vert » → « au Thé Vert »
            sortie.append("Thé")
        elif bas in ACCENTS_TRISTA:
            sortie.append(ACCENTS_TRISTA[bas])
        elif bas in MINUSCULES_TRISTA and sortie and i + 1 < len(mots):
            sortie.append(bas)
        else:
            sortie.append(m)
        i += 1
    return " ".join(sortie)


def _norm(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[´`’]", "'", t)


def marque_trista(nom, marques):
    """(marque de la sélection, reste du nom) ou (None, None)."""
    n = _norm(nom)
    cands = [(m, m) for m in marques] + [(a, ALIAS_MARQUES[a]) for a in ALIAS_MARQUES]
    for cle, marque in sorted(cands, key=lambda x: -len(x[0])):
        c = _norm(cle)
        if n.startswith(c + " ") and marque in marques:
            return marque, nom[len(cle):].strip()
    return None, None


def lignes_trista_seules(eans_soleluna):
    """Lignes « façon SoleLuna » pour les parfums du 2e grossiste absents de SoleLuna (marques de la sélection)."""
    if not os.path.exists(TRISTA):
        return None
    sel = os.path.join(os.path.dirname(sl.SITE), "selection.json")
    marques = json.load(open(sel, encoding="utf-8"))["marques"] if os.path.exists(sel) else []
    with open(TRISTA, encoding="utf-8-sig", newline="") as f:
        brut = list(csv.DictReader(f, delimiter=";"))
    if len(brut) < 200:
        return None
    lignes = []
    for l in brut:
        ean = re.sub(r"\D", "", l.get("ean") or "")
        nom = sl.propre(l.get("product"))
        # 18/11/2026 (Amine) : les testeurs Trista aussi (autorisation des marques) → option « – testeur » de la fiche
        testeur = bool(re.search(r"\btester\b", nom, re.I))
        if len(ean) < 8 or ean.lstrip("0") in eans_soleluna or EXCLUS_TRISTA.search(re.sub(r"\btester\b", " ", nom, flags=re.I)):
            continue
        marque, reste = marque_trista(nom, marques)
        if not marque:
            continue
        reste = re.sub(r"\s*\btester\b\s*", " ", reste, flags=re.I).strip()
        vm = re.search(r"(\d+(?:[.,]\d+)?)\s*ml\b", reste, re.I)
        if not vm:
            continue
        vol = vm.group(1).replace(",", ".")
        g = re.search(r"\((U|M|L|W)\)", reste[:vm.start()])
        if g:
            titre, typ, sexe = reste[:g.start()].strip(), reste[g.end():vm.start()].strip().lower(), g.group(1).upper()
        else:  # pas de genre indiqué : le type (EDP, Parfum…) sépare le titre
            avant = reste[:vm.start()]
            pos = min((m.start() for motif, _ in TYPES_TRISTA for m in [re.search(motif, avant, re.I)] if m), default=None)
            if pos is None:
                continue
            titre, typ, sexe = avant[:pos].strip(), avant[pos:].strip().lower(), "U"
        type_sl = next((t for motif, t in TYPES_TRISTA if re.search(motif, typ)), None)
        if not type_sl:
            continue
        if not titre:
            continue
        lignes.append({"ID": "T" + ean, "BRAND": marque, "TITLE": nom_propre(titre), "TYPE": type_sl,
                       "SEX": {"U": "UNI", "M": "M", "L": "W", "W": "W"}[sexe], "VOLUME": "%s ml" % vol.rstrip("0").rstrip(".") if "." in vol else "%s ml" % vol,
                       "SET": "", "STOCK": l.get("stock") or "0", "PRICE": l.get("price"), "EAN": ean,
                       "TESTER": "1" if testeur else "0", "DAMAGED": "", "SHADE": ""})
    # 15/11/2026 : un même parfum peut venir sous deux EAN avec deux genres (« (L) » et « (U) ») : un seul genre par parfum,
    # celui indiqué le plus souvent, « mixte » seulement si rien d'autre (sinon deux fiches pour le même parfum)
    from collections import Counter
    genres = defaultdict(Counter)
    for l in lignes:
        genres[(l["BRAND"], _cle_titre(l["TITLE"]), l["TYPE"])][l["SEX"]] += 1
    for l in lignes:
        c = genres[(l["BRAND"], _cle_titre(l["TITLE"]), l["TYPE"])]
        precis = [g for g, _ in c.most_common() if g != "UNI"]
        l["SEX"] = precis[0] if precis else "UNI"
    return lignes


def _cle_titre(t):
    n = _norm(t).replace("&", " and ")
    n = re.sub(r"[^a-z0-9]+", " ", n).strip()
    # 19/11/2026 (Torino21, Naxos) : « JTC Torino21 » = « ATP Torino 21 », « XJ 1861 Naxos » = « 1861 Naxos » : préfixes de collection Xerjoff
    # ignorés et « mot 21 » = « mot21 », pour reconnaître le même parfum malgré deux EAN et deux écritures
    n = re.sub(r"\b(jtc|atp|xj)\b", " ", n)
    # 19/11/2026 (contrôle de tous les parfums) : mots de gamme ou d'emballage que l'un des deux grossistes écrit et pas l'autre
    n = re.sub(r"\b(v collection|shooting stars|the narcotics|refillable|edition|collection)\b", " ", n)
    n = re.sub(r"\bcasamorati 1888 (?=[a-z])", "casamorati ", n)
    n = re.sub(r"\b1888 1888\b", "1888", n)
    n = re.sub(r"\bjoy by dior\b", "joy", n)
    n = re.sub(r"\bcalvin klein ck\b", "calvin klein", n)
    n = re.sub(r"\bfor man\b", "for men", n)
    n = re.sub(r"([a-z])\s+(\d)", r"\1\2", n)
    mots = n.split()
    mots = [m for i, m in enumerate(mots) if i == 0 or m != mots[i - 1]]  # « 1888 1888 » → « 1888 »
    return " ".join(sorted(mots))  # même parfum, mots dans un autre ordre (« Dylan Blue Pour Homme » / « Pour Homme Dylan Blue »)


def cle_fiche(p):
    """(titre, type) sans le genre : même parfum, quel que soit le genre écrit par le grossiste."""
    if " — " not in p["titre_fr"]:
        return None
    t, typ = p["titre_fr"].split(" — ", 1)
    typ = re.sub(r" (pour femme|pour homme|mixte|pour enfant)$", "", typ)
    typ = re.sub(r"^extrait de parfum$", "parfum", typ.lower())  # 19/11/2026 : Trista « Extrait de Parfum » = SoleLuna « Parfum »
    return (_cle_titre(t), typ)


def ajouter_sur_commande(produits, lignes_sl, r, photos):
    """Crée (ou complète) les fiches des parfums du 2e grossiste absents de SoleLuna. Renvoie un bilan ou None."""
    rb = reglages_bons_plans()
    if not rb["actif"]:
        return {"fiches": 0, "formats": 0, "completees": 0}
    eans = {re.sub(r"\D", "", l.get("EAN") or "").lstrip("0") for l in lignes_sl}
    lignes = lignes_trista_seules(eans)
    if lignes is None:
        return None
    groupes = defaultdict(list)
    for l in lignes:
        groupes[cle_groupe(l)].append(l)
    par_handle = {p["handle"]: p for p in produits}
    par_cle = {}
    for q in produits:
        c = cle_fiche(q)
        if c and not q["teintes"]:
            par_cle.setdefault(c, q)
    k = 1 / (1 + r["tva"]) - r.get("paiement_pct", 0)
    bilan = {"fiches": 0, "formats": 0, "completees": 0}
    for g in groupes.values():
        p = produit(g, r, photos, normaux_attente_auto=False)  # prix du 2e grossiste calculés d'abord, flacon « épuisé » ensuite
        for v in p["variantes"]:
            achat, stock = sl.nombre(v["_achat"]), max(0, int(sl.nombre(v["stock"])))
            frais = rb["envoi_eur"] + r.get("emballage_eur", 0) + r.get("envoi_client_eur", 0)  # 20/11/2026 : + emballage + envoi client
            base = achat * (1 + rb["majoration_pct"]) + frais + r.get("paiement_fixe", 0)
            prix = sl.arrondi_90_haut((base + rb["benefice_eur"]) / k)
            # 14/11/2026 (Amine) : sur ses propres fiches, format normal (« 100 ml ») et la fiche dit « Bon plan » (étiquette
            # sur-commande → note du thème) ; ajouté à une fiche SoleLuna, le format porte « · Bon plan » (voir plus bas)
            v.update(sku=PREFIXE_SUR_COMMANDE + v["ean"].lstrip("0"), prix="%.2f" % prix, stock=str(stock),
                     cout_ht="%.2f" % (achat * (1 + rb["majoration_pct"]) + frais), bon_plan=True,
                     sur_commande=True, _net="%.2f" % (prix * k - base))
        existante = par_handle.get(p["handle"])
        fusion = False
        if not existante and cle_fiche(p) in par_cle:  # même parfum chez SoleLuna, genre écrit autrement
            existante, fusion = par_cle[cle_fiche(p)], True
        if existante and not existante["teintes"]:  # même parfum déjà chez SoleLuna sous un autre EAN : formats ajoutés
            # 19/11/2026 : un format SoleLuna épuisé (sans option Bon plan) n'empêche plus d'ajouter le même format Trista
            formats = {v["format_fr"].split(" · ")[0] for v in existante["variantes"]
                       if " · " in v["format_fr"] or int(sl.nombre(v.get("stock") or 0)) > 0
                       or any(w["format_fr"].startswith(v["format_fr"] + " · ") for w in existante["variantes"])}
            normaux = {v["format_fr"]: float(v.get("prix") or 0) for v in existante["variantes"] if " – " not in v["format_fr"]
                       and " · " not in v["format_fr"]}

            def utile(v):  # 18/11/2026 : un testeur n'est proposé que s'il coûte moins cher que le flacon normal de même contenance
                if not v["format_fr"].endswith(" – testeur"):
                    return True
                ref = normaux.get(v["format_fr"][:-len(" – testeur")])
                return not ref or float(v["prix"]) < ref
            ajout = [dict(v, format_fr=v["format_fr"] + BON_PLAN_FR, format_nl=v["format_nl"] + BON_PLAN_NL,
                          sku=(PREFIXE_SUR_COMMANDE_FUSION if fusion else PREFIXE_SUR_COMMANDE) + v["ean"].lstrip("0"))
                     for v in p["variantes"] if v["format_fr"].split(" · ")[0] not in formats and utile(v)]
            if ajout:
                existante["variantes"] += ajout
                existante["tags"] = ", ".join([x for x in existante["tags"].split(", ") if x and x != "bon-plan"] + ["bon-plan"])
                bilan["completees"] += 1
                bilan["formats"] += len(ajout)
            continue
        if existante:
            continue
        ajouter_normaux_attente(p["variantes"])  # 22/11/2026 : jamais une fiche « testeur seul »
        p["tags"] = ", ".join([x for x in p["tags"].split(", ") if x] + ["bon-plan", "sur-commande"])
        p["sur_commande"] = True
        produits.append(p)
        par_handle[p["handle"]] = p
        bilan["fiches"] += 1
        bilan["formats"] += len(p["variantes"])
    return bilan


_RICHES = None
_PROFILS = None

# 17/11/2026 : libellés du profil (mêmes valeurs que theme_rk/snippets/qk-profil.liquid), FR puis NL
LIB = {
    "s": {"printemps": ("printemps", "lente"), "ete": ("été", "zomer"), "automne": ("automne", "herfst"), "hiver": ("hiver", "winter")},
    "t": {"legere": ("légère", "licht"), "moyenne": ("moyenne", "gemiddeld"), "longue": ("longue", "lang"),
          "journee": ("toute la journée", "de hele dag"), "lendemain": ("jusqu'au lendemain", "tot de volgende dag")},
    "si": {"discret": ("discret", "subtiel"), "modere": ("modéré", "gemiddeld"), "fort": ("prononcé", "sterk"),
           "tres_fort": ("très prononcé", "zeer sterk")},
    "o": {"quotidien": ("tous les jours", "elke dag"), "bureau": ("le bureau", "kantoor"), "rdv": ("un rendez-vous", "een date"),
          "diner": ("un dîner", "een etentje"), "soiree": ("les soirées", "uitgaan"), "mariage": ("un mariage", "een bruiloft"),
          "sport": ("le sport", "sport"), "vacances": ("les vacances", "vakantie"), "chic": ("un événement chic", "een chique gelegenheid"),
          "detente": ("la détente", "ontspannen")},
    "v": {"cozy": ("enveloppant", "knus"), "sensual": ("sensuel", "sensueel"), "elegant": ("élégant", "elegant"),
          "energetic": ("énergique", "energiek"), "romantic": ("romantique", "romantisch"), "calm": ("apaisant", "rustgevend"),
          "playful": ("joueur", "speels"), "fresh": ("frais", "fris"), "bold": ("audacieux", "gedurfd"), "mysterious": ("mystérieux", "mysterieus")},
    "ac": {"aldehyde": ("aldéhydé", "aldehydisch"), "amande": ("amande", "amandel"), "ambre": ("ambré", "amber"), "animal": ("animal", "animaal"),
           "aquatique": ("aquatique", "aquatisch"), "aromatique": ("aromatique", "aromatisch"), "balsamique": ("balsamique", "balsamico"),
           "alcool": ("liqueur", "likeur"), "caramel": ("caramel", "karamel"), "chocolat": ("chocolat", "chocolade"), "cannelle": ("cannelle", "kaneel"),
           "agrumes": ("agrumes", "citrus"), "coco": ("noix de coco", "kokos"), "cafe": ("café", "koffie"), "terreux": ("terreux", "aards"),
           "floral": ("floral", "bloemig"), "frais": ("frais", "fris"), "epice_frais": ("épicé frais", "fris kruidig"), "fruite": ("fruité", "fruitig"),
           "gourmand": ("gourmand", "gourmand"), "vert": ("vert", "groen"), "miel": ("miel", "honing"), "iris": ("iris", "iris"),
           "jasmin": ("jasmin", "jasmijn"), "lacte": ("lacté", "melkachtig"), "lavande": ("lavande", "lavendel"), "cuir": ("cuir", "leer"),
           "mousse": ("mousse", "mossig"), "muguet": ("muguet", "lelietje-van-dalen"), "musque": ("musqué", "musk"), "noisette": ("noisette", "nootachtig"),
           "oud": ("oud", "oud"), "ozonique": ("ozonique", "ozonisch"), "patchouli": ("patchouli", "patchoeli"), "peche": ("pêche", "perzik"),
           "pistache": ("pistache", "pistache"), "poudre": ("poudré", "poederig"), "rose": ("rose", "roos"), "fume": ("fumé", "rokerig"),
           "epice_doux": ("épicé doux", "zacht kruidig"), "sucre": ("sucré", "zoet"), "the": ("thé", "thee"), "tabac": ("tabac", "tabak"),
           "tropical": ("tropical", "tropisch"), "tubereuse": ("tubéreuse", "tuberoos"), "vanille": ("vanillé", "vanille"),
           "violette": ("violette", "viooltje"), "epice_chaud": ("épicé chaud", "warm kruidig"), "fleurs_blanches": ("fleurs blanches", "witte bloemen"),
           "boise": ("boisé", "houtig"), "fleurs_jaunes": ("fleurs jaunes", "gele bloemen")},
}


def profil_fi(handle):
    """Profil Fragrance Index de la fiche (config/profils_parfums.json), y compris sous une ancienne adresse (« -2 »)."""
    global _PROFILS
    if _PROFILS is None:
        import json, os
        f = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "profils_parfums.json")
        P = json.load(open(f, encoding="utf-8"))["parfums"] if os.path.exists(f) else {}
        _PROFILS = dict(P)
        for h, v in P.items():
            _PROFILS.setdefault(re.sub(r"-\d+$", "", h), v)
    return _PROFILS.get(handle)


def texte_profil(p, nl):
    """Bloc HTML de la description : pyramide, accords, ambiance, saison, tenue, sillage, occasions, année, parfumeur."""
    i = 1 if nl else 0
    e = lambda x: html.escape(x, quote=False)  # noqa: E731
    lib = lambda cle, codes: [LIB[cle][c][i] for c in codes if c in LIB[cle]]  # noqa: E731
    morceaux = []
    n = p.get("nn" if nl else "nf") or {}
    lignes = [(("Notes de tête", "Topnoten"), n.get("t")), (("Notes de cœur", "Hartnoten"), n.get("c")),
              (("Notes de fond", "Basisnoten"), n.get("f")), (("Notes", "Geurnoten"), n.get("n"))]
    lignes = ["<strong>%s :</strong> %s" % (e(k[i]), e(", ".join(v))) if not nl else "<strong>%s:</strong> %s" % (e(k[i]), e(", ".join(v)))
              for k, v in lignes if v]
    if lignes:
        morceaux.append("<h3>%s</h3><p>%s</p>" % ("Geurnoten" if nl else "Notes olfactives", "<br>".join(lignes)))
    f = []
    sep = ": " if nl else " : "
    if p.get("ac"):
        f.append(("Geurfamilie" if nl else "Famille olfactive") + sep + ", ".join(lib("ac", p["ac"])))
    if p.get("v"):
        f.append(("Sfeer" if nl else "Ambiance") + sep + ", ".join(lib("v", p["v"])))
    if p.get("s"):
        f.append(("Ideaal seizoen" if nl else "Saison idéale") + sep + ", ".join(lib("s", p["s"])))
    if p.get("t") in LIB["t"]:
        f.append(("Houdbaarheid" if nl else "Tenue") + sep + LIB["t"][p["t"]][i])
    if p.get("si") in LIB["si"]:
        f.append("Sillage" + sep + LIB["si"][p["si"]][i])
    if p.get("o"):
        f.append(("Ideaal voor" if nl else "Idéal pour") + sep + ", ".join(lib("o", p["o"])))
    if p.get("a"):
        f.append(("Uitgebracht in" if nl else "Sorti en") + " %d" % p["a"])
    if p.get("pf"):
        f.append(("Parfumeur" if len(p["pf"]) == 1 else ("Parfumeurs" if not nl else "Parfumeurs")) + sep + ", ".join(p["pf"]))
    if f:
        morceaux.append("<p>%s.</p>" % e(". ".join(x[:1].upper() + x[1:] for x in f)))
    # sur la fiche, le bloc « profil » montre déjà tout : ce texte y est masqué (CSS), il sert au chat et aux moteurs
    return '<div class="qk-desc-profil">%s</div>' % "".join(morceaux) if morceaux else ""


def descriptions_riches():
    """config/descriptions_parfums.json : descriptions vérifiées des parfums phares. Prises en compte seulement si « actif » est vrai
    (préparées le 10/11/2026, à activer en décembre quand les minutes GitHub du mois sont rechargées)."""
    global _RICHES
    if _RICHES is None:
        import json, os
        f = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "descriptions_parfums.json")
        d = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}
        _RICHES = d.get("parfums", {}) if d.get("actif") else {}
    return _RICHES


def coupe155(d):
    return d if len(d) <= 155 else d[:152].rsplit(" ", 1)[0] + "…"


def seo_textes(t_fr, t_nl, r, vols=None):
    """Titre (≤ 60 caractères) et méta-description (≤ 155) pour Google, FR + NL.
    09/11/2026 : plus de « | Qosmi » à la fin : Google Shopping reprend ce titre tel quel (et Google ajoute déjà
    le nom du site dans ses résultats). Trop long : on enlève « pour homme/femme », puis EDP/EDT, puis on coupe au mot."""
    import re as _re

    def titre(t):
        t = t.replace(" — ", " ").replace("— ", "")
        if len(t) <= 60:
            return t
        t2 = _re.sub(r" (pour (homme|femme|enfant)s?|mixte|voor (heren|dames|kinderen)|unisex)$", "", t)
        if len(t2) <= 60:
            return t2
        t3 = t2.replace("Eau de Parfum", "EDP").replace("Eau de Toilette", "EDT")
        return t3 if len(t3) <= 60 else t3[:61].rsplit(" ", 1)[0]

    def coupe(d):
        return d if len(d) <= 155 else d[:152].rsplit(" ", 1)[0] + "…"
    n_fr, n_nl = t_fr.replace(" — ", ", ").replace("— ", ""), t_nl.replace(" — ", ", ").replace("— ", "")
    v = sorted(set(vols or []), key=lambda x: float(_re.sub(r"[^0-9,.]", "", x).replace(",", ".") or 0))
    f_fr = (", " + joli_liste(v, "et")) if v else ""
    f_nl = (", " + joli_liste(v, "en")) if v else ""
    return {"seo_titre_fr": titre(t_fr), "seo_titre_nl": titre(t_nl),
            "seo_desc_fr": coupe("%s%s. 100 %% authentique et neuf, livré partout en Belgique. Paiement Bancontact." % (n_fr, f_fr)),
            "seo_desc_nl": coupe("%s%s. 100%% origineel en nieuw, geleverd in heel België. Betalen met Bancontact." % (n_nl, f_nl))}


def photos_officielles(produits):
    """Photos autorisées, prioritaires sur celles de Wholesale-Fragrances :
    - sites des marques (config/photos_marques.json : Mancera, Montale, Xerjoff ; config/photos_acquadiparma.json, 2400 px, 05/11/2026) ;
    - revendeurs qui ont donné leur accord : Parfumerie.be (config/photos_parfumerie.json, 2000 px, 05/11/2026),
      Parfuma (config/photos_parfuma.json, 1000 px, 05/11/2026), Riklis Karto (config/photos_riklis.json, 2048 px, 05/11/2026) et Skins (config/photos_skins.json, 1200 px, 05/11/2026).
    Correspondance par EAN d'abord, sinon par nom du parfum (testeurs compris) ; à égalité, la plus grande photo."""
    import photos_marques as pm
    dossier = os.path.dirname(sl.SITE)
    sources = []  # (qualité, par_ean, par_nom, marques limitées ou None)
    for nom, qualite in (("photos_corrections.json", 9), ("photos_deparfumeur.json", 7), ("photos_fi.json", 6), ("photos_hd.json", 5), ("photos_coffrets.json", 5), ("photos_aos.json", 3.5), ("photos_nose.json", 4), ("photos_elo.json", 4), ("photos_creed.json", 4), ("photos_ch.json", 4), ("photos_puig.json", 3.5), ("photos_notino.json", 3), ("photos_dg.json", 4), ("photos_jm.json", 3.5), ("photos_mm.json", 3.5), ("photos_tfi.json", 3.5), ("photos_ck.json", 3.5), ("photos_tt.json", 3.5), ("photos_lvmh.json", 3.5), ("photos_m2.json", 3.5), ("photos_m3.json", 3.5), ("photos_rosendo.json", 3.5), ("photos_retirees.json", 3.5), ("photos_manque.json", 3.5), ("photos_trouvees.json", 3.5), ("photos_fragrantica.json", 3), ("photos_ici.json", 2.5), ("photos_bijenkorf.json", 2.5), ("photos_acquadiparma.json", 4), ("photos_parfuma.json", 1.5), ("photos_parfumerie.json", 3), ("photos_riklis.json", 3), ("photos_skins.json", 2), ("photos_trista.json", 2), ("photos_marques.json", None)):
        chemin = os.path.join(dossier, nom)
        if not os.path.exists(chemin):
            continue
        ph = json.load(open(chemin, encoding="utf-8"))
        marques = {m.lower() for m in ph["marques"]} if "marques" in ph else None
        sources.append((qualite, ph.get("par_ean", {}), ph.get("par_nom", {}), marques, ph.get("par_fiche", {}),
                        bool(ph.get("par_fiche_prioritaire"))))
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
            for qualite, par_ean, par_nom, marques, par_fiche, fiche_prio in sources:
                if marques is not None and m not in marques:
                    continue
                q = qualite if qualite is not None else (1 if m == "xerjoff" else 2)  # photos du site Xerjoff : 590 px
                u = par_ean.get(v["ean"].lstrip("0"))
                if u:
                    choix.append((2, q, u))
                # 22/11/2026 : « par_fiche_prioritaire » (photos vérifiées à l'œil fiche par fiche) compte comme une correspondance EAN
                if fiche_prio and par_fiche.get(p["handle"]) and p.get("type_fr") != "Coffrets":
                    choix.append((2, q, par_fiche[p["handle"]]))
                u = par_nom.get(cle) or par_fiche.get(p["handle"])  # par_fiche : même parfum vérifié nom + type
                if p.get("type_fr") == "Coffrets":  # 10/11/2026 : un coffret seulement avec SA photo (par EAN), jamais celle du flacon seul
                    u = None
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
    global BILAN_SUR_COMMANDE
    BILAN_SUR_COMMANDE = ajouter_sur_commande(produits, lignes, r, photos)
    n_off = photos_officielles(produits)
    global BILAN_BONS_PLANS
    BILAN_BONS_PLANS = ajouter_bons_plans(produits, r)
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
             .replace(" – boîte abîmée", " – beschadigde doos").replace(BON_PLAN_FR, BON_PLAN_NL)
             .replace(SUR_COMMANDE_FR, SUR_COMMANDE_NL))


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

ECART_MAX_TESTEUR_EUR = 20  # 19/11/2026 (Amine) : un testeur coûte au plus 20 € de moins que le flacon normal


def plafond_testeurs(produits, ecart=ECART_MAX_TESTEUR_EUR):
    """19/11/2026 (Amine : « un tester soit moins cher de max 20 euro entre le normal et le tester ») : sur chaque fiche,
    le testeur d'une contenance est remonté à (flacon normal le moins cher de même contenance et teinte − 20 €) quand son
    prix calculé est plus bas. Le bénéfice ne fait qu'augmenter. Une fiche sans flacon normal garde le prix calculé."""
    n = 0
    for p in produits:
        normaux = {}
        for v in p["variantes"]:
            if " – " in v["format_fr"]:
                continue
            k = (v["format_fr"].split(" · ")[0], v.get("teinte") or "")
            pr = float(v.get("prix") or 0)
            if pr > 0:
                normaux[k] = min(normaux.get(k, pr), pr)
        for v in p["variantes"]:
            if " – testeur" not in v["format_fr"]:
                continue
            ref = normaux.get((v["format_fr"].split(" – ")[0], v.get("teinte") or ""))
            pr = float(v.get("prix") or 0)
            if ref and 0 < pr < ref - ecart:
                v["prix"] = "%.2f" % round(ref - ecart, 2)
                n += 1
    return n
