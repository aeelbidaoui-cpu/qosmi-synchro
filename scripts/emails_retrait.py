#!/usr/bin/env python3
"""Retrait sur place à Dilbeek (25/11/2026, Amine) — textes des e-mails clients.
- « Commande prête pour le retrait » : bouton pour choisir son créneau (page de réservation Google Agenda),
  horaires (soirs 18h-22h, samedi et dimanche 10h-20h), adresse, WhatsApp.
- « Confirmation de commande » (retrait) : on prépare la commande, on prévient par e-mail + WhatsApp.
Entrée : modèles copiés par site_nl.py --emails (rapports/theme/emails/*.json, FR + NL).
Sortie : config/emails_nl/103314161988.json (+ phrase corrigée dans config/emails_nl/103314063684.json),
config/emails_fr_a_coller/retrait_pret.liquid et confirmation_commande_retrait.txt (FR = modèle de base, à poser
dans l'éditeur Shopify). La version EN suit via emails_en.py."""
import json, os, re, sys
ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
RESERVER = "https://calendar.google.com/calendar/appointments/schedules/AcZssZ21kcmFYYgXhbyXJIUgW1X5hR-oQdIQ9notaniY_2yuXGN2UXqKXB96cYWhRj3kX8Zgt85bmgkF"
WHATSAPP = "https://wa.me/32465436329"
PRET = "103314161988"
CONFIRMATION = "103314063684"

TXT = {
 "fr": dict(
  objet="Ta commande Qosmi est prête à être retirée ({{ name }})",
  titre="Ta commande est prête !",
  p1="Bonne nouvelle{% if customer.first_name != blank %} {{ customer.first_name }}{% endif %} : ta commande {{ order_name }} t’attend à Dilbeek.",
  p2="Choisis maintenant le jour et l’heure de ton retrait : en semaine de 18h à 22h, le samedi et le dimanche de 10h à 20h.",
  bouton="Choisir mon créneau",
  p3="Au retrait, montre simplement ton numéro de commande ({{ order_name }}). Un empêchement ? Écris-nous sur <a href=\"" + WHATSAPP + "\">WhatsApp</a> au +32 465 43 63 29.",
  lieu="Lieu de retrait",
  ancienne="Tu recevras un e-mail dès que ta commande sera prête à être retirée.",
  nouvelle="Merci ! On prépare ta commande. Dès qu’elle est prête, on te prévient par e-mail et sur WhatsApp, et tu choisis toi-même quand tu viens la chercher à Dilbeek."),
 "nl": dict(
  objet="Je Qosmi-bestelling ligt klaar om af te halen ({{ name }})",
  titre="Je bestelling ligt klaar!",
  p1="Goed nieuws{% if customer.first_name != blank %} {{ customer.first_name }}{% endif %}: je bestelling {{ order_name }} ligt voor je klaar in Dilbeek.",
  p2="Kies nu de dag en het uur waarop je ze komt ophalen: op weekdagen van 18u tot 22u, op zaterdag en zondag van 10u tot 20u.",
  bouton="Kies mijn tijdstip",
  p3="Toon bij het afhalen gewoon je bestelnummer ({{ order_name }}). Lukt het toch niet? Stuur ons een bericht op <a href=\"" + WHATSAPP + "\">WhatsApp</a> via +32 465 43 63 29.",
  lieu="Afhaaladres",
  ancienne="Je ontvangt een e-mail wanneer je je bestelling kunt ophalen.",
  nouvelle="Bedankt! We maken je bestelling klaar. Zodra ze klaarligt, laten we het je weten via e-mail en WhatsApp, en kies je zelf wanneer je ze komt ophalen in Dilbeek."),
}


def bloc(t):
    return ("<h2>%(titre)s</h2> <p>%(p1)s</p> <p>%(p2)s</p> "
            "<table class=\"row actions\"> <tr> <td class=\"actions__cell\"> <table class=\"button main-action-cell\"> <tr> "
            "<td class=\"button__cell\"><a href=\"" + RESERVER + "\" class=\"button__text\">%(bouton)s</a></td> "
            "</tr> </table> </td> </tr> </table> <p style=\"margin-top: 16px;\">%(p3)s</p>") % t


def pret(corps, t):
    """Remplace le titre + les instructions de retrait par nos textes ; « Pickup location » traduit."""
    motif = re.compile(r"<h2>\s*\{\{\s*email_title\s*\}\}\s*</h2>\s*\{%\s*if pickup_instructions != blank\s*%\}.*?\{%\s*endif\s*%\}", re.S)
    if "qk-retrait" in corps:
        corps = re.sub(r"<!-- qk-retrait -->.*?<!-- /qk-retrait -->", lambda m: "<!-- qk-retrait -->" + bloc(t) + "<!-- /qk-retrait -->", corps, flags=re.S)
    else:
        corps, n = motif.subn(lambda m: "<!-- qk-retrait -->" + bloc(t) + "<!-- /qk-retrait -->", corps, count=1)
        if n != 1:
            sys.exit("Bloc « instructions de retrait » introuvable")
    corps = re.sub(r"<h4>\s*(Pickup location|Afhaallocatie|Ophaallocatie|Lieu de retrait|Afhaaladres)\s*</h4>", "<h4>%s</h4>" % t["lieu"], corps)
    return corps


def main():
    src = os.path.join(RACINE, sys.argv[1] if len(sys.argv) > 1 else "rapports/theme/emails")
    d = json.load(open(os.path.join(src, PRET + ".json"), encoding="utf-8"))
    fr = {c["key"]: c["value"] for c in d["translatableContent"]}
    nl = {c["key"]: c["value"] for c in d["translations"]}
    # FR (modèle de base) : à poser dans l'éditeur Shopify
    dossier = os.path.join(RACINE, "config", "emails_fr_a_coller")
    open(os.path.join(dossier, "retrait_pret.liquid"), "w", encoding="utf-8").write(pret(fr["body_html"], TXT["fr"]))
    open(os.path.join(dossier, "retrait_pret_objet.txt"), "w", encoding="utf-8").write(TXT["fr"]["objet"])
    open(os.path.join(dossier, "confirmation_commande_retrait.txt"), "w", encoding="utf-8").write(
        "Dans « Confirmation de commande », remplacer (3 fois) :\n%s\npar :\n%s\n" % (TXT["fr"]["ancienne"], TXT["fr"]["nouvelle"]))
    # NL : traduction enregistrée par site_nl.py --emails-envoyer
    e = {"id": "gid://shopify/EmailTemplate/" + PRET, "title": TXT["nl"]["objet"], "body_html": pret(nl["body_html"], TXT["nl"])}
    json.dump(e, open(os.path.join(RACINE, "config", "emails_nl", PRET + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    f = os.path.join(RACINE, "config", "emails_nl", CONFIRMATION + ".json")
    c = json.load(open(f, encoding="utf-8"))
    n = c["body_html"].count(TXT["nl"]["ancienne"])
    c["body_html"] = c["body_html"].replace(TXT["nl"]["ancienne"], TXT["nl"]["nouvelle"])
    json.dump(c, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Prêt pour retrait : FR + NL écrits ; confirmation NL : %d phrase(s) remplacée(s)" % n)


if __name__ == "__main__":
    main()
