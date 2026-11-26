#!/usr/bin/env python3
"""Messages de suivi de commande (26/11/2026, demande d'Amine).

Le client est prévenu à chaque étape :
  1. commande reçue      → e-mail Shopify « Confirmation de commande » (déjà en place) ;
  2. en préparation      → Amine ajoute l'étiquette « preparation » sur la commande (appli Shopify) ; ce script envoie
                           l'e-mail « Ta commande est en préparation » puis ajoute l'étiquette « msg-preparation » ;
  3. expédiée            → e-mail Shopify « Confirmation d'expédition » (envoyé quand l'étiquette Mondial Relay est créée,
                           scripts/mondial_relay.py, avec le lien de suivi) ;
  4. livrée              → e-mail Shopify « Livrée » (suivi du transporteur) ; ce script relève les commandes livrées
                           (étiquette « msg-livree ») et signale celles en route depuis longtemps ;
  5. avis                → invitation Trustpilot (app Trustpilot, réglée le 25/11/2026).

Lancé à chaque passage de la synchro horaire. E-mails envoyés au nom de Qosmi <contact@qosmi.be> (Gmail de Deway).

  python3 scripts/suivi_commandes.py           # envoie
  python3 scripts/suivi_commandes.py --essai   # montre ce qui serait envoyé, n'envoie rien
"""
import html, os, re, smtplib, sys
from email.message import EmailMessage
from email.utils import formataddr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ESSAI = "--essai" in sys.argv
BOITE = "contact@deway.be"
EXPEDITEUR = formataddr(("Qosmi", "contact@qosmi.be"))
LOGO = "https://qosmi.be/cdn/shop/files/qosmi-logo.png?height=90"

TEXTES = {
    "fr": ("Ta commande %s est en préparation",
           "Bonjour %s,",
           "Bonne nouvelle : nous préparons ta commande <strong>%s</strong>. Chaque parfum est vérifié et emballé avec soin.",
           "Tu recevras un nouvel e-mail avec ton lien de suivi dès que ton colis sera remis au transporteur.",
           "Voir ma commande",
           "Une question ? Réponds simplement à cet e-mail ou écris-nous sur WhatsApp au +32 465 43 63 29."),
    "nl": ("Je bestelling %s wordt klaargemaakt",
           "Hallo %s,",
           "Goed nieuws: we maken je bestelling <strong>%s</strong> klaar. Elk parfum wordt gecontroleerd en zorgvuldig verpakt.",
           "Je krijgt een nieuwe e-mail met je trackinglink zodra je pakket aan de vervoerder is overhandigd.",
           "Bekijk mijn bestelling",
           "Een vraag? Antwoord gewoon op deze e-mail of stuur ons een WhatsApp op +32 465 43 63 29."),
    "en": ("Your order %s is being prepared",
           "Hello %s,",
           "Good news: we are preparing your order <strong>%s</strong>. Every fragrance is checked and packed with care.",
           "You will receive another email with your tracking link as soon as your parcel is handed to the carrier.",
           "View my order",
           "A question? Just reply to this email or message us on WhatsApp at +32 465 43 63 29."),
}

Q = """query($q: String!) { orders(first: 50, query: $q) { nodes { id name email customerLocale statusPageUrl tags createdAt
       displayFulfillmentStatus customer { firstName }
       fulfillments(first: 5) { displayStatus createdAt trackingInfo { company number } } } } }"""
TAG = """mutation($id: ID!, $t: [String!]!) { tagsAdd(id: $id, tags: $t) { userErrors { message } } }"""


def corps(lg, o):
    sujet, bonjour, l1, l2, bouton, aide = TEXTES[lg]
    prenom = html.escape(((o.get("customer") or {}).get("firstName") or "").strip()) or {"fr": "", "nl": "", "en": ""}[lg]
    bonjour = bonjour % prenom if prenom else bonjour.replace(" %s,", ",")
    url = o.get("statusPageUrl") or "https://qosmi.be"
    nom = html.escape(o["name"])
    return sujet % o["name"], f"""<!doctype html><html><body style="margin:0;background:#f4f4f4;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;"><tr><td align="center" style="padding:28px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;">
<tr><td align="center" style="padding:30px 24px 8px;"><img src="{LOGO}" alt="Qosmi" height="30" style="display:block;height:30px;border:0;"></td></tr>
<tr><td style="padding:18px 32px 6px;font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:1.6;color:#111;">
<p style="margin:0 0 14px;">{bonjour}</p>
<p style="margin:0 0 14px;">{l1 % nom}</p>
<p style="margin:0 0 22px;">{l2}</p>
<p style="margin:0 0 26px;text-align:center;"><a href="{url}" style="display:inline-block;background:#111;color:#fff;text-decoration:none;padding:13px 26px;font-size:13px;letter-spacing:1px;text-transform:uppercase;">{bouton}</a></p>
<p style="margin:0 0 26px;font-size:13px;color:#666;">{aide}</p>
</td></tr></table></td></tr></table></body></html>"""


def envoyer(dest, sujet, html_corps):
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Reply-To"], msg["Subject"] = EXPEDITEUR, dest, "contact@qosmi.be", sujet
    msg.set_content(re.sub(r"<[^>]+>", " ", html_corps))
    msg.add_alternative(html_corps, subtype="html")
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=60) as smtp:
        smtp.starttls()
        smtp.login(BOITE, re.sub(r"\s+", "", os.environ["GMAIL_APP_PASSWORD"]))
        smtp.send_message(msg)


def main():
    from shopify_api import Shopify
    s = Shopify()
    # 2. en préparation
    n = 0
    for o in s.gql(Q, {"q": "tag:preparation -tag:msg-preparation"})["orders"]["nodes"]:
        if not o.get("email"):
            print("  %s : pas d'e-mail client" % o["name"]); continue
        lg = (o.get("customerLocale") or "fr")[:2]
        lg = lg if lg in TEXTES else "fr"
        sujet, h = corps(lg, o)
        if ESSAI:
            print("  [essai] %s → e-mail « %s » (%s)" % (o["name"], sujet, lg)); continue
        envoyer(o["email"], sujet, h)
        e = s.gql(TAG, {"id": o["id"], "t": ["msg-preparation"]})["tagsAdd"]["userErrors"]
        print("  %s : e-mail « en préparation » envoyé (%s)%s" % (o["name"], lg, " ; étiquette : %s" % e if e else ""))
        n += 1
    print("En préparation : %d e-mail(s)" % n)
    # 4. livrée (l'e-mail part de Shopify ; ici on relève et on signale les colis lents)
    for o in s.gql(Q, {"q": "fulfillment_status:shipped -tag:msg-livree"})["orders"]["nodes"]:
        st = [f.get("displayStatus") for f in o.get("fulfillments") or []]
        if st and all(x == "DELIVERED" for x in st):
            if not ESSAI:
                s.gql(TAG, {"id": o["id"], "t": ["msg-livree"]})
            print("  %s : livrée (e-mail « Livrée » de Shopify)" % o["name"])
        else:
            print("  %s : en route (%s)" % (o["name"], ", ".join(x or "?" for x in st)))


if __name__ == "__main__":
    main()
