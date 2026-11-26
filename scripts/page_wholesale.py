#!/usr/bin/env python3
"""Page « Wholesale B2B » (26/11/2026, demande d'Amine) : Qosmi vend aussi en gros aux professionnels, avec un numéro de
TVA ; l'offre est en cours de développement (comptes entreprise et catalogue B2B à venir sur le même Shopify).
FR + NL + EN, liée depuis le menu du bas de page (qosmi.be et qosmi.nl). Jamais de nom de fournisseur ni de prix.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WA = "https://wa.me/32465436329"
T = {
 "fr": ("wholesale", "Wholesale B2B : vente en gros aux professionnels", """
<p><strong>Qosmi vend aussi en gros aux professionnels</strong> : parfumeries, boutiques, concept stores, instituts de beauté et revendeurs en ligne. Parfums de marque, de niche et arabes, originaux et neufs, toujours avec facture.</p>
<h2>Conditions</h2>
<ul>
<li>Réservé aux entreprises disposant d'un <strong>numéro de TVA valide</strong>, en Belgique et dans l'Union européenne.</li>
<li>Facture établie au nom de votre société, conforme aux règles de TVA belges et européennes.</li>
<li>Tarifs et quantités communiqués sur demande, selon les produits.</li>
</ul>
<h2>Une offre en cours de développement</h2>
<p>Notre espace professionnel est en cours de développement : comptes entreprise, catalogue et tarifs dédiés arriveront prochainement. En attendant, vous pouvez déjà nous contacter pour nous présenter votre activité et vos besoins.</p>
<h2>Nous contacter</h2>
<p>E-mail : <a href="mailto:contact@qosmi.be">contact@qosmi.be</a> · WhatsApp : <a href="{WA}">+32 465 43 63 29</a></p>
<p>Merci d'indiquer le nom de votre société, votre numéro de TVA, votre pays et les produits ou marques qui vous intéressent.</p>
""".replace("{WA}", WA)),
 "nl": ("wholesale", "Wholesale B2B: groothandel voor professionals", """
<p><strong>Qosmi verkoopt ook in het groot aan professionals</strong>: parfumerieën, winkels, conceptstores, schoonheidsinstituten en onlineverkopers. Merk-, niche- en Arabische parfums, origineel en nieuw, altijd met factuur.</p>
<h2>Voorwaarden</h2>
<ul>
<li>Enkel voor bedrijven met een <strong>geldig btw-nummer</strong>, in België en in de Europese Unie.</li>
<li>Factuur op naam van uw bedrijf, volgens de Belgische en Europese btw-regels.</li>
<li>Prijzen en hoeveelheden op aanvraag, afhankelijk van de producten.</li>
</ul>
<h2>Een aanbod in ontwikkeling</h2>
<p>Onze professionele ruimte is in ontwikkeling: bedrijfsaccounts, een eigen catalogus en eigen tarieven volgen binnenkort. Ondertussen kunt u ons al contacteren om uw activiteit en uw noden voor te stellen.</p>
<h2>Contact</h2>
<p>E-mail: <a href="mailto:contact@qosmi.be">contact@qosmi.be</a> · WhatsApp: <a href="{WA}">+32 465 43 63 29</a></p>
<p>Vermeld de naam van uw bedrijf, uw btw-nummer, uw land en de producten of merken die u interesseren.</p>
""".replace("{WA}", WA)),
 "en": ("wholesale", "Wholesale B2B: trade sales for professionals", """
<p><strong>Qosmi also sells wholesale to professionals</strong>: perfumeries, shops, concept stores, beauty salons and online resellers. Designer, niche and Arabian fragrances, original and brand-new, always with an invoice.</p>
<h2>Conditions</h2>
<ul>
<li>Reserved for businesses with a <strong>valid VAT number</strong>, in Belgium and the European Union.</li>
<li>Invoice issued in your company's name, in line with Belgian and European VAT rules.</li>
<li>Prices and quantities on request, depending on the products.</li>
</ul>
<h2>An offer in development</h2>
<p>Our professional area is in development: business accounts, a dedicated catalogue and dedicated prices are coming soon. In the meantime, you can already contact us to introduce your business and your needs.</p>
<h2>Contact</h2>
<p>Email: <a href="mailto:contact@qosmi.be">contact@qosmi.be</a> · WhatsApp: <a href="{WA}">+32 465 43 63 29</a></p>
<p>Please include your company name, VAT number, country and the products or brands you are interested in.</p>
""".replace("{WA}", WA)),
}

SEO = {"fr": "Qosmi vend aussi en gros aux professionnels avec un numéro de TVA : parfums de marque, de niche et arabes, originaux et neufs, avec facture.",
       "nl": "Qosmi verkoopt ook in het groot aan professionals met een btw-nummer: merk-, niche- en Arabische parfums, origineel en nieuw, met factuur.",
       "en": "Qosmi also sells wholesale to professionals with a VAT number: designer, niche and Arabian fragrances, original and brand-new, with an invoice."}

INTERDITS = ["soleluna", "deloox", "qogita", "brasty", "trista", "marge", "margin", "ijsbergstraat", "dilbeek", "dupe", "€"]


def main():
    for loc, (_, _, b) in T.items():
        bad = [w for w in INTERDITS if w in b.lower()]
        if bad:
            sys.exit("Mot interdit (%s) : %s" % (loc, bad))
    from shopify_api import Shopify
    s = Shopify()
    h, t, body = T["fr"]
    champs = {"title": t, "handle": h, "body": body.strip(), "isPublished": True,
              "metafields": [{"namespace": "global", "key": "description_tag", "type": "single_line_text_field", "value": SEO["fr"]}]}
    d = s.gql('query($q: String!) { pages(first: 1, query: $q) { nodes { id } } }', {"q": "handle:%s" % h})["pages"]["nodes"]
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
    print("Champs traduisibles :", sorted(dig))
    for loc in ("nl", "en"):
        hh, tt, bb = T[loc]
        vals = {"title": tt, "body_html": bb.strip(), "meta_description": SEO[loc]}  # même adresse « wholesale » dans les 3 langues
        lst = [{"locale": loc, "key": k, "value": v, "translatableContentDigest": dig[k]} for k, v in vals.items() if k in dig]
        e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
                  {"id": pid, "t": lst})["translationsRegister"]["userErrors"]
        print("%s : %d champs, %s" % (loc.upper(), len(lst), e or "ok"))
    # lien dans le menu du bas de page (en tête), titres NL/EN via la traduction du lien
    menus = s.gql("{ menus(first: 20) { nodes { id handle title items { id title type resourceId url } } } }")["menus"]["nodes"]
    pied = next((m for m in menus if m["handle"] == "footer"), None)
    if pied and not any(i.get("resourceId") == pid for i in pied["items"]):
        garder = [{"id": i["id"], "title": i["title"], "type": i["type"],
                   **({"resourceId": i["resourceId"]} if i.get("resourceId") else {}),
                   **({"url": i["url"]} if i.get("url") and not i.get("resourceId") else {})} for i in pied["items"]]
        r = s.gql("""mutation($id: ID!, $t: String!, $h: String!, $i: [MenuItemUpdateInput!]!) {
                   menuUpdate(id: $id, title: $t, handle: $h, items: $i) { menu { items { id resourceId } } userErrors { field message } } }""",
                  {"id": pied["id"], "t": pied["title"], "h": pied["handle"],
                   "i": garder + [{"title": "Wholesale B2B", "type": "PAGE", "resourceId": pid}]})["menuUpdate"]
        print("Menu du bas de page :", r["userErrors"] or "lien ajouté")
        menus = s.gql("{ menus(first: 20) { nodes { id handle title items { id title type resourceId url } } } }")["menus"]["nodes"]
        pied = next((m for m in menus if m["handle"] == "footer"), None)
    lien = next((i for i in (pied or {}).get("items", []) if i.get("resourceId") == pid), None)
    if lien:
        lid = lien["id"].replace("MenuItem", "Link")
        try:
            tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": lid})
            dg = {x["key"]: x["digest"] for x in (tr["translatableResource"] or {}).get("translatableContent", [])}
            for loc, titre in (("nl", "Wholesale B2B"), ("en", "Wholesale B2B")):
                if "title" in dg:
                    e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
                              {"id": lid, "t": [{"locale": loc, "key": "title", "value": titre, "translatableContentDigest": dg["title"]}]})["translationsRegister"]["userErrors"]
                    print("Lien %s : %s" % (loc.upper(), e or "ok"))
        except Exception as ex:
            print("Traduction du lien non faite :", ex)
    print("Page OK :", pid)


if __name__ == "__main__":
    main()
