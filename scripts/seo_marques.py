#!/usr/bin/env python3
"""SEO : une vraie page par marque (09/11/2026, demande d'Amine « on doit tout optimiser »).

Avant : les liens « Découvrir Creed », la page Marques et le bandeau des marques menaient vers /collections/vendors?q=Creed,
une page générée par Shopify, sans texte, sans méta-description, absente du sitemap.

Ici, pour chaque marque de config/selection.json (« marques ») qui a des fiches en ligne :
- une collection automatique « Fournisseur = marque » (/collections/<marque>), publiée sur la boutique en ligne ;
- titre Google, méta-description et court texte d'introduction, en FR et en NL (traductions Shopify) ;
- la correspondance marque → adresse dans le métachamp de la boutique qosmi.marques (JSON), lu par le thème
  (sections qk-texte et qk-marques) pour faire pointer les liens vers ces pages.
Relançable : les collections existantes sont mises à jour, rien n'est supprimé.
"""
import json, os, re, sys, unicodedata

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def cle(s):
    return re.sub(r"[^a-z0-9]", "", slug(s))


GENERIQUES = {"homme", "femme", "pour homme", "pour femme", "woman", "man", "men", "women", "her", "him", "dolce", "the", "les", "une"}


def court(nom, marque):
    """« Creed Aventus — Eau de Parfum pour homme » → « Aventus »."""
    n = nom.split(" — ")[0].strip()
    if n.lower().startswith(marque.lower()):
        n = n[len(marque):].strip(" -–")
    n = re.sub(r"\s+(Eau de (Parfum|Toilette|Cologne)|Extrait de Parfum|Parfum|Elixir|EDP|EDT)\b.*$", "", n, flags=re.I).strip()
    return n or None


TEXTES = os.path.join(RACINE, "config", "marques_textes.json")


def presentation(marque):
    """21/11/2026 : présentation vérifiée de la marque (config/marques_textes.json), FR + NL, ou None."""
    if not os.path.exists(TEXTES):
        return None
    return json.load(open(TEXTES, encoding="utf-8")).get("marques", {}).get(marque)


def textes(marque, noms, liens=None):
    """liens : [(nom court, handle)] des fiches en ligne, ajoutés au texte de la page (liens internes suivis par Google)."""
    import html as _h
    noms = [n for n in noms if n][:3]

    def titre(debut, suite):
        t = debut
        for i in range(len(noms), 0, -1):
            essai = "%s%s%s | Qosmi" % (debut, suite, ", ".join(noms[:i]))
            if len(essai) <= 60:
                return essai
        return "%s | Qosmi" % t if len(t) + 8 <= 60 else t[:60]

    def coupe(d):
        return d if len(d) <= 155 else d[:152].rsplit(" ", 1)[0] + "…"
    liste_fr = (" : " + ", ".join(noms)) if noms else ""
    liste_nl = (": " + ", ".join(noms)) if noms else ""
    liste_en = liste_nl
    pres = presentation(marque) or {}
    lf = ['<a href="/products/%s">%s</a>' % (h, _h.escape(n, quote=False)) for n, h in (liens or [])[:8]]
    ln = ['<a href="/nl/products/%s">%s</a>' % (h, _h.escape(n, quote=False)) for n, h in (liens or [])[:8]]
    le = ['<a href="/en/products/%s">%s</a>' % (h, _h.escape(n, quote=False)) for n, h in (liens or [])[:8]]
    # 24/11/2026 : texte long en 3 parties titrées (config/marques_textes.json « long ») à la place de la courte présentation
    def long_html(lg):
        return "".join("<h2>%s</h2><p>%s</p>" % (_h.escape(t, quote=False), _h.escape(p, quote=False))
                       for t, p in (pres.get("long") or {}).get(lg, []))
    for lg in ("fr", "nl", "en"):
        if long_html(lg):
            pres = dict(pres)
            pres[lg + "_html"] = long_html(lg)
    extra_fr = (pres["fr_html"] if pres.get("fr_html") else "<p>%s</p>" % _h.escape(pres["fr"], quote=False) if pres.get("fr") else "") + \
               ("<p>À découvrir chez Qosmi : %s.</p>" % joli(lf, "et") if lf else "")
    extra_nl = (pres["nl_html"] if pres.get("nl_html") else "<p>%s</p>" % _h.escape(pres["nl"], quote=False) if pres.get("nl") else "") + \
               ("<p>Ontdek bij Qosmi: %s.</p>" % joli(ln, "en") if ln else "")
    extra_en = (pres["en_html"] if pres.get("en_html") else "<p>%s</p>" % _h.escape(pres["en"], quote=False) if pres.get("en") else "") + \
               ("<p>Discover at Qosmi: %s.</p>" % joli(le, "and") if le else "")
    pf = marque if marque.lower().startswith("parfums ") else "Parfums %s" % marque
    return {
        # 21/11/2026 : « en Belgique » / « kopen in België » (recherches « jo malone belgie », « parfum jo malone »…)
        # 26/11/2026 (audit SEO) : pas de « Parfums Parfums de Marly »
        "titre_fr": titre("%s en Belgique" % pf, " : ") if len("%s en Belgique | Qosmi" % pf) <= 60
        else titre(pf, " : "),
        "titre_nl": titre("%s parfums kopen in België" % marque, ": ") if len("%s parfums kopen in België | Qosmi" % marque) <= 60
        else titre("%s parfums" % marque, ": "),
        "meta_fr": coupe("Tous les parfums %s%s. Flacons originaux et neufs, livrés partout en Belgique." % (marque, liste_fr)),
        "meta_nl": coupe("Alle parfums van %s%s. Originele, nieuwe flacons, geleverd in heel België." % (marque, liste_nl)),
        # 22/11/2026 (Amine, version anglaise) : anglais pour les marchés hors Belgique / Pays-Bas
        "titre_en": titre("%s perfumes" % marque, ": "),
        "meta_en": coupe("All %s fragrances%s. Genuine, brand-new bottles, delivered in 9 European countries." % (marque, liste_en)),
        "corps_en": "<p>All %s fragrances at Qosmi%s. 100%% genuine, brand-new bottles, delivered in 9 European countries,"
                    " free pick-up point delivery from 2 items in Belgium, the Netherlands and Luxembourg.</p>"
                    % (marque, (", including " + joli(noms, "and")) if noms else "") +
                    ('<div class="qk-suite">%s</div>' % extra_en if extra_en else ""),
        "corps_fr": "<p>Tous les parfums %s chez Qosmi%s. Des flacons 100 %% authentiques et neufs, livrés en Belgique et dans 8 autres pays d'Europe,"
                    " livraison offerte dès 2 articles en Belgique, aux Pays-Bas et au Luxembourg.</p>" % (marque, (", dont " + joli(noms, "et")) if noms else "") +
                    ('<div class="qk-suite">%s</div>' % extra_fr if extra_fr else ""),
        "corps_nl": "<p>Alle parfums van %s bij Qosmi%s. 100%% originele, nieuwe flacons, geleverd in België en 8 andere Europese landen,"
                    " gratis vanaf 2 artikelen in België, Nederland en Luxemburg.</p>" % (marque, (", waaronder " + joli(noms, "en")) if noms else "") +
                    ('<div class="qk-suite">%s</div>' % extra_nl if extra_nl else ""),
    }


def joli(l, et):
    return l[0] if len(l) == 1 else "%s %s %s" % (", ".join(l[:-1]), et, l[-1])


def main(essai=False):
    from shopify_api import Shopify
    from seo_boutique import traduire
    from site_theme import publication_boutique
    s = Shopify()
    pub = publication_boutique(s)
    marques = [m for m in json.load(open(os.path.join(RACINE, "config", "selection.json"), encoding="utf-8"))["marques"]
               if not m.endswith("_")]
    table, faits, sans = {}, 0, []
    for m in marques:
        h = slug(m)
        prods = []
        for nom in dict.fromkeys([m, m.replace("´", "'"), m.replace("&", " & "), m.replace(" & ", "&")]):
            prods = s.gql("""query($q: String!) { products(first: 50, query: $q, sortKey: TITLE) { nodes { title vendor handle } } }""",
                          {"q": 'vendor:"%s" status:active published_status:published' % nom.replace('"', '')})["products"]["nodes"]
            prods = [p for p in prods if cle(p["vendor"]) == cle(m)]
            if prods:
                break
        if not prods:
            sans.append(m)
            continue
        v = prods[0]["vendor"]
        noms, liens = [], []
        for p in prods:
            n = court(p["title"], v)
            if n and "|" not in n and len(n) >= 3 and n.lower() not in GENERIQUES and n not in noms and len(n) <= 28:
                noms.append(n)
                liens.append((p["title"].split(" — ")[0], p["handle"]))
        noms = sorted(noms, key=len)  # les noms les plus courts sont en général les parfums phares (Aventus, Sauvage…)
        liens = sorted(liens, key=lambda x: len(x[0]))
        t = textes(m, noms, liens)
        if essai:
            print("%-22s /collections/%-22s %s | %s | %s" % (m, h, t["titre_fr"], t["titre_nl"], t["corps_fr"][:400]))
            continue
        exist = s.gql("query($h: String!) { collectionByIdentifier(identifier: {handle: $h}) { id } }", {"h": h}).get("collectionByIdentifier")
        champs = {"title": m, "descriptionHtml": t["corps_fr"], "seo": {"title": t["titre_fr"], "description": t["meta_fr"]}}
        if exist:
            r = s.gql("""mutation($c: CollectionInput!) { collectionUpdate(input: $c) { collection { id } userErrors { field message } } }""",
                      {"c": dict(champs, id=exist["id"])})["collectionUpdate"]
        else:
            r = s.gql("""mutation($c: CollectionInput!) { collectionCreate(input: $c) { collection { id } userErrors { field message } } }""",
                      {"c": dict(champs, handle=h, ruleSet={"appliedDisjunctively": False,
                                                           "rules": [{"column": "VENDOR", "relation": "EQUALS", "condition": v}]})})["collectionCreate"]
        if r["userErrors"]:
            print("  %s : ERREUR %s" % (m, r["userErrors"]))
            continue
        cid = r["collection"]["id"]
        if pub:
            s.gql("""mutation($id: ID!, $p: ID!) { publishablePublish(id: $id, input: [{publicationId: $p}]) { userErrors { message } } }""",
                  {"id": cid, "p": pub})
        tr = traduire(s, cid, {"body_html": t["corps_nl"], "meta_title": t["titre_nl"], "meta_description": t["meta_nl"]})
        tr += " · EN %s" % traduire(s, cid, {"body_html": t["corps_en"], "meta_title": t["titre_en"],
                                             "meta_description": t["meta_en"]}, locale="en")
        table[v] = h
        if m != v:
            table[m] = h
        faits += 1
        print("  %-22s /collections/%s · NL %s" % (m, h, tr))
    if essai:
        print("Sans fiche en ligne : %s" % ", ".join(sans))
        return
    shop = s.gql("{ shop { id } }")["shop"]["id"]
    r = s.gql("""mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) { metafields { key } userErrors { field message } } }""",
              {"m": [{"ownerId": shop, "namespace": "qosmi", "key": "marques", "type": "json", "value": json.dumps(table, ensure_ascii=False)}]})
    print("Pages marques : %d créées ou mises à jour ; sans fiche en ligne : %s ; métachamp qosmi.marques : %s"
          % (faits, ", ".join(sans) or "aucune", r["metafieldsSet"]["userErrors"] or "ok"))


if __name__ == "__main__":
    main(essai="--essai" in sys.argv)
