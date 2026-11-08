"""Qosmi « façon Riklis Karto » (demande d'Amine du 07/11/2026) appliqué au thème d'aperçu.

construire(fichiers, marques) reçoit le contenu actuel des fichiers du thème d'aperçu et renvoie
(fichiers_liquid_et_css, fichiers_json) à envoyer, dans cet ordre (les sections doivent exister avant les modèles).
Les sections et la feuille de style propres à Qosmi sont dans theme_rk/ (préfixe qk-).
"""
import copy, json, os

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(os.path.dirname(ICI), "theme_rk")
FICHIERS = ["layout/theme.liquid", "templates/index.json", "templates/product.json", "templates/collection.json",
            "templates/search.json", "sections/header-group.json", "sections/footer-group.json", "templates/cart.json"]
CARTE_TEXTE = "{% render 'qk-carte-texte', product: closest.product %}"
LIVRAISON = "Livraison en Belgique en 3 à 6 jours ouvrables · 2,95 €, offerte dès 2 articles"
# « Le parfum du jour » sur l'accueil (demande d'Amine du 08/11/2026) : grandes marques et parfums très connus, prix habituel.
# Un par jour à tour de rôle ; ceux qui ne sont pas en ligne, en stock et avec photo sont sautés automatiquement.
DU_JOUR = [
    "dior-sauvage-eau-de-toilette-pour-homme", "lancome-la-vie-est-belle-eau-de-parfum-pour-femme",
    "chanel-bleu-de-chanel-eau-de-parfum-pour-homme", "carolina-herrera-good-girl-eau-de-parfum-pour-femme",
    "creed-aventus-eau-de-parfum-pour-homme", "yves-saint-laurent-libre-eau-de-parfum-pour-femme",
    "giorgio-armani-acqua-di-gio-eau-de-parfum-pour-homme", "dior-j-adore-eau-de-parfum-pour-femme",
    "paco-rabanne-1-million-eau-de-toilette-pour-homme", "chanel-coco-mademoiselle-eau-de-parfum-pour-femme",
    "jean-paul-gaultier-le-male-eau-de-toilette-pour-homme", "lancome-idole-eau-de-parfum-pour-femme",
    "parfums-de-marly-layton-eau-de-parfum-mixte", "giorgio-armani-my-way-eau-de-parfum-pour-femme",
    "versace-eros-eau-de-toilette-pour-homme", "chanel-chance-eau-de-parfum-pour-femme",
    "dior-sauvage-elixir-parfum-pour-homme", "yves-saint-laurent-mon-paris-eau-de-parfum-pour-femme",
    "paco-rabanne-invictus-eau-de-toilette-pour-homme", "mugler-angel-eau-de-parfum-pour-femme",
    "hermes-terre-d-hermes-eau-de-toilette-pour-homme", "viktor-rolf-flowerbomb-eau-de-parfum-pour-femme",
    "yves-saint-laurent-y-eau-de-parfum-pour-homme", "dolce-gabbana-light-blue-eau-de-toilette-pour-femme",
    "xerjoff-erba-pura-eau-de-parfum-mixte", "gucci-bloom-eau-de-parfum-pour-femme",
    "dolce-gabbana-the-one-eau-de-parfum-pour-homme", "jean-paul-gaultier-scandal-eau-de-parfum-pour-femme",
    "chanel-allure-homme-sport-eau-extreme-eau-de-parfum-pour-homme", "lancome-la-nuit-tresor-eau-de-parfum-pour-femme",
    "paco-rabanne-phantom-eau-de-toilette-pour-homme", "givenchy-l-interdit-eau-de-parfum-pour-femme",
    "nishane-hacivat-extrait-de-parfum-mixte", "guerlain-shalimar-eau-de-parfum-pour-femme",
    "hugo-boss-boss-bottled-eau-de-parfum-pour-homme", "paco-rabanne-olympea-eau-de-parfum-pour-femme",
    "dior-fahrenheit-eau-de-toilette-pour-homme", "marc-jacobs-daisy-eau-de-toilette-pour-femme",
    "tom-ford-ombre-leather-eau-de-parfum-mixte", "dior-hypnotic-poison-eau-de-parfum-pour-femme",
    "carolina-herrera-bad-boy-eau-de-toilette-pour-homme", "burberry-her-eau-de-parfum-pour-femme",
    "parfums-de-marly-pegasus-eau-de-parfum-pour-homme", "tom-ford-black-orchid-eau-de-parfum-pour-femme",
    "giorgio-armani-code-eau-de-toilette-pour-homme", "jean-paul-gaultier-la-belle-eau-de-parfum-pour-femme",
    "yves-saint-laurent-la-nuit-de-l-homme-eau-de-toilette-pour-homme", "gucci-guilty-eau-de-parfum-pour-femme",
]

# Mise en avant sur l'accueil (demande d'Amine du 08/11/2026) : seulement les maisons choisies le 04/11 (les plus demandées),
# pas les marques ajoutées ensuite parce qu'elles avaient de belles photos. Les parfums arabes : les grands succès.
VEDETTES = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "selection.json"),
                          encoding="utf-8")).get("vedettes") or []
ARABES_VEDETTES = ["lattafa-khamrah-eau-de-parfum-mixte", "armaf-club-de-nuit-intense-man-eau-de-parfum-pour-homme",
                   "lattafa-yara-eau-de-parfum-pour-femme", "lattafa-asad-eau-de-parfum-pour-homme",
                   "afnan-9pm-eau-de-parfum-pour-homme", "al-haramain-amber-oud-gold-edition-eau-de-parfum-mixte",
                   "lattafa-khamrah-qahwa-eau-de-parfum-mixte", "armaf-club-de-nuit-woman-eau-de-parfum-pour-femme",
                   "lattafa-bade-e-al-oud-for-glory-eau-de-parfum-mixte", "rasasi-hawas-eau-de-parfum-pour-homme",
                   "lattafa-hayaati-eau-de-parfum-mixte", "armaf-club-de-nuit-untold-eau-de-parfum-mixte",
                   "afnan-supremacy-silver-eau-de-parfum-pour-homme", "lattafa-ana-abiyedh-eau-de-parfum-mixte",
                   "al-haramain-l-aventure-intense-eau-de-parfum-pour-homme", "lattafa-bade-e-al-oud-sublime-eau-de-parfum-mixte",
                   "armaf-club-de-nuit-milestone-eau-de-parfum-mixte", "lattafa-qaed-al-fursan-eau-de-parfum-mixte",
                   "ajmal-evoke-eau-de-parfum-pour-femme", "lattafa-mayar-eau-de-parfum-pour-femme"]
ANNONCES = ["Livraison offerte dès 2 articles · sinon 2,95 €",
            "Livrée partout en Belgique en 3 à 6 jours ouvrables",
            "Parfums 100 % authentiques et neufs",
            "Plus de 60 maisons, des grands classiques à la niche",
            "Paiement sécurisé : Bancontact, carte, Apple Pay",
            "14 jours pour changer d'avis"]


PARTAGE = """    {%- comment -%}qk-partage{%- endcomment -%}
    {%- unless page_image -%}
      {%- assign qk_partage = images['qosmi-partage.jpg'] -%}
      {%- if qk_partage -%}
        <meta property="og:image" content="https:{{ qk_partage | image_url: width: 1200 }}">
        <meta property="og:image:secure_url" content="https:{{ qk_partage | image_url: width: 1200 }}">
        <meta property="og:image:width" content="1200">
        <meta property="og:image:height" content="630">
        <meta property="og:image:alt" content="Qosmi, parfums de marque et de niche">
        <meta name="twitter:image" content="https:{{ qk_partage | image_url: width: 1200 }}">
      {%- endif -%}
    {%- endunless -%}
"""


FAQ_LD = """    {%- comment -%}qk-faq-ld{%- endcomment -%}
    {%- if template.name == 'article' and article -%}
      {%- if request.locale.iso_code == 'nl' -%}{%- assign qk_faq = article.metafields.qosmi.faq_nl.value -%}{%- else -%}{%- assign qk_faq = article.metafields.qosmi.faq_fr.value -%}{%- endif -%}
      {%- if qk_faq and qk_faq.size > 0 -%}
        <script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{%- for f in qk_faq -%}{"@type":"Question","name":{{ f.q | json }},"acceptedAnswer":{"@type":"Answer","text":{{ f.r | json }}}}{%- unless forloop.last -%},{%- endunless -%}{%- endfor -%}]}</script>
      {%- endif -%}
    {%- endif -%}
"""


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


def snippet_gpsr():
    """Mention GPSR (règlement (UE) 2023/988, art. 19) sur chaque fiche : fabricant ou personne responsable de la marque
    (config/gpsr.json, vérifié par Amine) + consignes de sécurité. Marque absente du fichier : consignes seules."""
    import html
    chemin = os.path.join(os.path.dirname(ICI), "config", "gpsr.json")
    data = json.load(open(chemin, encoding="utf-8")) if os.path.exists(chemin) else {}
    cas = []
    for marque, d in sorted(data.items()):
        if not d.get("fabricant") or d.get("confiance") == "faible":
            continue
        contact = d.get("contact", "")
        lien = ('<a href="%s" rel="nofollow">%s</a>' % (html.escape(contact if contact.startswith("http") else "mailto:" + contact),
                                                           html.escape(contact.replace("mailto:", "")))) if contact else ""
        cas.append("{%% when %s %%}<p><strong>{{ t_fab }}</strong> : %s, %s%s</p>" % (
            json.dumps(marque), html.escape(d["fabricant"]), html.escape(d["adresse"]), (" · " + lien) if lien else ""))
    return """{%- comment -%} Généré par scripts/theme_rk.py depuis config/gpsr.json — ne pas modifier à la main. {%- endcomment -%}
{%- liquid
  if request.locale.iso_code == 'nl'
    assign t_titre = 'Productveiligheid'
    assign t_fab = 'Fabrikant / verantwoordelijke persoon'
    assign t_avert = 'Ontvlambaar. Buiten bereik van kinderen houden. Niet in de ogen of op geïrriteerde huid sprayen. Uitsluitend voor uitwendig gebruik. Bewaren op een koele plaats, uit de buurt van warmte, vlammen en zonlicht. Lees de ingrediëntenlijst op de verpakking als u allergisch bent.'
  else
    assign t_titre = 'Sécurité du produit'
    assign t_fab = 'Fabricant / personne responsable'
    assign t_avert = "Inflammable. Tenir hors de portée des enfants. Ne pas vaporiser dans les yeux ni sur une peau irritée. Usage externe uniquement. Conserver au frais, à l'abri de la chaleur, des flammes et de la lumière. En cas d'allergie, consultez la liste des ingrédients sur l'emballage."
  endif
-%}
<details class="qk-gpsr">
  <summary>{{ t_titre }}</summary>
  {%- case product.vendor -%}
""" + "\n".join("    " + c for c in cas) + """
  {%- endcase -%}
  <p>{{ t_avert }}</p>
</details>
"""


def construire(fichiers, marques):
    liquides, jsons = fichiers_qk(), {}
    liquides["snippets/qk-gpsr.liquid"] = snippet_gpsr()

    # ---------- feuille de style ----------
    lay = fichiers["layout/theme.liquid"]
    if "qosmi-rk.css" not in lay:
        lay = lay.replace("</head>", "    {{ 'qosmi-rk.css' | asset_url | stylesheet_tag }}\n  </head>", 1)
    # image de partage (réseaux sociaux, WhatsApp) quand la page n'a pas d'image propre (demande d'Amine du 08/11/2026)
    if "qk-partage" not in lay:
        lay = lay.replace("</head>", PARTAGE + "  </head>", 1)
    # FAQ des articles du Journal en données structurées (08/11/2026)
    if "qk-faq-ld" not in lay:
        lay = lay.replace("</head>", FAQ_LD + "  </head>", 1)
    liquides["layout/theme.liquid"] = lay

    # ---------- accueil ----------
    e, d = lire(fichiers["templates/index.json"])
    d["sections"] = {
        "qk_hero": {"type": "qk-hero", "settings": {
            "titre": "Ton parfum,", "titre_doux": "au juste prix.",
            "texte": "Parfums de marque et de niche, 100 % authentiques.", "bouton": "Découvrir",
            "lien": "shopify://collections/parfums", "hauteur": 85,
            "image": "shopify://shop_images/qosmi-hero-ingredients.jpg",
            "video": "shopify://files/videos/qosmi-hero-ingredients-4k.mp4",
            # carrousel : 2e image = « Le parfum du jour » (08/11/2026)
            "dujour_titre": "Le parfum du jour", "dujour_compte": "Prochain parfum dans", "produits": DU_JOUR, "duree": 7}},
        "qk_favoris": {"type": "qk-onglets", "settings": {
            "titre": "Favoris", "nombre": 10, "vedettes": "\n".join(VEDETTES),
            "texte": "Les parfums qu'on nous demande le plus. Une sélection de grandes maisons et de niche, choisie avec soin."},
            "blocks": {
                "o1": {"type": "onglet", "settings": {"collection": "niche", "label": "Niche"}},
                "o2": {"type": "onglet", "settings": {"collection": "parfums-femme", "label": "Femme"}},
                "o3": {"type": "onglet", "settings": {"collection": "parfums-homme", "label": "Homme"}},
                "o4": {"type": "onglet", "settings": {"collection": "parfums-mixtes", "label": "Mixte"}},  # testeurs en suspens (08/11)
                "o5": {"type": "onglet", "settings": {"collection": "parfums-arabes", "label": "Arabes", "produits": ARABES_VEDETTES}}},  # 08/11/2026
            "block_order": ["o1", "o2", "o3", "o4", "o5"]},
        "qk_banniere": {"type": "qk-banniere", "settings": {
            "titre": "Les incontournables", "lien_texte": "Voir la niche", "lien": "shopify://collections/niche",
            "image": "shopify://shop_images/qosmi-banniere-niche.jpg",
            "image_mobile": "shopify://shop_images/qosmi-banniere-niche-mobile.jpg",
            "alt": "Parfums de Marly Layton, Maison Francis Kurkdjian Baccarat Rouge 540, Xerjoff Erba Pura, Nishane Hundred Silent Ways et Creed Aventus"}},
        "qk_tuiles": {"type": "qk-tuiles", "settings": {"titre": ""}, "blocks": {
            "t1": {"type": "tuile", "settings": {"collection": "niche", "titre": "Parfums de niche",
                                                 "produit": "sospiro-vibrato-eau-de-parfum-mixte",
                                                 "sous_titre": "Xerjoff, Nishane, Initio, Parfums de Marly et plus"}},
            "t2": {"type": "tuile", "settings": {"collection": "parfums-homme", "titre": "Parfums homme",  # testeurs en suspens (08/11)
                                                 "produit": "dior-sauvage-elixir-parfum-pour-homme",
                                                 "sous_titre": "Dior, Chanel, Tom Ford et plus"}},
            "t3": {"type": "tuile", "settings": {"collection": "parfums-mixtes", "titre": "Parfums mixtes",
                                                 "produit": "acqua-di-parma-colonia-eau-de-cologne-mixte",
                                                 "sous_titre": "À porter par tout le monde"}},
            "t4": {"type": "tuile", "settings": {"collection": "parfums-femme", "titre": "Parfums femme",
                                                 "produit": "chanel-coco-mademoiselle-eau-de-parfum-pour-femme",
                                                 "sous_titre": "Chanel, Dior, Guerlain et plus"}}},
            "block_order": ["t1", "t2", "t3", "t4"]},
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
        "<p class=\"qk-livraison\">{% if request.locale.iso_code == 'nl' %}Levering in België binnen 3 tot 6 werkdagen · 2,95 €, gratis vanaf 2 artikelen"
        "{% else %}" + LIVRAISON + "{% endif %}</p>")
    det["blocks"]["qk_rassurance"] = liquide(
        "<div class=\"qk-rassurance\">{% if request.locale.iso_code == 'nl' %}"
        "<span>Originele parfum, nieuw, met aankoopfactuur</span><span>14 dagen om van gedacht te veranderen (ongeopende fles)</span>"
        "<span>Betalen met Bancontact, kaart of Apple Pay</span>{% else %}"
        "<span>Parfum original, neuf, avec facture d'achat</span><span>14 jours pour changer d'avis (flacon non ouvert)</span>"
        "<span>Paiement Bancontact, carte ou Apple Pay</span>{% endif %}</div>")
    det["blocks"]["qk_gpsr"] = liquide("{% render 'qk-gpsr', product: closest.product %}")
    ordre = [k for k in det["block_order"] if k in det["blocks"] and not k.startswith("qk_")]
    i = ordre.index(next(k for k in ordre if det["blocks"][k]["type"] == "buy-buttons")) + 1
    det["block_order"] = ordre[:i] + ["qk_livraison", "qk_rassurance", "qk_gpsr"] + ordre[i:]
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
    # ---------- panier : rappel « livraison offerte dès 2 articles » (08/11/2026) ----------
    if "templates/cart.json" in fichiers:
        e, d = lire(fichiers["templates/cart.json"])
        d["sections"]["qk_panier_livraison"] = {"type": "qk-panier-livraison", "settings": {}}
        d["order"] = ["qk_panier_livraison"] + [k for k in d["order"] if k != "qk_panier_livraison"]
        jsons["templates/cart.json"] = ecrire(e, d)

    e, d = lire(fichiers["sections/header-group.json"])
    for s in d["sections"].values():
        if s["type"] == "header":
            s["settings"].update({"localization_position": "left", "divider_width": 1})
    # bandeau d'annonces : section Qosmi qui défile en continu (demande d'Amine du 08/11/2026), à la place de
    # « header-announcements » de Horizon (diaporama à flèches, texte décentré)
    for cle in [k for k, s in d["sections"].items() if s["type"] == "header-announcements"]:
        del d["sections"][cle]
        d["order"] = [k for k in d["order"] if k != cle]
    d["sections"]["qk_annonces"] = {"type": "qk-annonces", "settings": {"messages": "\n".join(ANNONCES), "duree": 45}}
    d["order"] = ["qk_annonces"] + [k for k in d["order"] if k != "qk_annonces"]
    jsons["sections/header-group.json"] = ecrire(e, d)

    # ---------- pied de page ----------
    e, d = lire(fichiers["sections/footer-group.json"])
    d["sections"] = {"qk_pied": {"type": "qk-pied", "settings": {"menu_parfums": "main-menu", "menu_infos": "footer",
                                                                 "email": "contact@qosmi.be"}}}
    d["order"] = ["qk_pied"]
    jsons["sections/footer-group.json"] = ecrire(e, d)
    return liquides, jsons
