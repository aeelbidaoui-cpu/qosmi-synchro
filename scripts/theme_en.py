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
EN = json.load(open(os.path.join(RACINE, "config", "theme_en.json"), encoding="utf-8"))["textes"]
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
    return texte, n


def main():
    total = fichiers = 0
    for f in sorted(glob.glob(os.path.join(RACINE, "theme_rk", "**", "*.liquid"), recursive=True)):
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
