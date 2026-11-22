#!/usr/bin/env python3
"""Version anglaise du thème Qosmi (22/11/2026, Amine : « oui vasy »).

Les sections et extraits qk-* écrivent leurs petits textes en double (« {% if qk_nl %}NL{% else %}FR{% endif %} »).
Ce script ajoute une troisième branche anglaise (« {% elsif qk_en %}EN ») pour chaque texte FR présent dans
config/theme_en.json, et la variable qk_en (vraie quand la boutique est affichée en anglais).
Sans traduction anglaise, rien ne change : le texte français reste affiché en anglais.
Relançable sans effet (un texte déjà traité n'est pas retouché).

  python3 scripts/theme_en.py          # modifie theme_rk/ sur place, puis action theme « theme-rk »
  python3 scripts/theme_en.py --essai  # compte seulement
"""
import glob, json, os, re, sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
_D = json.load(open(os.path.join(RACINE, "config", "theme_en.json"), encoding="utf-8"))
EN, JS, QUIZ = _D["textes"], _D.get("js", {}), _D.get("quiz", {})
LIT = r"'(?:[^'\\]|\\.)*'"
# JavaScript : nl ? 'NL' : 'FR'  →  nl ? 'NL' : en ? 'EN' : 'FR'
TERNAIRE = re.compile(r"\bnl \? (" + LIT + r") : (" + LIT + r")(?! *:)")
JS_LANGUE = {  # déclaration de la langue côté JavaScript
    "var nl = {{ qk_nl | json }}": "var nl = {{ qk_nl | json }}, en = {{ qk_en | json }}",
    "var nl = (document.documentElement.lang || '').indexOf('nl') === 0;":
        "var nl = (document.documentElement.lang || '').indexOf('nl') === 0, en = (document.documentElement.lang || '').indexOf('en') === 0;",
}
# remplacements faits à la main (textes sur plusieurs lignes ou calculés)
MAIN = [
    ("""zone.textContent = nl ? 'De kaart kon niet laden. Geen probleem: we kiezen het afhaalpunt het dichtst bij je adres.'
                              : "La carte""", """zone.textContent = nl ? 'De kaart kon niet laden. Geen probleem: we kiezen het afhaalpunt het dichtst bij je adres.'
                              : en ? "The map couldn't load. No problem: we'll use the pick-up point closest to your address."
                              : "La carte"""),
    ("p.textContent = nl ? 'Geur ' + (k + 1) : 'Odeur ' + (k + 1);", "p.textContent = nl ? 'Geur ' + (k + 1) : en ? 'Scent ' + (k + 1) : 'Odeur ' + (k + 1);"),
    ("""          : (tous ? tous + ' parfums avec '""", """          : en ? (tous ? tous + ' fragrances with ' + (sel.length > 1 ? 'these ' + sel.length + ' scents' : 'this scent') : 'Fragrances with some of your scents')
          : (tous ? tous + ' parfums avec '"""),
    ("t.textContent = nl ? f[2] : f[1];", "t.textContent = nl ? f[2] : en ? (f[3] || f[1]) : f[1];"),
    ("b.textContent = nl ? o.nl : o.fr;", "b.textContent = nl ? o.nl : en ? (o.en || o.fr) : o.fr;"),
    ("return { id: id, t: nl ? o.nl : o.fr };", "return { id: id, t: nl ? o.nl : en ? (o.en || o.fr) : o.fr };"),
    ("[f, f, f])[nl ? 2 : 1];", "[f, f, f, f])[nl ? 2 : en ? 3 : 1];"),
    ("""        : { agrumes: 'frais et hespéridé""", """        : en ? { agrumes: 'fresh and zesty: energising citrus', fleurs: 'floral: from powdery flowers to lush white flowers', fruits: 'fruity and juicy',
          gourmand: 'gourmand: vanilla, caramel, tonka bean', epices: 'spicy, with warm or peppery spices', bois: 'woody: from creamy sandalwood to dry vetiver',
          ambre: 'warm and ambery: resins, musks or oud', frais: 'fresh and aromatic: lavender, herbs, marine notes' }
        : { agrumes: 'frais et hespéridé"""),
    ("""        : { agrumes: 'les agrumes'""", """        : en ? { agrumes: 'citrus', fleurs: 'flowers', fruits: 'fruity notes', gourmand: 'gourmand notes', epices: 'spices', bois: 'woods', ambre: 'ambery notes', frais: 'fresh, aromatic notes' }
        : { agrumes: 'les agrumes'"""),
    ("fr: o[2], nl: o[3], tout:", "fr: o[2], nl: o[3], en: o[4], tout:"),
    ("function nomOdeur(i, nl) { var o = odeurs[i]; return nl ? o.nl : o.fr; }",
     "var en = (document.documentElement.lang || '').indexOf('en') === 0;\n  function nomOdeur(i, nl) { var o = odeurs[i]; return nl ? o.nl : en ? (o.en || o.fr) : o.fr; }"),
    ("var langue = {{ qk_nl | json }} ? 'nl' : 'fr';", "var langue = {{ qk_nl | json }} ? 'nl' : ({{ qk_en | json }} ? 'en' : 'fr');"),
]
ESSAI = "--essai" in sys.argv

COND = r"(qk_nl|nl|request\.locale\.iso_code == 'nl')"
# {% if COND %}NL{% else %}FR{% endif %}  (sans autre balise Liquid à l'intérieur des deux textes)
MOTIF = re.compile(r"(\{%-? *if " + COND + r" *-?%\})((?:(?!\{%).)*?)(\{%-? *else *-?%\})((?:(?!\{%).)*?)(\{%-? *endif *-?%\})", re.S)
EN_DE = {"qk_nl": "qk_en", "nl": "en", "request.locale.iso_code == 'nl'": "request.locale.iso_code == 'en'"}
ASSIGN = {
    "{%- if request.locale.iso_code == 'nl' -%}{%- assign qk_nl = true -%}{%- endif -%}":
        "{%- assign qk_en = false -%}{%- if request.locale.iso_code == 'en' -%}{%- assign qk_en = true -%}{%- endif -%}",
    "{%- if request.locale.iso_code == 'nl' -%}{%- assign nl = true -%}{%- endif -%}":
        "{%- assign en = false -%}{%- if request.locale.iso_code == 'en' -%}{%- assign en = true -%}{%- endif -%}",
}


def traiter(texte):
    n = 0
    for a, b in ASSIGN.items():
        if a in texte and b not in texte:
            texte = texte.replace(a, a + b)

    def remplace(m):
        nonlocal n
        ouv, cond, nl, sinon, fr, fin = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6)
        en = EN.get(fr)
        if en is None:
            return m.group(0)
        n += 1
        tiret_g = "-" if sinon.startswith("{%-") else ""
        tiret_d = "-" if sinon.endswith("-%}") else ""
        return "%s%s{%%%s elsif %s %s%%}%s%s%s%s" % (ouv, nl, tiret_g, EN_DE[cond], tiret_d, en, sinon, fr, fin)

    texte = MOTIF.sub(remplace, texte)

    # --- JavaScript
    for a, b in JS_LANGUE.items():
        if a in texte and b not in texte:
            texte = texte.replace(a, b)
            n += 1
    for a, b in MAIN:
        if a in texte and b not in texte:
            texte = texte.replace(a, b)
            n += 1

    def tern(m):
        nonlocal n
        fr_lit = m.group(2)
        fr = fr_lit[1:-1].replace("\\'", "'")
        en = JS.get(fr)
        if en is None:
            return m.group(0)
        n += 1
        return "nl ? %s : en ? %s : %s" % (m.group(1), json.dumps(en, ensure_ascii=False), fr_lit)
    texte = TERNAIRE.sub(tern, texte)

    # quiz : T(fr, nl) lit l'anglais dans QEN
    tq = "function T(fr, n) { return nl ? n : fr.replace("
    if tq in texte and "var QEN" not in texte:
        texte = texte.replace(tq, "var QEN = " + json.dumps(QUIZ, ensure_ascii=False) + ";\n      "
                              "function T(fr, n) { return nl ? n : en && QEN[fr] ? QEN[fr] : fr.replace(")
        n += 1
    return texte, n


def main():
    total = fichiers = 0
    for f in sorted((glob.glob(os.path.join(RACINE, "theme_rk", "**", "*.liquid"), recursive=True)
                    + glob.glob(os.path.join(RACINE, "theme_rk", "assets", "*.js")))):
        avant = open(f, encoding="utf-8").read()
        apres, n = traiter(avant)
        if n:
            fichiers += 1
            total += n
            print("%-45s %3d texte(s) anglais" % (os.path.relpath(f, RACINE), n))
            # contrôle : autant de if que de endif, et pas d'elsif en double
            if apres.count("{%") - apres.count("%}") != avant.count("{%") - avant.count("%}"):
                sys.exit("Balises déséquilibrées dans %s : arrêt." % f)
            if not ESSAI and apres != avant:
                open(f, "w", encoding="utf-8").write(apres)
    print("Total : %d textes anglais dans %d fichiers%s" % (total, fichiers, " (essai)" if ESSAI else ""))


if __name__ == "__main__":
    main()
