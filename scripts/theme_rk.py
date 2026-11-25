"""Qosmi « façon Riklis Karto » (demande d'Amine du 07/11/2026) appliqué au thème d'aperçu.

construire(fichiers, marques) reçoit le contenu actuel des fichiers du thème d'aperçu et renvoie
(fichiers_liquid_et_css, fichiers_json) à envoyer, dans cet ordre (les sections doivent exister avant les modèles).
Les sections et la feuille de style propres à Qosmi sont dans theme_rk/ (préfixe qk-).
"""
import copy, json, os

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(os.path.dirname(ICI), "theme_rk")
FICHIERS = ["layout/theme.liquid", "templates/index.json", "templates/product.json", "templates/collection.json",
            "templates/search.json", "sections/header-group.json", "sections/footer-group.json", "templates/cart.json",
            "sections/main-collection.liquid", "sections/search-results.liquid", "snippets/predictive-search-products-list.liquid"]
OPTIONNELS = ["snippets/meta-tags.liquid",  # 09/11/2026 : titre Google de l'accueil FR (lu s'il existe)
              "sections/header.liquid", "sections/product-information.liquid", "sections/main-blog-post.liquid"]  # 26/11/2026 : audit SEO (H1, données structurées)

# 26/11/2026 (audit SEO) : données produit de Shopify corrigées à l'affichage : https au lieu de http, @id absolus, état neuf et
# vendeur sur chaque offre, tailles (variesBy), et sans le paragraphe « Dans le même esprit » (liens vers d'autres parfums)
QK_PRODUIT_LD = ("{%- comment -%}qk-produit-ld{%- endcomment -%}"
    "{%- capture qk_sd -%}{{ closest.product | structured_data }}{%- endcapture -%}"
    "{%- capture qk_id -%}\"@id\":\"{{ request.origin | replace: '/', '\\/' }}\\/{%- endcapture -%}"
    "{%- assign qk_sd = qk_sd | replace: 'http:\\/\\/schema.org\\/', 'https:\\/\\/schema.org\\/' | replace: '\"@id\":\"\\/', qk_id"
    " | replace: '\"@type\":\"Offer\",', '\"@type\":\"Offer\",\"itemCondition\":\"https:\\/\\/schema.org\\/NewCondition\",\"seller\":{\"@id\":\"https:\\/\\/qosmi.be\\/#org\"},\"hasMerchantReturnPolicy\":{\"@id\":\"https:\\/\\/qosmi.be\\/#retours\"},'"
    " | replace: '\"@type\":\"ProductGroup\",', '\"@type\":\"ProductGroup\",\"variesBy\":[\"https:\\/\\/schema.org\\/size\"],' -%}"
    "{%- assign qk_ms = 'Dans le même esprit|In dezelfde sfeer|In the same spirit' | split: '|' -%}{%- for qk_m in qk_ms -%}"
    "{%- assign qk_p = qk_sd | split: qk_m -%}{%- if qk_p.size > 1 -%}{%- assign qk_r = qk_p[1] | split: '\",\"hasVariant\"' -%}"
    "{%- if qk_r.size == 2 -%}{%- assign qk_t = qk_p[0] | split: '\\n' | join: ' ' | strip -%}"
    "{%- assign qk_sd = qk_t | append: '\",\"hasVariant\"' | append: qk_r[1] -%}{%- endif -%}{%- endif -%}{%- endfor -%}"
    "{{ qk_sd }}")

# 26/11/2026 (audit SEO) : données des articles du Magazine : auteur = l'organisation Qosmi (pas une « personne »), éditeur relié
# à la fiche entreprise (#org, avec logo), https, @id absolu, et date de modification jamais antérieure à la publication
QK_ARTICLE_LD = ("{%- comment -%}qk-article-ld{%- endcomment -%}"
    "{%- capture qk_ad -%}{{ article | structured_data }}{%- endcapture -%}"
    "{%- capture qk_id -%}\"@id\":\"{{ request.origin | replace: '/', '\\/' }}\\/{%- endcapture -%}"
    "{%- assign qk_ad = qk_ad | replace: 'http:\\/\\/schema.org\\/', 'https:\\/\\/schema.org\\/' | replace: '\"@id\":\"\\/', qk_id -%}"
    "{%- assign qk_p = qk_ad | split: '\"author\":{' -%}{%- if qk_p.size == 2 -%}{%- assign qk_r = qk_p[1] | split: '}' -%}"
    "{%- assign qk_reste = qk_p[1] | remove_first: qk_r[0] | remove_first: '}' -%}"
    "{%- assign qk_ad = qk_p[0] | append: '\"author\":{\"@type\":\"Organization\",\"@id\":\"https:\\/\\/qosmi.be\\/#org\",\"name\":\"Qosmi\",\"url\":\"https:\\/\\/qosmi.be\\/\"}' | append: qk_reste -%}{%- endif -%}"
    "{%- assign qk_ad = qk_ad | replace: '\"publisher\":{\"@type\":\"Organization\",\"name\":\"Qosmi\"}', '\"publisher\":{\"@id\":\"https:\\/\\/qosmi.be\\/#org\"}' -%}"
    "{%- assign qk_pub = qk_ad | split: '\"datePublished\":\"' -%}{%- assign qk_mod = qk_ad | split: '\"dateModified\":\"' -%}"
    "{%- if qk_pub.size == 2 and qk_mod.size == 2 -%}{%- assign qk_dp = qk_pub[1] | split: '\"' | first -%}{%- assign qk_dm = qk_mod[1] | split: '\"' | first -%}"
    "{%- if qk_dm < qk_dp -%}{%- capture qk_a -%}\"dateModified\":\"{{ qk_dm }}\"{%- endcapture -%}{%- capture qk_b -%}\"dateModified\":\"{{ qk_dp }}\"{%- endcapture -%}"
    "{%- assign qk_ad = qk_ad | replace: qk_a, qk_b -%}{%- endif -%}{%- endif -%}"
    "{{ qk_ad }}")


# 26/11/2026 (audit SEO) : qosmi.nl (marché Pays-Bas) : les titres et descriptions traduits pour la Belgique disent « in België »
QK_META_MARCHE = ("{%- comment -%}qk-meta-marche{%- endcomment -%}"
    "{%- if request.host contains 'qosmi.nl' -%}"
    "{%- assign page_title = page_title | replace: 'in België', 'in Nederland' -%}"
    "{%- assign page_description = page_description | replace: 'heel België', 'heel Nederland' | replace: 'in België', 'in Nederland' -%}"
    "{%- endif -%}"
    "{%- assign page_title = page_title | replace: 'Parfums Parfums ', 'Parfums ' -%}"
    # collections vides (testeurs, soins, maquillage…) : pas indexées tant qu'elles n'ont aucun produit
    "{%- if request.page_type == 'collection' and collection.products_count == 0 -%}<meta name=\"robots\" content=\"noindex, follow\">{%- endif -%}"
    "{%- comment -%}/qk-meta-marche{%- endcomment -%}")


def ambiance(n, alt, cote, fr, nl, lien):
    """Bloc photo + texte (photos d'ambiance Unsplash validées par Amine le 09/11/2026, qosmi-ambiance-<n>.jpg ;
    n peut aussi être un nom de fichier, ex. les images d'Amine de assets/site)."""
    return {"type": "qk-ambiance", "settings": {
        "fichier": n if isinstance(n, str) else "qosmi-ambiance-%d.jpg" % n, "alt": alt, "cote": cote,
        "surtitre": fr[0], "titre": fr[1], "texte": "<p>%s</p>" % fr[2], "lien_texte": fr[3],
        "surtitre_nl": nl[0], "titre_nl": nl[1], "texte_nl": "<p>%s</p>" % nl[2], "lien_texte_nl": nl[3], "lien": lien}}


# 09/11/2026 (SEO) : l'accueil FR n'avait que « Qosmi » comme titre et aucune méta-description (le NL était bon).
ACCUEIL_FR = ("{%- if request.page_type == 'index' and request.locale.iso_code == 'fr' -%}"
              "{%- assign page_title = 'Qosmi – Parfums de marque et de niche en Belgique' -%}"
              "{%- assign page_description = 'Parfumerie en ligne belge : Creed, Xerjoff, Chanel, Dior, Tom Ford et plus de 100 maisons. "
              "Parfums 100 % authentiques et neufs, livrés partout en Belgique.' -%}"
              "{%- endif -%}\n")
# 09/11/2026 (SEO) : la boutique en données structurées, avec sa politique de retour (Google la lit au niveau de la boutique).
ORG_LD = """    {%- comment -%}qk-org-ld{%- endcomment -%}<script type="application/ld+json" id="qk-org-ld">{"@context":"https://schema.org","@type":"OnlineStore","@id":"https://qosmi.be/#org","name":"Qosmi","alternateName":["qosmi.be","qosmi.nl","Qosmi parfums"],"url":"https://qosmi.be/","logo":"https:{{ 'qosmi-logo.png' | file_url }}","description":"Qosmi est une parfumerie en ligne belge (Deway BV) : parfums de marque, de niche et arabes 100 % authentiques et neufs, plus de 100 maisons, livraison dans 9 pays d'Europe et retrait gratuit à Dilbeek.","slogan":"Fragrance & Beauty","sameAs":["https://www.instagram.com/qosmi.be","https://qosmi.nl/"],"email":"contact@qosmi.be","telephone":"+32465436329","vatID":"BE1040851867","taxID":"1040.851.867","legalName":"Deway BV","contactPoint":[{"@type":"ContactPoint","contactType":"customer service","email":"contact@qosmi.be","telephone":"+32465436329","availableLanguage":["French","Dutch","English"],"areaServed":["BE","NL","LU","FR","ES","PT","IT","DE","PL"]}],"location":{"@type":"Place","name":"Qosmi Dilbeek (retrait des commandes)","address":{"@type":"PostalAddress","streetAddress":"Alfons Gossetlaan 34","postalCode":"1702","addressLocality":"Dilbeek","addressCountry":"BE"}},"areaServed":["BE","NL","LU","FR","ES","PT","IT","DE","PL"],"currenciesAccepted":"EUR","paymentAccepted":["Bancontact","Visa","Mastercard","Apple Pay"],"knowsAbout":["parfum","parfumerie de niche","parfums arabes","eau de parfum","notes olfactives"],"hasMerchantReturnPolicy":{"@type":"MerchantReturnPolicy","@id":"https://qosmi.be/#retours","applicableCountry":["BE","NL","LU","FR","ES","PT","IT","DE","PL"],"returnPolicyCountry":"BE","returnPolicyCategory":"https://schema.org/MerchantReturnFiniteReturnWindow","merchantReturnDays":14,"returnMethod":"https://schema.org/ReturnByMail","returnFees":"https://schema.org/ReturnShippingFees","merchantReturnLink":"https://qosmi.be/pages/retours"},"subjectOf":{"@type":"AboutPage","url":"https://qosmi.be/pages/a-propos"}}</script>{%- if request.page_type == 'index' -%}<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","@id":"{{ request.origin }}/#site","name":"Qosmi","alternateName":["qosmi.be","qosmi.nl","Qosmi parfums"],"url":"{{ request.origin }}/","inLanguage":["fr-BE","nl-BE","en"],"publisher":{"@id":"https://qosmi.be/#org"},"potentialAction":{"@type":"SearchAction","target":{"@type":"EntryPoint","urlTemplate":"{{ request.origin }}/search?q={search_term_string}"},"query-input":"required name=search_term_string"}}</script>{%- endif -%}{%- comment -%}/qk-org-ld{%- endcomment -%}
"""

# 23/11/2026 (plan SEO) : conditions de livraison des 9 pays en données structurées, sur la page Livraison (Google ShippingService)
LIVRAISON_LD = """    {%- comment -%}qk-livraison-ld{%- endcomment -%}
    {%- if request.page_type == 'page' -%}{%- case page.handle -%}{%- when 'livraison', 'levering', 'shipping' -%}<script type="application/ld+json">{"@context":"https://schema.org","@type":"OnlineStore","@id":"https://qosmi.be/#org","name":"Qosmi","url":"https://qosmi.be/","areaServed":["BE","NL","LU","FR","ES","PT","IT","DE","PL"],"hasShippingService":[{"@type":"ShippingService","name":"Point relais Mondial Relay","fulfillmentType":"https://schema.org/FulfillmentTypeCollectionPoint","handlingTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":1,"maxValue":2,"unitCode":"DAY"}},"shippingConditions":[{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"BE"},"shippingRate":{"@type":"MonetaryAmount","value":2.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":5,"maxValue":5,"unitCode":"DAY"}},"numItems":{"@type":"QuantitativeValue","maxValue":1}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"BE"},"shippingRate":{"@type":"MonetaryAmount","value":0,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":5,"maxValue":5,"unitCode":"DAY"}},"numItems":{"@type":"QuantitativeValue","minValue":2}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"NL"},"shippingRate":{"@type":"MonetaryAmount","value":3.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":7,"maxValue":7,"unitCode":"DAY"}},"numItems":{"@type":"QuantitativeValue","maxValue":1}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"NL"},"shippingRate":{"@type":"MonetaryAmount","value":0,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":7,"maxValue":7,"unitCode":"DAY"}},"numItems":{"@type":"QuantitativeValue","minValue":2}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"LU"},"shippingRate":{"@type":"MonetaryAmount","value":3.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":7,"maxValue":7,"unitCode":"DAY"}},"numItems":{"@type":"QuantitativeValue","maxValue":1}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"LU"},"shippingRate":{"@type":"MonetaryAmount","value":0,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":7,"maxValue":7,"unitCode":"DAY"}},"numItems":{"@type":"QuantitativeValue","minValue":2}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"FR"},"shippingRate":{"@type":"MonetaryAmount","value":4.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":7,"maxValue":7,"unitCode":"DAY"}}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"ES"},"shippingRate":{"@type":"MonetaryAmount","value":5.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":8,"maxValue":9,"unitCode":"DAY"}}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"PT"},"shippingRate":{"@type":"MonetaryAmount","value":5.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":8,"maxValue":9,"unitCode":"DAY"}}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"IT"},"shippingRate":{"@type":"MonetaryAmount","value":5.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":8,"maxValue":9,"unitCode":"DAY"}}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"DE"},"shippingRate":{"@type":"MonetaryAmount","value":7.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":8,"maxValue":9,"unitCode":"DAY"}}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"PL"},"shippingRate":{"@type":"MonetaryAmount","value":7.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":8,"maxValue":9,"unitCode":"DAY"}}}]},{"@type":"ShippingService","name":"Livraison à domicile","fulfillmentType":"https://schema.org/FulfillmentTypeDelivery","handlingTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":1,"maxValue":2,"unitCode":"DAY"}},"shippingConditions":[{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"BE"},"shippingRate":{"@type":"MonetaryAmount","value":6.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":5,"maxValue":5,"unitCode":"DAY"}}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"LU"},"shippingRate":{"@type":"MonetaryAmount","value":12.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":7,"maxValue":7,"unitCode":"DAY"}}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"FR"},"shippingRate":{"@type":"MonetaryAmount","value":12.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":7,"maxValue":7,"unitCode":"DAY"}}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"ES"},"shippingRate":{"@type":"MonetaryAmount","value":12.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":8,"maxValue":9,"unitCode":"DAY"}}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"PT"},"shippingRate":{"@type":"MonetaryAmount","value":12.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":8,"maxValue":9,"unitCode":"DAY"}}},{"@type":"ShippingConditions","shippingDestination":{"@type":"DefinedRegion","addressCountry":"DE"},"shippingRate":{"@type":"MonetaryAmount","value":12.95,"currency":"EUR"},"transitTime":{"@type":"ServicePeriod","businessDays":["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday"],"duration":{"@type":"QuantitativeValue","minValue":8,"maxValue":9,"unitCode":"DAY"}}}]}]}</script>{%- endcase -%}{%- endif -%}
"""


def logos_slugs():
    """Marques dont le logo est dans les Fichiers Shopify (config/logos_marques.json), une par ligne (nom simplifié).
    Sert aux pages de marque et à la bande des marques de l'accueil (logos cliquables, demande d'Amine du 08/11/2026)."""
    chemin = os.path.join(os.path.dirname(ICI), "config", "logos_marques.json")
    logos = json.load(open(chemin, encoding="utf-8"))["par_marque"] if os.path.exists(chemin) else {}
    return "\n".join(sorted(v["slug"] for v in logos.values()))

# 10/11/2026 (site lent, signalé par Amine) : la bande de l'accueil n'affiche plus les 132 marques (264 logos dans la page,
# 264 recherches d'image côté Shopify) mais les 40 plus connues qui ont un logo ; les autres sont sur la page Marques.
MARQUES_PHARES = ["Dior", "Chanel", "Creed", "Tom Ford", "Yves Saint Laurent", "Xerjoff", "Parfums de Marly", "Maison Francis Kurkdjian",
                  "Giorgio Armani", "Guerlain", "Hermes", "Versace", "Lattafa", "Initio", "Nishane", "By Kilian", "Le Labo", "Amouage",
                  "Mancera", "Montale", "Dolce&Gabbana", "Gucci", "Prada", "Jean Paul Gaultier", "Carolina Herrera", "Paco Rabanne",
                  "Valentino", "Givenchy", "Lancôme", "Bvlgari", "Acqua di Parma", "Diptyque", "Jo Malone", "Frederic Malle",
                  "Viktor & Rolf", "Narciso Rodriguez", "Tiziana Terenzi", "Kayali", "Armaf", "Afnan", "Rasasi", "Maison Alhambra",
                  "Al Haramain", "Swiss Arabian", "Ajmal", "Loewe", "Memo Paris", "Cartier", "Boucheron", "Calvin Klein", "Hugo Boss"]


def marques_bande(marques):
    """Marques phares d'abord (dans cet ordre), puis les autres ; le thème garde les 40 premières qui ont un logo."""
    toutes = [m for m in marques if not m.endswith("_")]
    return [m for m in MARQUES_PHARES if m in toutes] + [m for m in toutes if m not in MARQUES_PHARES]


ACHETER = """{%- if closest.product.available -%}
<button type="button" class="qk-acheter" data-qk-acheter>{% if request.locale.iso_code == 'nl' %}Nu kopen{% elsif request.locale.iso_code == 'en' %}Buy now{% else %}Acheter maintenant{% endif %}</button>
<script>
document.querySelectorAll('[data-qk-acheter]').forEach(function (b) {
  if (b.dataset.pret) return; b.dataset.pret = '1';
  b.addEventListener('click', function () {
    var f = document.querySelector('form[action*="/cart/add"]');
    var id = f && f.querySelector('[name="id"]');
    var q = document.querySelector('input[name="quantity"]');
    if (!id) { window.location.href = (window.Shopify && Shopify.routes ? Shopify.routes.root : '/') + 'cart'; return; }
    b.disabled = true;
    var racine = (window.Shopify && Shopify.routes) ? Shopify.routes.root : '/';
    fetch(racine + 'cart/add.js', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ items: [{ id: +id.value, quantity: Math.max(1, parseInt(q && q.value, 10) || 1) }] }) })
      .then(function () { window.location.href = racine + 'cart'; })
      .catch(function () { b.disabled = false; });
  });
});
</script>
{%- endif -%}"""
CARTE_TEXTE = "{% render 'qk-carte-texte', product: closest.product %}"
LIVRAISON = "Point relais 2,95 € · offert dès 2 articles · à domicile 6,95 €"  # 18/11/2026 (Amine)
LIVRAISON_ANCIEN = "Livraison 2,95 € · offerte dès 2 articles"  # formulation sans « sinon » (demande d'Amine du 08/11/2026, 22 h) ; sans délai (demande d'Amine du 08/11/2026 : le délai est donné au paiement et dans les pages légales)
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
ARABES_VEDETTES = [  # 08/11/2026 : grands succès arabes réellement en ligne (moins chers que Deloox avec 3 € net) ; les fiches masquées ne s'affichent pas
    "armaf-club-de-nuit-intense-man-eau-de-parfum-pour-homme", "lattafa-qaed-al-fursan-eau-de-parfum-mixte",
    "al-haramain-amber-oud-gold-edition-eau-de-parfum-mixte", "armaf-club-de-nuit-precieux-i-extrait-de-parfum-mixte",
    "afnan-supremacy-in-heaven-eau-de-parfum-pour-homme", "rasasi-hawas-fire-eau-de-parfum-pour-homme",
    "al-haramain-l-aventure-intense-eau-de-parfum-pour-homme", "lattafa-eclaire-eau-de-parfum-pour-femme",
    "armaf-club-de-nuit-milestone-eau-de-parfum-mixte", "afnan-turathi-brown-eau-de-parfum-pour-homme",
    "al-haramain-amber-oud-tobacco-edition-eau-de-parfum-mixte", "armaf-odyssey-eau-de-parfum-pour-homme",
    "armaf-club-de-nuit-untold-eau-de-parfum-mixte", "hamidi-the-lost-paradise-sublime-cherry-eau-de-parfum-mixte",
    "amouage-existence-eau-de-parfum-mixte", "lattafa-khamrah-eau-de-parfum-mixte", "lattafa-yara-eau-de-parfum-pour-femme",
    "rasasi-hawas-eau-de-parfum-pour-homme", "afnan-9pm-eau-de-parfum-pour-homme", "lattafa-asad-eau-de-parfum-pour-homme"]
ANNONCES = ["Livraison offerte dès 2 articles (BE · NL · LU)",
            "Livraison suivie dans 9 pays d'Europe",
            "Parfums 100 % authentiques et neufs",
            "Plus de 100 maisons, des grands classiques à la niche",
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
  elsif request.locale.iso_code == 'en'
    assign t_titre = 'Product safety'
    assign t_fab = 'Manufacturer / responsible person'
    assign t_avert = 'Flammable. Keep out of reach of children. Do not spray into the eyes or onto irritated skin. For external use only. Store in a cool place, away from heat, flames and sunlight. If you have allergies, check the ingredient list on the packaging.'
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



def snippet_recherche():
    """Fenêtre de recherche vide (demande d'Amine du 08/11/2026) : au lieu des 4 premiers parfums du catalogue (toujours les
    Acqua di Parma, ordre alphabétique), 4 grands classiques de DU_JOUR, qui changent chaque jour ; les fiches non disponibles
    sont sautées. Remplace le snippet d'origine du thème (même balisage, même carte produit)."""
    liste = ",".join(DU_JOUR)
    return """{%- comment -%} Généré par scripts/theme_rk.py (snippet_recherche) — ne pas modifier à la main. {%- endcomment -%}
<div
  id="predictive-search-results"
  class="predictive-search-dropdown"
  role="listbox"
  aria-expanded="true"
  style="--color-shadow: rgb(var(--color-foreground-rgb) / {{ shadow_opacity }});"
>
  {% if load_empty_state %}
    <div class="predictive-search-results__inner">
      <div id="predictive-search-products" class="predictive-search-results__products"{% if products_test_id %} data-testid="{{ products_test_id }}"{% endif %}>
        <h4 class="predictive-search-results__title">{% if request.locale.iso_code == 'nl' %}Populair{% elsif request.locale.iso_code == 'en' %}Must-haves{% else %}Les incontournables{% endif %}</h4>
        <ul class="predictive-search-results__list predictive-search-results__wrapper-products list-unstyled">
          {%- assign qk_liste = '""" + liste + """' | split: ',' -%}
          {%- assign qk_jour = 'now' | date: '%j' | times: 1 -%}
          {%- assign qk_depart = qk_jour | times: 4 | modulo: qk_liste.size -%}
          {%- assign qk_vus = 0 -%}
          {%- for i in (0..40) -%}
            {%- if qk_vus >= 4 -%}{%- break -%}{%- endif -%}
            {%- assign qk_idx = qk_depart | plus: i | modulo: qk_liste.size -%}
            {%- assign qk_p = all_products[qk_liste[qk_idx]] -%}
            {%- if qk_p != blank and qk_p.available and qk_p.featured_image -%}
              {%- assign qk_vus = qk_vus | plus: 1 -%}
              <li class="predictive-search-results__card predictive-search-results__card--product" ref="resultsItems[]">
                {% render 'resource-card', resource_type: 'product', resource: qk_p, image_width: 500, image_hover: true, image_aspect_ratio: '4 / 5', product_view_context: 'search' %}
              </li>
            {%- endif -%}
          {%- endfor -%}
        </ul>
      </div>
    </div>
  {% endif %}
</div>
"""

# 10/11/2026 (demande d'Amine) : les coffrets ne se voient que dans la collection Coffrets (et la mise en avant de l'accueil),
# jamais dans les autres collections (marques, niche, arabes) ni dans la recherche, sauf si on cherche un coffret.
QK_COFFRET = "{%- if product.type == 'Coffrets' or product.type == 'Geschenksets' -%}{%- continue -%}{%- endif -%}"
QK_COFFRET_COLL = ("{%- if collection.handle != 'coffrets' -%}{%- if product.type == 'Coffrets' or product.type == 'Geschenksets'"
                   " -%}{%- continue -%}{%- endif -%}{%- endif -%}")
QK_COFFRET_RECH = ("{%- assign qk_t = qk_termes | downcase -%}{%- unless qk_t contains 'coffret' or qk_t contains 'geschenk' or qk_t contains 'gift' -%}"
                   + QK_COFFRET + "{%- endunless -%}")
COFFRETS_VEDETTES = [  # coffrets à belle photo (≥ 800 px, Notino et Trista), seuls mis en avant sur l'accueil
    "hermes-terre-d-hermes-coffret-2", "xerjoff-discovery-set-i-coffret",
    "armaf-club-de-nuit-intense-man-coffret", "afnan-supremacy-not-only-intense-coffret", "lattafa-yara-collection-coffret",
    "armaf-club-de-nuit-woman-coffret", "afnan-discovery-set-9pm-coffret", "orientica-luxury-collection-discovery-set-coffret",
    "lattafa-bade-e-al-oud-collection-coffret", "lattafa-najdia-coffret", "lattafa-fakhar-lattafa-coffret",
    "lattafa-ameer-al-oudh-coffret", "lattafa-washwashah-coffret", "lattafa-sheikh-al-shuyukh-coffret", "lattafa-pure-oudi-coffret"]


def sans_coffrets(texte, boucle, garde):
    """Ajoute le filtre des coffrets juste après chaque boucle « boucle » (une seule fois)."""
    if "qk-coffrets" in texte:
        return texte
    return texte.replace(boucle, boucle + "{%- comment -%}qk-coffrets{%- endcomment -%}" + garde)


def snippet_notes_du_jour():
    """10/11/2026 (demande d'Amine : « Le parfum du jour » plus beau) : famille et 3 notes du parfum du jour,
    tirées de config/descriptions_parfums.json (FR et NL)."""
    chemin = os.path.join(os.path.dirname(ICI), "config", "descriptions_parfums.json")
    D = json.load(open(chemin, encoding="utf-8"))["parfums"] if os.path.exists(chemin) else {}
    def trois(n, bas=True):
        l = n.get("cle") or [x for k in ("tete", "coeur", "fond") for x in n.get(k, [])[:1]]
        out = []
        for x in l:
            if x not in out:
                out.append(x)
        return [x[0].lower() + x[1:] if bas else x for x in out[:3]]
    lignes = ["{%- comment -%} Généré par scripts/theme_rk.py (snippet_notes_du_jour) : ne pas modifier à la main. {%- endcomment -%}",
              "{%- case h -%}"]
    for h in DU_JOUR:
        d = D.get(h)
        if not d:
            continue
        fr, nl = trois(d.get("notes_fr") or {}), trois(d.get("notes_nl") or {}, False)
        if not fr:
            continue
        esc = lambda t: (t or "").replace("<", "").replace(">", "")
        lignes.append("{%%- when '%s' -%%}<span class=\"qk-dujour__notes\">{%%- if nl -%%}%s<b>%s</b>{%%- else -%%}%s<b>%s</b>{%%- endif -%%}</span>" % (
            h, ("<i>%s</i>" % esc(d.get("famille_nl"))) if d.get("famille_nl") else "", esc(" · ".join(nl)),
            ("<i>%s</i>" % esc(d.get("famille_fr"))) if d.get("famille_fr") else "", esc(" · ".join(fr))))
    lignes.append("{%- endcase -%}")
    return "\n".join(lignes) + "\n"


def construire(fichiers, marques):
    liquides, jsons = fichiers_qk(), {}
    liquides["snippets/qk-gpsr.liquid"] = snippet_gpsr()
    liquides["snippets/qk-du-jour-notes.liquid"] = snippet_notes_du_jour()
    # recherche par odeurs + parfums aux notes proches (12/11/2026) : index tiré de config/descriptions_parfums.json
    import odeurs as _odeurs
    liquides["assets/qk-odeurs.js"] = _odeurs.asset_js()
    liquides["snippets/predictive-search-empty-state.liquid"] = snippet_recherche()
    liquides["sections/main-collection.liquid"] = sans_coffrets(fichiers["sections/main-collection.liquid"],
                                                                "{% for product in collection.products %}", QK_COFFRET_COLL)
    rech = fichiers["sections/search-results.liquid"]
    if "qk-coffrets" not in rech:
        rech = sans_coffrets(rech, "{% for product in products %}", QK_COFFRET_RECH)
        rech = rech.replace("{% paginate search.results", "{%- assign qk_termes = search.terms -%}\n    {% paginate search.results", 1)
    liquides["sections/search-results.liquid"] = rech
    pred = fichiers["snippets/predictive-search-products-list.liquid"]
    if "qk-coffrets" not in pred:
        tete, sep, corps = pred.partition("{%- enddoc -%}")
        if not sep:
            tete, sep, corps = "", "", pred
        pred = tete + sep + "\n{%- assign qk_termes = predictive_search.terms -%}" + corps
        pred = pred.replace(
            "{% for product in products limit: limit %}",
            "{% for product in products limit: limit %}{%- comment -%}qk-coffrets{%- endcomment -%}" + QK_COFFRET_RECH)
    liquides["snippets/predictive-search-products-list.liquid"] = pred

    # ---------- feuille de style ----------
    lay = fichiers["layout/theme.liquid"]
    # favoris (08/11/2026) : cœurs sur les cartes et la fiche, page /pages/favoris, liste gardée dans le navigateur
    if "qk-favoris.js" not in lay:
        lay = lay.replace("</head>", "    <script src=\"{{ 'qk-favoris.js' | asset_url }}\" defer></script>\n  </head>", 1)
    # « Complète ta commande » dans le panier (13/11/2026)
    if "qk-paiement.js" not in lay:  # 15/11/2026 : Bancontact d'abord dans le panier, autres moyens derrière un bouton
        lay = lay.replace("</head>", "    <script type=\"module\" src=\"{{ 'qk-paiement.js' | asset_url }}\"></script>\n  </head>", 1)
    # 20/11/2026 (Amine) : plus de carte Mondial Relay dans le panier (« ça ne fluidifie pas l'expérience client ») ;
    # sans choix, le point relais le plus proche de l'adresse est pris (CGV art. 4.1)
    lay = lay.replace("    <script type=\"module\" src=\"{{ 'qk-relais-tiroir.js' | asset_url }}\"></script>\n", "")
    if "qk-bancontact-logo" not in lay:
        lay = lay.replace("</body>", "  <template id=\"qk-bancontact-logo\">{{ 'bancontact' | payment_type_svg_tag }}</template>\n  </body>", 1)
    if "QK_SUR_COMMANDE" not in lay:  # 14/11/2026 : fiche propre au 2e grossiste → note « Bon plan » sur toute la fiche
        lay = lay.replace("</head>", "    {%- if template.name == 'product' and product.tags contains 'sur-commande' -%}<script>window.QK_SUR_COMMANDE = true;</script>{%- endif -%}\n  </head>", 1)
    if "QK_BF" not in lay:  # 17/11/2026 : Black Friday -10 % (27-30/11) : ligne sous le prix des fiches de la sélection
        lay = lay.replace("</head>", "    {%- if template.name == 'product' -%}{%- assign qk_bf_h = product.collections | map: 'handle' -%}{%- if qk_bf_h contains 'black-friday' -%}<script>window.QK_BF = {{ 'now' | date: '%Y%m%d' }};</script>{%- endif -%}{%- endif -%}\n  </head>", 1)
    if "qk-bf.js" not in lay:
        lay = lay.replace("</head>", "    <script type=\"module\" src=\"{{ 'qk-bf.js' | asset_url }}\"></script>\n  </head>", 1)
    if "qk-bonplan.js" not in lay:  # 14/11/2026 : option « Bon plan » (cachée si épuisée, délai expliqué)
        lay = lay.replace("</head>", "    <script type=\"module\" src=\"{{ 'qk-bonplan.js' | asset_url }}\"></script>\n  </head>", 1)
    if "qk-cadeau.js" not in lay:  # 13/11/2026 : message cadeau dans le panier
        lay = lay.replace("</head>", "    <script type=\"module\" src=\"{{ 'qk-cadeau.js' | asset_url }}\"></script>\n  </head>", 1)
    if "qk-complete.js" not in lay:
        lay = lay.replace("</head>", "    <script>window.QK_COMPLETE = { odeurs: \"{{ 'qk-odeurs.js' | asset_url }}\", outils: \"{{ 'qk-odeurs-outils.js' | asset_url }}\" };</script>\n"
                                     "    <script type=\"module\" src=\"{{ 'qk-complete.js' | asset_url }}\"></script>\n  </head>", 1)
    # retour après la vérification anti-robot de Shopify (13/11/2026) : si un formulaire Qosmi a noté sa page de retour
    # (sessionStorage « qk-retour », 15 min) et que le client atterrit ailleurs, on le renvoie vers la page de confirmation
    if "qk-retour" not in lay:
        lay = lay.replace("</head>", "    <script>/* qk-retour */(function(){try{var r=JSON.parse(sessionStorage.getItem('qk-retour')||'null');"
                                     "if(!r||Date.now()-r.t>9e5){sessionStorage.removeItem('qk-retour');return;}"
                                     "var apres=/customer_posted=true/.test(location.search)||document.referrer.indexOf('/challenge')>=0;"
                                     "if(!apres)return;sessionStorage.removeItem('qk-retour');"
                                     "if(location.pathname+location.search!==r.url)location.replace(r.url);}catch(e){}})();</script>\n  </head>", 1)
    if "qk-inscription" not in lay:  # 17/11/2026 : fenêtre d'inscription aux e-mails (cadeau de bienvenue, Black Friday)
        lay = lay.replace("</body>", "  {% render 'qk-inscription' %}\n  </body>", 1)
    if "qosmi-rk.css" not in lay:
        lay = lay.replace("</head>", "    {{ 'qosmi-rk.css' | asset_url | stylesheet_tag }}\n  </head>", 1)
    # image de partage (réseaux sociaux, WhatsApp) quand la page n'a pas d'image propre (demande d'Amine du 08/11/2026)
    if "qk-partage" not in lay:
        lay = lay.replace("</head>", PARTAGE + "  </head>", 1)
    # FAQ des articles du Journal en données structurées (08/11/2026)
    if "qk-faq-ld" not in lay:
        lay = lay.replace("</head>", FAQ_LD + "  </head>", 1)
    # données de livraison (23/11/2026) : remplacées à chaque passage (FR livraison, NL levering, EN shipping)
    import re as _re0
    lay = _re0.sub(r"    \{%- comment -%\}qk-livraison-ld\{%- endcomment -%\}.*?\{%- endif -%\}\n", "", lay, flags=_re0.S)
    lay = lay.replace("</head>", LIVRAISON_LD + "  </head>", 1)
    # 17/11/2026 : « qosmi » corrigé en « kosmi » par Google → nom de marque, autres noms, logo, Instagram, WebSite (nom du site)
    import re as _re
    lay = _re.sub(r"    \{%- if request\.page_type == 'index' -%\}<script type=\"application/ld\+json\" id=\"qk-org-ld\">.*?\{%- endif -%\}\n", "", lay, flags=_re.S)
    lay = _re.sub(r"    \{%- comment -%\}qk-org-ld\{%- endcomment -%\}.*?\{%- comment -%\}/qk-org-ld\{%- endcomment -%\}\n", "", lay, flags=_re.S)  # 25/11/2026 : sur toutes les pages
    lay = lay.replace("</head>", ORG_LD + "  </head>", 1)
    # titre et méta-description de l'accueil FR : dans le fichier qui écrit <title>
    if "Parfums de marque et de niche en Belgique" not in lay + fichiers.get("snippets/meta-tags.liquid", ""):
        if "<title" in fichiers.get("snippets/meta-tags.liquid", ""):
            liquides["snippets/meta-tags.liquid"] = ACCUEIL_FR + fichiers["snippets/meta-tags.liquid"]
        elif "<title" in lay:
            lay = ACCUEIL_FR + lay
        else:
            print("  (titre de l'accueil : balise <title> introuvable, rien changé)")
    # 26/11/2026 (audit SEO) : frais de livraison des 9 pays aussi sur les fiches produit (même @id que la boutique)
    lay = _re0.sub(r"    \{%- comment -%\}qk-livraison-produit-ld\{%- endcomment -%\}.*?\{%- endif -%\}\n", "", lay, flags=_re0.S)
    _ship = _re0.search(r"<script type=\"application/ld\+json\">.*?</script>", LIVRAISON_LD, _re0.S).group(0)
    lay = lay.replace("</head>", "    {%- comment -%}qk-livraison-produit-ld{%- endcomment -%}{%- if request.page_type == 'product' -%}" + _ship + "{%- endif -%}\n  </head>", 1)
    # 26/11/2026 : vérification Bing Webmaster Tools (qosmi.nl ; qosmi.be est vérifié par l'import Search Console)
    if "msvalidate.01" not in lay:
        lay = lay.replace("</head>", "    {%- if request.page_type == 'index' -%}<meta name=\"msvalidate.01\" content=\"A252B7BA294BAC727EBE6AE61402D2A5\" />{%- endif -%}\n  </head>", 1)
    liquides["layout/theme.liquid"] = lay
    # titres et descriptions : qosmi.nl dit « Nederland », plus de « Parfums Parfums de Marly »
    meta = liquides.get("snippets/meta-tags.liquid", fichiers.get("snippets/meta-tags.liquid"))
    if meta and "<title" in meta:
        meta = _re0.sub(r"\{%- comment -%\}qk-meta-marche\{%- endcomment -%\}.*?\{%- comment -%\}/qk-meta-marche\{%- endcomment -%\}", "", meta, flags=_re0.S)
        if meta.startswith(ACCUEIL_FR):
            meta = ACCUEIL_FR + QK_META_MARCHE + meta[len(ACCUEIL_FR):]
        else:
            meta = QK_META_MARCHE + meta
        liquides["snippets/meta-tags.liquid"] = meta
    else:
        print("  (meta-tags.liquid introuvable : titres qosmi.nl non corrigés)")
    # en-tête : un seul H1 (celui du bandeau d'accueil) et plus de 2e bloc « Organization » (doublon de qk-org-ld)
    hdr = fichiers.get("sections/header.liquid")
    if hdr:
        n0 = len(hdr)
        hdr = hdr.replace('<h1 class="visually-hidden">{{ shop.name }}</h1>', '<p class="visually-hidden">{{ shop.name }}</p>')
        k = hdr.find('"@type": "Organization"')
        if k > 0:
            a = hdr.rfind('<script type="application/ld+json">', 0, k)
            b = hdr.find("</script>", k)
            if a > 0 and b > k and k - a < 300:
                hdr = hdr[:a] + "{%- comment -%}qk : bloc Organization retiré (doublon, audit SEO 26/11/2026){%- endcomment -%}" + hdr[b + 9:]
        print("  en-tête : H1 caché -> p, Organization retiré (%d -> %d caractères)" % (n0, len(hdr)))
        liquides["sections/header.liquid"] = hdr
    blog = fichiers.get("sections/main-blog-post.liquid")
    if blog:
        if "{{ article | structured_data }}" in blog:
            liquides["sections/main-blog-post.liquid"] = blog.replace("{{ article | structured_data }}", QK_ARTICLE_LD)
            print("  articles : données structurées corrigées")
        elif "qk-article-ld" in blog:
            a = blog.index("{%- comment -%}qk-article-ld{%- endcomment -%}")
            b = blog.index("{{ qk_ad }}", a) + len("{{ qk_ad }}")
            liquides["sections/main-blog-post.liquid"] = blog[:a] + QK_ARTICLE_LD + blog[b:]
            print("  articles : données structurées mises à jour")
    pinfo = fichiers.get("sections/product-information.liquid")
    if pinfo:
        if "{{ closest.product | structured_data }}" in pinfo:
            pinfo = pinfo.replace("{{ closest.product | structured_data }}", QK_PRODUIT_LD)
            liquides["sections/product-information.liquid"] = pinfo
            print("  fiche produit : données structurées corrigées")
        elif "qk-produit-ld" in pinfo:
            a = pinfo.index("{%- comment -%}qk-produit-ld{%- endcomment -%}")
            b = pinfo.index("{{ qk_sd }}", a) + len("{{ qk_sd }}")
            liquides["sections/product-information.liquid"] = pinfo[:a] + QK_PRODUIT_LD + pinfo[b:]
            print("  fiche produit : données structurées mises à jour")

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
                "o5": {"type": "onglet", "settings": {"collection": "parfums-arabes", "label": "Arabes", "produits": ARABES_VEDETTES}},
                "o6": {"type": "onglet", "settings": {"collection": "coffrets", "label": "Coffrets", "produits": COFFRETS_VEDETTES}}},
            "block_order": ["o1", "o2", "o3", "o4", "o5", "o6"]},
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
            "titre": "Marques", "liste": "\n".join(marques_bande(marques)), "logos": logos_slugs(), "maximum": 40,
            "tout_texte": "Toutes les marques", "tout_texte_nl": "Alle merken", "tout_lien": "/pages/marques",
            "texte": "Des parfums originaux et neufs, des grandes maisons aux créateurs de niche."}},
        # 13/11/2026 : bloc Noël vers le guide cadeaux (demande d'Amine), à retirer après les fêtes
        "qk_amb_noel": ambiance("qosmi-decor-coffret-noel.jpg", "Coffret cadeau en carton, papier de soie et anis étoilé", "gauche",
            ("Noël", "Idées cadeaux parfum", "Des coffrets, des parfums pour tous les budgets et de l'aide pour choisir celui qui lui ressemble. "
             "Tu peux aussi ajouter un petit mot au moment de commander.", "Voir le guide cadeaux"),
            ("Kerst", "Parfum cadeau-ideeën", "Geschenksets, parfums voor elk budget en hulp om de geur te kiezen die bij die persoon past. "
             "Je kunt bij je bestelling ook een kort berichtje toevoegen.", "Bekijk de cadeaugids"),
            "/pages/idees-cadeaux-noel"),
        "qk_amb_journal": ambiance(3, "Main qui vaporise un parfum", "droite",
            ("Le Magazine", "Le bon geste", "Conseils pour bien porter ton parfum, matières premières, portraits de parfumeurs : tout ce qu'il faut savoir avant de choisir.", "Lire le Magazine"),
            ("Het Magazine", "De juiste reflex", "Tips om je parfum goed te dragen, grondstoffen, portretten van parfumeurs: alles wat je moet weten voor je kiest.", "Lees het Magazine"),
            "/blogs/journal"),
        "qk_amb_arabes": ambiance(4, "Flacons de parfum dorés dans la lumière", "gauche",
            ("Parfums arabes", "L'Orient en flacon", "Oud, ambre, vanille, rose : Lattafa, Armaf, Al Haramain, Afnan et bien d'autres maisons des Émirats.", "Découvrir"),
            ("Arabische parfums", "Het Oosten in een flacon", "Oud, amber, vanille, roos: Lattafa, Armaf, Al Haramain, Afnan en nog veel meer huizen uit de Emiraten.", "Ontdek"),
            "/collections/parfums-arabes"),
        # 13/11/2026 : photo d'Amine (Gemini) « flacons sur une console en marbre », vidéo de l'accueil gardée
        "qk_apropos": ambiance("qosmi-accueil-flacons.jpg", "Flacons de parfum sur une console en marbre, pétales séchés et branche d'olivier", "droite",
            ("À propos", "Qosmi", "Qosmi, c'est une parfumerie en ligne belge, simple et honnête : des parfums 100 % authentiques, neufs, au juste prix. "
             "On choisit les maisons qu'on aime, des grands classiques aux créateurs de niche, et on te les livre en Belgique et dans 8 autres pays d'Europe.", "Voir tous les parfums"),
            ("Over ons", "Qosmi", "Qosmi is een Belgische online parfumerie, eenvoudig en eerlijk: 100% originele, nieuwe parfums tegen de juiste prijs. "
             "We kiezen de huizen die we graag hebben, van grote klassiekers tot nichecreateurs, en leveren ze in België en 8 andere Europese landen.", "Alle parfums"),
            "/collections/parfums"),
        "qk_apropos_ancien": {"type": "qk-texte", "disabled": True, "settings": {
            "surtitre": "À propos", "titre": "Qosmi",
            "texte": "<p>Qosmi, c'est une parfumerie en ligne belge, simple et honnête : des parfums 100 % authentiques, "
                     "neufs, au juste prix. On choisit les maisons qu'on aime, des grands classiques aux créateurs de niche, "
                     "et on te les livre en Belgique et dans 8 autres pays d'Europe.</p>",
            "lien_texte": "Voir tous les parfums", "lien": "shopify://collections/parfums", "alignement": "centre"}},
    }
    d["order"] = ["qk_hero", "qk_favoris", "qk_amb_noel", "qk_amb_journal", "qk_banniere", "qk_tuiles", "qk_amb_arabes", "qk_marques", "qk_apropos", "qk_apropos_ancien"]
    jsons["templates/index.json"] = ecrire(e, d)

    # ---------- fiche produit ----------
    e, d = lire(fichiers["templates/product.json"])
    main = d["sections"]["main"]
    if "media-gallery" in main["blocks"]:
        # 22/11/2026 (Amine) : les photos défilent en carrousel (flèches + vignettes), plus l'une sous l'autre
        main["blocks"]["media-gallery"]["settings"].update({
            "media_columns": "one", "large_first_image": True, "media_presentation": "carousel",
            "icons_style": "arrow", "slideshow_controls_style": "thumbnails", "thumbnail_position": "bottom",
            "slideshow_mobile_controls_style": "dots", "aspect_ratio": "1"})
    det = main["blocks"]["product-details"]
    grp_id = next(k for k, b in det["blocks"].items() if b["type"] == "group")
    grp = det["blocks"][grp_id]
    for k in [k for k, b in grp["blocks"].items() if b["type"] == "text"]:
        del grp["blocks"][k]
    grp["blocks"]["qk_titre"] = liquide(
        "{%- assign t = closest.product.title | split: ' — ' -%}{%- assign n = t[0] | remove_first: closest.product.vendor | strip -%}"
        "{%- if n == blank -%}{%- assign n = t[0] -%}{%- endif -%}"
        # 10/11/2026 (SEO) : la marque fait partie du titre principal (H1 « Creed Aventus »), même rendu qu'avant
        "{% render 'qk-etiquette', product: closest.product, classe: 'qk-etiquette--fiche' %}"
        "<div class=\"qk-titre-ligne\"><h1 class=\"qk-titre-produit\"><span class=\"qk-marque-produit\">{{ closest.product.vendor }}</span> {{ n }}</h1>"
        "{% render 'qk-favori', product: closest.product, classe: 'qk-fav--fiche' %}</div>"
        "{%- if t[1] -%}<p class=\"qk-type-produit\">{{ t[1] }}</p>{%- endif -%}")
    grp["block_order"] = ["qk_titre"] + [k for k in grp.get("block_order", grp["blocks"]) if k in grp["blocks"] and k != "qk_titre"]
    for k in ("qosmi_livraison", "qosmi_garanties"):
        det["blocks"].pop(k, None)
    det["blocks"]["qk_livraison"] = liquide(
        "<p class=\"qk-livraison\">{% if request.locale.iso_code == 'nl' %}Afhaalpunt € 2,95 · gratis vanaf 2 artikelen · aan huis € 6,95"
        "{% elsif request.locale.iso_code == 'en' %}Pickup point €2.95 · free from 2 items · home delivery €6.95"
        "{% else %}" + LIVRAISON + "{% endif %}</p>")
    det["blocks"]["qk_rassurance"] = liquide(
        "<div class=\"qk-rassurance\">{% if request.locale.iso_code == 'nl' %}"
        "<span>Originele parfum, nieuw, met aankoopfactuur</span><span>14 dagen om van gedacht te veranderen (ongeopende fles)</span>"
        "<span>Betalen met Bancontact, kaart of Apple Pay</span>{% elsif request.locale.iso_code == 'en' %}"
        "<span>Original fragrance, new, with purchase invoice</span><span>14 days to change your mind (unopened bottle)</span>"
        "<span>Pay with Bancontact, card or Apple Pay</span>{% else %}"
        "<span>Parfum original, neuf, avec facture d'achat</span><span>14 jours pour changer d'avis (flacon non ouvert)</span>"
        "<span>Paiement Bancontact, carte ou Apple Pay</span>{% endif %}</div>")
    det["blocks"]["qk_gpsr"] = liquide("{% render 'qk-gpsr', product: closest.product %}")
    # Profil du parfum (13/11/2026) : saison, tenue, sillage, occasions, pyramide (métachamp qosmi.profil)
    det["blocks"]["qk_profil"] = liquide("{% render 'qk-profil', product: closest.product %}")
    # « Acheter maintenant » (demande d'Amine du 08/11/2026) : remplace « Acheter avec Shop », qui demandait de se connecter.
    # Ajoute le format choisi au panier et ouvre la page panier. Le bouton Shop Pay est masqué en CSS (.shopify-payment-button).
    det["blocks"]["qk_acheter"] = liquide(ACHETER)
    # 25/11/2026 (Amine : trop de défilement sur ordinateur) : sur grand écran, la pyramide, la description et la sécurité
    # du produit passent sous la photo (colonne de gauche) ; sur mobile rien ne bouge.
    det["blocks"]["qk_sous_photo"] = liquide(
        "<script>(function(){function go(){if(!window.matchMedia('(min-width: 990px)').matches)return;"
        "var m=document.querySelector('.product-information__media');var d=document.querySelector('.product-details');"
        "if(!m||!d||m.querySelector('.qk-sous-photo'))return;var box=document.createElement('div');box.className='qk-sous-photo';"
        "var items=[];var p=d.querySelector('.qk-profil');if(p)items.push(p.parentElement||p);"
        "d.querySelectorAll('rte-formatter.text-block').forEach(function(t){if(t.querySelector('.qk-desc-profil')||t.textContent.length>160)items.push(t);});"
        "var g=d.querySelector('.qk-gpsr');if(g)items.push(g.parentElement||g);"
        "items.forEach(function(x){if(x&&!box.contains(x))box.appendChild(x);});if(box.children.length)m.appendChild(box);}"
        "if(document.readyState!=='loading')go();else document.addEventListener('DOMContentLoaded',go);})();</script>")
    ordre = [k for k in det["block_order"] if k in det["blocks"] and not k.startswith("qk_")]
    i = ordre.index(next(k for k in ordre if det["blocks"][k]["type"] == "buy-buttons")) + 1
    det["block_order"] = ordre[:i] + ["qk_acheter", "qk_livraison", "qk_rassurance", "qk_profil", "qk_gpsr"] + ordre[i:] + ["qk_sous_photo"]
    # 25/11/2026 (Amine) : bandeau fil d'Ariane tout en haut de la fiche, pour espacer l'en-tête et la photo
    d["sections"]["qk_fil"] = {"type": "qk-fil", "settings": {}}
    d["order"] = ["qk_fil"] + [k for k in d["order"] if k != "qk_fil"]
    d["sections"]["qk_marque"] = {"type": "qk-texte", "settings": {"mode_marque": True, "alignement": "centre"}}
    d["order"] = [k for k in d["order"] if k != "qk_marque"]
    d["order"].insert(d["order"].index("main") + 1 if "main" in d["order"] else 1, "qk_marque")
    for s in d["sections"].values():
        if s["type"] == "product-recommendations":
            for b in s["blocks"].values():
                if b["type"] == "text":
                    b["settings"]["text"] = "<h3>Tu aimeras aussi</h3>"
    cartes(d)
    d["sections"]["qk_amb"] = ambiance(6, "Flacon de parfum sur une fourrure blanche", "gauche",
        ("Qosmi", "100 % authentique", "Chaque parfum est neuf et d'origine. Livraison dans 9 pays d'Europe, offerte en point relais dès 2 articles en Belgique, aux Pays-Bas et au Luxembourg.", "Nos marques"),
        ("Qosmi", "100% origineel", "Elk parfum is nieuw en origineel. Levering in 9 Europese landen, gratis in een afhaalpunt vanaf 2 artikelen in België, Nederland en Luxemburg.", "Onze merken"),
        "/pages/marques")
    d["order"] = [k for k in d["order"] if k != "qk_amb"] + ["qk_amb"]
    # « Préviens-moi quand il revient » (12/11/2026) : la section se place d'elle-même sous le bouton d'achat
    d["sections"]["qk_alerte"] = {"type": "qk-alerte", "settings": {}}
    d["order"] = [k for k in d["order"] if k != "qk_alerte"]
    d["order"].insert(d["order"].index("main") + 1 if "main" in d["order"] else 0, "qk_alerte")
    # « Parfums aux notes proches » (12/11/2026) : avant « Tu aimeras aussi » du thème
    d["sections"]["qk_proches"] = {"type": "qk-proches", "settings": {}}
    d["order"] = [k for k in d["order"] if k != "qk_proches"]
    reco = next((k for k in d["order"] if d["sections"][k]["type"] == "product-recommendations"), "qk_amb")
    d["order"].insert(d["order"].index(reco), "qk_proches")
    # Avis clients Judge.me (13/11/2026) : juste avant « Parfums aux notes proches »
    d["sections"]["qk_avis"] = {"type": "qk-avis", "settings": {}}
    d["order"] = [k for k in d["order"] if k != "qk_avis"]
    d["order"].insert(d["order"].index("qk_proches"), "qk_avis")
    jsons["templates/product.json"] = ecrire(e, d)

    # ---------- collections et recherche ----------
    for nom in ("templates/collection.json", "templates/search.json"):
        e, d = lire(fichiers[nom])
        cartes(d)
        if nom == "templates/collection.json":
            # en-tête Qosmi : titre et texte à gauche, image des flacons à droite (demande d'Amine du 08/11/2026) ;
            # l'en-tête d'origine est gardé mais désactivé
            # pages de marque : logo de la maison (config/logos_marques.json, logos Fragrantica vérifiés à la main, 08/11/2026)
            chemin_logos = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "logos_marques.json")
            logos = json.load(open(chemin_logos, encoding="utf-8"))["par_marque"] if os.path.exists(chemin_logos) else {}
            d["sections"]["qk_entete"] = {"type": "qk-entete-collection", "settings": {"logos": "\n".join(sorted(v["slug"] for v in logos.values()))}}
            for k, s in d["sections"].items():
                if k != "qk_entete" and s.get("type") == "section":
                    s["disabled"] = True
            d["order"] = ["qk_entete"] + [k for k in d["order"] if k != "qk_entete"]
        if nom == "templates/collection.json":
            d["sections"]["qk_amb"] = ambiance(2, "Flacons de parfum alignés, en lumière douce", "droite",
                ("Toutes nos marques", "Plus de 100 maisons", "Des grands classiques aux créateurs de niche, retrouve chaque maison sur sa page.", "Voir les marques"),
                ("Al onze merken", "Meer dan 100 huizen", "Van grote klassiekers tot nichecreateurs: elk huis heeft zijn eigen pagina.", "Bekijk de merken"),
                "/pages/marques")
        else:
            d["sections"]["qk_amb"] = ambiance(7, "Reflets dorés d'un flacon de parfum", "gauche",
                ("Besoin d'idées ?", "Le Magazine", "Guides, conseils et parfums du jour pour t'aider à trouver le tien.", "Lire le Magazine"),
                ("Ideeën nodig?", "Het Magazine", "Gidsen, tips en parfums van de dag om de jouwe te vinden.", "Lees het Magazine"),
                "/blogs/journal")
        d["order"] = [k for k in d["order"] if k != "qk_amb"] + ["qk_amb"]
        jsons[nom] = ecrire(e, d)

    # ---------- en-tête ----------
    # ---------- panier : rappel « livraison offerte dès 2 articles » (08/11/2026) ----------
    if "templates/cart.json" in fichiers:
        e, d = lire(fichiers["templates/cart.json"])
        d["sections"]["qk_panier_livraison"] = {"type": "qk-panier-livraison", "settings": {}}
        d["sections"].pop("qk_point_relais", None)  # 20/11/2026 : carte Mondial Relay retirée du panier (Amine)
        if "order" in d:
            d["order"] = [k for k in d["order"] if k != "qk_point_relais"]
        # panier en français et suggestions variées (demande d'Amine du 08/11/2026) : titre « Panier » ; la liste
        # « You may also like » du thème (4 premiers produits du catalogue, tous pareils) est remplacée par qk-suggestions
        for sec in d["sections"].values():
            for b in sec.get("blocks", {}).values():
                if b.get("type") == "_cart-title":
                    b["settings"]["title"] = "Panier"
        for k in [k for k, sec in d["sections"].items() if sec.get("type") == "product-list"]:
            del d["sections"][k]
        d["sections"]["qk_suggestions"] = {"type": "qk-suggestions", "settings": {"titre": "Tu aimeras aussi", "produits": DU_JOUR, "nombre": 8}}
        d["sections"]["qk_amb"] = ambiance(5, "Pivoine blanche dans un petit flacon de verre", "droite",
            ("Un cadeau ?", "Offre un parfum", "La livraison en point relais est offerte dès 2 articles en Belgique, aux Pays-Bas et au Luxembourg.", "Idées de parfums"),
            ("Een cadeau?", "Geef een parfum", "Gratis levering in een afhaalpunt vanaf 2 artikelen in België, Nederland en Luxemburg.", "Parfumideeën"),
            "/collections/parfums")
        d["order"] = ["qk_panier_livraison"] + [k for k in d["order"] if k in d["sections"] and k not in ("qk_panier_livraison", "qk_point_relais", "qk_suggestions", "qk_amb")] + ["qk_suggestions", "qk_amb"]
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
