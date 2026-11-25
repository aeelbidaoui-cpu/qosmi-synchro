#!/usr/bin/env python3
"""Version anglaise des e-mails clients personnalisés (22/11/2026, Amine : version anglaise du site).
Part de la version néerlandaise (config/emails_nl/*.json, même mise en forme que le FR) et remplace chaque texte par
sa traduction anglaise ; liens /nl/ -> /en/. Écrit config/emails_en/*.json, envoyés par site_nl.py --emails-envoyer-en.
Contrôle : aucun mot néerlandais courant ne doit rester (sinon arrêt)."""
import glob, json, os, re, sys
ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)

T = [  # (néerlandais, anglais) — appliqués du plus long au plus court
 # 25/11/2026 : retrait sur place à Dilbeek (emails_retrait.py)
 ('order-number__text">\n                              Bestel',
  'order-number__text">\n                              Order'),
 ('<td class="link__cell">of <a href="{{ shop.url }}">',
  '<td class="link__cell">or <a href="{{ shop.url }}">'),
 ('line.quantity }} van {{',
  'line.quantity }} of {{'),
 ('{% capture link_text %}Bekijken{% endcapture %}',
  '{% capture link_text %}View{% endcapture %}'),
 ('Bedankt! We maken je bestelling klaar. Zodra ze klaarligt, laten we het je weten via e-mail en WhatsApp, en kies je zelf wanneer je ze komt ophalen in Dilbeek.',
  "Thank you! We're preparing your order. As soon as it's ready, we'll let you know by email and on WhatsApp, and you choose when to pick it up in Dilbeek."),
 ('Je Qosmi-bestelling ligt klaar om af te halen',
  'Your Qosmi order is ready for pickup'),
 ('Je bestelling ligt klaar!',
  'Your order is ready!'),
 ('Goed nieuws{% if customer.first_name != blank %} {{ customer.first_name }}{% endif %}: je bestelling {{ order_name }} ligt voor je klaar in Dilbeek.',
  'Good news{% if customer.first_name != blank %} {{ customer.first_name }}{% endif %}: your order {{ order_name }} is waiting for you in Dilbeek.'),
 ('Kies nu de dag en het uur waarop je ze komt ophalen: op weekdagen van 18u tot 22u, op zaterdag en zondag van 10u tot 20u.',
  'Now choose the day and time of your pickup: weekdays from 6 pm to 10 pm, Saturday and Sunday from 10 am to 8 pm.'),
 ('Kies mijn tijdstip',
  'Choose my time slot'),
 ('Toon bij het afhalen gewoon je bestelnummer ({{ order_name }}). Lukt het toch niet? Stuur ons een bericht op',
  "When you pick up, just show your order number ({{ order_name }}). Can't make it? Send us a message on"),
 ('</a> via +32 465 43 63 29.',
  '</a> at +32 465 43 63 29.'),
 ('Afhaaladres',
  'Pickup location'),
 ('Enkele artikelen van je bestelling kunnen worden afgehaald',
  'Some items of your order are ready for pickup'),
 ('Je bestelling kan worden afgehaald',
  'Your order is ready for pickup'),
 ('Breng je bevestigingsmail mee wanneer je je bestelling komt ophalen.',
  'Bring your confirmation email when you pick up your order.'),
 ('Kaart openen',
  'Open map'),
 ('Af te halen artikelen',
  'Items ready for pickup'),
 ('Je bestelling bekijken',
  'View your order'),
 (", we hebben je bestelling ontvangen. Het bedrag wordt van je betaalmethode afgeschreven wanneer je bestelling klaar is om te worden afgehandeld. We laten het je weten wanneer deze onderweg is.",
  ", we've received your order. Your payment method will be charged when your order is ready to be fulfilled. We'll let you know when it's on its way."),
 (" we maken je bestelling gereed voor bezorging.", ", we're getting your order ready for delivery."),
 ("We zorgen ervoor dat je bestelling klaar is voor verzending. We zullen je op de hoogte stellen wanneer deze is verzonden.",
  "We're getting your order ready to be shipped. We'll let you know when it has been sent."),
 ("we leveren je pakket in het Mondial Relay-afhaalpunt het dichtst bij je adres.", "we deliver your parcel to the Mondial Relay pick-up point closest to your address."),
 ("De ontvanger van de cadeaubon ontvangt een e-mail met de cadeauboncode.", "The gift card recipient will receive an email with the gift card code."),
 ("Je ontvangt verschillende e-mails voor alle cadeaubonnen.", "You'll receive separate emails for all gift cards."),
 ("Hieronder vind je alle gegevens van je bestelling. Je factuur staat op de pagina van je bestelling.",
  "Below are all the details of your order. Your invoice is on your order page."),
 ("Zodra je bestelling verzonden is, krijg je een e-mail met een trackingnummer om ze te volgen.",
  "As soon as your order has been shipped, you'll receive an email with a tracking number to follow it."),
 ("Als je vragen hebt, beantwoord dan deze e-mail of neem contact met ons op via", "If you have any questions, reply to this email or contact us at"),
 ("Goed nieuws! De laatste artikelen van je bestelling zijn onderweg.", "Good news! The last items of your order are on their way."),
 ("Goed nieuws! Een deel van je bestelling is onderweg. De rest volgt zo snel mogelijk.", "Good news! Part of your order is on its way. The rest will follow as soon as possible."),
 ("Goed nieuws! Je pakket is onderweg.", "Good news! Your parcel is on its way."),
 ("Je pakket wordt bezorgd door", "Your parcel is delivered by"),
 ("onze vervoerder", "our carrier"),
 (" en je trackingcode is:", " and your tracking code is:"),
 ("Op deze pagina vind je realtime informatie over de levering van je pakket.", "On this page you'll find real-time information about the delivery of your parcel."),
 ("het kan enkele uren duren voordat de vervoerder je trackingcode activeert. Zie je nog niets, probeer het dan later opnieuw.",
  "it can take a few hours for the carrier to activate your tracking code. If you don't see anything yet, try again later."),
 ("Het kan enkele uren duren voordat de vervoerder je trackingcode activeert. Zie je nog niets, probeer het dan later opnieuw.",
  "It can take a few hours for the carrier to activate your tracking code. If you don't see anything yet, try again later."),
 ("-10&nbsp;% op een selectie, van 27 tot 30 november, automatisch in je winkelmandje", "-10% on a selection, from 27 to 30 November, automatically in your basket"),
 ("Bestel vóór woensdag 16 december om op tijd geleverd te worden", "Order before Wednesday 16 December to receive it in time"),
 ("is op jouw aanvraag geannuleerd en de betaling is vervallen.", "has been cancelled at your request and the payment has been voided."),
 ("is geannuleerd omdat we onvoldoende voorraad hebben om de bestelling af te handelen, en de betaling is vervallen.",
  "has been cancelled because we don't have enough stock to fulfil it, and the payment has been voided."),
 ("is geannuleerd vanwege onvoorziene omstandigheden en de betaling is ongeldig verklaard.", "has been cancelled due to unforeseen circumstances and the payment has been voided."),
 ("is geannuleerd omdat de betaling is geweigerd.", "has been cancelled because the payment was declined."),
 ("is geannuleerd vanwege een fout van een medewerker en je betaling is ongeldig verklaard.", "has been cancelled due to a staff error and your payment has been voided."),
 ("is geannuleerd vanwege onvoorziene omstandigheden en de betaling is vervallen.", "has been cancelled due to unforeseen circumstances and the payment has been voided."),
 ("is op jouw aanvraag geannuleerd en is terugbetaald.", "has been cancelled at your request and has been refunded."),
 ("is geannuleerd omdat we onvoldoende voorraad hebben om de bestelling af te handelen, en is terugbetaald.",
  "has been cancelled because we don't have enough stock to fulfil it, and has been refunded."),
 ("is geannuleerd vanwege onvoorziene omstandigheden en is terugbetaald.", "has been cancelled due to unforeseen circumstances and has been refunded."),
 ("is geannuleerd vanwege een fout van een medewerker en je betaling is teruggestort.", "has been cancelled due to a staff error and your payment has been refunded."),
 ("is op jouw aanvraag geannuleerd en is nog niet terugbetaald.", "has been cancelled at your request and has not been refunded yet."),
 ("is geannuleerd omdat we onvoldoende voorraad hebben om de bestelling af te handelen, en is nog niet terugbetaald.",
  "has been cancelled because we don't have enough stock to fulfil it, and has not been refunded yet."),
 ("is geannuleerd vanwege onvoorziene omstandigheden en is nog niet terugbetaald.", "has been cancelled due to unforeseen circumstances and has not been refunded yet."),
 ("is geannuleerd vanwege een fout van een medewerker en je betaling is nog niet teruggestort.", "has been cancelled due to a staff error and your payment has not been refunded yet."),
 (". Het kan tot 10 dagen duren voordat deze terugbetaling op je rekening staat.", ". It can take up to 10 days for this refund to appear in your account."),
 (", je hebt een parfum in je winkelmandje laten liggen. Het is nog beschikbaar: je rondt je bestelling af in één klik. Goed om weten: levering is gratis vanaf 2 artikelen.",
  ", you left a fragrance in your basket. It's still available: finish your order in one click. Good to know: delivery is free from 2 items in Belgium, the Netherlands and Luxembourg."),
 (", je hebt een paar parfums in je winkelmandje laten liggen. Ze zijn nog beschikbaar: je rondt je bestelling af in één klik. Goed om weten: levering is gratis vanaf 2 artikelen.",
  ", you left a few fragrances in your basket. They're still available: finish your order in one click. Good to know: delivery is free from 2 items in Belgium, the Netherlands and Luxembourg."),
 ("De tracking van je pakket is bijgewerkt: hier is de nieuwe link.", "The tracking of your parcel has been updated: here is the new link."),
 ("De tracking van een deel van je bestelling is bijgewerkt: hier is de nieuwe link.", "The tracking of part of your order has been updated: here is the new link."),
 ("Goed nieuws! De laatste artikelen van je bestelling komen vandaag aan.", "Good news! The last items of your order arrive today."),
 ("Goed nieuws! Een deel van je bestelling komt vandaag aan.", "Good news! Part of your order arrives today."),
 ("Goed nieuws! Je pakket komt vandaag aan.", "Good news! Your parcel arrives today."),
 ("Niet thuis? Op de trackingpagina zie je hoe je je pakket kunt ophalen.", "Not at home? The tracking page shows how to collect your parcel."),
 ("Je pakket is geleverd. We hopen dat je parfum je bevalt, en bedankt voor je vertrouwen!", "Your parcel has been delivered. We hope you love your fragrance, and thank you for your trust!"),
 ("De laatste artikelen van je bestelling zijn geleverd. Veel plezier ermee, en bedankt voor je vertrouwen!", "The last items of your order have been delivered. Enjoy them, and thank you for your trust!"),
 ("Een deel van je bestelling is geleverd. De rest volgt zo snel mogelijk.", "Part of your order has been delivered. The rest will follow as soon as possible."),
 ("Heb je je pakket niet ontvangen of is er een probleem? Beantwoord gewoon deze e-mail of schrijf ons via", "Didn't receive your parcel, or is there a problem? Just reply to this email or write to us at"),
 (", we lossen het op.", ", we'll sort it out."),
 ("Wil je geen herinneringen over je winkelwagen ontvangen?", "Don't want to receive basket reminders?"),
 ("Je ontvangt een e-mail wanneer je je bestelling kunt ophalen.", "You'll receive an email when your order is ready for pick-up."),
 ("Bedankt voor je bestelling bij Qosmi!", "Thank you for your order at Qosmi!"),
 ("Downloaden om te volgen met", "Download to track with"), ("Bestelling volgen met", "Track order with"),
 ("Bestelling en factuur bekijken", "View order and invoice"), ("Bekijk mijn bestelling en factuur", "View my order and invoice"),
 ("Je bestelling en factuur:", "Your order and invoice:"), ("Je bestelling bekijken", "View your order"), ("Bekijk mijn bestelling", "View my order"),
 ("Mijn bestelling afronden", "Complete my order"), ("Bezoek onze winkel", "Visit our shop"), ("Besteloverzicht", "Order summary"),
 ("Algemene verkoopsvoorwaarden:", "Terms and conditions of sale:"), ("Retourneren en herroepingsformulier:", "Returns and withdrawal form:"),
 ("100 % originele parfums", "100% genuine fragrances"), ("een merk van Deway BV", "a brand of Deway BV"),
 ("Kerstcadeau-ideeën", "Christmas gift ideas"), ("Verwijderde artikelen", "Removed items"),
 ("Totaal verschuldigd bij ontvangst", "Total due on receipt"), ("Totaal verschuldigd bij fulfilment", "Total due on fulfilment"),
 ("Totaal verschuldigd op", "Total due on"), ("Totaal betaald vandaag", "Total paid today"), ("Totaal betaald", "Total paid"),
 ("Het totaalbedrag in CNY bekijken in WeChat", "View the total in CNY in WeChat"), ("Het totaalbedrag in CNY bekijken in Alipay", "View the total in CNY in Alipay"),
 ("Betaald met Shop Pay-termijnbetalingen", "Paid with Shop Pay Installments"), ("Contant geld afronden", "Cash rounding"),
 ("Saldo cadeaubon -", "Gift card balance -"), ("Cadeaubon (eindigend op", "Gift card (ending in"), ("(eindigend op", "(ending in"),
 (": te betalen vóór", ": due before"), ("/maand gedurende", "/month for"), ("Gekocht met", "Purchased with"),
 ("Aangepaste informatie", "Custom information"), ("Bezorginformatie:", "Delivery information:"), ("Je afhaalpunt:", "Your pick-up point:"),
 ("Verwachte bezorging ·", "Expected delivery ·"), ("Verwachte bezorging", "Expected delivery"), ("Verwachte levering:", "Expected delivery:"),
 ("Bestelnummer:", "Order number:"), ("Bestelnummer", "Order number"), ("Bestelkortingen", "Order discounts"), ("Bestelkorting", "Order discount"),
 ("Bezorgadres", "Shipping address"), ("Factuuradres", "Billing address"), ("Verzendmethode", "Shipping method"),
 ("Andere trackingcodes:", "Other tracking codes:"), ("Volg je pakket", "Track your parcel"), ("In je pakket", "In your parcel"),
 ("Je winkelmandje", "Your basket"), ("Klantenservice", "Customer service"), ("Mijn account", "My account"), ("Ontdek qosmi.be", "Discover qosmi.be"),
 ("Onderdeel van:", "Part of:"), ("Voor:", "For:"), ("Kwijtgescholden", "Waived"), ("Douanerechten", "Duties"), ("Terugbetaald", "Refunded"),
 ("Terugbetaling", "Refund"), ("Subtotaal", "Subtotal"), ("Verzending", "Shipping"), ("Ophalen", "Pick-up"), ("Totaal", "Total"),
 ("Je bespaart", "You save"), ("Betaald", "Paid"), ("Betaling", "Payment"), ("Kosten", "Fees"), ("Locatie", "Location"),
 ("eindigt op", "ending in"), ("maanden", "months"), ("artikelen", "items"), ("Afmelden", "Unsubscribe"), ("klik hier", "click here"),
 ("Let op:", "Please note:"), ("Gratis", "Free"), ("Btw", "VAT"), (">Bestel<", ">Order<"), ("Bestelling", "Order"),
 ("Hallo", "Hello"),
 # objets
 ("Bevestiging van bestelling", "Order confirmation"), ("Volg je bestelling", "Track your order"),
 ("Je Qosmi-bestelling is geannuleerd", "Your Qosmi order has been cancelled"), ("Je terugbetaling van Qosmi", "Your refund from Qosmi"),
 ("Je parfum wacht op je bij Qosmi", "Your fragrance is waiting for you at Qosmi"), ("Tracking van je pakket bijgewerkt", "Your parcel tracking has been updated"),
 ("Je pakket komt vandaag aan", "Your parcel arrives today"), ("Je pakket is geleverd", "Your parcel has been delivered"),
 ("parfums wachten nog op je", "fragrances are still waiting for you"), ("parfum wacht nog op je", "fragrance is still waiting for you"),
 # liens
 ("/nl/pages/algemene-verkoopsvoorwaarden", "/en/pages/terms-and-conditions-of-sale"), ("/nl/pages/retourneren", "/en/pages/returns"),
 ("/nl/pages/kerstcadeaus", "/en/pages/idees-cadeaux-noel"), ("/nl/collections/black-friday", "/en/collections/black-friday"),
]
T += [
 (", we hebben je bestelling goed ontvangen", ", we've received your order"), ("Bedankt", "Thank you"),
 ("Zodra je hebt betaald, krijg je een bevestigingsmail.", "Once you've paid, you'll receive a confirmation email."),
 ("Je betaling wordt verwerkt. Je ontvangt een e-mail wanneer je bestelling is bevestigd.", "Your payment is being processed. You'll receive an email when your order is confirmed."),
 (" Volg je verzending om de bezorgingsstatus te zien.", " Track your shipment to see the delivery status."),
 (" Volg je zending om de bezorgingsstatus te zien.", " Track your shipment to see the delivery status."),
 ("De laatste items van je bestelling zijn onderweg", "The last items of your order are on their way"),
 ("Een aantal items van je bestelling is onderweg", "Some items of your order are on their way"),
 ("Sommige items van je bestelling zijn onderweg", "Some items of your order are on their way"),
 ("Het laatste artikel van je bestelling is onderweg", "The last item of your order is on its way"),
 ("Eén artikel van je bestelling is onderweg", "One item of your order is on its way"),
 ("Je bestelling is onderweg", "Your order is on its way"),
 ("Je bestelling is geannuleerd", "Your order has been cancelled"),
 ("Je bestelling is terugbetaald", "Your order has been refunded"), ("Je hebt een terugbetaling ontvangen", "You've received a refund"),
 ("Sommige items in je bestelling zijn terugbetaald", "Some items in your order have been refunded"),
 ("Total terugbetaald bedrag:", "Total amount refunded:"), ("Totaal terugbetaald bedrag:", "Total amount refunded:"),
 ("Je fragrance", "Your fragrance"), ("Je fragrances", "Your fragrances"),
 ("Je verzendingsstatus is bijgewerkt", "Your shipping status has been updated"),
 ("De laatste items van je bestelling zijn klaar voor bezorging", "The last items of your order are out for delivery"),
 ("Sommige items van je bestelling zijn klaar voor bezorging", "Some items of your order are out for delivery"),
 ("Het laatste artikel van je bestelling is klaar voor bezorging", "The last item of your order is out for delivery"),
 ("Eén artikel van je bestelling is klaar voor bezorging", "One item of your order is out for delivery"),
 ("Eén artikel in je bestelling is klaar voor bezorging", "One item of your order is out for delivery"),
 ("Je bestelling is klaar voor bezorging", "Your order is out for delivery"),
 ("De laatste items van je bestelling zijn bezorgd", "The last items of your order have been delivered"),
 ("Sommige items van je bestelling zijn bezorgd", "Some items of your order have been delivered"),
 ("Het laatste artikel van je bestelling is bezorgd", "The last item of your order has been delivered"),
 ("Eén artikel van je bestelling is bezorgd", "One item of your order has been delivered"),
 ("Je bestelling is bezorgd", "Your order has been delivered"),
]
T += [(a.replace(" items ", " artikelen "), b) for a, b in T if " items " in a]
RESTES = re.compile(r"\b(je|jouw|bestelling|pakket|bedankt|winkelmandje|wordt|hebben|onze|vandaag|geleverd|terugbetaald|afhaalpunt|verschuldigd)\b", re.I)


def texte_visible(b):
    b = re.sub(r"<style.*?</style>", "", b, flags=re.S)
    b = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", "", b, flags=re.S)
    b = re.sub(r"\{\{.*?\}\}|\{%.*?%\}", " ", b, flags=re.S)
    return re.sub(r"<[^>]+>", " ", b)


def main():
    os.makedirs(os.path.join(RACINE, "config", "emails_en"), exist_ok=True)
    tri = sorted(T, key=lambda x: -len(x[0]))
    pb = 0
    for f in sorted(glob.glob(os.path.join(RACINE, "config", "emails_nl", "*.json"))):
        e = json.load(open(f, encoding="utf-8"))
        for k in ("title", "body_html"):
            v = e[k]
            for a, b in tri:
                v = v.replace(a, b)
            e[k] = v
        reste = sorted(set(m.group(0).lower() for m in RESTES.finditer(texte_visible(e["body_html"]) + " " + e["title"])))
        if reste:
            pb += 1
            print("%s : mots néerlandais restants %s" % (os.path.basename(f), reste))
            for m in RESTES.finditer(texte_visible(e["body_html"])):
                t = texte_visible(e["body_html"])
                print("   …%s…" % t[max(0, m.start() - 80):m.end() + 40].replace("\n", " "))
                break
        json.dump(e, open(os.path.join(RACINE, "config", "emails_en", os.path.basename(f)), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("%s « %s »" % (os.path.basename(f), e["title"][:70]))
    if pb:
        sys.exit("Textes néerlandais restants dans %d e-mail(s)" % pb)


if __name__ == "__main__":
    main()
