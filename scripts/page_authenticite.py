#!/usr/bin/env python3
"""Page « Parfums authentiques : nos garanties » (26/11/2026, audit SEO, accord d'Amine du 26/11 : « oui »).
Les audits SEO notaient que « 100 % authentiques » n'était appuyé par aucune page. Cette page explique, en faits simples,
pourquoi et comment Qosmi garantit l'authenticité. Jamais de nom de fournisseur, pas d'adresse, pas de prix. FR + NL + EN.
Elle est liée depuis chaque fiche (bloc de réassurance, scripts/theme_rk.py) et depuis le bas de page.

  python3 scripts/page_authenticite.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WA = "https://wa.me/32465436329"
T = {
 "fr": ("authenticite", "Parfums authentiques : nos garanties", """
<p><strong>Tous les parfums vendus par Qosmi sont des originaux, neufs, de la marque indiquée.</strong> Pas de copie, pas de parfum « inspiré de », pas de flacon reconditionné. Voici ce que nous garantissons, et comment le vérifier vous-même.</p>
<h2>D'où viennent nos parfums ?</h2>
<p>Nous achetons uniquement auprès de distributeurs établis dans l'Union européenne, qui revendent les produits des marques. Chaque achat est facturé, et chaque parfum peut être retracé jusqu'à son lot de fabrication.</p>
<h2>Une facture avec chaque commande</h2>
<p>Chaque commande est accompagnée d'une facture de Qosmi, boutique d'une société belge enregistrée (voir la page <a href="/pages/a-propos">À propos</a>). Elle vous sert de preuve d'achat, par exemple pour un cadeau ou en cas de question.</p>
<h2>Comment vérifier un parfum ?</h2>
<ul>
<li>Le flacon et la boîte portent le même <strong>code de lot</strong> (une suite de chiffres et de lettres, souvent gravée sous le flacon et imprimée sous la boîte).</li>
<li>Ce code permet de retrouver la date de fabrication auprès de la marque ou sur des sites spécialisés dans les codes de lot.</li>
<li>Le parfum est neuf : jamais ouvert ni utilisé avant de vous être envoyé.</li>
</ul>
<h2>Et les testeurs ?</h2>
<p>Un testeur est un parfum authentique, de la même composition, que la marque destine aux démonstrations en magasin. Il est livré dans un emballage plus simple (boîte blanche ou brune), parfois sans bouchon décoratif. Sur le site, les testeurs sont toujours indiqués comme tels.</p>
<h2>Pourquoi nos prix sont-ils plus doux ?</h2>
<p>Qosmi vend uniquement en ligne, sans magasin ni vitrine à financer, et compare ses prix chaque semaine. C'est ce qui permet des prix justes, toute l'année, sans fausses promotions.</p>
<h2>Si vous avez un doute</h2>
<p>Écrivez-nous avec une photo du flacon et de la boîte : nous vous répondons sous 2 jours ouvrables. Un produit abîmé ou non conforme est remplacé ou remboursé, frais à notre charge. Et vous avez toujours 14 jours après réception pour changer d'avis (flacon non ouvert) : voir la page <a href="/pages/retours">Retours</a>.</p>
<h2>Paiement et livraison</h2>
<p>Paiement sécurisé par Bancontact, carte bancaire ou Apple Pay. Livraison en Belgique et dans 8 autres pays européens (Pays-Bas, Luxembourg, France, Allemagne, Espagne, Portugal, Italie, Pologne) : voir la page <a href="/pages/livraison">Livraison</a>.</p>
<p>Contact : <a href="mailto:contact@qosmi.be">contact@qosmi.be</a> · WhatsApp <a href="{WA}">+32 465 43 63 29</a>.</p>
""".replace("{WA}", WA)),
 "nl": ("echtheid", "Echte parfums: onze garanties", """
<p><strong>Alle parfums die Qosmi verkoopt zijn originelen, nieuw, van het vermelde merk.</strong> Geen kopieën, geen parfums « geïnspireerd op », geen hervulde flessen. Dit is wat we garanderen, en hoe je het zelf kunt nakijken.</p>
<h2>Waar komen onze parfums vandaan?</h2>
<p>We kopen alleen bij distributeurs die in de Europese Unie gevestigd zijn en de producten van de merken doorverkopen. Elke aankoop wordt gefactureerd en elk parfum is terug te voeren tot zijn productiepartij.</p>
<h2>Een factuur bij elke bestelling</h2>
<p>Bij elke bestelling hoort een factuur van Qosmi, de winkel van een geregistreerd Belgisch bedrijf (zie <a href="/nl/pages/over-qosmi">Over Qosmi</a>). Dat is je aankoopbewijs, bijvoorbeeld voor een cadeau of als je een vraag hebt.</p>
<h2>Hoe controleer je een parfum?</h2>
<ul>
<li>De fles en de doos dragen dezelfde <strong>batchcode</strong> (een reeks cijfers en letters, vaak gegraveerd onder de fles en gedrukt onder de doos).</li>
<li>Met die code vind je de productiedatum terug bij het merk of op websites die batchcodes uitlezen.</li>
<li>Het parfum is nieuw: nooit geopend of gebruikt voor het naar jou vertrekt.</li>
</ul>
<h2>En testers?</h2>
<p>Een tester is een echt parfum, met dezelfde samenstelling, dat het merk bedoelt voor demonstraties in de winkel. Het komt in een eenvoudigere verpakking (witte of bruine doos), soms zonder sierdop. Op de site staan testers altijd als tester vermeld.</p>
<h2>Waarom zijn onze prijzen lager?</h2>
<p>Qosmi verkoopt alleen online, zonder winkel of etalage, en vergelijkt zijn prijzen elke week. Zo houden we eerlijke prijzen, het hele jaar door, zonder nepkortingen.</p>
<h2>Twijfel je?</h2>
<p>Stuur ons een foto van de fles en de doos: we antwoorden binnen 2 werkdagen. Een beschadigd of niet-conform product wordt vervangen of terugbetaald, kosten voor ons. En je hebt altijd 14 dagen na ontvangst om van gedachten te veranderen (ongeopende fles): zie <a href="/nl/pages/retourneren">Retourneren</a>.</p>
<h2>Betalen en levering</h2>
<p>Veilig betalen met Bancontact, bankkaart of Apple Pay. Levering in België en 8 andere Europese landen (Nederland, Luxemburg, Frankrijk, Duitsland, Spanje, Portugal, Italië, Polen): zie de pagina <a href="/nl/pages/levering">Levering</a>.</p>
<p>Contact: <a href="mailto:contact@qosmi.be">contact@qosmi.be</a> · WhatsApp <a href="{WA}">+32 465 43 63 29</a>.</p>
""".replace("{WA}", WA)),
 "en": ("authenticity", "Authentic fragrances: our guarantees", """
<p><strong>Every fragrance sold by Qosmi is an original, new, from the brand stated.</strong> No copies, no "inspired by" scents, no refilled bottles. Here is what we guarantee, and how you can check it yourself.</p>
<h2>Where do our fragrances come from?</h2>
<p>We buy only from distributors established in the European Union who resell the brands' products. Every purchase is invoiced, and every fragrance can be traced back to its production batch.</p>
<h2>An invoice with every order</h2>
<p>Every order comes with an invoice from Qosmi, the shop of a registered Belgian company (see <a href="/en/pages/about-qosmi">About Qosmi</a>). It is your proof of purchase, for a gift or if you have a question.</p>
<h2>How to check a fragrance</h2>
<ul>
<li>The bottle and the box carry the same <strong>batch code</strong> (a string of numbers and letters, often engraved under the bottle and printed under the box).</li>
<li>The code lets you find the production date with the brand or on websites that read batch codes.</li>
<li>The fragrance is new: never opened or used before it is sent to you.</li>
</ul>
<h2>What about testers?</h2>
<p>A tester is an authentic fragrance, with the same formula, that the brand makes for in-store demonstrations. It comes in simpler packaging (white or brown box), sometimes without a decorative cap. On the site, testers are always labelled as such.</p>
<h2>Why are our prices lower?</h2>
<p>Qosmi sells online only, with no shop or window display to pay for, and compares its prices every week. That is how we keep fair prices all year round, with no fake discounts.</p>
<h2>If you have a doubt</h2>
<p>Send us a photo of the bottle and the box: we reply within 2 working days. A damaged or non-conforming product is replaced or refunded, at our cost. And you always have 14 days after delivery to change your mind (unopened bottle): see <a href="/en/pages/returns">Returns</a>.</p>
<h2>Payment and delivery</h2>
<p>Secure payment by Bancontact, card or Apple Pay. Delivery in Belgium and 8 other European countries (Netherlands, Luxembourg, France, Germany, Spain, Portugal, Italy, Poland): see the <a href="/en/pages/shipping">Delivery</a> page.</p>
<p>Contact: <a href="mailto:contact@qosmi.be">contact@qosmi.be</a> · WhatsApp <a href="{WA}">+32 465 43 63 29</a>.</p>
""".replace("{WA}", WA)),
}

SEO = {"fr": "Parfums 100 % authentiques chez Qosmi : originaux neufs achetés auprès de distributeurs européens, facture, code de lot, testeurs expliqués, retours 14 jours.",
       "nl": "Echte parfums bij Qosmi: nieuwe originelen van Europese distributeurs, factuur, batchcode, testers uitgelegd, 14 dagen bedenktijd.",
       "en": "Authentic fragrances at Qosmi: new originals from European distributors, invoice, batch code, testers explained, 14-day returns."}


INTERDITS = ["soleluna", "wholesale", "grossiste", "groothandel", "deloox", "qogita", "brasty", "trista", "marge", "margin",
             "ijsbergstraat", "dilbeek", "dupe", "€"]


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
                   "i": [{"title": "Authenticité", "type": "PAGE", "resourceId": pid}] + garder})["menuUpdate"]
        print("Menu du bas de page :", r["userErrors"] or "lien ajouté")
        menus = s.gql("{ menus(first: 20) { nodes { id handle title items { id title type resourceId url } } } }")["menus"]["nodes"]
        pied = next((m for m in menus if m["handle"] == "footer"), None)
    lien = next((i for i in (pied or {}).get("items", []) if i.get("resourceId") == pid), None)
    if lien:
        lid = lien["id"].replace("MenuItem", "Link")
        try:
            tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": lid})
            dg = {x["key"]: x["digest"] for x in (tr["translatableResource"] or {}).get("translatableContent", [])}
            for loc, titre in (("nl", "Echtheid"), ("en", "Authenticity")):
                if "title" in dg:
                    e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
                              {"id": lid, "t": [{"locale": loc, "key": "title", "value": titre, "translatableContentDigest": dg["title"]}]})["translationsRegister"]["userErrors"]
                    print("Lien %s : %s" % (loc.upper(), e or "ok"))
        except Exception as ex:
            print("Traduction du lien non faite :", ex)
    print("Page OK :", pid)


if __name__ == "__main__":
    main()
