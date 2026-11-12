#!/usr/bin/env python3
"""Pages légales Qosmi sur Shopify (FR + traduction NL) et liens dans le menu du bas de page.

  python3 scripts/site_pages.py            → crée ou met à jour les 5 pages, leurs traductions NL et le menu
  python3 scripts/site_pages.py --apercu   → écrit les pages en HTML dans exports/ (rien n'est envoyé)

Paramètres (e-mail du service client, frais de livraison) : config/site.json.
"""
import datetime as dt, json, os, re, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from site_pages_contenu import PAGES, ENTREPRISE  # noqa: E402

RACINE = os.path.dirname(ICI)
CFG = os.path.join(RACINE, "config", "site.json")
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MAAND = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"]
INTERDITS = ["soleluna", "wholesale", "premierproducts", "premier products", "prague", "praha", "brasty", "qogita", "deloox",
             "stockperfume", "trista", "marge", "margin", "coût d'achat", "inkoopprijs"]


def cfg():
    with open(CFG, encoding="utf-8") as f:
        return json.load(f)


IMAGES = {}  # {img_<nom>: adresse CDN} des images de assets/site (scripts/images_site.py), remplies par envoyer()


def remplir(html, c, nl=False):
    d = dt.date.today()
    v = dict(ENTREPRISE, email=c["email_service_client"],
             frais_livraison=c["frais_livraison"], frais_livraison_nl=c["frais_livraison"],
             delai_total=c["delai_livraison_fr"], delai_total_nl=c["delai_livraison_nl"],
             date="%d %s %d" % (d.day, MOIS[d.month - 1], d.year), date_nl="%d %s %d" % (d.day, MAAND[d.month - 1], d.year))
    v.update(IMAGES)
    html = html.strip()
    for k, val in v.items():
        html = html.replace("{%s}" % k, str(val))
    if nl:  # liens internes vers la version néerlandaise
        for p in PAGES:
            html = html.replace('href="/pages/%s"' % p["handle"], 'href="/nl/pages/%s"' % p["handle_nl"])
    html = re.sub(r'<figure class="qk-page-image">\s*<img src="\{img_[a-z_]+\}"[^>]*>\s*</figure>', "", html)  # image pas encore envoyée
    reste = re.findall(r"\{[a-z_]+\}", html)
    if reste:
        raise SystemExit("Champ non rempli : %s" % reste)
    bas = html.lower()
    for mot in INTERDITS:
        if mot in bas:
            raise SystemExit("Contrôle de confidentialité : « %s » trouvé dans une page. Rien n'est envoyé." % mot)
    return html


def apercu():
    c = cfg()
    out = os.path.join(RACINE, "exports", "Qosmi - pages legales - apercu.html")
    parts = ["<!doctype html><meta charset='utf-8'><title>Qosmi — pages légales</title>"
             "<style>body{font-family:system-ui;max-width:760px;margin:40px auto;padding:0 16px;line-height:1.55}"
             "h1{border-top:3px solid #2B1E2F;padding-top:24px;margin-top:56px}</style>"]
    for p in PAGES:
        parts.append("<h1>%s</h1>%s" % (p["titre"], remplir(p["fr"], c)))
        parts.append("<h1>%s (NL)</h1>%s" % (p["titre_nl"], remplir(p["nl"], c, nl=True)))
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("Aperçu : %s" % out)


def envoyer():
    from shopify_api import Shopify
    import images_site
    c = cfg()
    IMAGES.update({"img_" + n.replace("qosmi-", "").replace(".jpg", "").replace("-", "_"): u for n, u in images_site.urls(Shopify()).items()})
    for p in PAGES:  # contrôle complet avant d'envoyer quoi que ce soit
        remplir(p["fr"], c), remplir(p["nl"], c, nl=True)
    s = Shopify()
    ids = {}
    for p in PAGES:
        corps_fr, corps_nl = remplir(p["fr"], c), remplir(p["nl"], c, nl=True)
        d = s.gql('query($q: String!) { pages(first: 1, query: $q) { nodes { id handle } } }',
                  {"q": "handle:%s" % p["handle"]})["pages"]["nodes"]
        champs = {"title": p["titre"], "handle": p["handle"], "body": corps_fr, "isPublished": True}
        if d:
            r = s.gql("mutation($id: ID!, $p: PageUpdateInput!) { pageUpdate(id: $id, page: $p) { page { id } userErrors { field message } } }",
                      {"id": d[0]["id"], "p": champs})["pageUpdate"]
            action = "mise à jour"
        else:
            r = s.gql("mutation($p: PageCreateInput!) { pageCreate(page: $p) { page { id } userErrors { field message } } }",
                      {"p": champs})["pageCreate"]
            action = "créée"
        if r["userErrors"]:
            print("  ERREUR %s : %s" % (p["titre"], r["userErrors"]))
            continue
        pid = r["page"]["id"]
        ids[p["handle"]] = pid
        tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }",
                   {"id": pid})["translatableResource"]
        dig = {x["key"]: x["digest"] for x in tr["translatableContent"]}
        t = [{"locale": "nl", "key": k, "value": v, "translatableContentDigest": dig[k]}
             for k, v in (("title", p["titre_nl"]), ("body_html", corps_nl), ("handle", p["handle_nl"])) if k in dig]
        e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) {
                       userErrors { field message } } }""", {"id": pid, "t": t})["translationsRegister"]["userErrors"]
        print("  %-32s %s, NL : %s" % (p["titre"], action, "ok" if not e else e))
    # menu du bas de page
    menus = s.gql("{ menus(first: 20) { nodes { id handle title items { id title type resourceId url } } } }")["menus"]["nodes"]
    pied = next((m for m in menus if m["handle"] == "footer"), None)
    if not pied:
        print("Menu « footer » introuvable : liens à ajouter à la main (Boutique en ligne → Menus).")
        return
    garder = [{"id": i["id"], "title": i["title"], "type": i["type"],
               **({"resourceId": i["resourceId"]} if i.get("resourceId") else {}),
               **({"url": i["url"]} if i.get("url") and not i.get("resourceId") else {})}
              for i in pied["items"] if i.get("resourceId") not in ids.values()]
    nouveaux = [{"title": p["titre"], "type": "PAGE", "resourceId": ids[p["handle"]]} for p in PAGES if p["handle"] in ids]
    r = s.gql("""mutation($id: ID!, $t: String!, $h: String!, $i: [MenuItemUpdateInput!]!) {
                   menuUpdate(id: $id, title: $t, handle: $h, items: $i) { menu { id } userErrors { field message } } }""",
              {"id": pied["id"], "t": pied["title"], "h": pied["handle"], "i": garder + nouveaux})["menuUpdate"]
    print("Menu du bas de page :", "ok (%d liens)" % len(garder + nouveaux) if not r["userErrors"] else r["userErrors"])


POLITIQUES = {  # politiques Shopify (pied de la page de paiement) ← nos pages légales
    "TERMS_OF_SERVICE": "conditions-generales-de-vente",
    "SHIPPING_POLICY": "livraison",
    "REFUND_POLICY": "retours",
    "PRIVACY_POLICY": "confidentialite",
    "LEGAL_NOTICE": "mentions-legales",
}


def politiques():
    """Remplit les politiques de Shopify (Paramètres → Politiques), affichées au paiement, avec nos textes FR + NL.
    Coordonnées (obligatoire) : raison sociale, adresse, e-mail, numéros d'entreprise et de TVA."""
    from shopify_api import Shopify
    c = cfg()
    par = {p["handle"]: p for p in PAGES}
    contenus = {}
    for typ, h in POLITIQUES.items():
        contenus[typ] = (remplir(par[h]["fr"], c), remplir(par[h]["nl"], c, nl=True))
    e = ENTREPRISE
    contenus["CONTACT_INFORMATION"] = (
        "<p><strong>%s</strong><br>%s<br>E-mail : <a href=\"mailto:%s\">%s</a><br>Numéro d'entreprise (BCE) : %s<br>TVA : %s</p>"
        % (e["raison"], e["adresse"], c["email_service_client"], c["email_service_client"], e["bce"], e["tva"]),
        "<p><strong>%s</strong><br>%s<br>E-mail: <a href=\"mailto:%s\">%s</a><br>Ondernemingsnummer (KBO): %s<br>Btw: %s</p>"
        % (e["raison"], e["adresse_nl"], c["email_service_client"], c["email_service_client"], e["bce"], e["tva"]))
    for fr, nl in contenus.values():
        for mot in INTERDITS:
            if mot in (fr + nl).lower():
                raise SystemExit("Contrôle de confidentialité : « %s ». Rien n'est envoyé." % mot)
    s = Shopify()
    for typ, (fr, nl) in contenus.items():
        r = s.gql("""mutation($p: ShopPolicyInput!) { shopPolicyUpdate(shopPolicy: $p) { shopPolicy { id url } userErrors { field message } } }""",
                  {"p": {"type": typ, "body": fr}})["shopPolicyUpdate"]
        if r["userErrors"]:
            print("  %-20s ERREUR %s" % (typ, r["userErrors"]))
            continue
        pid = r["shopPolicy"]["id"]
        tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }",
                   {"id": pid})["translatableResource"]
        dig = {x["key"]: x["digest"] for x in (tr or {}).get("translatableContent", [])}
        t = [{"locale": "nl", "key": "body", "value": nl, "translatableContentDigest": dig["body"]}] if "body" in dig else []
        err = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) {
                         userErrors { field message } } }""", {"id": pid, "t": t})["translationsRegister"]["userErrors"] if t else "pas de champ traduisible"
        print("  %-20s ok (%s), NL : %s" % (typ, r["shopPolicy"]["url"], "ok" if not err else err))


def politiques_nl():
    """Traduction NL des politiques Shopify (remplies en FR dans l'admin le 08/11/2026)."""
    from shopify_api import Shopify
    c = cfg()
    par = {p["handle"]: p for p in PAGES}
    e = ENTREPRISE
    nl = {t: remplir(par[h]["nl"], c, nl=True) for t, h in POLITIQUES.items()}
    nl["CONTACT_INFORMATION"] = ("<p><strong>%s</strong><br>%s<br>E-mail: <a href=\"mailto:%s\">%s</a><br>Ondernemingsnummer (KBO): %s<br>Btw: %s</p>"
                                 % (e["raison"], e["adresse_nl"], c["email_service_client"], c["email_service_client"], e["bce"], e["tva"]))
    s = Shopify()
    res = s.gql("""{ translatableResources(first: 20, resourceType: SHOP_POLICY) { nodes { resourceId
                     translatableContent { key value digest } } } }""")["translatableResources"]["nodes"]
    for r in res:
        body = next((x for x in r["translatableContent"] if x["key"] == "body"), None)
        if not body:
            continue
        typ = next((t for t in nl if t != "CONTACT_INFORMATION" and _meme(body["value"], remplir(par[POLITIQUES[t]]["fr"], c))), None)
        if typ is None and "Numéro d'entreprise (BCE)" in body["value"] and len(body["value"]) < 400:
            typ = "CONTACT_INFORMATION"
        if typ is None:
            print("  politique non reconnue :", r["resourceId"], body["value"][:60])
            continue
        err = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) {
                         userErrors { field message } } }""",
                    {"id": r["resourceId"], "t": [{"locale": "nl", "key": "body", "value": nl[typ], "translatableContentDigest": body["digest"]}]})
        print("  %-20s NL : %s" % (typ, err["translationsRegister"]["userErrors"] or "ok"))


def _meme(a, b):
    import re as _re
    # la ligne « Version du … » change de date : on la retire avant de comparer
    n = lambda x: _re.sub(r"\s+", " ", _re.sub(r"<[^>]+>", " ", _re.sub(r"Version du [^<]*", "", x))).strip()[:120]
    return n(a) == n(b)


if __name__ == "__main__":
    if "--politiques-nl" in sys.argv:
        politiques_nl()
    elif "--politiques" in sys.argv:
        politiques()
    else:
        apercu() if "--apercu" in sys.argv else envoyer()
