#!/usr/bin/env python3
"""Page « Questions fréquentes » (/pages/faq, NL : veelgestelde vragen) — 13/11/2026, demande d'Amine (sur le modèle de la FAQ de Nose Paris).

Les réponses suivent les CGV et les pages Livraison et Retours (22/11/2026 : 9 pays, 6 à 7 jours ouvrables en Belgique, 8 à 11 ailleurs ; 2,95 € offerte dès 2 articles en Belgique,
14 jours, Bancontact / carte / Apple Pay). Un seul endroit à modifier : la liste FAQ ci-dessous.

  python3 scripts/page_faq.py --section   # régénère theme_rk/sections/qk-faq.liquid (à déployer avec theme-rk)
  python3 scripts/page_faq.py             # crée ou met à jour la page Shopify (modèle page.faq) + titre NL
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIL = "contact@qosmi.be"
M = '<a href="mailto:%s">%s</a>' % (MAIL, MAIL)

# (thème FR, thème NL, [(question FR, réponse FR, question NL, réponse NL)])
FAQ = [
    ("Commande et paiement", "Bestellen en betalen", [
        ("Vos parfums sont-ils authentiques ?",
         "Oui. Tous nos parfums sont des produits d'origine, neufs, vendus avec une facture d'achat. Nous ne vendons ni copies ni parfums « inspirés de ».",
         "Zijn jullie parfums origineel?",
         "Ja. Al onze parfums zijn originele, nieuwe producten, verkocht met een aankoopfactuur. Wij verkopen geen namaak en geen parfums die ‘geïnspireerd zijn op’."),
        ("Quels moyens de paiement acceptez-vous ?",
         "Bancontact, carte bancaire et Apple Pay. Le paiement est sécurisé et confirmé tout de suite par e-mail.",
         "Hoe kan ik betalen?",
         "Met Bancontact, bankkaart en Apple Pay. De betaling is beveiligd en wordt meteen per e-mail bevestigd."),
        ("Puis-je modifier ou annuler ma commande ?",
         "Écris-nous au plus vite à %s avec ton numéro de commande : si le colis n'est pas encore parti, nous faisons notre possible. Une fois le colis reçu, tu peux aussi utiliser ton droit de rétractation de 14 jours." % M,
         "Kan ik mijn bestelling wijzigen of annuleren?",
         "Schrijf ons zo snel mogelijk op %s met je bestelnummer: als het pakket nog niet vertrokken is, doen we ons best. Na ontvangst kan je ook je herroepingsrecht van 14 dagen gebruiken." % M),
    ]),
    ("Livraison", "Levering", [
        ("Combien coûte la livraison ?",
         "En Belgique : point relais Mondial Relay 2,95 €, <strong>offert dès 2 articles</strong>, ou livraison à domicile 6,95 €. Aux Pays-Bas et au Luxembourg : point relais 3,95 €, offert dès 2 articles. Dans les autres pays, les prix sont sur la page <a href=\"/pages/livraison\">Livraison</a>.",
         "Hoeveel kost de verzending?",
         "In België: Mondial Relay-afhaalpunt € 2,95, <strong>gratis vanaf 2 artikelen</strong>, of levering aan huis € 6,95. In Nederland en Luxemburg: afhaalpunt € 3,95, gratis vanaf 2 artikelen. Voor de andere landen staan de prijzen op de pagina <a href=\"/pages/livraison\">Levering</a>."),
        ("Quand vais-je recevoir mon colis ?",
         "En Belgique, en 6 à 7 jours ouvrables après la confirmation du paiement ; aux Pays-Bas, au Luxembourg et en France, en 8 à 9 jours ouvrables ; dans les autres pays, en 9 à 11 jours ouvrables. Le délai de ta commande est rappelé dans l'e-mail de confirmation.",
         "Wanneer ontvang ik mijn pakket?",
         "In België binnen 6 tot 7 werkdagen na bevestiging van de betaling; in Nederland, Luxemburg en Frankrijk binnen 8 tot 9 werkdagen; in de andere landen binnen 9 tot 11 werkdagen. De termijn van je bestelling staat ook in de bevestigingsmail."),
        ("Livrez-vous en dehors de la Belgique ?",
         "Oui : nous livrons en Belgique, aux Pays-Bas, au Luxembourg, en France, en Espagne, au Portugal, en Italie, en Allemagne et en Pologne. Prix et délais sur la page <a href=\"/pages/livraison\">Livraison</a>.",
         "Leveren jullie buiten België?",
         "Ja: wij leveren in België, Nederland, Luxemburg, Frankrijk, Spanje, Portugal, Italië, Duitsland en Polen. Prijzen en termijnen vind je op de pagina <a href=\"/pages/livraison\">Levering</a>."),
        ("Comment suivre mon colis ?",
         "Dès l'expédition, tu reçois un e-mail avec le lien de suivi.",
         "Hoe volg ik mijn pakket?",
         "Zodra je pakket vertrekt, krijg je een e-mail met de trackinglink."),
        ("Mon colis est abîmé, en retard ou incomplet",
         "Écris-nous à %s avec ton numéro de commande et, si possible, des photos. Nous trouvons une solution avec toi." % M,
         "Mijn pakket is beschadigd, te laat of onvolledig",
         "Schrijf ons op %s met je bestelnummer en, zo mogelijk, foto's. We zoeken samen een oplossing." % M),
    ]),
    ("Retours", "Retourneren", [
        ("Puis-je retourner un parfum ?",
         "Oui, tu as <strong>14 jours</strong> après réception pour changer d'avis. Écris-nous, puis renvoie le colis dans les 14 jours. Nous te remboursons, frais de livraison initiaux compris, au plus tard 14 jours après ta demande. Les frais de retour sont à ta charge. Tout est expliqué sur la page <a href=\"/pages/retours\">Retours</a>.",
         "Kan ik een parfum terugsturen?",
         "Ja, je hebt <strong>14 dagen</strong> na ontvangst om van gedachten te veranderen. Schrijf ons en stuur het pakket binnen 14 dagen terug. We betalen je terug, inclusief de oorspronkelijke verzendkosten, uiterlijk 14 dagen na je aanvraag. De retourkosten zijn voor jou. Alles staat op de pagina <a href=\"/pages/retours\">Retourneren</a>."),
        ("Et si j'ai déjà ouvert ou vaporisé le parfum ?",
         "Un produit scellé (film, opercule) dont le scellé a été retiré ne peut pas être repris, pour des raisons d'hygiène. Un flacon vaporisé perd de sa valeur : cette différence peut être déduite du remboursement.",
         "En als ik het parfum al geopend of verstoven heb?",
         "Een verzegeld product (folie, zegel) waarvan de verzegeling verbroken is, kan om hygiënische redenen niet terug. Een verstoven fles verliest waarde: dat verschil kan van de terugbetaling worden afgetrokken."),
        ("J'ai reçu un produit défectueux ou le mauvais produit",
         "Écris-nous à %s : dans ce cas, les frais de retour sont à notre charge." % M,
         "Ik kreeg een defect of verkeerd product",
         "Schrijf ons op %s: in dat geval zijn de retourkosten voor ons." % M),
    ]),
    ("Choisir son parfum", "Je parfum kiezen", [
        ("Quelle différence entre eau de toilette, eau de parfum et extrait ?",
         "C'est la concentration en essences. En général, une eau de toilette est plus légère, une eau de parfum plus concentrée, et un parfum ou un extrait l'est encore plus. Plus c'est concentré, plus le parfum tient et se fait sentir en principe, mais cela dépend aussi de la composition et de ta peau.",
         "Wat is het verschil tussen eau de toilette, eau de parfum en extrait?",
         "Het gaat om de concentratie aan geurstoffen. Meestal is een eau de toilette lichter, een eau de parfum geconcentreerder en een parfum of extrait nog meer. Hoe geconcentreerder, hoe langer de geur in principe blijft, maar dat hangt ook af van de samenstelling en je huid."),
        ("Comment trouver un parfum qui me plaît ?",
         "Fais notre <a href=\"/pages/quiz\">quiz</a>, ou cherche à partir des odeurs que tu aimes avec la <a href=\"/pages/odeurs\">recherche par odeurs</a>. Sur chaque fiche, le bloc « Parfums aux notes proches » te propose des parfums de la même famille.",
         "Hoe vind ik een parfum dat ik mooi vind?",
         "Doe onze <a href=\"/pages/quiz\">quiz</a>, of zoek vanuit de geuren die je mooi vindt met <a href=\"/pages/odeurs\">zoeken op geur</a>. Op elke productpagina toont het blok ‘Parfums met gelijkaardige noten’ parfums uit dezelfde familie."),
        ("Que veulent dire notes de tête, de cœur et de fond ?",
         "Ce sont les trois temps d'un parfum. Les notes de tête se sentent dès la vaporisation et partent vite. Les notes de cœur forment le caractère du parfum pendant quelques heures. Les notes de fond, plus lourdes, restent le plus longtemps sur la peau. D'autres mots du parfum sont expliqués dans notre <a href=\"/pages/lexique\">lexique</a>.",
         "Wat betekenen top-, hart- en basisnoten?",
         "Dat zijn de drie fases van een parfum. Topnoten ruik je meteen na het sprayen en ze verdwijnen snel. Hartnoten bepalen een paar uur lang het karakter van het parfum. Basisnoten zijn zwaarder en blijven het langst op je huid. Meer parfumwoorden vind je in ons <a href=\"/pages/lexique\">geurwoordenboek</a>."),
        ("Comment faire tenir mon parfum plus longtemps ?",
         "Vaporise-le sur une peau propre et hydratée, sur les points chauds (poignets, cou, creux des coudes), sans frotter. Une touche sur les vêtements ou les cheveux aide aussi à garder le sillage.",
         "Hoe blijft mijn parfum langer hangen?",
         "Spray het op een propere, gehydrateerde huid, op de warme plekken (polsen, hals, binnenkant van de ellebogen), zonder te wrijven. Een beetje op je kleren of haar helpt ook."),
        ("Comment conserver mon parfum ?",
         "À l'abri de la lumière et de la chaleur, flacon bien fermé. Évite la salle de bain, où l'humidité et les écarts de température abîment le parfum plus vite.",
         "Hoe bewaar ik mijn parfum?",
         "Uit het licht en weg van warmte, met de dop goed dicht. Vermijd de badkamer: vocht en temperatuurschommelingen beschadigen het parfum sneller."),
    ]),
    ("Ton compte et le site", "Je account en de site", [
        ("Le parfum que je veux est en rupture",
         "Sur sa fiche, clique sur « Préviens-moi quand il revient » et laisse ton e-mail : tu reçois un message dès qu'il est de nouveau disponible.",
         "Het parfum dat ik wil is uitverkocht",
         "Klik op de productpagina op ‘Laat me weten wanneer hij terug is’ en laat je e-mailadres achter: je krijgt een bericht zodra het weer beschikbaar is."),
        ("Comment garder des parfums de côté ?",
         "Clique sur le cœur d'un parfum pour l'ajouter à tes <a href=\"/pages/favoris\">favoris</a>. Tu les retrouves sur la page Favoris.",
         "Hoe bewaar ik parfums voor later?",
         "Klik op het hartje van een parfum om het aan je <a href=\"/pages/favoris\">favorieten</a> toe te voegen. Je vindt ze terug op de pagina Favorieten."),
        ("Comment vous contacter ?",
         "Par e-mail à %s. Nous répondons en français, en néerlandais et en anglais." % M,
         "Hoe kan ik jullie contacteren?",
         "Per e-mail op %s. We antwoorden in het Nederlands, Frans en Engels." % M),
    ]),
]


# 22/11/2026 (version anglaise) : thèmes et questions en anglais, clé = texte FR.
THEMES_EN = {"Commande et paiement": "Orders and payment", "Livraison": "Delivery", "Retours": "Returns",
             "Choisir son parfum": "Choosing your fragrance", "Ton compte et le site": "Your account and the site"}
FAQ_EN = {
    "Vos parfums sont-ils authentiques ?": ("Are your fragrances authentic?",
        "Yes. All our fragrances are genuine, brand-new products, sold with a purchase invoice. We don't sell copies or fragrances “inspired by” others."),
    "Quels moyens de paiement acceptez-vous ?": ("Which payment methods do you accept?",
        "Bancontact, bank card and Apple Pay. Payment is secure and confirmed straight away by email."),
    "Puis-je modifier ou annuler ma commande ?": ("Can I change or cancel my order?",
        "Write to us as soon as possible at %s with your order number: if the parcel hasn't left yet, we'll do our best. Once you've received it, you can also use your 14-day right of withdrawal." % M),
    "Combien coûte la livraison ?": ("How much is delivery?",
        "In Belgium: Mondial Relay pick-up point €2.95, <strong>free from 2 items</strong>, or home delivery €6.95. In the Netherlands and Luxembourg: pick-up point €3.95, free from 2 items. Prices for the other countries are on the <a href=\"/pages/livraison\">Shipping</a> page."),
    "Quand vais-je recevoir mon colis ?": ("When will I receive my parcel?",
        "In Belgium, within 6 to 7 working days after payment is confirmed; in the Netherlands, Luxembourg and France, within 8 to 9 working days; in the other countries, within 9 to 11 working days. Your order's delivery time is also in the confirmation email."),
    "Livrez-vous en dehors de la Belgique ?": ("Do you deliver outside Belgium?",
        "Yes: we deliver to Belgium, the Netherlands, Luxembourg, France, Spain, Portugal, Italy, Germany and Poland. Prices and delivery times are on the <a href=\"/pages/livraison\">Shipping</a> page."),
    "Comment suivre mon colis ?": ("How do I track my parcel?",
        "As soon as it ships, you'll get an email with the tracking link."),
    "Mon colis est abîmé, en retard ou incomplet": ("My parcel is damaged, late or incomplete",
        "Write to us at %s with your order number and, if possible, photos. We'll find a solution together." % M),
    "Puis-je retourner un parfum ?": ("Can I return a fragrance?",
        "Yes, you have <strong>14 days</strong> after receipt to change your mind. Write to us, then send the parcel back within 14 days. We'll refund you, including the original delivery costs, no later than 14 days after your request. Return costs are paid by you. Everything is explained on the <a href=\"/pages/retours\">Returns</a> page."),
    "Et si j'ai déjà ouvert ou vaporisé le parfum ?": ("What if I've already opened or sprayed the fragrance?",
        "A sealed product (film, seal) whose seal has been removed can't be taken back, for hygiene reasons. A sprayed bottle loses value: that difference may be deducted from the refund."),
    "J'ai reçu un produit défectueux ou le mauvais produit": ("I received a faulty or wrong product",
        "Write to us at %s: in that case, return costs are paid by us." % M),
    "Quelle différence entre eau de toilette, eau de parfum et extrait ?": ("What's the difference between eau de toilette, eau de parfum and extrait?",
        "It's the concentration of fragrance oils. Generally, an eau de toilette is lighter, an eau de parfum more concentrated, and a parfum or extrait even more so. The more concentrated it is, the longer it usually lasts and projects, but it also depends on the composition and your skin."),
    "Comment trouver un parfum qui me plaît ?": ("How do I find a fragrance I'll like?",
        "Take our <a href=\"/pages/quiz\">quiz</a>, or start from the scents you love with <a href=\"/pages/odeurs\">search by scent</a>. On every product page, the “Fragrances with similar notes” block suggests fragrances from the same family."),
    "Que veulent dire notes de tête, de cœur et de fond ?": ("What do top, heart and base notes mean?",
        "They're the three stages of a fragrance. Top notes are what you smell right after spraying, and they fade quickly. Heart notes shape the fragrance's character for a few hours. Base notes are heavier and stay on the skin the longest. More fragrance words are explained in our <a href=\"/pages/lexique\">glossary</a>."),
    "Comment faire tenir mon parfum plus longtemps ?": ("How can I make my fragrance last longer?",
        "Spray it on clean, moisturised skin, on pulse points (wrists, neck, inner elbows), without rubbing. A touch on your clothes or hair also helps keep the trail."),
    "Comment conserver mon parfum ?": ("How should I store my fragrance?",
        "Away from light and heat, with the bottle tightly closed. Avoid the bathroom, where humidity and temperature changes damage fragrance faster."),
    "Le parfum que je veux est en rupture": ("The fragrance I want is out of stock",
        "On its product page, click “Notify me when it's back” and leave your email: you'll get a message as soon as it's available again."),
    "Comment garder des parfums de côté ?": ("How do I save fragrances for later?",
        "Click the heart on a fragrance to add it to your <a href=\"/pages/favoris\">favourites</a>. You'll find them on the Favourites page."),
    "Comment vous contacter ?": ("How can I contact you?",
        "By email at %s. We reply in French, Dutch and English." % M),
}

INTERDITS = ["soleluna", "wholesale", "deloox", "qogita", "brasty", "trista", "marge", "margin", "dilbeek"]


def texte(h):
    return html.unescape(re.sub(r"<[^>]+>", "", h))


def section():
    for _, _, qs in FAQ:
        for q in qs:
            bas = " ".join(q).lower()
            for m in INTERDITS:
                if m in bas:
                    raise SystemExit("Contrôle de confidentialité : « %s » dans la FAQ" % m)

    def bloc(nl, en=False):
        out = []
        for t_fr, t_nl, qs in FAQ:
            out.append('<h2 class="qk-faq__theme">%s</h2>' % (t_nl if nl else THEMES_EN[t_fr] if en else t_fr))
            for q_fr, r_fr, q_nl, r_nl in qs:
                q, r = (q_nl, r_nl) if nl else FAQ_EN[q_fr] if en else (q_fr, r_fr)
                if en:
                    r = r.replace('href="/pages/', 'href="/en/pages/')
                if nl:
                    r = r.replace('href="/pages/', 'href="/nl/pages/').replace("/nl/pages/retours", "/nl/pages/retourneren").replace("/nl/pages/lexique", "/nl/pages/geurwoordenboek")
                out.append('<details class="qk-faq__q"><summary>%s</summary><div class="qk-faq__r"><p>%s</p></div></details>' % (q, r))
        return "\n".join(out)

    def ld(nl, en=False):
        e = [{"@type": "Question", "name": (q_nl if nl else FAQ_EN[q_fr][0] if en else q_fr),
              "acceptedAnswer": {"@type": "Answer", "text": texte(r_nl if nl else FAQ_EN[q_fr][1] if en else r_fr)}}
             for _, _, qs in FAQ for q_fr, r_fr, q_nl, r_nl in qs]
        return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": e}, ensure_ascii=False)

    liq = """{%- comment -%} Généré par scripts/page_faq.py : ne pas modifier à la main. FAQ Qosmi (13/11/2026). {%- endcomment -%}
{%- assign qk_nl = false -%}{%- if request.locale.iso_code == 'nl' -%}{%- assign qk_nl = true -%}{%- endif -%}{%- assign qk_en = false -%}{%- if request.locale.iso_code == 'en' -%}{%- assign qk_en = true -%}{%- endif -%}
<section class="qk-section qk-faq">
  <div class="qk-largeur qk-faq__largeur">
    <img class="qk-faq__image" src="{{ 'qosmi-papier-lavande.jpg' | file_url }}" alt="" width="2400" height="793" loading="eager">
    <h1 class="qk-titre-section">{% if qk_nl %}Veelgestelde vragen{% elsif qk_en %}FAQ{% else %}Questions fréquentes{% endif %}</h1>
    <p class="qk-faq__intro">{% if qk_nl %}Bestellen, levering, retourneren of je parfum kiezen: hier vind je de antwoorden. Staat je vraag er niet bij? Schrijf ons op <a href="mailto:MAIL">MAIL</a>.{% elsif qk_en %}Orders, delivery, returns or choosing a fragrance: it's all here. Can't find your question? Write to us at <a href="mailto:MAIL">MAIL</a>.{% else %}Commande, livraison, retours ou choix d'un parfum : tout est ici. Ta question n'y est pas ? Écris-nous à <a href="mailto:MAIL">MAIL</a>.{% endif %}</p>
    <input class="qk-faq__recherche" type="search" data-qk-faq-recherche placeholder="{% if qk_nl %}Zoek een vraag…{% elsif qk_en %}Search for a question…{% else %}Rechercher une question…{% endif %}" aria-label="{% if qk_nl %}Zoek een vraag{% elsif qk_en %}Search for a question{% else %}Rechercher une question{% endif %}">
    <div data-qk-faq>
      {%- if qk_nl -%}
BLOC_NL
      {%- elsif qk_en -%}
BLOC_EN
      {%- else -%}
BLOC_FR
      {%- endif -%}
    </div>
    <p class="qk-faq__vide" data-qk-faq-vide hidden>{% if qk_nl %}Geen vraag gevonden. Schrijf ons gerust op <a href="mailto:MAIL">MAIL</a>.{% elsif qk_en %}No question found. Write to us at <a href="mailto:MAIL">MAIL</a>.{% else %}Aucune question trouvée. Écris-nous à <a href="mailto:MAIL">MAIL</a>.{% endif %}</p>
  </div>
  {%- if qk_nl -%}
  <script type="application/ld+json">LD_NL</script>
  {%- elsif qk_en -%}
  <script type="application/ld+json">LD_EN</script>
  {%- else -%}
  <script type="application/ld+json">LD_FR</script>
  {%- endif -%}
  <script>
    (function () {
      var c = document.querySelector('[data-qk-faq-recherche]'), v = document.querySelector('[data-qk-faq-vide]');
      if (!c) return;
      var norm = function (s) { return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLowerCase(); };
      c.addEventListener('input', function () {
        var q = norm(c.value.trim()), n = 0;
        document.querySelectorAll('.qk-faq__q').forEach(function (d) {
          var ok = !q || norm(d.textContent).indexOf(q) >= 0;
          d.hidden = !ok; if (ok) n++;
          if (q && ok) d.open = true;
        });
        document.querySelectorAll('.qk-faq__theme').forEach(function (h) {
          var e = h.nextElementSibling, vis = false;
          while (e && !e.classList.contains('qk-faq__theme')) { if (!e.hidden) vis = true; e = e.nextElementSibling; }
          h.hidden = !vis;
        });
        v.hidden = n > 0;
      });
    })();
  </script>
</section>
{% schema %}
{ "name": "Qosmi · FAQ", "tag": "div", "settings": [] }
{% endschema %}
"""
    liq = (liq.replace("BLOC_NL", bloc(True)).replace("BLOC_EN", bloc(False, True)).replace("BLOC_FR", bloc(False))
              .replace("LD_NL", ld(True)).replace("LD_EN", ld(False, True)).replace("LD_FR", ld(False)).replace("MAIL", MAIL))
    open(os.path.join(RACINE, "theme_rk", "sections", "qk-faq.liquid"), "w", encoding="utf-8").write(liq)
    open(os.path.join(RACINE, "theme_rk", "templates", "page.faq.json"), "w", encoding="utf-8").write(
        json.dumps({"sections": {"main": {"type": "qk-faq", "settings": {}}}, "order": ["main"]}, indent=2) + "\n")
    print("Section qk-faq : %d questions" % sum(len(q) for _, _, q in FAQ))


def page():
    from shopify_api import Shopify
    s = Shopify()
    champs = {"title": "Questions fréquentes", "handle": "faq", "body": "", "isPublished": True, "templateSuffix": "faq"}
    d = s.gql('query($q: String!) { pages(first: 1, query: $q) { nodes { id } } }', {"q": "handle:faq"})["pages"]["nodes"]
    if d:
        r = s.gql("mutation($id: ID!, $p: PageUpdateInput!) { pageUpdate(id: $id, page: $p) { page { id } userErrors { field message } } }",
                  {"id": d[0]["id"], "p": champs})["pageUpdate"]
    else:
        r = s.gql("mutation($p: PageCreateInput!) { pageCreate(page: $p) { page { id } userErrors { field message } } }", {"p": champs})["pageCreate"]
    if r["userErrors"]:
        sys.exit("Refus : %s" % json.dumps(r["userErrors"], ensure_ascii=False))
    pid = r["page"]["id"]
    tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": pid})
    dig = {x["key"]: x["digest"] for x in (tr["translatableResource"] or {}).get("translatableContent", [])}
    t = [{"locale": "nl", "key": k, "value": v, "translatableContentDigest": dig[k]}
         for k, v in (("title", "Veelgestelde vragen"), ("handle", "veelgestelde-vragen")) if k in dig]
    e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
              {"id": pid, "t": t})["translationsRegister"]["userErrors"]
    print("Page FAQ OK :", pid, "NL :", e or "ok")


if __name__ == "__main__":
    section() if "--section" in sys.argv else page()
