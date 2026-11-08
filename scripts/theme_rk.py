"""Qosmi « façon Riklis Karto » (demande d'Amine du 07/11/2026) appliqué au thème d'aperçu.

construire(fichiers, marques) reçoit le contenu actuel des fichiers du thème d'aperçu et renvoie
(fichiers_liquid_et_css, fichiers_json) à envoyer, dans cet ordre (les sections doivent exister avant les modèles).
Les sections et la feuille de style propres à Qosmi sont dans theme_rk/ (préfixe qk-).
"""
import copy, json, os

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(os.path.dirname(ICI), "theme_rk")
FICHIERS = ["layout/theme.liquid", "templates/index.json", "templates/product.json", "templates/collection.json",
            "templates/search.json", "sections/header-group.json", "sections/footer-group.json"]
CARTE_TEXTE = "{% render 'qk-carte-texte', product: closest.product %}"
LIVRAISON = "Livraison partout en Belgique en 6 à 7 jours ouvrables · 6,95 €"


def lire(texte):
    i = texte.find("{")
    return texte[:i], json.loads(texte[i:])


def ecrire(entete, d):
    return entete + json.dumps(d, ensure_ascii=False, indent=2)


def liquide(code):
    return {"type": "custom-liquid", "settings": {"custom_liquid": code}, "blocks": {}}


def fichiers_qk():
    out = {}
    for racine, _, noms in os.walk(DOSSIER):
        for n in noms:
            chemin = os.path.join(racine, n)
            out[os.path.relpath(chemin, DOSSIER).replace(os.sep, "/")] = open(chemin, encoding="utf-8").read()
    return out


def cartes(noeud):
    """Dans toute carte produit d'Horizon : titre + prix remplacés par « marque · prix / nom » (snippet qk-carte-texte)."""
    if isinstance(noeud, dict):
        if noeud.get("type") == "_product-card" and "blocks" in noeud:
            b = noeud["blocks"]
            for k in [k for k, x in b.items() if x["type"] in ("product-title", "price")]:
                del b[k]
            b["qk_texte"] = liquide(CARTE_TEXTE)
            ordre = [k for k in noeud.get("block_order", list(b)) if k in b and k != "qk_texte"]
            noeud["block_order"] = ordre + ["qk_texte"]
            noeud.setdefault("settings", {})["product_card_gap"] = 0
            for x in b.values():  # toutes les photos dans un même cadre 4:5 (sinon chaque carte prend la forme de sa photo)
                if x.get("type") == "_product-card-gallery":
                    x.setdefault("settings", {})["image_ratio"] = "portrait"
        for v in list(noeud.values()):
            cartes(v)
    elif isinstance(noeud, list):
        for v in noeud:
            cartes(v)


def construire(fichiers, marques):
    liquides, jsons = fichiers_qk(), {}

    # ---------- feuille de style ----------
    lay = fichiers["layout/theme.liquid"]
    if "qosmi-rk.css" not in lay:
        lay = lay.replace("</head>", "    {{ 'qosmi-rk.css' | asset_url | stylesheet_tag }}\n  </head>", 1)
    liquides["layout/theme.liquid"] = lay

    # ---------- accueil ----------
    e, d = lire(fichiers["templates/index.json"])
    d["sections"] = {
        "qk_hero": {"type": "qk-hero", "settings": {
            "titre": "Ton parfum,", "titre_doux": "au juste prix.",
            "texte": "Parfums de marque et de niche, 100 % authentiques.", "bouton": "Découvrir",
            "lien": "shopify://collections/parfums", "hauteur": 85,
            "image": "shopify://shop_images/qosmi-hero-ingredients.jpg",
            "video": "shopify://files/videos/72773816287556"}},
        "qk_favoris": {"type": "qk-onglets", "settings": {
            "titre": "Favoris", "nombre": 10,
            "texte": "Les parfums qu'on nous demande le plus. Une sélection de grandes maisons et de niche, choisie avec soin."},
            "blocks": {
                "o1": {"type": "onglet", "settings": {"collection": "niche", "label": "Niche"}},
                "o2": {"type": "onglet", "settings": {"collection": "parfums-femme", "label": "Femme"}},
                "o3": {"type": "onglet", "settings": {"collection": "parfums-homme", "label": "Homme"}},
                "o4": {"type": "onglet", "settings": {"collection": "testeurs", "label": "Testeurs"}}},
            "block_order": ["o1", "o2", "o3", "o4"]},
        "qk_banniere": {"type": "qk-banniere", "settings": {
            "titre": "Les incontournables", "lien_texte": "Voir la niche", "lien": "shopify://collections/niche",
            "image": "shopify://shop_images/qosmi-banniere-niche.jpg",
            "image_mobile": "shopify://shop_images/qosmi-banniere-niche-mobile.jpg",
            "alt": "Parfums de Marly Layton, Maison Francis Kurkdjian Baccarat Rouge 540, Xerjoff Erba Pura, Nishane Hundred Silent Ways et Creed Aventus"}},
        "qk_tuiles": {"type": "qk-tuiles", "settings": {"titre": ""}, "blocks": {
            "t1": {"type": "tuile", "settings": {"collection": "niche", "titre": "Parfums de niche",
                                                 "produit": "sospiro-vibrato-eau-de-parfum-mixte",
                                                 "sous_titre": "Xerjoff, Nishane, Initio, Parfums de Marly et plus"}},
            "t2": {"type": "tuile", "settings": {"collection": "testeurs", "titre": "Testeurs",
                                                 "produit": "tom-ford-private-blend-lost-cherry-eau-de-parfum-mixte",
                                                 "sous_titre": "Le même parfum, sans la boîte, moins cher"}},
            "t3": {"type": "tuile", "settings": {"collection": "parfums-mixtes", "titre": "Parfums mixtes",
                                                 "produit": "acqua-di-parma-colonia-eau-de-cologne-mixte",
                                                 "sous_titre": "À porter par tout le monde"}}},
            "block_order": ["t1", "t2", "t3"]},
        "qk_marques": {"type": "qk-marques", "settings": {
            "titre": "Marques", "liste": "\n".join(marques),
            "texte": "Des parfums originaux et neufs, des grandes maisons aux créateurs de niche."}},
        "qk_apropos": {"type": "qk-texte", "settings": {
            "surtitre": "À propos", "titre": "Qosmi",
            "texte": "<p>Qosmi, c'est une parfumerie en ligne belge, simple et honnête : des parfums 100 % authentiques, "
                     "neufs, au juste prix. On choisit les maisons qu'on aime, des grands classiques aux créateurs de niche, "
                     "et on te les livre partout en Belgique.</p>",
            "lien_texte": "Voir tous les parfums", "lien": "shopify://collections/parfums", "alignement": "centre"}},
    }
    d["order"] = ["qk_hero", "qk_favoris", "qk_banniere", "qk_tuiles", "qk_marques", "qk_apropos"]
    jsons["templates/index.json"] = ecrire(e, d)

    # ---------- fiche produit ----------
    e, d = lire(fichiers["templates/product.json"])
    main = d["sections"]["main"]
    if "media-gallery" in main["blocks"]:
        main["blocks"]["media-gallery"]["settings"].update({"media_columns": "one", "large_first_image": True})
    det = main["blocks"]["product-details"]
    grp_id = next(k for k, b in det["blocks"].items() if b["type"] == "group")
    grp = det["blocks"][grp_id]
    for k in [k for k, b in grp["blocks"].items() if b["type"] == "text"]:
        del grp["blocks"][k]
    grp["blocks"]["qk_titre"] = liquide(
        "{%- assign t = closest.product.title | split: ' — ' -%}{%- assign n = t[0] | remove_first: closest.product.vendor | strip -%}"
        "{%- if n == blank -%}{%- assign n = t[0] -%}{%- endif -%}"
        "<p class=\"qk-marque-produit\">{{ closest.product.vendor }}</p><h1 class=\"qk-titre-produit\">{{ n }}</h1>"
        "{%- if t[1] -%}<p class=\"qk-type-produit\">{{ t[1] }}</p>{%- endif -%}")
    grp["block_order"] = ["qk_titre"] + [k for k in grp.get("block_order", grp["blocks"]) if k in grp["blocks"] and k != "qk_titre"]
    for k in ("qosmi_livraison", "qosmi_garanties"):
        det["blocks"].pop(k, None)
    det["blocks"]["qk_livraison"] = liquide(
        "<p class=\"qk-livraison\">{% if request.locale.iso_code == 'nl' %}Levering in heel België binnen 6 tot 7 werkdagen · 6,95 €"
        "{% else %}" + LIVRAISON + "{% endif %}</p>")
    det["blocks"]["qk_rassurance"] = liquide(
        "<div class=\"qk-rassurance\">{% if request.locale.iso_code == 'nl' %}"
        "<span>Originele parfum, nieuw, met aankoopfactuur</span><span>14 dagen om van gedacht te veranderen (ongeopende fles)</span>"
        "<span>Betalen met Bancontact, kaart of Apple Pay</span>{% else %}"
        "<span>Parfum original, neuf, avec facture d'achat</span><span>14 jours pour changer d'avis (flacon non ouvert)</span>"
        "<span>Paiement Bancontact, carte ou Apple Pay</span>{% endif %}</div>")
    ordre = [k for k in det["block_order"] if k in det["blocks"] and not k.startswith("qk_")]
    i = ordre.index(next(k for k in ordre if det["blocks"][k]["type"] == "buy-buttons")) + 1
    det["block_order"] = ordre[:i] + ["qk_livraison", "qk_rassurance"] + ordre[i:]
    d["sections"]["qk_marque"] = {"type": "qk-texte", "settings": {"mode_marque": True, "alignement": "centre"}}
    d["order"] = [k for k in d["order"] if k != "qk_marque"]
    d["order"].insert(1, "qk_marque")
    for s in d["sections"].values():
        if s["type"] == "product-recommendations":
            for b in s["blocks"].values():
                if b["type"] == "text":
                    b["settings"]["text"] = "<h3>Tu aimeras aussi</h3>"
    cartes(d)
    jsons["templates/product.json"] = ecrire(e, d)

    # ---------- collections et recherche ----------
    for nom in ("templates/collection.json", "templates/search.json"):
        e, d = lire(fichiers[nom])
        cartes(d)
        jsons[nom] = ecrire(e, d)

    # ---------- en-tête ----------
    e, d = lire(fichiers["sections/header-group.json"])
    for s in d["sections"].values():
        if s["type"] == "header":
            s["settings"].update({"localization_position": "left", "divider_width": 1})
        if s["type"] == "header-announcements":
            for b in s["blocks"].values():
                if b["type"] == "_announcement":
                    b["settings"]["text"] = "Livraison partout en Belgique · Parfums 100 % authentiques"
    jsons["sections/header-group.json"] = ecrire(e, d)

    # ---------- pied de page ----------
    e, d = lire(fichiers["sections/footer-group.json"])
    d["sections"] = {"qk_pied": {"type": "qk-pied", "settings": {"menu_parfums": "main-menu", "menu_infos": "footer",
                                                                 "email": "contact@qosmi.be"}}}
    d["order"] = ["qk_pied"]
    jsons["sections/footer-group.json"] = ecrire(e, d)
    return liquides, jsons
