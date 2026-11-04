"""Direction A (« sobre et luxe, Mimi discrète », choisie par Amine le 04/11/2026) appliquée au thème Horizon.

construire(fichiers, police) reçoit le contenu actuel des fichiers du thème publié et renvoie les fichiers modifiés.
Rien d'autre n'est touché : les sections et blocs gardent les réglages d'Horizon qui ne sont pas listés ici.
"""
import copy, json

NOIR, GRIS, TRAIT = "#111111", "#444444", "#E6E6E6"
FICHIERS = ["config/settings_data.json", "sections/header-group.json", "sections/footer-group.json",
            "templates/index.json", "templates/product.json"]


def lire(texte):
    i = texte.find("{")
    return texte[:i], json.loads(texte[i:])


def ecrire(entete, d):
    return entete + json.dumps(d, ensure_ascii=False, indent=2)


def texte_bloc(modele, texte, preset="rte", couleur=None):
    b = copy.deepcopy(modele)
    b["settings"]["text"] = texte
    b["settings"]["type_preset"] = preset
    if couleur is not None:
        b["settings"]["text_color"] = couleur
    b["blocks"] = {}
    b.pop("name", None)
    return b


def construire(fichiers, police="jost"):
    out = {}
    # ---------- réglages généraux ----------
    e, d = lire(fichiers["config/settings_data.json"])
    c = d["current"]
    c.update({
        "type_body_font": "%s_n4" % police, "type_subheading_font": "%s_n5" % police,
        "type_heading_font": "%s_n5" % police, "type_accent_font": "%s_n5" % police,
        "type_size_paragraph": "16", "type_case_h1": "uppercase", "type_case_h2": "uppercase",
        "color_palette": {"background": "#ffffff", "foreground": NOIR, "color1": GRIS, "color2": TRAIT},
        "page_width": "wide", "card_hover_effect": "subtle-zoom",
        "button_border_radius_primary": 0, "button_border_radius_secondary": 0, "badge_corner_radius": 0,
        "badge_text_transform": "uppercase", "card_corner_radius": 0, "product_corner_radius": 0,
        "inputs_border_radius": 0, "popover_border_radius": 0, "variant_button_radius": 0,
        "variant_button_width": "default-width-buttons", "badge_sale_background_color": NOIR,
        "badge_sale_text_color": "#ffffff",
        "logo": "shopify://shop_images/qosmi-logo.png", "logo_inverse": "shopify://shop_images/qosmi-logo-blanc.png",
        "favicon": "shopify://shop_images/qosmi-favicon.png", "logo_height": 30, "logo_height_mobile": 22,
    })
    out["config/settings_data.json"] = ecrire(e, d)

    # ---------- en-tête ----------
    e, d = lire(fichiers["sections/header-group.json"])
    for s in d["sections"].values():
        if s["type"] == "header-announcements":
            for b in s["blocks"].values():
                if b["type"] == "_announcement":
                    b["settings"].update({"text": "Livraison partout en Belgique · 6,95 € · Parfums 100 % authentiques",
                                          "case": "uppercase"})
        if s["type"] == "header":
            s["settings"].update({"logo_position": "center", "menu_position": "left", "search_position": "right",
                                  "show_country": False, "show_language": True, "divider_width": 1,
                                  "enable_sticky_header": "always"})
            m = s["blocks"].get("header-menu")
            if m:
                m["settings"].update({"menu": "main-menu", "type_case_primary_link": "uppercase",
                                      "type_font_primary_size": "0.8125rem"})
    out["sections/header-group.json"] = ecrire(e, d)

    # ---------- pied de page ----------
    e, d = lire(fichiers["sections/footer-group.json"])
    for s in d["sections"].values():
        for b in s.get("blocks", {}).values():
            if b["type"] == "group":
                for t in b.get("blocks", {}).values():
                    if "Join our email list" in t["settings"].get("text", ""):
                        t["settings"]["text"] = "<h2>Nouveautés et offres</h2>"
                    elif "exclusive deals" in t["settings"].get("text", ""):
                        t["settings"]["text"] = "<p>Un e-mail par mois, pas plus.</p>"
            if b["type"] == "email-signup":
                b["settings"]["label"] = "S'inscrire"
    out["sections/footer-group.json"] = ecrire(e, d)

    # ---------- accueil ----------
    e, d = lire(fichiers["templates/index.json"])
    hero_id = next(k for k, s in d["sections"].items() if s["type"] == "hero")
    hero = d["sections"][hero_id]
    tid = next(k for k, b in hero["blocks"].items() if b["type"] == "text")
    bid = next(k for k, b in hero["blocks"].items() if b["type"] == "button")
    modele_texte = hero["blocks"][tid]
    blanc = hero["blocks"][tid]["settings"].get("text_color", "{{ settings.color_palette.background }}")
    hero["blocks"]["qosmi_surtitre"] = texte_bloc(modele_texte, "<p>Parfums de marque et de niche</p>", "rte", blanc)
    hero["blocks"]["qosmi_surtitre"]["settings"]["case"] = "uppercase"
    hero["blocks"][tid]["settings"].update({"text": "<h1>Ton parfum, au juste prix.</h1>", "type_preset": "h1"})
    hero["blocks"][bid]["settings"].update({"label": "Découvrir les parfums", "link": "shopify://collections/parfums"})
    hero["block_order"] = ["qosmi_surtitre", tid, bid]
    hero["settings"].update({"background_color": "#2B2B2B", "section_height": "large",
                             "horizontal_alignment_flex_direction_column": "flex-start"})
    pl_id = next(k for k, s in d["sections"].items() if s["type"] == "product-list")
    pl = d["sections"][pl_id]

    def liste(collection, titre, bouton):
        s = copy.deepcopy(pl)
        s["settings"]["collection"] = collection
        h = s["blocks"]["static-header"]
        for b in h["blocks"].values():
            if b["type"] == "_product-list-text":
                b["settings"]["text"] = "<h3>%s</h3>" % titre
            if b["type"] == "_product-list-button":
                b["settings"]["label"] = bouton
        for b in s["blocks"]["static-product-card"]["blocks"].values():
            if b["type"] == "_product-card-gallery":
                b["settings"]["image_ratio"] = "portrait"
        return s

    d["sections"][pl_id] = liste("niche", "Les plus demandés", "Tout voir")
    d["sections"]["qosmi_testeurs"] = liste("testeurs", "Testeurs : le même parfum, moins cher", "Voir les testeurs")
    edito = {"type": "section", "blocks": {
        "qosmi_edito_sur": texte_bloc(modele_texte, "<p>Bon à savoir</p>", "rte", GRIS),
        "qosmi_edito_titre": texte_bloc(modele_texte, "<h2>Un testeur, c'est le même parfum. Juste sans la boîte.</h2>", "h3", NOIR),
        "qosmi_edito_texte": texte_bloc(modele_texte, "<p>Les marques fabriquent des flacons pour les parfumeries, à faire "
                                        "sentir en magasin. Le parfum est identique ; l'emballage est simple, parfois sans "
                                        "bouchon. Résultat : le même parfum, moins cher.</p>", "rte", GRIS),
    }, "block_order": ["qosmi_edito_sur", "qosmi_edito_titre", "qosmi_edito_texte"], "settings": {}}
    edito["blocks"]["qosmi_edito_sur"]["settings"]["case"] = "uppercase"
    for k in ("qosmi_edito_titre", "qosmi_edito_texte"):
        edito["blocks"][k]["settings"]["max_width"] = "narrow"
    reassurance = {"type": "section", "blocks": {
        "qosmi_r1": texte_bloc(modele_texte, "<p><strong>100 % AUTHENTIQUES</strong><br>Des parfums originaux, neufs, avec "
                               "leur facture d'achat.</p>", "rte", NOIR),
        "qosmi_r2": texte_bloc(modele_texte, "<p><strong>LIVRÉS EN 4 À 7 JOURS</strong><br>Partout en Belgique, 6,95 € la "
                               "commande.</p>", "rte", NOIR),
        "qosmi_r3": texte_bloc(modele_texte, "<p><strong>14 JOURS POUR CHANGER D'AVIS</strong><br>Flacon non ouvert ? Tu le "
                               "renvoies, on te rembourse.</p>", "rte", NOIR),
    }, "block_order": ["qosmi_r1", "qosmi_r2", "qosmi_r3"], "settings": {"content_direction": "row", "gap": 32}}
    d["sections"]["qosmi_reassurance"] = reassurance
    d["sections"]["qosmi_edito"] = edito
    d["order"] = [hero_id, pl_id, "qosmi_reassurance", "qosmi_testeurs", "qosmi_edito"]
    out["templates/index.json"] = ecrire(e, d)

    # ---------- fiche produit ----------
    e, d = lire(fichiers["templates/product.json"])
    main = d["sections"]["main"]
    det = main["blocks"]["product-details"]
    grp_id = next(k for k, b in det["blocks"].items() if b["type"] == "group")
    grp = det["blocks"][grp_id]
    titre_id = next(k for k, b in grp["blocks"].items() if b["type"] == "text")
    modele = grp["blocks"][titre_id]
    grp["blocks"]["qosmi_marque"] = texte_bloc(modele, "<p>{{ closest.product.vendor }}</p>", "rte", GRIS)
    grp["block_order"] = ["qosmi_marque"] + [x for x in grp["block_order"] if x != "qosmi_marque"]
    desc_id = next(k for k, b in det["blocks"].items() if b["type"] == "text")
    det["blocks"]["qosmi_livraison"] = texte_bloc(det["blocks"][desc_id], "<p>Livraison partout en Belgique en 4 à 7 jours "
                                                  "ouvrables · 6,95 €</p>", "rte", NOIR)
    det["blocks"]["qosmi_garanties"] = texte_bloc(det["blocks"][desc_id], "<p>✓ Parfum original, neuf, avec facture d'achat<br>"
                                                  "✓ 14 jours pour changer d'avis (flacon non ouvert)<br>"
                                                  "✓ Paiement Bancontact, carte ou Apple Pay</p>", "rte", NOIR)
    ordre = [x for x in det["block_order"] if x not in ("qosmi_livraison", "qosmi_garanties")]
    i = ordre.index(next(k for k in ordre if det["blocks"][k]["type"] == "buy-buttons")) + 1
    det["block_order"] = ordre[:i] + ["qosmi_livraison"] + ordre[i:] + ["qosmi_garanties"]
    for b in main["blocks"].values():
        if b["type"] == "disclosures":
            b["settings"]["heading"] = ""
    for s in d["sections"].values():
        if s["type"] == "product-recommendations":
            for b in s["blocks"].values():
                if b["type"] == "text" and "You may also like" in b["settings"].get("text", ""):
                    b["settings"]["text"] = "<h3>Tu aimeras aussi</h3>"
    out["templates/product.json"] = ecrire(e, d)
    return out
