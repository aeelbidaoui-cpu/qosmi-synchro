"""Lot n°4 (demande d'Amine du 09/11/2026) : le lot n°1 réutilisé, mélangé, un jour FR / un jour NL.
Les jours FR reprennent les visuels du lot 1 (sauf « 3 parfums arabes », sans l'étiquette Noël) ;
les jours NL ont des visuels traduits ici. Visuels dans out5/, nommés l4-<id>-<k>.jpg."""
import os
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(ICI, "visuels_lot2.py")).read()
exec(_src.split("P = {}")[0])
_nl = open(os.path.join(ICI, "visuels_lot2_nl.py")).read()
exec(_nl[_nl.index("LIBELLES = "):_nl.index("\nP = {}")])
OUT5 = os.path.join(ICI, "out5")

P = {}
P["22-sel-arabes"] = selection("3 parfums<br>arabes<br>à offrir", [
    ("khamrah", "Lattafa", "Khamrah", "Cannelle, dattes, praline, vanille", "Chaud et gourmand, taillé pour l'hiver.", "2022"),
    ("yara", "Lattafa", "Yara", "Orchidée, fruits exotiques, vanille", "Doux et réconfortant. Il a lancé toute une ligne.", "2020"),
    ("asad", "Lattafa", "Asad", "Poivre noir, tabac, café, vanille", "Son nom veut dire « lion » en arabe.", "Eau de parfum")],
    "Ton préféré ?", "Toute notre sélection<br>de parfums arabes<br>est sur qosmi.be.", fin_droite="Parfums arabes")

P["06-pdj-jadore"] = nl(pdj("jadore", "Dior · 1999", "J'adore", "Mandarijn, roos, jasmijn, witte musk", "Calice Becker"))
P["07-bio-kurkdjian"] = nl(bio("Francis<br>Kurkdjian", "f2361-francis-kurkdjian-parfumeur", "Parfumeur · Parijs",
    ["Op zijn 15e besluit hij parfumeur te worden, zonder iets van het vak te kennen.",
     "In 1990 gaat hij naar ISIPCA, de parfumschool van Versailles. Vijf jaar later tekent hij Le Male voor Jean Paul Gaultier.",
     "In 2009 opent hij zijn eigen huis."],
    ("« Het ingrediënt interesseert me niet. Wat voor mij telt, is de emotie van het resultaat. »", "Francis Kurkdjian"),
    [("lemale", "Le Male", "Jean Paul Gaultier · 1995"), ("aquauni", "Aqua Universalis Cologne Forte", "MFK · 2021"), ("gfgold", "Gentle Fluidity Gold", "MFK · 2019")]))
P["09-mat-vanille"] = nl(matiere("De vanille", "De vrucht van een orchidee", "vanille", "50% 50%", "Waar komt vanille vandaan?",
    "De vrucht van een orchidee. Oorspronkelijk uit Mexico, vandaag vooral geteeld op Madagaskar en Réunion.",
    "De peul bevat honderden geurmoleculen. Zoet, vet, een beetje kruidig.",
    "Shalimar van Guerlain maakte haar in 1925 onmisbaar in de parfumerie.",
    [("shalimar", "Guerlain", "Shalimar"), ("yara", "Lattafa", "Yara")]))
P["15-conseil-concentrations"] = nl(conseil("Eau de toilette,<br>eau de parfum,<br>extrait: wat is<br>het verschil?", [
    ("Eau de toilette", "Meestal 5 tot 15 % parfumconcentraat. Lichter en frisser."),
    ("Eau de parfum", "Rond 15 tot 20 %. Houdt langer, met een duidelijker spoor."),
    ("Extrait", "20 % en meer. De rijkste versie, aan te brengen met kleine toetsjes."),
    ("Let op", "Eenzelfde lijn kan per versie behoorlijk anders ruiken. Het is niet altijd dezelfde formule, alleen sterker.")],
    "En jij?", "Team eau de toilette<br>of team extrait?",
    flacons_slide=(3, "De drie in het echt", [("lemale", "Le Male<br>Eau de toilette"), ("jadore", "J'adore<br>Eau de parfum"), ("hacivat", "Hacivat<br>Extrait")])))
P["17-mat-rose"] = nl(matiere("De roos", "De koningin van de bloemen", "rose", "50% 40%", "Welke rozen in de parfumerie?",
    "Twee grote rozen: de centifolia of meiroos, geteeld in Frankrijk en Marokko, en de Damascusroos, in Bulgarije en Turkije.",
    "Gedistilleerd geeft de Damascusroos een frisse, bijna citroenachtige olie. De centifolia geeft een warmere absolue, met honingtonen.",
    "Al sinds de oudheid maakt men parfums met roos.",
    [("delina", "Parfums de Marly", "Delina"), ("coco", "Chanel", "Coco Mademoiselle")]))
P["18-sel-mixtes"] = nl(selection("3 parfums<br>om samen<br>te delen", [
    ("ckone", "Calvin Klein", "CK One", "Citrus, groene thee, musk", "Voor haar en voor hem, al sinds 1994.", "1994 · Alberto Morillas"),
    ("colonia", "Acqua di Parma", "Colonia", "Citrus, lavendel, vetiver", "De eau de Cologne waarmee het huis begon.", "1916"),
    ("redtob", "Mancera", "Red Tobacco", "Kaneel, saffraan, tabak, vanille", "Voor wie graag opvalt.", "2017")],
    "Welke delen<br>jullie?", "Zeg het ons<br>in de reacties.", sur="Valentijn"))
P["19-pdj-hypnotic"] = nl(pdj("hp", "Dior · 1998", "Hypnotic Poison", "Kokos, bittere amandel, vanille", "Annick Menardo", taille=104))
P["21-conseil-tester"] = nl(conseil("Zo test je<br>een parfum<br>goed", [
    ("Begin met een geurstrip", "Daarmee maak je een eerste selectie, zonder je huid te verzadigen."),
    ("Dan op de huid", "Een parfum verandert op je huid. Daar moet je het beoordelen."),
    ("Neem je tijd", "De eerste minuten tonen alleen de topnoten. Wacht minstens een uur voor je beslist."),
    ("Maximaal drie", "Daarboven raakt je neus verzadigd en ruikt alles hetzelfde."),
    ("Laat je neus rusten", "Ruik tussen twee tests aan je trui of aan de huid van je onderarm.")],
    "Bewaar dit<br>voor later", "Sla deze post op<br>voor je volgende<br>parfumerie-uitstap.", couverture_fl=["erba", "hacivat", "aquauni"]))
P["24-pdj-hacivat"] = nl(pdj("hacivat", "Nishane · 2017", "Hacivat", "Ananas, grapefruit, patchoeli, eikenmos", "Extrait de parfum"))
P["26-bio-morillas"] = nl(bio("Alberto<br>Morillas", "f142-alberto-morillas", "Parfumeur · geboren in 1950 in Sevilla",
    ["Hij heeft nooit een parfumschool gevolgd.",
     "Als student aan de kunstacademie van Genève komt hij toevallig bij Firmenich terecht, op de afdeling chemie, en leert het vak zelf door grondstoffen te bestuderen.",
     "Eerste grote succes: Must de Cartier, in 1981. In 2003 krijgt hij de prijs François Coty."],
    None,
    [("ckone", "CK One", "Calvin Klein · 1994"), ("lbh", "Light Blue pour Homme", "Dolce&Gabbana · 2007")]))
P["27-conseil-peau"] = nl(conseil("Waarom ruikt<br>een parfum<br>anders op jou<br>dan op anderen?", [
    ("Je huid", "Droog of vet: ze houdt de noten niet op dezelfde manier vast. Op een droge huid verdampt parfum sneller."),
    ("Je temperatuur", "Een warmere huid verspreidt het parfum meer."),
    ("Het seizoen", "Kou remt de verspreiding af, warmte versterkt ze. Eenzelfde parfum kan per seizoen veranderen."),
    ("Je neus went eraan", "Na een paar minuten ruik je je eigen parfum niet meer. Anderen wel. Je hoeft dus niet de hele dag bij te sprayen.")],
    "De goede reflex", "Test altijd<br>op je eigen huid<br>voor je koopt."))
P["29-mat-bergamote"] = nl(matiere("De bergamot", "De glans van de eerste seconden", "bergamote", "50% 50%", "Wat is bergamot?",
    "Een citrusvrucht van de bergamotboom, tussen bittere sinaasappel en citroen. Ze groeit vooral in Calabrië, in het zuiden van Italië.",
    "Zacht, fris-zuur, licht bitter: je vindt haar vooral in de topnoten, van colognes tot de warmste parfums.",
    "In 1925 was Shalimar een van de eerste parfums die er zoveel van gebruikte.",
    [("sauvage", "Dior", "Sauvage Parfum"), ("colonia", "Acqua di Parma", "Colonia")]))

if __name__ == "__main__":
    import sys
    os.makedirs(OUT5, exist_ok=True)
    seuls = sys.argv[1:]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for nom, slides in P.items():
            if seuls and nom not in seuls:
                continue
            for f in os.listdir(OUT5):
                if f.startswith("l4-" + nom + "-"):
                    os.remove(os.path.join(OUT5, f))
            for k, h in enumerate(slides, 1):
                f = os.path.join(OUT5, "l4-%s-%d.html" % (nom, k))
                open(f, "w").write(h)
                pg.goto("file://" + f)
                pg.wait_for_timeout(250)
                pg.screenshot(path=os.path.join(OUT5, "l4-%s-%d.jpg" % (nom, k)), type="jpeg", quality=93)
                os.remove(f)
        b.close()
    print("ok", sum(len(v) for k, v in P.items() if not seuls or k in seuls), "visuels")
