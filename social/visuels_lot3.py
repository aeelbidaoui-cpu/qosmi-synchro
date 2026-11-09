"""Lot n°3 (demande d'Amine du 09/11/2026) : les « jumeaux » du lot n°2, postés plus tard et espacés.
- les publications FR du lot 2 reviennent en néerlandais ;
- les publications NL du lot 2 reviennent en français ;
- les publications de saison (Noël, réveillon, Nouvel An, anniversaires 2026) ne reviennent pas.
Visuels dans out4/, nommés l3-<id>-<k>.jpg."""
import os
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(ICI, "visuels_lot2.py")).read()
exec(_src.split("P = {}")[0])                      # gabarits et conseil_photos()
exec("P = {}\n" + _src.split("P = {}", 1)[1].split('if __name__')[0])   # versions FR du lot 2
_P2 = P
_nl = open(os.path.join(ICI, "visuels_lot2_nl.py")).read()
exec(_nl[_nl.index("LIBELLES = "):_nl.index("\nP = {}")])  # LIBELLES, nl()
OUT4 = os.path.join(ICI, "out4")

P = {}
# --- en français : les jumeaux des publications NL du lot 2 ---
for k in ["02-conseil-hiver", "06-mat-tonka", "10-pdj-fahrenheit", "12-conseil-superposer", "14-bio-ellena", "18-pdj-neroli",
          "20-mat-patchouli", "22-pdj-bloom", "24-conseil-pyramide", "26-mat-cannelle", "28-conseil-doser"]:
    P[k] = _P2[k]
P["30-sel-valentin"] = selection("La Saint-<br>Valentin,<br>c'est dans<br>une semaine", [
    ("prn", "Guerlain", "La Petite Robe Noire", "Cerise, amande, rose, réglisse", "Gourmande, et sûre d'elle.", "2012 · Thierry Wasser"),
    ("spicebomb", "Viktor&Rolf", "Spicebomb", "Pamplemousse, safran, piment, cannelle", "Pour lui, s'il aime les parfums qui réchauffent.", "2012 · Olivier Polge"),
    ("kenzoworld", "Kenzo", "Kenzo World", "Pivoine, jasmin, Ambroxan", "Un flacon en forme d'œil, impossible à oublier.", "2016 · Francis Kurkdjian")],
    "Encore<br>le temps !", "Toutes nos idées<br>sur qosmi.be.", fin_droite="qosmi.be", sur="Saint-Valentin", taille_titre=88)

# --- en néerlandais : les jumeaux des publications FR du lot 2 ---
P["03-pdj-prn"] = nl(pdj("prn", "Guerlain · 2012", "La Petite Robe Noire", "Kers, amandel, roos, zoethout", "Thierry Wasser", taille=88))
P["05-bio-ropion"] = nl(bio("Dominique<br>Ropion", "f121-dominique-ropion", "Parfumeur",
    ["Zijn moeder en grootvader werkten bij Roure, een huis van grondstoffen. Als tiener brengt hij er zijn vakanties door met afwegen.",
     "Op zijn 15e ontmoet hij er al Jacques Polge en Jean-Louis Sieuzac. Hij studeert fysica en werkt van 1989 tot 1998 samen met Sieuzac.",
     "In 2001 gaat hij naar IFF. Hij tekende Ysatis, Amarige, Alien, en een deel van L'Interdit en Invictus."],
    ("« Een formule draai en keer je in alle richtingen. »", "Dominique Ropion"),
    [("ysatis", "Ysatis", "Givenchy · 1984"), ("amarige", "Amarige", "Givenchy · 1991"), ("interdit", "L'Interdit", "Givenchy · 2018")]))
P["07-sel-fraiches"] = nl(selection("3 frisse<br>parfums<br>om te geven", [
    ("orangeverte", "Hermès", "Eau d'Orange Verte", "Sinaasappel, mandarijn, munt, eikenmos", "Een sprankelende eau de Cologne, om te delen.", "1979 · Françoise Caron"),
    ("voyage", "Hermès", "Voyage d'Hermès", "Citroen, thee, kardemom, witte musk", "Een flacon die draait, als een reisvoorwerp.", "2010 · Jean-Claude Ellena"),
    ("lagune", "Hermès", "Un Jardin sur la Lagune", "Magnolia, pittosporum, lelie, zilte noten", "Geïnspireerd op een geheime tuin in Venetië.", "2019 · Christine Nagel")],
    "Jouw favoriet?", "1, 2 of 3<br>in de reacties."))
P["13-mat-iris"] = nl(matiere("De iris", "De bloem die geurt via haar wortel", "iris", "50% 50%", "Waar komt iris vandaan?",
    "In de parfumerie gebruikt men niet de bloem maar de wortelstok, de ondergrondse stengel. Die droogt ongeveer drie jaar voor hij gedistilleerd wordt.",
    "Een ton iris levert maar twee kilo essentiële olie op. Het is een van de duurste grondstoffen: poederig, boterig, houtig.",
    "De gele lis, de moerasiris, is het symbool van Brussel.",
    [("gentleman", "Givenchy", "Gentleman"), ("bloom", "Gucci", "Bloom")]))
P["15-pdj-tuscan"] = nl(pdj("tuscan", "Tom Ford · 2007", "Tuscan Leather", "Framboos, saffraan, jasmijn, leer", "Private Blend", taille=96))
P["19-conseil-familles"] = nl(conseil_photos("De grote<br>geurfamilies", [
    ("Citrus", "De citrusvruchten: citroen, bergamot, sinaasappel. Fris en sprankelend.", "bergamote", "50% 50%", "De bergamot"),
    ("Bloemig", "Roos, jasmijn, tuberoos… De grootste familie.", "rose", "50% 45%", "De roos"),
    ("Houtig", "Ceder, sandelhout, vetiver. Droog of romig, altijd elegant.", "santal", "50% 50%", "Het sandelhout"),
    ("Amber", "Ook oosters genoemd: vanille, specerijen, harsen. Warm en omhullend.", "vanille", "50% 50%", "De vanille"),
    ("Chypre", "Bergamot, eikenmos, patchoeli. De naam komt van Chypre, een parfum van Coty uit 1917.", "patchouli", "50% 45%", "De patchoeli"),
    ("Fougère", "Lavendel, coumarine, eikenmos. De grote klassieker bij herenparfums.", "tonka", "50% 55%", "De tonkaboon, rijk aan coumarine")],
    "En jij?", "Welke familie<br>ben jij?"))
P["21-pdj-kenzoworld"] = nl(pdj("kenzoworld", "Kenzo · 2016", "Kenzo World", "Pioen, jasmijn, Ambroxan", "Francis Kurkdjian", taille=110))
P["23-bio-nagel"] = nl(bio("Christine<br>Nagel", "f146-christine-nagel", "Parfumeur · geboren in 1959 in Genève",
    ["Ze is opgeleid als chemicus en begint bij Firmenich, op de afdeling chromatografie: ze analyseert parfums, molecule per molecule.",
     "Alberto Morillas laat haar zijn akkoorden ruiken. Ze besluit parfumeur te worden en tekent daarna onder meer The One van Dolce&Gabbana en Miss Dior Chérie.",
     "In 2014 gaat ze naar Hermès, waar ze sinds 2016 de creatie van de parfums leidt."],
    None,
    [("lagune", "Un Jardin sur la Lagune", "Hermès · 2019"), ("basilic", "Eau de Basilic Pourpre", "Hermès · 2022")]), elle=True)
P["25-pdj-habitrouge"] = nl(pdj("habitrouge", "Guerlain · 1965", "Habit Rouge", "Lavendel, neroli, roos, vanille", "Jean-Paul Guerlain", taille=110))
P["27-conseil-conserver"] = nl(conseil("Hoe lang<br>blijft een<br>parfum<br>goed?", [
    ("Gesloten: heel lang", "Goed bewaard kan een ongeopende flacon jaren mee."),
    ("Geopend: een paar jaar", "Eenmaal aangebroken blijft hij meestal meerdere jaren mooi, als hij goed bewaard wordt."),
    ("Zijn drie vijanden", "Licht, warmte en lucht. Bewaar hem in zijn doos, in een kast."),
    ("Tekenen die niet liegen", "Een donkerdere kleur, een zure of metaalachtige geur bij het begin: hij is bedorven.")],
    "Doe de test", "Ruik eens aan je<br>oudste flacon."))
P["29-pdj-invictus"] = nl(pdj("invictus", "Paco Rabanne · 2013", "Invictus", "Grapefruit, zeenoot, guaiakhout, patchoeli", "Eau de toilette"))

if __name__ == "__main__":
    import sys
    os.makedirs(OUT4, exist_ok=True)
    seuls = sys.argv[1:]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for nom, slides in P.items():
            if seuls and nom not in seuls:
                continue
            for f in os.listdir(OUT4):
                if f.startswith("l3-" + nom + "-"):
                    os.remove(os.path.join(OUT4, f))
            for k, h in enumerate(slides, 1):
                f = os.path.join(OUT4, "l3-%s-%d.html" % (nom, k))
                open(f, "w").write(h)
                pg.goto("file://" + f)
                pg.wait_for_timeout(250)
                pg.screenshot(path=os.path.join(OUT4, "l3-%s-%d.jpg" % (nom, k)), type="jpeg", quality=93)
                os.remove(f)
        b.close()
    print("ok", sum(len(v) for k, v in P.items() if not seuls or k in seuls), "visuels")
