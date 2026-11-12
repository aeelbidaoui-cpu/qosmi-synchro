#!/usr/bin/env python3
"""Page « Questions fréquentes » (/pages/faq, NL : veelgestelde vragen) — 13/11/2026, demande d'Amine (sur le modèle de la FAQ de Nose Paris).

Les réponses suivent les CGV et les pages Livraison et Retours (2,95 €, offerte dès 2 articles, 3 à 6 jours ouvrables,
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
         "2,95 € par commande, et la livraison est <strong>offerte dès 2 articles</strong>.",
         "Hoeveel kost de verzending?",
         "€ 2,95 per bestelling, en de verzending is <strong>gratis vanaf 2 artikelen</strong>."),
        ("Quand vais-je recevoir mon colis ?",
         "En 3 à 6 jours ouvrables après la confirmation du paiement. Le délai de ta commande est rappelé dans l'e-mail de confirmation.",
         "Wanneer ontvang ik mijn pakket?",
         "Binnen 3 tot 6 werkdagen na bevestiging van de betaling. De termijn van je bestelling staat ook in de bevestigingsmail."),
        ("Livrez-vous en dehors de la Belgique ?",
         "Pas pour le moment : nous livrons partout en Belgique.",
         "Leveren jullie buiten België?",
         "Voorlopig niet: wij leveren in heel België."),
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
         "Ce sont les trois temps d'un parfum. Les notes de tête se sentent dès la vaporisation et partent vite. Les notes de cœur forment le caractère du parfum pendant quelques heures. Les notes de fond, plus lourdes, restent le plus longtemps sur la peau.",
         "Wat betekenen top-, hart- en basisnoten?",
         "Dat zijn de drie fases van een parfum. Topnoten ruik je meteen na het sprayen en ze verdwijnen snel. Hartnoten bepalen een paar uur lang het karakter van het parfum. Basisnoten zijn zwaarder en blijven het langst op je huid."),
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

    def bloc(nl):
        out = []
        for t_fr, t_nl, qs in FAQ:
            out.append('<h2 class="qk-faq__theme">%s</h2>' % (t_nl if nl else t_fr))
            for q_fr, r_fr, q_nl, r_nl in qs:
                q, r = (q_nl, r_nl) if nl else (q_fr, r_fr)
                if nl:
                    r = r.replace('href="/pages/', 'href="/nl/pages/').replace("/nl/pages/retours", "/nl/pages/retourneren")
                out.append('<details class="qk-faq__q"><summary>%s</summary><div class="qk-faq__r"><p>%s</p></div></details>' % (q, r))
        return "\n".join(out)

    def ld(nl):
        e = [{"@type": "Question", "name": (q_nl if nl else q_fr),
              "acceptedAnswer": {"@type": "Answer", "text": texte(r_nl if nl else r_fr)}}
             for _, _, qs in FAQ for q_fr, r_fr, q_nl, r_nl in qs]
        return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": e}, ensure_ascii=False)

    liq = """{%- comment -%} Généré par scripts/page_faq.py : ne pas modifier à la main. FAQ Qosmi (13/11/2026). {%- endcomment -%}
{%- assign qk_nl = false -%}{%- if request.locale.iso_code == 'nl' -%}{%- assign qk_nl = true -%}{%- endif -%}
<section class="qk-section qk-faq">
  <div class="qk-largeur qk-faq__largeur">
    <img class="qk-faq__image" src="{{ 'qosmi-papier-lavande.jpg' | file_url }}" alt="" width="2400" height="793" loading="eager">
    <h1 class="qk-titre-section">{% if qk_nl %}Veelgestelde vragen{% else %}Questions fréquentes{% endif %}</h1>
    <p class="qk-faq__intro">{% if qk_nl %}Bestellen, levering, retourneren of je parfum kiezen: hier vind je de antwoorden. Staat je vraag er niet bij? Schrijf ons op <a href="mailto:MAIL">MAIL</a>.{% else %}Commande, livraison, retours ou choix d'un parfum : tout est ici. Ta question n'y est pas ? Écris-nous à <a href="mailto:MAIL">MAIL</a>.{% endif %}</p>
    <input class="qk-faq__recherche" type="search" data-qk-faq-recherche placeholder="{% if qk_nl %}Zoek een vraag…{% else %}Rechercher une question…{% endif %}" aria-label="{% if qk_nl %}Zoek een vraag{% else %}Rechercher une question{% endif %}">
    <div data-qk-faq>
      {%- if qk_nl -%}
BLOC_NL
      {%- else -%}
BLOC_FR
      {%- endif -%}
    </div>
    <p class="qk-faq__vide" data-qk-faq-vide hidden>{% if qk_nl %}Geen vraag gevonden. Schrijf ons gerust op <a href="mailto:MAIL">MAIL</a>.{% else %}Aucune question trouvée. Écris-nous à <a href="mailto:MAIL">MAIL</a>.{% endif %}</p>
  </div>
  {%- if qk_nl -%}
  <script type="application/ld+json">LD_NL</script>
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
    liq = (liq.replace("BLOC_NL", bloc(True)).replace("BLOC_FR", bloc(False))
              .replace("LD_NL", ld(True)).replace("LD_FR", ld(False)).replace("MAIL", MAIL))
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
