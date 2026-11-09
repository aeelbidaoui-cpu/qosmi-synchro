"""Lot n°2 : un jour en français, le lendemain en néerlandais (demande d'Amine du 09/11/2026).
Les 15 publications néerlandaises sont refaites ici en NL (mêmes gabarits, libellés traduits) ; elles remplacent les visuels FR
du même nom dans out3/."""
import os
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(ICI, "visuels_lot2.py")).read().split("P = {}")[0])

LIBELLES = [("Glisse →", "Swipe →"), ("Joyeux anniversaire", "Gelukkige verjaardag"), ("Le conseil Qosmi", "De Qosmi-tip"),
            ("Le conseil", "De tip"), ("Le parfum du jour", "Het parfum van de dag"), ("Le parfumeur", "De parfumeur"),
            ("Le saviez-vous", "Wist je dat"), ("Matière première", "Grondstof"), ("À sentir", "Te ruiken"),
            (">ans<", ">jaar<"), ("dans le flacon", "in de flacon"), ("Les trois sur qosmi.be", "Alle drie op qosmi.be"), ("La sélection", "De selectie")]


def nl(pages, elle=False):
    out = []
    for h in pages:
        for a, b in LIBELLES:
            h = h.replace(a, b)
        h = h.replace("Ses créations chez Qosmi", "Haar creaties bij Qosmi" if elle else "Zijn creaties bij Qosmi")
        h = h.replace("Son parcours", "Haar verhaal" if elle else "Zijn verhaal")
        out.append(h)
    return out


P = {}
P["02-conseil-hiver"] = nl(conseil("Je parfum<br>in de winter:<br>4 tips", [
    ("Kies warme noten", "Vanille, amber, specerijen, hout: de zwaardere basisnoten houden beter stand in de kou."),
    ("Hydrateer je huid", "Kou droogt de huid uit, en een droge huid houdt parfum minder goed vast. Eerst een ongeparfumeerde crème, en dat maakt het verschil."),
    ("Bescherm je flacon", "Laat je flacon niet achter in een ijskoude auto: grote temperatuurverschillen beschadigen het parfum."),
    ("Doseer licht binnen", "In een goed verwarmde ruimte verspreidt parfum zich sterker. Twee verstuivingen zijn genoeg.")],
    "Jouw<br>winterparfum?", "Vertel het ons<br>in de reacties."))
P["04-sel-elle"] = nl(selection("3 cadeaus<br>voor haar", [
    ("myway", "Giorgio Armani", "My Way", "Bergamot, oranjebloesem, tuberoos, vanille", "Een stralend en zacht boeket witte bloemen.", "Eau de parfum · 2020"),
    ("organza", "Givenchy", "Organza", "Neroli, jasmijn, ylang-ylang, vanille", "Een flacon in de vorm van een gedrapeerd silhouet.", "1996 · Sophie Labbé"),
    ("chance", "Chanel", "Chance", "Roze peper, jasmijn, patchoeli, vanille", "De ronde flacon van Chanel, een veilige keuze om te geven.", "Eau de parfum · Jacques Polge")],
    "Onder de<br>kerstboom?", "Zeg welke<br>in de reacties.", sur="Kerstspecial"))
P["06-mat-tonka"] = nl(matiere("De tonkaboon", "Amandel, hooi, karamel", "tonka", "50% 55%", "Wat is een tonkaboon?",
    "Het zaad van een grote boom uit Zuid-Amerika. Gedroogd en daarna in rum geweekt, raakt het bedekt met kleine kristallen coumarine.",
    "Die coumarine geeft haar geur: amandelachtig, met noten van hooi en karamel.",
    "Jicky van Guerlain, in 1889, was een van de allereerste parfums die haar gebruikten.",
    [("khamrah", "Lattafa", "Khamrah"), ("lveb", "Lancôme", "La Vie est Belle")]))
P["08-anniv-eausauvage"] = nl(anniv("60", "eausauvage", "Dior · 1966 – 2026", "Eau<br>Sauvage", "Citroen, bergamot, basilicum, vetiver", "Edmond Roudnitska"))
P["10-pdj-fahrenheit"] = nl(pdj("fahrenheit", "Dior · 1988", "Fahrenheit", "Mandarijn, viooltjesblad, leer, berk", "Jean-Louis Sieuzac", taille=110))
P["12-conseil-superposer"] = nl(conseil("Twee parfums<br>combineren:<br>zo doe<br>je het", [
    ("Begin eenvoudig", "Twee parfums, niet meer: één als basis, één om het op te fleuren."),
    ("Het rijkste eerst", "Verstuif eerst het warmste (houtig, vanille), daarna het lichtste erover."),
    ("Zoek een gemeenschappelijke noot", "Een gedeelde noot, zoals vanille of citrus, helpt beide parfums bij elkaar te passen."),
    ("Test voor je vertrekt", "Probeer je duo op een rustige dag, en wacht een uur om te zien hoe het evolueert.")],
    "Jouw favoriete<br>duo?", "Vertel ons je combinatie<br>in de reacties."))
P["14-bio-ellena"] = nl(bio("Jean-Claude<br>Ellena", "f149-jean-claude-ellena", "Parfumeur · geboren in Grasse",
    ["Als zoon van een parfumeur begint hij op zijn 16e bij Chiris in Grasse, en in 1968 gaat hij naar de parfumschool van Givaudan in Genève.",
     "Op zijn 28e tekent hij First voor Van Cleef & Arpels. In 2004 wordt hij de huisparfumeur van Hermès.",
     "Hij schrijft korte formules: ongeveer 200 grondstoffen, waar velen er meer dan duizend gebruiken."],
    ("« Mijn vak is je iets laten geloven met heel weinig middelen. »", "Jean-Claude Ellena"),
    [("terre", "Terre d'Hermès", "Hermès · 2006"), ("jardintoit", "Un Jardin sur le Toit", "Hermès · 2011"), ("jourabsolu", "Jour d'Hermès Absolu", "Hermès · 2014")]))
P["16-sel-reveillon"] = nl(selection("3 parfums<br>voor oudjaar", [
    ("nuittresor", "Lancôme", "La Nuit Trésor", "Roos, passievrucht, vanille, koffie", "De nachtelijke, zoetere kant van Trésor.", "Eau de parfum · 2015"),
    ("onemillion", "Paco Rabanne", "1 Million", "Mandarijn, kaneel, roos, leer", "Een flacon in de vorm van een goudstaaf, om te schitteren om middernacht.", "2008"),
    ("interdit", "Givenchy", "L'Interdit", "Bergamot, oranjebloesem, tuberoos, patchoeli", "De terugkeer, in 2018, van een parfum gemaakt voor Audrey Hepburn.", "Eau de parfum · 2018")],
    "Klaar voor<br>middernacht?", "Welke draag jij<br>vanavond?", sur="Oudejaarsspecial"))
P["18-pdj-neroli"] = nl(pdj("neroli", "Tom Ford · 2007", "Neroli Portofino", "Bergamot, neroli, oranjebloesem, amber", "Rodrigo Flores-Roux", taille=96))
P["20-mat-patchouli"] = nl(matiere("Patchoeli", "Aarde, hout en kamfer", "patchouli", "50% 45%", "Waar komt patchoeli vandaan?",
    "Een tropische plant, vooral geteeld in Indonesië. De verse bladeren ruiken bijna nergens naar: pas door drogen en distilleren komt de geur vrij.",
    "Aards, houtig, licht kamferachtig. Het helpt ook om andere noten vast te houden en het parfum langer te laten duren.",
    "In de jaren 90 maakte Angel van Thierry Mugler het weer populair.",
    [("prn", "Guerlain", "La Petite Robe Noire"), ("nuittresor", "Lancôme", "La Nuit Trésor")]))
P["22-pdj-bloom"] = nl(pdj("bloom", "Gucci · 2017", "Bloom", "Tuberoos, jasmijn, iris", "Alberto Morillas"))
P["24-conseil-pyramide"] = nl(conseil("Top, hart,<br>basis:<br>zo lees je<br>een parfum", [
    ("De topnoten", "De eerste minuten. Vaak citrus of frisse noten, die snel verdampen."),
    ("De hartnoten", "Die nemen het over en geven het parfum zijn karakter: bloemen, specerijen, fruit."),
    ("De basisnoten", "Die blijven urenlang op de huid: hout, vanille, musk, amber."),
    ("De goede reflex", "Beoordeel een parfum nooit op de eerste seconden. Wacht op het hart.")],
    "Jouw beurt", "Welke noot ruik jij<br>eerst in jouw<br>parfum?"))
P["26-mat-cannelle"] = nl(matiere("Kaneel", "De oudste specerij", "cannelle", "50% 55%", "Waar komt kaneel vandaan?",
    "De binnenste schors van de kaneelboom, oorspronkelijk uit tropisch Azië. Vandaag komt ze vooral uit Sri Lanka, de Seychellen en Madagaskar.",
    "Warm, zoet en kruidig: kaneel verwarmt amberachtige en houtige parfums.",
    "In de oudheid gebruikte men kaneel al om te balsemen.",
    [("onemillion", "Paco Rabanne", "1 Million"), ("bossedp", "Hugo Boss", "Boss Bottled")]))
P["28-conseil-doser"] = nl(conseil("Hoeveel keer<br>verstuiven?", [
    ("Eau de toilette", "Meestal 3 of 4 keer. Ze is lichter en verdampt sneller."),
    ("Eau de parfum", "2 of 3 keer is genoeg."),
    ("Extrait", "1 of 2 keer, of een paar toetsjes met je vingertoppen."),
    ("Denk aan de anderen", "Op kantoor of op restaurant ruik je je parfum van dichtbij, niet op drie meter.")],
    "En jij?", "Hoeveel pschitt<br>'s ochtends?"))
P["30-sel-valentin"] = nl(selection("Valentijn<br>is binnen<br>een maand", [
    ("prn", "Guerlain", "La Petite Robe Noire", "Kers, amandel, roos, zoethout", "Zoet en zelfzeker.", "2012 · Thierry Wasser"),
    ("spicebomb", "Viktor&Rolf", "Spicebomb", "Grapefruit, saffraan, chili, kaneel", "Voor hem, als hij van verwarmende parfums houdt.", "2012 · Olivier Polge"),
    ("kenzoworld", "Kenzo", "Kenzo World", "Pioen, jasmijn, Ambroxan", "Een flacon in de vorm van een oog die je niet vergeet.", "2016 · Francis Kurkdjian")],
    "Al aan het<br>voorbereiden?", "Al onze ideeën<br>op qosmi.be.", fin_droite="qosmi.be", sur="Valentijn", taille_titre=88))

if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for nom, slides in P.items():
            for f in os.listdir(OUT2):
                if f.startswith(nom + "-") and f.endswith(".jpg"):
                    os.remove(os.path.join(OUT2, f))
            for k, h in enumerate(slides, 1):
                f = os.path.join(OUT2, "%s-%d.html" % (nom, k))
                open(f, "w").write(h)
                pg.goto("file://" + f)
                pg.wait_for_timeout(200)
                pg.screenshot(path=os.path.join(OUT2, "%s-%d.jpg" % (nom, k)), type="jpeg", quality=93)
                os.remove(f)
        b.close()
    print("ok", sum(len(v) for v in P.values()), "visuels NL")
