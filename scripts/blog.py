#!/usr/bin/env python3
"""Journal Qosmi (blog) — demande d'Amine du 08/11/2026 : un article par semaine, publié automatiquement, FR + NL,
signé « L'équipe Qosmi », avec des photos.

Chaque article est un fichier blog/articles/<numéro>-<sujet>.json :
  {"handle": "...", "date": "AAAA-MM-JJ", "tags": [...], "image": "<handle d'une fiche>", "couverture": "<fichier>.jpg" (facultatif),
   "fr": {"titre", "resume", "seo_titre", "seo_desc", "corps", "faq": [{"q", "r"}]},
   "nl": {"titre", "handle", "resume", "seo_titre", "seo_desc", "corps", "faq": [...]}}
Image de couverture (demande d'Amine du 08/11/2026 : les flacons ne doivent pas être coupés dans le Journal) :
  - "couverture" : image horizontale de blog/couvertures/ (composée avec scripts/entetes_collections.py, flacons détourés) ;
  - sinon : la photo de la fiche "image", posée entière au centre d'un bandeau blanc 2400 × 1000 (rien n'est coupé).
Dans "corps" (HTML) :
  [[photo:<handle>]]           photo de la fiche (déjà sur Shopify, photos autorisées) avec lien vers la fiche
  [[photos:<h1>,<h2>,<h3>]]    rangée de photos de fiches
  [[produit:<handle>|texte]]   lien vers la fiche (texte facultatif : sinon le nom du parfum)
  [[notes:tete=<clé>|texte,…;coeur=…;fond=…]]  pyramide olfactive illustrée (photos rondes des ingrédients, blog/notes.json ;
                               texte facultatif : sinon le nom de l'ingrédient dans la langue de l'article)
  [[concentrations]]           visuel des concentrations (eau de Cologne → extrait)
  [[collection:<handle>|texte]] lien vers une collection (adresse NL traduite si elle existe)
  [[marque:<nom>|texte]]       lien vers tous les parfums d'une marque
  [[page:<handle>|texte]]      lien vers une page du site (adresse NL dans PAGES_NL)
Les liens NL pointent vers l'adresse néerlandaise de la fiche. Une fiche qui n'est pas en ligne n'est jamais liée.
La FAQ est ajoutée en bas de l'article et reprise en données structurées (FAQPage) par le thème.

Règles de contenu (voir blog/LIGNE_EDITORIALE.md) : jamais « testé » / « on a senti » ; pas de prix d'achat, de fournisseur,
de marge ni de prix de concurrents ; pas de commune d'établissement.

Usage : python scripts/blog.py            (publie ou met à jour tous les articles)
        python scripts/blog.py --essai    (contrôle les fichiers sans rien envoyer)
"""
import glob, html, json, os, re, sys, urllib.parse

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
DOSSIER = os.path.join(RACINE, "blog", "articles")
BLOG = {"handle": "journal", "anciens": ["actualites", "news"], "titre": "Le Magazine Qosmi", "titre_nl": "Qosmi Magazine"}  # renommé le 10/11/2026 (demande d'Amine)
AUTEUR = "L'équipe Qosmi"
INTERDITS = ["soleluna", "wholesale", "prix d'achat", "marge", "dilbeek", "notino", "deloox", "douglas", "ici paris",
             "j'ai testé", "on a testé", "nous avons testé", "testé pour vous", "getest", "wij hebben getest"]
Q_FICHE = """query($h: String!) { productByIdentifier(identifier: {handle: $h}) { id title status onlineStoreUrl
  featuredMedia { preview { image { url altText } } } translations(locale: "nl") { key value } } }"""


def charger():
    arts = []
    for chemin in sorted(glob.glob(os.path.join(DOSSIER, "*.json"))):
        a = json.load(open(chemin, encoding="utf-8"))
        a["_fichier"] = os.path.basename(chemin)
        for langue in ("fr", "nl"):
            for cle in ("titre", "resume", "seo_titre", "seo_desc", "corps", "faq"):
                if not a.get(langue, {}).get(cle):
                    raise SystemExit("%s : champ manquant %s.%s" % (a["_fichier"], langue, cle))
            texte = json.dumps(a[langue], ensure_ascii=False).lower()
            mauvais = [m for m in INTERDITS if m in texte]
            if mauvais:
                raise SystemExit("%s (%s) : mots interdits %s" % (a["_fichier"], langue, mauvais))
            if len(a[langue]["seo_titre"]) > 70 or len(a[langue]["seo_desc"]) > 160:
                raise SystemExit("%s (%s) : titre SEO > 70 ou description > 160 caractères" % (a["_fichier"], langue))
        arts.append(a)
    return arts


def fiches_citees(a):
    hs = {a["image"]}
    for langue in ("fr", "nl"):
        for m in re.finditer(r"\[\[(photo|photos|produit):([^\]|]+)", a[langue]["corps"]):
            hs |= {h.strip() for h in m.group(2).split(",")}
    return hs


COLLECTIONS_NL = {}


def collections_nl(s):
    """handle FR -> handle NL des collections (traductions Shopify)."""
    d = s.gql("""{ collections(first: 100) { nodes { handle translations(locale: "nl") { key value } } } }""")["collections"]["nodes"]
    return {c["handle"]: next((t["value"] for t in c["translations"] if t["key"] == "handle"), c["handle"]) for c in d}


PAGES_NL = {"diagnostic": "geurdiagnose", "faq": "veelgestelde-vragen", "lexique": "geurwoordenboek",
            "idees-cadeaux-noel": "kerstcadeaus"}  # adresses NL des pages (quiz, odeurs… gardent la même)


def rendu(corps, fiches, langue):
    def lien(h):
        f = fiches.get(h)
        if not f:
            return None
        if langue == "nl":
            return "/nl/products/%s" % (f["handle_nl"] or h)
        return "/products/%s" % h

    def figure(h, seule=True):
        f = fiches.get(h)
        if not f or not f["image"]:
            return ""
        nom = html.escape(f["titre"])
        src = f["image"] + ("&" if "?" in f["image"] else "?") + "width=800"
        img = '<img src="%s" alt="%s" loading="lazy" width="800" height="1000">' % (src, nom)
        return '<figure class="qk-fig%s"><a href="%s">%s</a><figcaption><a href="%s">%s</a></figcaption></figure>' % (
            "" if seule else " qk-fig--rang", lien(h), img, lien(h), nom)

    def remplace(m):
        genre, reste = m.group(1), m.group(2)
        if genre == "photo":
            return figure(reste.strip())
        if genre == "photos":
            return '<div class="qk-sel">%s</div>' % "".join(figure(h.strip(), False) for h in reste.split(","))
        h, _, texte = reste.partition("|")
        h = h.strip()
        f = fiches.get(h)
        texte = texte.strip() or (f["titre"] if f else h)
        return '<a href="%s">%s</a>' % (lien(h), html.escape(texte)) if f else html.escape(texte)
    def autres(m):
        genre, (cle, _, texte) = m.group(1), m.group(2).partition("|")
        cle = cle.strip()
        prefixe = "/nl" if langue == "nl" else ""
        if genre == "page":  # 13/11/2026 : pages du site (diagnostic, quiz, guide cadeaux…)
            h = PAGES_NL.get(cle, cle) if langue == "nl" else cle
            return '<a href="%s/pages/%s">%s</a>' % (prefixe, h, html.escape(texte.strip() or cle))
        if genre == "collection":
            h = COLLECTIONS_NL.get(cle, cle) if langue == "nl" else cle
            return '<a href="%s/collections/%s">%s</a>' % (prefixe, h, html.escape(texte.strip() or cle))
        return '<a href="%s/collections/vendors?q=%s">%s</a>' % (prefixe, urllib.parse.quote(cle), html.escape(texte.strip() or cle))
    corps = re.sub(r"\[\[(collection|marque|page):([^\]]+)\]\]", autres, corps)
    corps = re.sub(r"\[\[notes:([^\]]+)\]\]", lambda m: notes_html(m.group(1), langue), corps)
    corps = corps.replace("[[concentrations]]", concentrations_html(langue))
    return re.sub(r"\[\[(photo|photos|produit):([^\]]+)\]\]", remplace, corps)


RACINE_BLOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blog")
NOTES_URL = {}  # clé d'ingrédient → adresse Shopify de sa photo


def notes_citees(a):
    cles = set()
    for langue in ("fr", "nl"):
        for m in re.finditer(r"\[\[notes:([^\]]+)\]\]", a[langue]["corps"]):
            for etage in m.group(1).split(";"):
                cles |= {x.split("|")[0].strip() for x in etage.partition("=")[2].split(",") if x.strip()}
    return cles


def notes_html(spec, langue):
    conf = json.load(open(os.path.join(RACINE_BLOG, "notes.json"), encoding="utf-8"))
    titres = {"tete": ("Notes de tête", "Topnoten"), "coeur": ("Notes de cœur", "Hartnoten"), "fond": ("Notes de fond", "Basisnoten")}
    etages = []
    for etage in spec.split(";"):
        nom, _, liste = etage.partition("=")
        nom = nom.strip()
        items = []
        for x in liste.split(","):
            cle, _, texte = x.partition("|")
            cle = cle.strip()
            if not cle:
                continue
            texte = texte.strip() or conf.get(cle, {}).get(langue, cle)
            u = NOTES_URL.get(cle)
            img = ('<img src="%s?width=360" alt="%s" loading="lazy" width="180" height="180">' % (u, html.escape(texte))) if u else ""
            items.append('<figure class="qk-note">%s<figcaption>%s</figcaption></figure>' % (img, html.escape(texte)))
        t = titres.get(nom, (nom, nom))[0 if langue == "fr" else 1]
        etages.append('<div class="qk-notes__etage"><p class="qk-notes__titre">%s</p><div class="qk-notes__liste">%s</div></div>' % (t, "".join(items)))
    return '<div class="qk-notes">%s</div>' % "".join(etages)


def concentrations_html(langue):
    lignes = [("Eau de Cologne", 2, 5, "Fraîche, quelques heures", "Fris, enkele uren"),
              ("Eau de Toilette", 5, 15, "Lumineuse, en journée", "Licht, overdag"),
              ("Eau de Parfum", 10, 20, "Plus ronde, la plus vendue", "Voller, de bestseller"),
              ("Extrait de Parfum", 15, 30, "Dense, très tenace", "Rijk, zeer lang"),]
    maxi = 35.0
    titre = "Part de concentré parfumé (repères)" if langue == "fr" else "Aandeel parfumconcentraat (richtcijfers)"
    out = []
    for nom, a, b, fr, nl in lignes:
        out.append('<div class="qk-conc__ligne"><span class="qk-conc__nom">%s</span><span class="qk-conc__piste">'
                   '<span class="qk-conc__barre" style="left:%.1f%%;width:%.1f%%"></span></span>'
                   '<span class="qk-conc__val">%d–%d %%</span><span class="qk-conc__desc">%s</span></div>'
                   % (nom, a / maxi * 100, (b - a) / maxi * 100, a, b, fr if langue == "fr" else nl))
    return '<div class="qk-conc"><p class="qk-conc__titre">%s</p>%s</div>' % (titre, "".join(out))


def faq_html(faq, langue):
    titre = "Questions fréquentes" if langue == "fr" else "Veelgestelde vragen"
    blocs = "".join("<h3>%s</h3><p>%s</p>" % (html.escape(x["q"]), html.escape(x["r"])) for x in faq)
    return '<section class="qk-faq"><h2>%s</h2>%s</section>' % (titre, blocs)


def main():
    arts = charger()
    print("Articles : %d" % len(arts))
    if "--essai" in sys.argv:
        for a in arts:
            print("  %s → /blogs/%s/%s (%s)" % (a["_fichier"], BLOG["handle"], a["handle"], ", ".join(sorted(fiches_citees(a)))))
        return
    from shopify_api import Shopify
    from seo_boutique import traduire
    s = Shopify()

    # ---------- le blog ----------
    blogs = s.gql("{ blogs(first: 20) { nodes { id handle title } } }")["blogs"]["nodes"]
    blog = next((b for b in blogs if b["handle"] == BLOG["handle"]), None) or \
        next((b for b in blogs if b["handle"] in BLOG["anciens"]), None)
    if blog:
        r = s.gql("""mutation($id: ID!, $b: BlogUpdateInput!) { blogUpdate(id: $id, blog: $b) { blog { id handle } userErrors { field message } } }""",
                  {"id": blog["id"], "b": {"title": BLOG["titre"], "handle": BLOG["handle"], "redirectNewHandle": True}})["blogUpdate"]
    else:
        r = s.gql("""mutation($b: BlogCreateInput!) { blogCreate(blog: $b) { blog { id handle } userErrors { field message } } }""",
                  {"b": {"title": BLOG["titre"], "handle": BLOG["handle"]}})["blogCreate"]
    if r["userErrors"]:
        raise SystemExit("Blog : %s" % r["userErrors"])
    blog_id = r["blog"]["id"]
    print("Blog : %s (/blogs/%s) — NL : %s" % (BLOG["titre"], r["blog"]["handle"], traduire(s, blog_id, {"title": BLOG["titre_nl"]})))
    COLLECTIONS_NL.update(collections_nl(s))
    existants = {x["handle"]: x["id"] for x in s.gql("query($id: ID!) { blog(id: $id) { articles(first: 250) { nodes { id handle } } } }",
                                                     {"id": blog_id})["blog"]["articles"]["nodes"]}

    # ---------- les articles ----------
    for a in arts:
        fiches = {}
        for h in sorted(fiches_citees(a)):
            p = s.gql(Q_FICHE, {"h": h})["productByIdentifier"]
            if not p or p["status"] != "ACTIVE" or not p.get("onlineStoreUrl"):
                print("  ! %s : fiche %s absente ou pas en ligne — pas de lien ni de photo" % (a["_fichier"], h))
                continue
            img = (((p.get("featuredMedia") or {}).get("preview") or {}).get("image") or {}).get("url")
            fiches[h] = {"titre": p["title"].replace(" — ", " "), "image": img,
                         "handle_nl": next((t["value"] for t in p["translations"] if t["key"] == "handle"), None)}
        if a["image"] not in fiches:
            raise SystemExit("%s : la fiche de l'image principale (%s) n'est pas en ligne" % (a["_fichier"], a["image"]))
        import photos_adp as pa
        for cle in sorted(notes_citees(a)):
            if cle not in NOTES_URL:
                nom = "qosmi-note-%s.jpg" % cle
                NOTES_URL[cle] = pa.adresse_fichier(s, nom) or pa.envoyer(s, os.path.join(RACINE_BLOG, "notes", nom), alt=cle)
        corps = {l: rendu(a[l]["corps"], fiches, l) + faq_html(a[l]["faq"], l) for l in ("fr", "nl")}
        couv = couverture(s, a, fiches[a["image"]]["image"])
        champs = {"title": a["fr"]["titre"], "handle": a["handle"], "body": corps["fr"], "summary": "<p>%s</p>" % html.escape(a["fr"]["resume"]),
                  "author": {"name": AUTEUR}, "tags": a.get("tags", []), "isPublished": True,
                  "image": {"url": couv or fiches[a["image"]]["image"], "altText": a["fr"]["titre"] if couv else fiches[a["image"]]["titre"]},
                  "metafields": [
                      {"namespace": "global", "key": "title_tag", "type": "single_line_text_field", "value": a["fr"]["seo_titre"]},
                      {"namespace": "global", "key": "description_tag", "type": "multi_line_text_field", "value": a["fr"]["seo_desc"]},
                      {"namespace": "qosmi", "key": "faq_fr", "type": "json", "value": json.dumps(a["fr"]["faq"], ensure_ascii=False)},
                      {"namespace": "qosmi", "key": "faq_nl", "type": "json", "value": json.dumps(a["nl"]["faq"], ensure_ascii=False)}]}
        if a["handle"] in existants:
            champs.pop("handle")
            r = s.gql("""mutation($id: ID!, $a: ArticleUpdateInput!) { articleUpdate(id: $id, article: $a) { article { id handle } userErrors { field message } } }""",
                      {"id": existants[a["handle"]], "a": champs})["articleUpdate"]
            action = "mis à jour"
        else:
            champs["blogId"] = blog_id
            champs["publishDate"] = a["date"] + "T07:00:00Z"
            r = s.gql("""mutation($a: ArticleCreateInput!) { articleCreate(article: $a) { article { id handle } userErrors { field message } } }""",
                      {"a": champs})["articleCreate"]
            action = "publié"
        if r["userErrors"]:
            print("  REFUS %s : %s" % (a["_fichier"], json.dumps(r["userErrors"], ensure_ascii=False)[:500]))
            continue
        aid = r["article"]["id"]
        nl = a["nl"]
        t = traduire(s, aid, {"title": nl["titre"], "body_html": corps["nl"], "summary_html": "<p>%s</p>" % html.escape(nl["resume"]),
                              "handle": nl.get("handle") or a["handle"], "meta_title": nl["seo_titre"], "meta_description": nl["seo_desc"]})
        print("  %s %s : https://qosmi.be/blogs/%s/%s — NL : %s" % (a["_fichier"], action, BLOG["handle"], a["handle"], t))


def couverture(s, a, url_fiche):
    """Adresse Shopify de l'image de couverture horizontale de l'article (envoyée une seule fois par nom)."""
    import tempfile, urllib.request
    import photos_adp as pa
    dossier = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blog", "couvertures")
    nom = a.get("couverture")
    if nom:
        return pa.adresse_fichier(s, nom) or pa.envoyer(s, os.path.join(dossier, nom), alt=a["fr"]["titre"])
    nom = "qosmi-journal-%s.jpg" % a["handle"]
    u = pa.adresse_fichier(s, nom)
    if u or not url_fiche:
        return u
    try:
        from PIL import Image
    except ImportError:
        return None
    from io import BytesIO
    photo = Image.open(BytesIO(urllib.request.urlopen(url_fiche, timeout=60).read())).convert("RGB")
    photo.thumbnail((2000, 880), Image.LANCZOS)
    toile = Image.new("RGB", (2400, 1000), (255, 255, 255))
    toile.paste(photo, ((2400 - photo.width) // 2, (1000 - photo.height) // 2))
    chemin = os.path.join(tempfile.mkdtemp(), nom)
    toile.save(chemin, quality=90)
    return pa.envoyer(s, chemin, alt=a["fr"]["titre"])


if __name__ == "__main__":
    main()
