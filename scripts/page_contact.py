#!/usr/bin/env python3
"""Page Contact (26/11/2026, demande d'Amine) : e-mail, WhatsApp et délais de réponse, au-dessus du formulaire. Pas d'adresse
(choix d'Amine). FR + NL + EN. Seuls le texte et la méta-description changent : titre et adresse de la page restent."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WA = "https://wa.me/32465436329"
T = {
    "fr": """
<p>Une question sur un parfum, une commande ou une livraison ? Écris-nous, nous te répondons avec plaisir.</p>
<ul>
<li><strong>E-mail :</strong> <a href="mailto:contact@qosmi.be">contact@qosmi.be</a></li>
<li><strong>WhatsApp :</strong> <a href="{WA}">+32 465 43 63 29</a></li>
<li><strong>Quand ?</strong> Nous répondons les jours ouvrables, du lundi au vendredi, en général dans les 2 jours.</li>
</ul>
<p>Pour une commande, indique ton numéro de commande : nous te répondrons plus vite. Tu peux aussi utiliser le formulaire ci-dessous.</p>
<p>Avant d'écrire, tu trouveras peut-être ta réponse dans la <a href="/pages/faq">FAQ</a>, sur la page <a href="/pages/livraison">Livraison</a> ou sur la page <a href="/pages/authenticite">Authenticité</a>.</p>
""",
    "nl": """
<p>Een vraag over een parfum, een bestelling of een levering? Schrijf ons, we helpen je graag.</p>
<ul>
<li><strong>E-mail:</strong> <a href="mailto:contact@qosmi.be">contact@qosmi.be</a></li>
<li><strong>WhatsApp:</strong> <a href="{WA}">+32 465 43 63 29</a></li>
<li><strong>Wanneer?</strong> We antwoorden op werkdagen, van maandag tot vrijdag, meestal binnen 2 dagen.</li>
</ul>
<p>Gaat het om een bestelling? Vermeld je bestelnummer, dan antwoorden we sneller. Je kunt ook het formulier hieronder gebruiken.</p>
<p>Misschien vind je je antwoord al in de <a href="/nl/pages/faq">FAQ</a>, op de pagina <a href="/nl/pages/livraison">Levering</a> of op de pagina <a href="/nl/pages/echtheid">Echtheid</a>.</p>
""",
    "en": """
<p>A question about a fragrance, an order or a delivery? Write to us, we are happy to help.</p>
<ul>
<li><strong>Email:</strong> <a href="mailto:contact@qosmi.be">contact@qosmi.be</a></li>
<li><strong>WhatsApp:</strong> <a href="{WA}">+32 465 43 63 29</a></li>
<li><strong>When?</strong> We reply on working days, Monday to Friday, usually within 2 days.</li>
</ul>
<p>About an order? Include your order number and we will reply faster. You can also use the form below.</p>
<p>You may already find your answer in the <a href="/en/pages/faq">FAQ</a>, on the <a href="/en/pages/livraison">Delivery</a> page or on the <a href="/en/pages/authenticity">Authenticity</a> page.</p>
""",
}
SEO = {"fr": "Contacter Qosmi : e-mail contact@qosmi.be ou WhatsApp +32 465 43 63 29. Réponse les jours ouvrables, en général sous 2 jours.",
       "nl": "Contact met Qosmi: e-mail contact@qosmi.be of WhatsApp +32 465 43 63 29. Antwoord op werkdagen, meestal binnen 2 dagen.",
       "en": "Contact Qosmi: email contact@qosmi.be or WhatsApp +32 465 43 63 29. We reply on working days, usually within 2 days."}


def main():
    from shopify_api import Shopify
    s = Shopify()
    d = s.gql('query($q: String!) { pages(first: 1, query: $q) { nodes { id title } } }', {"q": "handle:contact"})["pages"]["nodes"]
    if not d:
        sys.exit("page contact introuvable")
    pid = d[0]["id"]
    r = s.gql("mutation($id: ID!, $p: PageUpdateInput!) { pageUpdate(id: $id, page: $p) { page { id } userErrors { field message } } }",
              {"id": pid, "p": {"body": T["fr"].replace("{WA}", WA).strip(),
                                "metafields": [{"namespace": "global", "key": "description_tag", "type": "single_line_text_field", "value": SEO["fr"]}]}})["pageUpdate"]
    print("FR :", r["userErrors"] or "ok")
    tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": pid})
    dig = {x["key"]: x["digest"] for x in (tr["translatableResource"] or {}).get("translatableContent", [])}
    for loc in ("nl", "en"):
        vals = {"body_html": T[loc].replace("{WA}", WA).strip(), "meta_description": SEO[loc]}
        lst = [{"locale": loc, "key": k, "value": v, "translatableContentDigest": dig[k]} for k, v in vals.items() if k in dig]
        e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
                  {"id": pid, "t": lst})["translationsRegister"]["userErrors"]
        print("%s : %d champs, %s" % (loc.upper(), len(lst), e or "ok"))


if __name__ == "__main__":
    main()
