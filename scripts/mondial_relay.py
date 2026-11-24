#!/usr/bin/env python3
"""Étiquettes Mondial Relay pour les commandes Qosmi (demande d'Amine du 22/11/2026 : « vasy fait ca »).

Pour chaque commande payée et pas encore expédiée, livrée en point relais Mondial Relay (ou à domicile hors Belgique) :
  1. cherche le point relais Mondial Relay le plus proche de l'adresse du client (recherche publique du widget Mondial Relay) ;
  2. crée l'expédition et l'étiquette avec l'API Connect de Mondial Relay (identifiants du compte d'Amine, secrets GitHub
     MR_LOGIN, MR_PASSWORD, MR_CUSTOMER_ID, saisis par Amine lui-même) ;
  3. envoie les étiquettes PDF par e-mail à contact@deway.be (Gmail de Deway, mot de passe d'application dans le secret
     GitHub GMAIL_APP_PASSWORD, saisi par Amine) ; jamais dans le dépôt ni dans les journaux : données personnelles ;
  4. marque la commande expédiée dans Shopify avec le numéro de suivi : le client reçoit l'e-mail d'expédition.

Chaque étiquette est facturée par Mondial Relay : rien n'est créé sans que l'action soit lancée exprès.
  python3 scripts/mondial_relay.py --essai               # liste ce qui serait fait, sans rien créer ni payer
  python3 scripts/mondial_relay.py --creer "#1001,#1002"  # crée les étiquettes de ces commandes
  python3 scripts/mondial_relay.py --creer toutes         # toutes les commandes en attente

Dans les journaux : numéro de commande, pays, nombre d'articles, poids et point relais seulement (pas de nom ni d'adresse).
"""
import json, os, re, smtplib, sys, time, unicodedata, urllib.parse, urllib.request
from email.message import EmailMessage
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import Shopify  # noqa: E402

API = "https://connect-api.mondialrelay.com/api/shipment"
RECHERCHE = ("https://widget.mondialrelay.com/parcelshop-picker/v3_0/services/parcelshop-picker.svc/SearchPR?"
             "Brand=BDTEST%20%20&Country={pays}&PostCode={cp}&City={ville}&ColLivMod=24R&Weight=&NbResults=5"
             "&SearchDelay=&SearchFar=75&Service=&Latitude=&Longitude=")
SUIVI = "https://www.mondialrelay.be/fr-be/suivi-de-colis/?numeroExpedition={num}&codePostal={cp}"
RELAIS, DOMICILE = "Point relais Mondial Relay", "Livraison à domicile"
GRAMMES_ARTICLE = 500      # un parfum emballé ≈ 0,5 kg
CARTON = (25, 20, 10)      # cm
EXPEDITEUR = {"AddressAdd1": "QOSMI", "Streetname": "Ijsbergstraat", "HouseNo": "73", "CountryCode": "BE",
              "PostCode": "1701", "City": "Dilbeek", "Email": "contact@qosmi.be"}
MF = ("qosmi_prive", "mondial_relay")
BOITE = "contact@deway.be"  # 22/11/2026 (Amine) : étiquettes envoyées sur le mail de Deway

COMMANDES = """query($q: String, $a: String) { orders(first: 50, after: $a, query: $q, sortKey: CREATED_AT) {
  pageInfo { hasNextPage endCursor }
  nodes { id name email phone displayFulfillmentStatus displayFinancialStatus cancelledAt
    metafield(namespace: "qosmi_prive", key: "mondial_relay") { value }
    shippingLine { title }
    shippingAddress { firstName lastName company address1 address2 city zip countryCodeV2 phone }
    lineItems(first: 50) { nodes { quantity requiresShipping } }
    fulfillmentOrders(first: 10) { nodes { id status } } } } }"""


def propre(t, n):
    """Texte accepté par Mondial Relay : majuscules sans accents, longueur limitée."""
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9 ,./'&()+-]", " ", t).strip()[:n].upper()


def telephone(num, pays):
    n = re.sub(r"[^\d+]", "", num or "")
    if n.startswith("00"):
        n = "+" + n[2:]
    if n and not n.startswith("+"):
        pref = {"BE": "32", "NL": "31", "LU": "352", "FR": "33", "ES": "34", "PT": "351", "IT": "39", "DE": "49", "PL": "48"}
        n = "+" + pref.get(pays, "") + n.lstrip("0")
    return n


def point_relais(adr):
    pays, cp = adr["countryCodeV2"], (adr["zip"] or "").strip()
    url = RECHERCHE.format(pays=pays, cp=urllib.parse.quote(cp), ville=urllib.parse.quote(adr.get("city") or ""))
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
        d = json.load(r)
    pr = d.get("PRList") or []
    return ("%s-%s" % (pays, pr[0]["ID"]), "%s, %s" % (pr[0]["Nom"].title(), pr[0]["Ville"].title())) if pr else (None, None)


def a_expedier(s):
    out, apres = [], None
    while True:
        d = s.gql(COMMANDES, {"q": "fulfillment_status:unfulfilled status:open", "a": apres})["orders"]
        for o in d["nodes"]:
            if o["cancelledAt"] or o["displayFinancialStatus"] not in ("PAID", "PARTIALLY_REFUNDED") or (o["metafield"] or {}).get("value"):
                continue
            mode = (o["shippingLine"] or {}).get("title") or ""
            adr = o["shippingAddress"]
            if not adr:
                continue
            if mode == RELAIS or (mode == DOMICILE and adr["countryCodeV2"] != "BE"):
                out.append(o)
        if not d["pageInfo"]["hasNextPage"]:
            return out
        apres = d["pageInfo"]["endCursor"]


def adresse_xml(parent, champs):
    adr = ET.SubElement(parent, "Address")
    for k in ("Title", "Firstname", "Lastname", "Streetname", "HouseNo", "CountryCode", "PostCode", "City",
              "AddressAdd1", "AddressAdd2", "AddressAdd3", "PhoneNo", "MobileNo", "Email"):
        ET.SubElement(adr, k).text = champs.get(k, "")


def demande(o, mode, lieu, grammes):
    adr = o["shippingAddress"]
    pays = adr["countryCodeV2"]
    tel = telephone(adr.get("phone") or o.get("phone"), pays)
    req = ET.Element("ShipmentCreationRequest", {"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                                 "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                                                 "xmlns": "http://www.example.org/Request"})
    ctx = ET.SubElement(req, "Context")
    for k, v in (("Login", os.environ["MR_LOGIN"].strip()), ("Password", os.environ["MR_PASSWORD"].strip()),
                 ("CustomerId", os.environ["MR_CUSTOMER_ID"].strip()), ("Culture", "fr-FR"), ("VersionAPI", "1.0")):
        ET.SubElement(ctx, k).text = v
    sortie = ET.SubElement(req, "OutputOptions")
    ET.SubElement(sortie, "OutputFormat").text = "10x15"
    ET.SubElement(sortie, "OutputType").text = "PdfUrl"
    sh = ET.SubElement(ET.SubElement(req, "ShipmentsList"), "Shipment")
    ET.SubElement(sh, "OrderNo").text = o["name"].lstrip("#")[:15]
    ET.SubElement(sh, "CustomerNo").text = ""
    ET.SubElement(sh, "ParcelCount").text = "1"
    ET.SubElement(sh, "DeliveryMode", {"Mode": mode, "Location": lieu or ""})
    ET.SubElement(sh, "CollectionMode", {"Mode": "CCC", "Location": ""})
    p = ET.SubElement(ET.SubElement(sh, "Parcels"), "Parcel")
    ET.SubElement(p, "Content").text = "PARFUM"
    for k, v in zip(("Length", "Width", "Depth"), CARTON):
        ET.SubElement(p, k, {"Value": str(v), "Unit": "cm"})
    ET.SubElement(p, "Weight", {"Value": str(grammes), "Unit": "gr"})
    exp = dict(EXPEDITEUR, MobileNo=telephone(os.environ.get("MR_TELEPHONE") or "+32465436329", "BE"))
    adresse_xml(ET.SubElement(sh, "Sender"), exp)
    dest = {"Firstname": propre(adr.get("firstName"), 30), "Lastname": propre(adr.get("lastName"), 30),
            "Streetname": propre(adr.get("address1"), 40), "CountryCode": pays,
            "PostCode": (adr.get("zip") or "").strip().upper(), "City": propre(adr.get("city"), 30),
            "AddressAdd1": propre(adr.get("company"), 30), "AddressAdd2": propre(adr.get("address2"), 30),
            "MobileNo": tel, "Email": (o.get("email") or "").strip()}
    adresse_xml(ET.SubElement(sh, "Recipient"), dest)
    return b'<?xml version="1.0" encoding="utf-8"?>' + ET.tostring(req, encoding="utf-8")


def appeler(corps):
    req = urllib.request.Request(API, data=corps, method="POST",
                                 headers={"Accept": "application/xml", "Content-Type": "text/xml"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            texte = r.read().decode("utf-8-sig")
    except urllib.error.HTTPError as e:
        texte = e.read().decode("utf-8-sig", "replace")
    racine = ET.fromstring(texte)
    def tous(nom):
        return [e for e in racine.iter() if e.tag.split("}")[-1] == nom]
    statuts = [(e.get("Code"), e.get("Level"), e.get("Message")) for e in tous("Status")]
    envoi = next((e.get("ShipmentNumber") for e in tous("Shipment") if e.get("ShipmentNumber")), None)
    pdf = next(((e.text or "").strip() for e in tous("Output") if (e.text or "").strip().startswith("http")), None)
    return envoi, pdf, statuts


def envoyer_mail(etiquettes, bilan):
    """Un seul e-mail par passage, toutes les étiquettes en pièces jointes (Gmail de Deway, SMTP)."""
    msg = EmailMessage()
    msg["From"], msg["To"] = "Qosmi <%s>" % BOITE, BOITE
    msg["Subject"] = "Étiquettes Mondial Relay : %s" % ", ".join(n for n, _ in etiquettes)
    msg.set_content("Étiquettes Mondial Relay créées pour les commandes Qosmi (format 10x15) :\n\n" + "\n".join(bilan)
                    + "\n\nLes commandes sont marquées expédiées dans Shopify et les clients ont reçu le lien de suivi.")
    for nom, contenu in etiquettes:
        msg.add_attachment(contenu, maintype="application", subtype="pdf", filename="etiquette-%s.pdf" % nom.lstrip("#"))
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=60) as smtp:
        smtp.starttls()
        smtp.login(BOITE, re.sub(r"\s+", "", os.environ["GMAIL_APP_PASSWORD"]))
        smtp.send_message(msg)


def expedier_shopify(s, o, num, cp):
    fos = [f["id"] for f in o["fulfillmentOrders"]["nodes"] if f["status"] in ("OPEN", "IN_PROGRESS")]
    r = s.gql("""mutation($f: FulfillmentInput!) { fulfillmentCreate(fulfillment: $f) { fulfillment { id } userErrors { message } } }""",
              {"f": {"lineItemsByFulfillmentOrder": [{"fulfillmentOrderId": i} for i in fos], "notifyCustomer": True,
                     "trackingInfo": {"company": "Mondial Relay", "number": num, "url": SUIVI.format(num=num, cp=urllib.parse.quote(cp))}}})
    return r["fulfillmentCreate"]["userErrors"]


def main():
    essai = "--essai" in sys.argv
    choix = sys.argv[sys.argv.index("--creer") + 1] if "--creer" in sys.argv else ""
    if not essai and not choix:
        sys.exit(__doc__)
    s = Shopify()
    try:
        liste = a_expedier(s)
    except SystemExit:
        raise
    except Exception as e:  # accès aux données client refusé, etc.
        sys.exit("Lecture des commandes impossible : %s" % str(e)[:300])
    if choix and choix != "toutes":
        voulues = {("#" + x.strip().lstrip("#")) for x in choix.split(",") if x.strip()}
        liste = [o for o in liste if o["name"] in voulues]
    print("Commandes à expédier par Mondial Relay : %d" % len(liste))
    if essai:  # contrôle de l'accès aux adresses clients sur la dernière commande (oui/non seulement)
        try:
            d = s.gql("{ orders(first: 1, reverse: true) { nodes { name shippingAddress { zip countryCodeV2 } } } }")["orders"]["nodes"]
            print("Accès aux adresses de livraison : %s" % ("oui" if d and (d[0]["shippingAddress"] or {}).get("zip") else "non ou aucune commande"))
        except Exception as e:
            print("Accès aux adresses de livraison : refusé (%s)" % str(e)[:200])
    manquants = [k for k in ("MR_LOGIN", "MR_PASSWORD", "MR_CUSTOMER_ID") if not os.environ.get(k, "").strip()]
    if not essai and manquants:
        sys.exit("Secrets GitHub manquants : %s (à ajouter par Amine dans Settings → Secrets and variables → Actions)." % ", ".join(manquants))
    if not essai and not os.environ.get("GMAIL_APP_PASSWORD", "").strip():
        sys.exit("Secret GitHub GMAIL_APP_PASSWORD manquant (mot de passe d'application Google de contact@deway.be) : aucune étiquette créée.")
    bilan, etiquettes = [], []
    for o in liste:
        adr = o["shippingAddress"]
        pays = adr["countryCodeV2"]
        n = sum(li["quantity"] for li in o["lineItems"]["nodes"] if li["requiresShipping"]) or 1
        grammes = max(100, n * GRAMMES_ARTICLE)
        if o["shippingLine"]["title"] == RELAIS:
            mode, (lieu, nom_pr) = "24R", point_relais(adr)
        else:
            mode, lieu, nom_pr = "HOM", "", "domicile"
        tel_ok = bool(telephone(adr.get("phone") or o.get("phone"), pays))
        ligne = "%s · %s · %d article(s) · %d g · %s %s%s" % (o["name"], pays, n, grammes, mode, lieu or "", "" if lieu or mode == "HOM" else " (aucun point relais trouvé)")
        if mode == "HOM" and not tel_ok:
            ligne += " · téléphone manquant (obligatoire à domicile)"
        if essai or (mode == "24R" and not lieu):
            print("  " + ligne)
            continue
        envoi, pdf, statuts = appeler(demande(o, mode, lieu, grammes))
        erreurs = [st for st in statuts if (st[1] or "").lower().startswith("err")]
        if not envoi or erreurs:
            print("  %s → refus Mondial Relay : %s" % (o["name"], "; ".join("%s %s" % (c, m) for c, _, m in statuts) or "réponse vide"))
            bilan.append("❌ %s : refus Mondial Relay (%s)" % (o["name"], "; ".join(m or "" for _, _, m in statuts)[:200]))
            continue
        # le numéro est gardé tout de suite sur la commande : jamais deux étiquettes pour la même commande
        s.gql("""mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) { userErrors { message } } }""",
              {"m": [{"ownerId": o["id"], "namespace": MF[0], "key": MF[1], "type": "single_line_text_field", "value": envoi}]})
        if pdf:
            with urllib.request.urlopen(pdf, timeout=60) as r:
                etiquettes.append((o["name"], r.read()))
        err = expedier_shopify(s, o, envoi, adr.get("zip") or "")
        print("  %s → expédition %s · étiquette : %s · Shopify : %s" % (o["name"], envoi, "OK" if pdf else "PAS DE PDF",
                                                                        "expédiée" if not err else err))
        bilan.append("%s %s : expédition %s · %s · %s%s" % ("OK" if pdf else "SANS PDF", o["name"], envoi, pays,
                                                            nom_pr if mode == "24R" else "domicile",
                                                            "" if not err else " (Shopify : %s)" % err[0]["message"]))
        time.sleep(1)
    if bilan:
        envoyer_mail(etiquettes, bilan)
        print("E-mail envoyé à %s : %d étiquette(s)" % (BOITE, len(etiquettes)))


if __name__ == "__main__":
    if "--test-api" in sys.argv:  # vérifie les identifiants avec une demande volontairement incomplète : rien n'est créé
        o = {"name": "#TEST", "email": "contact@qosmi.be", "phone": "", "shippingAddress": {
            "firstName": "", "lastName": "", "company": "TEST", "address1": "", "address2": "", "city": "", "zip": "",
            "countryCodeV2": "BE", "phone": ""}}
        envoi, pdf, statuts = appeler(demande(o, "24R", "", 0))
        print("Expédition créée : %s (attendu : aucune)" % envoi)
        for c, niv, m in statuts:
            print("  statut %s %s : %s" % (c, niv, m))
        if any(c == "10001" for c, _, _ in statuts):
            print("→ identifiants REFUSÉS par Mondial Relay")
        else:
            print("→ identifiants acceptés (les erreurs ci-dessus portent sur la demande de test incomplète, c'est normal)")
    elif "--test-mail" in sys.argv:  # vérifie l'envoi vers contact@deway.be, sans étiquette ni frais
        envoyer_mail([], ["Test : si tu lis ce mail, l'envoi des étiquettes Mondial Relay fonctionne."])
        print("E-mail de test envoyé à %s" % BOITE)
    else:
        main()
