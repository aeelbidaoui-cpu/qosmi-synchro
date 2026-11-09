"""Qosmi — lot n°2 (30 publications, 16/12/2026 → 14/01/2027). Mêmes gabarits que le lot 1. Rendu 1080×1350 dans out3/."""
import os, html
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(ICI, "visuels_lot1.py")).read().split("# ---------- le lot ----------")[0].replace('OUT2 = os.path.join(ICI, "out2")', 'OUT2 = os.path.join(ICI, "out3")'))
e = html.escape


def mimi(couleur="#ffffff", taille=300):
    """Mimi, la mascotte Qosmi (même trait que la page 404), ici souriante."""
    return f"""<svg viewBox="0 0 64 64" width="{taille}" height="{taille}" style="display:block">
  <g transform="translate(12,7)" fill="none" stroke="{couleur}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="20" cy="8" r="6"/><rect x="15" y="14" width="10" height="5" rx="1.5"/><rect x="5" y="19" width="30" height="27" rx="10"/>
    <circle cx="14" cy="30" r="1.6" fill="{couleur}"/><circle cx="26" cy="30" r="1.6" fill="{couleur}"/>
    <path d="M15 36 q5 5 10 0"/>
  </g></svg>"""


def fete(sur, titre_html, texte_html, droite):
    etoiles = "".join(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{s}px;height:{s}px;border-radius:50%;background:#ffffff;opacity:{o}"></div>'
                      for x, y, s, o in [(140, 260, 6, .7), (860, 210, 8, .9), (930, 520, 5, .6), (210, 610, 7, .8), (760, 700, 5, .5), (120, 900, 5, .6), (900, 860, 7, .8)])
    return [page(f"""
{etoiles}
<div class="haut" style="position:relative"><span>{sur}</span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0;position:relative;display:flex;flex-direction:column;align-items:center;text-align:center">
  {mimi()}
  <div class="t" style="font-size:120px;margin-top:40px">{titre_html}</div>
  <div class="notes" style="font-size:38px;margin-top:30px;line-height:1.45">{texte_html}</div>
</div>
<div style="position:relative;display:flex;justify-content:space-between;align-items:flex-end"><span class="sur" style="color:#bdbdbd">qosmi.be</span><span class="sur" style="color:#bdbdbd">{droite}</span></div>""",
                 fond=NOIR, couleur="#ffffff")]


P = {}
P["01-sel-lui"] = selection("3 cadeaux<br>de dernière<br>minute<br>pour lui", [
    ("spicebomb", "Viktor&Rolf", "Spicebomb", "Pamplemousse, safran, piment, cannelle", "Un flacon en forme de grenade, pour un parfum épicé qui ne passe pas inaperçu.", "2012 · Olivier Polge"),
    ("gentleman", "Givenchy", "Gentleman", "Poivre noir, iris, patchouli, vanille", "L'élégance d'un costume bien coupé, avec une touche d'iris.", "Eau de parfum · 2018"),
    ("bossedp", "Hugo Boss", "Boss Bottled", "Poivre noir, pomme, cannelle, vétiver", "La version eau de parfum d'un classique né en 1998.", "2020 · Honorine Blanc")],
    "Lequel pour lui ?", "1, 2 ou 3<br>en commentaire.", sur="Spécial Noël", taille_titre=88)
P["02-conseil-hiver"] = conseil("Ton parfum<br>en hiver :<br>4 conseils", [
    ("Mise sur les notes chaudes", "Vanille, ambre, épices, bois : les notes de fond, plus lourdes, tiennent mieux quand il fait froid."),
    ("Hydrate ta peau", "Le froid l'assèche, et une peau sèche retient moins le parfum. Une crème sans parfum avant, et ça change tout."),
    ("Protège ton flacon", "Pas de flacon oublié dans une voiture glacée : les écarts de température abîment le parfum."),
    ("Dose léger à l'intérieur", "Dans une pièce bien chauffée, le parfum diffuse davantage. Deux pulvérisations suffisent.")],
    "Ton parfum<br>d'hiver ?", "Dis-nous lequel<br>en commentaire.")
P["03-pdj-prn"] = pdj("prn", "Guerlain · 2012", "La Petite Robe Noire", "Cerise, amande, rose, réglisse", "Thierry Wasser", taille=88)
P["04-sel-elle"] = selection("3 cadeaux<br>pour elle", [
    ("myway", "Giorgio Armani", "My Way", "Bergamote, fleur d'oranger, tubéreuse, vanille", "Un bouquet de fleurs blanches, lumineux et doux.", "Eau de parfum · 2020"),
    ("organza", "Givenchy", "Organza", "Néroli, jasmin, ylang-ylang, vanille", "Un flacon en forme de silhouette drapée.", "1996 · Sophie Labbé"),
    ("chance", "Chanel", "Chance", "Baies roses, jasmin, patchouli, vanille", "Le flacon rond de Chanel, une valeur sûre à offrir.", "Eau de parfum · Jacques Polge")],
    "Sous le sapin ?", "Dis-nous lequel<br>en commentaire.", sur="Spécial Noël")
P["05-bio-ropion"] = bio("Dominique<br>Ropion", "f121-dominique-ropion", "Parfumeur",
    ["Sa mère et son grand-père travaillaient chez Roure, une maison de matières premières. Adolescent, il y passe ses vacances à faire des pesées.",
     "À 15 ans, il y croise déjà Jacques Polge et Jean-Louis Sieuzac. Il étudie la physique, puis travaille avec Sieuzac de 1989 à 1998.",
     "Il entre chez IFF en 2001. On lui doit Ysatis, Amarige, Alien, et une partie de L'Interdit et d'Invictus."],
    ("« Une formule, ça se triture dans tous les sens. »", "Dominique Ropion"),
    [("ysatis", "Ysatis", "Givenchy · 1984"), ("amarige", "Amarige", "Givenchy · 1991"), ("interdit", "L'Interdit", "Givenchy · 2018")])
P["06-mat-tonka"] = matiere("La fève tonka", "Amande, foin, caramel", "tonka", "50% 55%", "Qu'est-ce que la fève tonka ?",
    "La graine d'un grand arbre d'Amérique du Sud. Séchée, puis macérée dans du rhum, elle se couvre de petits cristaux de coumarine.",
    "C'est la coumarine qui lui donne son odeur : amandée, avec des notes de foin et de caramel.",
    "Jicky de Guerlain, en 1889, a été l'un des tout premiers parfums à l'utiliser.",
    [("khamrah", "Lattafa", "Khamrah"), ("lveb", "Lancôme", "La Vie est Belle")])
P["07-sel-fraiches"] = selection("3 parfums<br>frais<br>à offrir", [
    ("orangeverte", "Hermès", "Eau d'Orange Verte", "Orange, mandarine, menthe, mousse de chêne", "Une eau de Cologne pétillante, à partager.", "1979 · Françoise Caron"),
    ("voyage", "Hermès", "Voyage d'Hermès", "Citron, thé, cardamome, muscs blancs", "Un flacon qui pivote, comme un objet de voyage.", "2010 · Jean-Claude Ellena"),
    ("lagune", "Hermès", "Un Jardin sur la Lagune", "Magnolia, pittosporum, lys, notes salées", "Inspiré d'un jardin secret de Venise.", "2019 · Christine Nagel")],
    "Ton préféré ?", "1, 2 ou 3<br>en commentaire.", sur="Spécial Noël")
P["08-anniv-eausauvage"] = anniv("60", "eausauvage", "Dior · 1966 – 2026", "Eau<br>Sauvage", "Citron, bergamote, basilic, vétiver", "Edmond Roudnitska")
P["09-fete-noel"] = fete("Joyeux Noël", "Joyeux<br>Noël", "Toute l'équipe Qosmi<br>te souhaite de belles fêtes.", "24 · 12")
P["10-pdj-fahrenheit"] = pdj("fahrenheit", "Dior · 1988", "Fahrenheit", "Mandarine, feuille de violette, cuir, bouleau", "Jean-Louis Sieuzac", taille=110)
P["11-anniv-lightblue"] = anniv("25", "lightbluef", "Dolce&Gabbana · 2001 – 2026", "Light Blue", "Citron de Sicile, pomme, bambou, cèdre", "Olivier Cresp")
P["12-conseil-superposer"] = conseil("Superposer<br>deux parfums :<br>le mode<br>d'emploi", [
    ("Commence simple", "Deux parfums, pas plus : un pour la base, un pour la relever."),
    ("Le plus riche d'abord", "Vaporise d'abord le plus chaud (boisé, vanillé), puis le plus léger par-dessus."),
    ("Cherche un point commun", "Une note partagée, comme la vanille ou les agrumes, aide les deux parfums à s'accorder."),
    ("Teste avant de sortir", "Essaie ton duo un jour calme, et attends une heure pour voir comment il évolue.")],
    "Ton duo<br>préféré ?", "Dis-nous ton mélange<br>en commentaire.")
P["13-mat-iris"] = matiere("L'iris", "La fleur qui sent par sa racine", "iris", "50% 50%", "D'où vient l'iris ?",
    "En parfumerie, on n'utilise pas la fleur mais le rhizome, la tige souterraine. Il sèche environ trois ans avant d'être distillé.",
    "Une tonne d'iris ne donne que deux kilos d'huile essentielle. C'est l'une des matières les plus chères : poudrée, beurrée, boisée.",
    "L'iris des marais, jaune, est le symbole de Bruxelles.",
    [("gentleman", "Givenchy", "Gentleman"), ("bloom", "Gucci", "Bloom")])
P["14-bio-ellena"] = bio("Jean-Claude<br>Ellena", "f149-jean-claude-ellena", "Parfumeur · né à Grasse",
    ["Fils de parfumeur, il commence à 16 ans chez Chiris, à Grasse, puis entre à l'école de parfumerie Givaudan, à Genève, en 1968.",
     "À 28 ans, il signe First pour Van Cleef & Arpels. En 2004, il devient le parfumeur exclusif d'Hermès.",
     "Il écrit des formules courtes : environ 200 matières premières, là où beaucoup en utilisent plus de mille."],
    ("Son métier « consiste à vous faire croire avec très peu de moyens ».", "Jean-Claude Ellena"),
    [("terre", "Terre d'Hermès", "Hermès · 2006"), ("jardintoit", "Un Jardin sur le Toit", "Hermès · 2011"), ("jourabsolu", "Jour d'Hermès Absolu", "Hermès · 2014")])
P["15-pdj-tuscan"] = pdj("tuscan", "Tom Ford · 2007", "Tuscan Leather", "Framboise, safran, jasmin, cuir", "Private Blend", taille=96)
P["16-sel-reveillon"] = selection("3 parfums<br>pour le<br>réveillon", [
    ("nuittresor", "Lancôme", "La Nuit Trésor", "Rose, fruit de la passion, vanille, café", "Le côté nuit de Trésor, plus gourmand.", "Eau de parfum · 2015"),
    ("onemillion", "Paco Rabanne", "1 Million", "Mandarine, cannelle, rose, cuir", "Un flacon en forme de lingot d'or, pour briller à minuit.", "2008"),
    ("interdit", "Givenchy", "L'Interdit", "Bergamote, fleur d'oranger, tubéreuse, patchouli", "Le retour, en 2018, d'un parfum créé pour Audrey Hepburn.", "Eau de parfum · 2018")],
    "Prêt pour<br>minuit ?", "Dis-nous lequel<br>tu portes ce soir.", sur="Spécial réveillon")
P["17-fete-annee"] = fete("Bonne année", "Bonne<br>année<br>2027", "Merci d'avoir été là en 2026.<br>On se retrouve demain.", "01 · 01")
P["18-pdj-neroli"] = pdj("neroli", "Tom Ford · 2007", "Neroli Portofino", "Bergamote, néroli, fleur d'oranger, ambre", "Rodrigo Flores-Roux", taille=96)
P["19-conseil-familles"] = conseil("Les grandes<br>familles<br>olfactives", [
    ("Hespéridée", "Les agrumes : citron, bergamote, orange. Frais et pétillant."),
    ("Florale", "Rose, jasmin, tubéreuse… La famille la plus vaste."),
    ("Boisée", "Cèdre, santal, vétiver. Sec ou crémeux, toujours élégant."),
    ("Ambrée", "On dit aussi orientale : vanille, épices, résines. Chaude et enveloppante."),
    ("Chyprée", "Bergamote, mousse de chêne, patchouli. Son nom vient de Chypre, un parfum de Coty de 1917."),
    ("Fougère", "Lavande, coumarine, mousse de chêne. Le grand classique des parfums pour homme.")],
    "Et toi ?", "Tu es plutôt<br>quelle famille ?")
P["20-mat-patchouli"] = matiere("Le patchouli", "Terre, bois et camphre", "patchouli", "50% 45%", "D'où vient le patchouli ?",
    "Une plante tropicale cultivée surtout en Indonésie. Ses feuilles fraîches ne sentent presque rien : c'est le séchage puis la distillation qui révèlent son odeur.",
    "Terreuse, boisée, un peu camphrée. Il sert aussi à fixer les autres notes et à faire durer le parfum.",
    "Dans les années 1990, Angel de Thierry Mugler l'a remis à la mode.",
    [("prn", "Guerlain", "La Petite Robe Noire"), ("nuittresor", "Lancôme", "La Nuit Trésor")])
P["21-pdj-kenzoworld"] = pdj("kenzoworld", "Kenzo · 2016", "Kenzo World", "Pivoine, jasmin, Ambroxan", "Francis Kurkdjian", taille=110)
P["22-pdj-bloom"] = pdj("bloom", "Gucci · 2017", "Bloom", "Tubéreuse, jasmin, iris", "Alberto Morillas")
P["23-bio-nagel"] = bio("Christine<br>Nagel", "f146-christine-nagel", "Parfumeur · née en 1959 à Genève",
    ["Chimiste de formation, elle commence chez Firmenich, au service chromatographie : elle analyse les parfums, molécule par molécule.",
     "Alberto Morillas lui fait sentir ses accords. Elle décide de devenir parfumeur, et signe ensuite The One de Dolce&Gabbana ou Miss Dior Chérie.",
     "Elle entre chez Hermès en 2014 et dirige la création de ses parfums depuis 2016."],
    None,
    [("lagune", "Un Jardin sur la Lagune", "Hermès · 2019"), ("basilic", "Eau de Basilic Pourpre", "Hermès · 2022")])
P["24-conseil-pyramide"] = conseil("Tête, cœur,<br>fond :<br>comment se lit<br>un parfum", [
    ("Les notes de tête", "Les premières minutes. Souvent des agrumes ou des notes fraîches, qui s'évaporent vite."),
    ("Les notes de cœur", "Elles prennent le relais et donnent sa personnalité au parfum : fleurs, épices, fruits."),
    ("Les notes de fond", "Celles qui restent des heures sur la peau : bois, vanille, muscs, ambre."),
    ("Le bon réflexe", "Ne juge jamais un parfum sur les premières secondes. Attends son cœur.")],
    "À toi", "Quelle note sens-tu<br>en premier sur<br>ton parfum ?")
P["25-pdj-habitrouge"] = pdj("habitrouge", "Guerlain · 1965", "Habit Rouge", "Lavande, néroli, rose, vanille", "Jean-Paul Guerlain", taille=110)
P["26-mat-cannelle"] = matiere("La cannelle", "La plus ancienne des épices", "cannelle", "50% 55%", "D'où vient la cannelle ?",
    "L'écorce intérieure du cannelier, un arbre originaire d'Asie tropicale. Elle vient aujourd'hui surtout du Sri Lanka, des Seychelles et de Madagascar.",
    "Chaude, sucrée, épicée : elle réchauffe les parfums ambrés et boisés.",
    "Dans l'Antiquité, on s'en servait déjà pour embaumer.",
    [("onemillion", "Paco Rabanne", "1 Million"), ("bossedp", "Hugo Boss", "Boss Bottled")])
P["27-conseil-conserver"] = conseil("Combien<br>de temps se<br>garde un<br>parfum ?", [
    ("Fermé, très longtemps", "Bien rangé, un flacon jamais ouvert peut se garder des années."),
    ("Ouvert, quelques années", "Une fois entamé, il reste en général beau plusieurs années, s'il est bien conservé."),
    ("Ses trois ennemis", "La lumière, la chaleur et l'air. Garde-le dans sa boîte, dans un placard."),
    ("Les signes qui ne trompent pas", "Une couleur qui fonce, une odeur aigre ou métallique au début : il a tourné.")],
    "Fais le test", "Va sentir ton plus<br>vieux flacon.")
P["28-conseil-doser"] = conseil("Combien de<br>pulvérisations ?", [
    ("Eau de toilette", "En général 3 ou 4. Elle est plus légère et s'évapore plus vite."),
    ("Eau de parfum", "2 ou 3 suffisent."),
    ("Extrait", "1 ou 2, ou quelques touches du bout des doigts."),
    ("Pense aux autres", "Au bureau ou au restaurant, ton parfum doit se sentir de près, pas à trois mètres.")],
    "Et toi ?", "Combien de pschitt<br>le matin ?")
P["29-pdj-invictus"] = pdj("invictus", "Paco Rabanne · 2013", "Invictus", "Pamplemousse, note marine, gaïac, patchouli", "Eau de toilette")
P["30-sel-valentin"] = selection("La Saint-<br>Valentin,<br>c'est dans<br>un mois", [
    ("prn", "Guerlain", "La Petite Robe Noire", "Cerise, amande, rose, réglisse", "Gourmande, et sûre d'elle.", "2012 · Thierry Wasser"),
    ("spicebomb", "Viktor&Rolf", "Spicebomb", "Pamplemousse, safran, piment, cannelle", "Pour lui, s'il aime les parfums qui réchauffent.", "2012 · Olivier Polge"),
    ("kenzoworld", "Kenzo", "Kenzo World", "Pivoine, jasmin, Ambroxan", "Un flacon en forme d'œil, impossible à oublier.", "2016 · Francis Kurkdjian")],
    "Tu prépares<br>déjà ?", "Toutes nos idées<br>sur qosmi.be.", fin_droite="qosmi.be", sur="Saint-Valentin", taille_titre=88)

if __name__ == "__main__":
    import sys
    seuls = sys.argv[1:]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for nom, slides in P.items():
            if seuls and not any(s in nom for s in seuls):
                continue
            for k, h in enumerate(slides, 1):
                f = os.path.join(OUT2, "%s-%d.html" % (nom, k))
                open(f, "w").write(h)
                pg.goto("file://" + f)
                pg.wait_for_timeout(200)
                pg.screenshot(path=os.path.join(OUT2, "%s-%d.jpg" % (nom, k)), type="jpeg", quality=93)
                os.remove(f)
        b.close()
    print("ok", sum(len(v) for v in P.values()), "visuels")
