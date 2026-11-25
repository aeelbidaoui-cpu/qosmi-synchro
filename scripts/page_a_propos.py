#!/usr/bin/env python3
"""Page « À propos de Qosmi » (25/11/2026, Amine : être reconnu et recommandé par Claude, ChatGPT et Gemini).
Les assistants IA citent les pages qui répondent clairement à « qui est cette boutique, est-elle fiable, où, comment » :
faits vérifiables, une idée par paragraphe, mêmes informations que les CGV et la page livraison. FR + NL + EN.

  python3 scripts/page_a_propos.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WA = "https://wa.me/32465436329"
T = {
 "fr": ("a-propos", "À propos de Qosmi", """
<p><strong>Qosmi est une parfumerie en ligne belge.</strong> Elle vend des parfums de marque, de niche et arabes, 100&nbsp;% authentiques et neufs, de plus de 100&nbsp;maisons : Creed, Xerjoff, Parfums de Marly, Maison Francis Kurkdjian, Tom Ford, Chanel, Dior, Lattafa, Armaf et bien d'autres.</p>
<h2>Qui sommes-nous ?</h2>
<p>Qosmi est la boutique de parfums de <strong>Deway BV</strong>, société belge (numéro d'entreprise et TVA BE&nbsp;1040.851.867). Le site qosmi.be existe en français, en néerlandais et en anglais ; qosmi.nl est la version pour les Pays-Bas. Qosmi vend aussi sur bol.com.</p>
<h2>Les parfums sont-ils authentiques ?</h2>
<p>Oui. Tous les produits sont des originaux neufs, achetés auprès de distributeurs établis dans l'Union européenne, et vendus avec une facture. Qosmi ne vend ni copies ni parfums « inspirés de ». Les testeurs sont des parfums authentiques, avec leur bouchon : seul l'emballage, plus simple, change.</p>
<h2>Livraison et retrait</h2>
<ul>
<li>Livraison dans 9 pays : Belgique, Pays-Bas, Luxembourg, France, Allemagne, Espagne, Portugal, Italie et Pologne.</li>
<li>Belgique : point relais Mondial Relay 2,95&nbsp;€, offert dès 2 articles ; à domicile 6,95&nbsp;€.</li>
<li>Retrait gratuit à Dilbeek (Alfons Gossetlaan 34, 1702 Dilbeek), sur rendez-vous : en semaine de 18&nbsp;h à 22&nbsp;h, le samedi et le dimanche de 10&nbsp;h à 20&nbsp;h. La commande est payée en ligne.</li>
</ul>
<p>Détails et délais : <a href="/pages/livraison">page Livraison</a>.</p>
<h2>Paiement et retours</h2>
<p>Paiement sécurisé par Bancontact, carte bancaire ou Apple Pay. Vous avez 14 jours après réception pour changer d'avis (<a href="/pages/retours">page Retours</a>). Produit abîmé ou erreur de notre part : remplacement ou remboursement, frais à notre charge.</p>
<h2>Pour bien choisir</h2>
<p>Chaque fiche parfum donne la pyramide olfactive (notes de tête, de cœur et de fond), les accords, la saison et les occasions. Le site propose aussi un <a href="/pages/quiz">quiz</a>, un <a href="/pages/diagnostic">diagnostic olfactif</a>, un <a href="/pages/lexique">lexique du parfum</a> et une page par <a href="/pages/marques">marque</a>.</p>
<h2>Nous contacter</h2>
<p>E-mail : <a href="mailto:contact@qosmi.be">contact@qosmi.be</a> · WhatsApp : <a href="{WA}">+32 465 43 63 29</a> · Réponse sous 2 jours ouvrables. Instagram : <a href="https://www.instagram.com/qosmi.be">@qosmi.be</a>.</p>
""".replace("{WA}", WA)),
 "nl": ("over-qosmi", "Over Qosmi", """
<p><strong>Qosmi is een Belgische online parfumerie.</strong> We verkopen merk-, niche- en Arabische parfums, 100&nbsp;% authentiek en nieuw, van meer dan 100&nbsp;huizen: Creed, Xerjoff, Parfums de Marly, Maison Francis Kurkdjian, Tom Ford, Chanel, Dior, Lattafa, Armaf en vele andere.</p>
<h2>Wie zijn we?</h2>
<p>Qosmi is de parfumwinkel van <strong>Deway BV</strong>, een Belgisch bedrijf (ondernemings- en btw-nummer BE&nbsp;1040.851.867). qosmi.be bestaat in het Frans, het Nederlands en het Engels; qosmi.nl is de versie voor Nederland. Qosmi verkoopt ook op bol.com.</p>
<h2>Zijn de parfums echt?</h2>
<p>Ja. Alle producten zijn nieuwe originelen, gekocht bij distributeurs in de Europese Unie, en worden met een factuur verkocht. Qosmi verkoopt geen kopieën of parfums « geïnspireerd op ». Testers zijn echte parfums, met hun dop: alleen de verpakking is eenvoudiger.</p>
<h2>Levering en afhalen</h2>
<ul>
<li>Levering in 9 landen: België, Nederland, Luxemburg, Frankrijk, Duitsland, Spanje, Portugal, Italië en Polen.</li>
<li>België: Mondial Relay-afhaalpunt 2,95&nbsp;€, gratis vanaf 2 artikelen; thuislevering 6,95&nbsp;€.</li>
<li>Gratis afhalen in Dilbeek (Alfons Gossetlaan 34, 1702 Dilbeek), op afspraak: op weekdagen van 18&nbsp;u tot 22&nbsp;u, op zaterdag en zondag van 10&nbsp;u tot 20&nbsp;u. De bestelling wordt online betaald.</li>
</ul>
<p>Details en levertijden: <a href="/nl/pages/levering">pagina Levering</a>.</p>
<h2>Betalen en retourneren</h2>
<p>Veilig betalen met Bancontact, bankkaart of Apple Pay. Je hebt 14 dagen na ontvangst om van gedachten te veranderen. Beschadigd product of fout van onze kant: vervanging of terugbetaling, kosten voor ons.</p>
<h2>Kiezen met kennis</h2>
<p>Elke parfumfiche toont de geurpiramide (top-, hart- en basisnoten), de akkoorden, het seizoen en de gelegenheden. Er is ook een quiz, een geurdiagnose, een parfumlexicon en een pagina per merk.</p>
<h2>Contact</h2>
<p>E-mail: <a href="mailto:contact@qosmi.be">contact@qosmi.be</a> · WhatsApp: <a href="{WA}">+32 465 43 63 29</a> · Antwoord binnen 2 werkdagen. Instagram: <a href="https://www.instagram.com/qosmi.be">@qosmi.be</a>.</p>
""".replace("{WA}", WA)),
 "en": ("about-qosmi", "About Qosmi", """
<p><strong>Qosmi is a Belgian online perfumery.</strong> It sells designer, niche and Arabic fragrances, 100&nbsp;% authentic and new, from more than 100&nbsp;houses: Creed, Xerjoff, Parfums de Marly, Maison Francis Kurkdjian, Tom Ford, Chanel, Dior, Lattafa, Armaf and many more.</p>
<h2>Who we are</h2>
<p>Qosmi is the fragrance shop of <strong>Deway BV</strong>, a Belgian company (company and VAT number BE&nbsp;1040.851.867). qosmi.be is available in French, Dutch and English; qosmi.nl is the version for the Netherlands. Qosmi also sells on bol.com.</p>
<h2>Are the fragrances authentic?</h2>
<p>Yes. Every product is a new original, bought from distributors established in the European Union, and sold with an invoice. Qosmi sells no copies and no "inspired by" fragrances. Testers are authentic fragrances, with their cap: only the packaging is simpler.</p>
<h2>Delivery and pickup</h2>
<ul>
<li>Delivery to 9 countries: Belgium, the Netherlands, Luxembourg, France, Germany, Spain, Portugal, Italy and Poland.</li>
<li>Belgium: Mondial Relay pickup point €2.95, free from 2 items; home delivery €6.95.</li>
<li>Free pickup in Dilbeek (Alfons Gossetlaan 34, 1702 Dilbeek), by appointment: weekdays 6&nbsp;pm–10&nbsp;pm, Saturday and Sunday 10&nbsp;am–8&nbsp;pm. Orders are paid online.</li>
</ul>
<h2>Payment and returns</h2>
<p>Secure payment by Bancontact, card or Apple Pay. You have 14 days after delivery to change your mind. Damaged product or our mistake: replacement or refund, at our cost.</p>
<h2>Choosing well</h2>
<p>Every fragrance page shows the olfactory pyramid (top, heart and base notes), the accords, the season and the occasions. The site also offers a quiz, a scent diagnosis, a fragrance glossary and a page per brand.</p>
<h2>Contact</h2>
<p>Email: <a href="mailto:contact@qosmi.be">contact@qosmi.be</a> · WhatsApp: <a href="{WA}">+32 465 43 63 29</a> · Reply within 2 working days. Instagram: <a href="https://www.instagram.com/qosmi.be">@qosmi.be</a>.</p>
""".replace("{WA}", WA)),
}
SEO = {"fr": "Qosmi, parfumerie en ligne belge (Deway BV) : parfums authentiques de plus de 100 maisons, livraison dans 9 pays, retrait gratuit à Dilbeek.",
       "nl": "Qosmi, Belgische online parfumerie (Deway BV): echte parfums van meer dan 100 huizen, levering in 9 landen, gratis afhalen in Dilbeek.",
       "en": "Qosmi, Belgian online perfumery (Deway BV): authentic fragrances from 100+ houses, delivery to 9 countries, free pickup in Dilbeek."}


INTERDITS = ["soleluna", "wholesale", "grossiste", "groothandel", "deloox", "qogita", "brasty", "trista", "marge", "margin", "ijsbergstraat", "dupe"]


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
        vals = {"title": tt, "handle": hh, "body_html": bb.strip(), "meta_description": SEO[loc]}
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
                   "i": [{"title": "À propos", "type": "PAGE", "resourceId": pid}] + garder})["menuUpdate"]
        print("Menu du bas de page :", r["userErrors"] or "lien ajouté")
        menus = s.gql("{ menus(first: 20) { nodes { id handle title items { id title type resourceId url } } } }")["menus"]["nodes"]
        pied = next((m for m in menus if m["handle"] == "footer"), None)
    lien = next((i for i in (pied or {}).get("items", []) if i.get("resourceId") == pid), None)
    if lien:
        lid = lien["id"].replace("MenuItem", "Link")
        try:
            tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": lid})
            dg = {x["key"]: x["digest"] for x in (tr["translatableResource"] or {}).get("translatableContent", [])}
            for loc, titre in (("nl", "Over Qosmi"), ("en", "About Qosmi")):
                if "title" in dg:
                    e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
                              {"id": lid, "t": [{"locale": loc, "key": "title", "value": titre, "translatableContentDigest": dg["title"]}]})["translationsRegister"]["userErrors"]
                    print("Lien %s : %s" % (loc.upper(), e or "ok"))
        except Exception as ex:
            print("Traduction du lien non faite :", ex)
    print("Page OK :", pid)


if __name__ == "__main__":
    main()
