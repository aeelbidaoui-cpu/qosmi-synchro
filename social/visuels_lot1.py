"""Qosmi — lot n°1 (30 publications, 16/11 → 15/12/2026) : les 25 nouvelles publications.
Réutilise le style de gen.py (mêmes fonctions de page). Rendu 1080×1350 dans out2/."""
import os, html, json
from PIL import Image
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(ICI, "gen.py")).read().split("S = {}")[0])  # BASE, page(), flacon(), points(), bas(), couleurs
OUT2 = os.path.join(ICI, "out2")
os.makedirs(OUT2, exist_ok=True)
MAT = "file://" + ICI + "/mat/%s.jpg"
POR = "file://" + ICI + "/por/%s.jpg"
e = html.escape


def ratio(f):
    w, h = Image.open(os.path.join(ICI, "fl", f + ".png")).size
    return w / h


def hauteur(f, hmax, lmax):
    """Hauteur d'affichage pour qu'un flacon tienne dans hmax × lmax."""
    return int(min(hmax, lmax / ratio(f)))


def rangee(fls, bas_px, hmax=470, lmax=290):
    xs = {1: ["50%"], 2: ["32%", "68%"], 3: ["20%", "50%", "80%"]}[len(fls)]
    return "".join(flacon(f, hauteur(f, hmax, lmax), bas_px, x) for f, x in zip(fls, xs))


def pied(n, i, droite):
    return f'<div style="position:relative;display:flex;justify-content:space-between;align-items:center">{points(n, i)}<span class="sur">{droite}</span></div>'


# ---------- gabarits ----------
def pdj(f, marque_annee, nom, notes, droite, taille=132):
    return [page(f"""
<div class="haut"><span>Le parfum du jour</span><span class="logo">QOSMI</span></div>
{flacon(f, hauteur(f, 700, 640), 430)}
<div style="margin-top:auto;position:relative">
  <div class="sur">{marque_annee}</div>
  <div class="t" style="font-size:{taille}px;margin:14px 0 22px">{e(nom)}</div>
  <div class="notes">{notes}</div>
  <div style="height:34px"></div>
  {bas('qosmi.be', droite)}
</div>""")]


def anniv(num, f, marque_annees, nom_html, notes, droite):
    return [page(f"""
<div class="haut"><span>Joyeux anniversaire</span><span class="logo">QOSMI</span></div>
<div style="position:relative;margin-top:40px">
  <div style="font-size:330px;font-weight:300;line-height:.86;letter-spacing:-.03em">{num}</div>
  <div class="t" style="font-size:54px;margin-top:4px">ans</div>
</div>
{flacon(f, hauteur(f, 600, 420), 560, '70%')}
<div style="margin-top:auto;position:relative">
  <div class="sur">{marque_annees}</div>
  <div class="t" style="font-size:96px;margin:12px 0 18px">{nom_html}</div>
  <div class="notes">{notes}</div>
  <div style="height:30px"></div>
  {bas('qosmi.be', droite)}
</div>""", fond="#ffffff")]


def selection(titre_html, items, fin_titre, fin_texte, fin_droite="Les trois sur qosmi.be", sur="La sélection", taille_titre=96):
    n = len(items) + 2
    sl = [page(f"""
<div class="haut"><span class="sur" style="color:inherit">{sur}</span><span class="logo">QOSMI</span></div>
<div class="t" style="font-size:{taille_titre}px;margin-top:70px;position:relative">{titre_html}</div>
{rangee([i[0] for i in items], 190)}
<div style="margin-top:auto;position:relative;display:flex;justify-content:space-between;align-items:center">{points(n, 0)}<span class="sur">Glisse →</span></div>""")]
    for k, (f, marque, nom, notes, phrase, info) in enumerate(items, 1):
        taille = 96 if len(nom) <= 14 else 78 if len(nom) <= 20 else 64
        sl.append(page(f"""
<div class="haut"><span class="num">0{k}</span><span class="logo">QOSMI</span></div>
{flacon(f, hauteur(f, 620, 600), 480)}
<div style="margin-top:auto;position:relative">
  <div class="sur">{marque}</div>
  <div class="t" style="font-size:{taille}px;margin:12px 0 18px">{e(nom)}</div>
  <div class="notes" style="font-weight:400">{notes}</div>
  <div class="notes" style="font-size:27px;color:{DOUX};margin-top:12px;line-height:1.35">{e(phrase)}</div>
  <div style="height:30px"></div>
  <div style="display:flex;justify-content:space-between;align-items:center">{points(n, k)}<span class="sur" style="font-size:20px">{info}</span></div>
</div>"""))
    sl.append(page(f"""
<div class="haut"><span></span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0;position:relative">
  <div class="t" style="font-size:96px">{fin_titre}</div>
  <div class="notes" style="font-size:40px;margin-top:30px;line-height:1.4">{fin_texte}</div>
</div>
<div style="position:relative;display:flex;justify-content:space-between;align-items:flex-end">{points(n, n - 1)}<span class="sur">{fin_droite}</span></div>""",
                   fond=NOIR, couleur="#ffffff"))
    return sl


def conseil(titre_html, gestes, fin_titre, fin_texte, flacons_slide=None, couverture_fl=None):
    """flacons_slide = (position après le geste n°, titre, [(fichier, légende)])."""
    extra = 1 if flacons_slide else 0
    n = len(gestes) + 2 + extra
    cov_fl = rangee(couverture_fl, 120, 400, 260) if couverture_fl else ""
    sl = [page(f"""
<div class="haut"><span class="sur" style="color:inherit">Le conseil</span><span class="logo">QOSMI</span></div>
<div style="{'margin-top:70px' if couverture_fl else 'margin:auto 0'};position:relative">
  <div class="t" style="font-size:92px">{titre_html}</div>
</div>
{cov_fl}
<div style="margin-top:auto;position:relative;display:flex;justify-content:space-between;align-items:center">{points(n, 0)}<span class="sur">Glisse →</span></div>""", fond="#ffffff")]
    idx = 1
    for i, (titre, texte) in enumerate(gestes, 1):
        sl.append(page(f"""
<div class="haut"><span></span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0">
  <div style="font-size:300px;font-weight:300;line-height:.9;letter-spacing:-.02em">0{i}</div>
  <div class="t" style="font-size:72px;margin:46px 0 30px">{e(titre)}</div>
  <div class="notes" style="font-size:38px;line-height:1.42;max-width:880px">{e(texte)}</div>
</div>
<div style="display:flex;justify-content:space-between;align-items:center">{points(n, idx)}<span class="sur">Le conseil Qosmi</span></div>""",
                       fond="#ffffff" if i % 2 else GRIS))
        idx += 1
        if flacons_slide and flacons_slide[0] == i:
            _, t, fls = flacons_slide
            xs = {2: ["30%", "70%"], 3: ["19%", "50%", "81%"]}[len(fls)]
            etiq = "".join(f'<div style="position:absolute;left:{x};transform:translateX(-50%);bottom:250px;width:300px;text-align:center"><div class="sur" style="color:{NOIR};font-size:22px;line-height:1.4">{lab}</div></div>' for (f, lab), x in zip(fls, xs))
            sl.append(page(f"""
<div class="haut"><span class="sur" style="color:inherit">{t}</span><span class="logo">QOSMI</span></div>
{''.join(flacon(f, hauteur(f, 520, 270), 380, x) for (f, _), x in zip(fls, xs))}
{etiq}
<div style="margin-top:auto">{pied(n, idx, 'Le conseil Qosmi')}</div>"""))
            idx += 1
    sl.append(page(f"""
<div class="haut"><span></span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0">
  <div class="t" style="font-size:92px">{fin_titre}</div>
  <div class="notes" style="font-size:40px;margin-top:30px;line-height:1.4">{fin_texte}</div>
</div>
<div style="display:flex;justify-content:space-between;align-items:flex-end">{points(n, n - 1)}<span class="sur">qosmi.be</span></div>""",
                   fond=NOIR, couleur="#ffffff"))
    return sl


def matiere(nom, accroche, img, pos, question, texte1, texte2, savoir, fls):
    n = 3
    s1 = page(f"""
<img src="{MAT % img}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:{pos}">
<div class="haut" style="position:relative"><span>Matière première</span><span class="logo">QOSMI</span></div>
<div style="position:relative;margin-top:60px">
  <div class="t" style="font-size:{170 if len(nom) <= 8 else 132}px">{e(nom)}</div>
  <div class="sur" style="color:{NOIR};margin-top:18px">{accroche}</div>
</div>
<div style="margin-top:auto;position:relative;display:flex;justify-content:space-between;align-items:center">{points(n, 0)}<span class="sur" style="color:{NOIR}">Glisse →</span></div>""")
    s2 = page(f"""
<div class="haut"><span class="sur" style="color:inherit">{question}</span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0">
  <div class="notes" style="font-size:46px;line-height:1.36;font-weight:400">{e(texte1)}</div>
  <div class="notes" style="font-size:34px;margin-top:40px;line-height:1.45;color:{DOUX}">{e(texte2)}</div>
  <div style="margin-top:56px;padding-top:30px;border-top:1px solid #d9d9d9">
    <div class="sur">Le saviez-vous</div>
    <div class="notes" style="font-size:36px;margin-top:12px;line-height:1.4">{e(savoir)}</div>
  </div>
</div>
<div style="display:flex;justify-content:space-between;align-items:center">{points(n, 1)}<span class="sur">Matière première</span></div>""", fond="#ffffff")
    xs = ["30%", "70%"] if len(fls) == 2 else ["50%"]
    etiq = "".join(f'<div style="position:absolute;left:{x};transform:translateX(-50%);bottom:250px;width:380px;text-align:center"><div class="sur" style="font-size:20px">{m}</div><div style="font-size:30px;font-weight:500;letter-spacing:.04em;text-transform:uppercase;margin-top:8px">{e(nm)}</div></div>' for (f, m, nm), x in zip(fls, xs))
    s3 = page(f"""
<div class="haut"><span class="sur" style="color:inherit">À sentir</span><span class="logo">QOSMI</span></div>
<div class="t" style="font-size:64px;margin-top:50px;position:relative">{e(nom)} dans le flacon</div>
{''.join(flacon(f, hauteur(f, 560, 360), 400, x) for (f, _, _), x in zip(fls, xs))}
{etiq}
<div style="margin-top:auto">{pied(n, 2, 'qosmi.be')}</div>""")
    return [s1, s2, s3]


def bio(nom_html, portrait, sous, parcours, citation, creations):
    n = 3
    s1 = page(f"""
<img src="{POR % portrait}" style="position:absolute;left:0;right:0;top:150px;width:100%;height:760px;object-fit:cover;object-position:50% 25%;filter:grayscale(1)">
<div class="haut" style="position:relative"><span>Le parfumeur</span><span class="logo">QOSMI</span></div>
<div style="margin-top:auto;position:relative">
  <div class="sur">{sous}</div>
  <div class="t" style="font-size:104px;margin:14px 0 26px">{nom_html}</div>
  {pied(n, 0, 'Glisse →')}
</div>""", fond="#ffffff")
    cit = f'<div style="margin-top:56px;padding-top:30px;border-top:1px solid #d9d9d9"><div class="notes" style="font-size:36px;line-height:1.4;font-style:italic">{e(citation[0])}</div><div class="sur" style="margin-top:14px">{citation[1]}</div></div>' if citation else ""
    s2 = page(f"""
<div class="haut"><span class="sur" style="color:inherit">Son parcours</span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0">
  {''.join(f'<div class="notes" style="font-size:40px;line-height:1.4;margin-bottom:28px;{"font-weight:400" if i == 0 else ""}">{e(p)}</div>' for i, p in enumerate(parcours))}
  {cit}
</div>
{pied(n, 1, 'Le parfumeur')}""", fond="#ffffff")
    xs = {2: ["30%", "70%"], 3: ["19%", "50%", "81%"]}[len(creations)]
    etiq = "".join(f'<div style="position:absolute;left:{x};transform:translateX(-50%);bottom:250px;width:320px;text-align:center"><div style="font-size:28px;font-weight:500;letter-spacing:.04em;text-transform:uppercase;line-height:1.15">{e(nm)}</div><div class="sur" style="font-size:19px;margin-top:8px">{info}</div></div>' for (f, nm, info), x in zip(creations, xs))
    s3 = page(f"""
<div class="haut"><span class="sur" style="color:inherit">Ses créations chez Qosmi</span><span class="logo">QOSMI</span></div>
{''.join(flacon(f, hauteur(f, 500, 280 if len(creations) == 3 else 360), 380, x) for (f, _, _), x in zip(creations, xs))}
{etiq}
<div style="margin-top:auto">{pied(n, 2, 'qosmi.be')}</div>""")
    return [s1, s2, s3]


# ---------- le lot ----------
P = {}
P["06-pdj-jadore"] = pdj("jadore", "Dior · 1999", "J'adore", "Mandarine, rose, jasmin, muscs blancs", "Calice Becker")
P["07-bio-kurkdjian"] = bio("Francis<br>Kurkdjian", "f2361-francis-kurkdjian-parfumeur", "Parfumeur · Paris",
    ["Il décide de devenir parfumeur à 15 ans, sans rien connaître du métier.",
     "Il entre à l'ISIPCA, l'école de parfumerie de Versailles, en 1990. Cinq ans plus tard, il signe Le Male pour Jean Paul Gaultier.",
     "En 2009, il ouvre sa propre maison."],
    ("« L'ingrédient ne m'intéresse pas. Ce qui compte pour moi, c'est l'émotion du résultat. »", "Francis Kurkdjian"),
    [("lemale", "Le Male", "Jean Paul Gaultier · 1995"), ("aquauni", "Aqua Universalis Cologne Forte", "MFK · 2021"), ("gfgold", "Gentle Fluidity Gold", "MFK · 2019")])
P["08-sel-noel-elle"] = selection("3 cadeaux<br>pour elle", [
    ("libre", "Yves Saint Laurent", "Libre", "Lavande, fleur d'oranger, vanille", "Élégant, sans jamais être sage.", "Eau de parfum"),
    ("lveb", "Lancôme", "La Vie est Belle", "Poire, iris, praline, vanille", "Le gourmand qu'on ne présente plus.", "2012"),
    ("flowerbomb", "Viktor&Rolf", "Flowerbomb", "Thé, jasmin, orchidée, rose, patchouli", "Le tout premier parfum de la maison, en forme de grenade.", "2005")],
    "Sous le sapin ?", "Dis-nous lequel<br>en commentaire.", sur="Spécial Noël")
P["09-mat-vanille"] = matiere("La vanille", "Le fruit d'une orchidée", "vanille", "50% 50%", "D'où vient la vanille ?",
    "Le fruit d'une orchidée. Originaire du Mexique, elle pousse aujourd'hui surtout à Madagascar et à La Réunion.",
    "Sa gousse réunit des centaines de molécules odorantes. Sucrée, grasse, un peu épicée.",
    "Shalimar de Guerlain, en 1925, l'a rendue incontournable en parfumerie.",
    [("shalimar", "Guerlain", "Shalimar"), ("yara", "Lattafa", "Yara")])
P["10-conseil-offrir"] = conseil("4 conseils<br>pour offrir<br>un parfum sans<br>te tromper", [
    ("Regarde ce qu'il porte déjà", "Le flacon dans la salle de bain en dit long. Note le nom, et cherche dans la même famille."),
    ("Pense à ses goûts", "Plutôt desserts et café ? Pense gourmand. Plutôt nature et grand air ? Pense frais ou boisé."),
    ("Mise sur un classique", "En cas de doute, un parfum que beaucoup aiment déjà reste un pari sûr."),
    ("Choisis la bonne taille", "Pour une première fois, un 30 ou 50 ml. S'il l'adore, le grand flacon suivra.")],
    "Besoin d'aide ?", "Envoie-nous un message,<br>on t'aide à choisir.",
    flacons_slide=(3, "Trois classiques", [("jadore", "J'adore<br>Dior"), ("bleu", "Bleu de Chanel<br>Chanel"), ("lveb", "La Vie est Belle<br>Lancôme")]),
    couverture_fl=["jadore", "bleu", "lveb"])
P["11-pdj-shalimar"] = pdj("shalimar", "Guerlain · 1925", "Shalimar", "Bergamote, iris, vanille, fève tonka", "Jacques Guerlain")
P["12-sel-noel-lui"] = selection("3 cadeaux<br>pour lui", [
    ("bleu", "Chanel", "Bleu de Chanel", "Agrumes, gingembre, santal", "Le premier grand masculin de Chanel depuis Égoïste.", "2010 · Jacques Polge"),
    ("sauvage", "Dior", "Sauvage Parfum", "Mandarine, bergamote, santal, vanille", "La version concentrée de Sauvage, plus chaude.", "2019 · François Demachy"),
    ("aventus", "Creed", "Aventus", "Ananas, bouleau, mousse de chêne", "La maison dit s'être inspirée de Napoléon.", "2010")],
    "Ton choix ?", "1, 2 ou 3<br>en commentaire.", sur="Spécial Noël")
P["13-anniv-terre"] = anniv("20", "terre", "Hermès · 2006 – 2026", "Terre<br>d'Hermès", "Pamplemousse, silex, poivre, cèdre", "Jean-Claude Ellena")
P["14-bio-bisch"] = bio("Quentin<br>Bisch", "f166-quentin-bisch", "Parfumeur · né en 1983 à Strasbourg",
    ["À 11 ans, il annonce à un professeur qu'il sera parfumeur.",
     "Trop faible en sciences pour les écoles de parfumerie, il fait un master en arts du spectacle, puis écrit aux grandes maisons.",
     "Assistant à Grasse, il est ensuite formé chez Givaudan."],
    ("Il se souvient encore du parfum de chacun de ses professeurs.", "Sa mémoire olfactive"),
    [("delina", "Delina", "Parfums de Marly · 2017"), ("valaya", "Valaya", "Parfums de Marly · 2023"), ("verygoodgirl", "Very Good Girl", "Carolina Herrera")])
P["15-conseil-concentrations"] = conseil("Eau de toilette,<br>eau de parfum,<br>extrait : quelle<br>différence ?", [
    ("Eau de toilette", "En général 5 à 15 % de concentré de parfum. Plus légère, plus fraîche."),
    ("Eau de parfum", "Autour de 15 à 20 %. Plus de tenue, un sillage plus présent."),
    ("Extrait", "20 % et plus. La version la plus riche, à poser par petites touches."),
    ("Attention", "Une même ligne peut sentir assez différemment d'une version à l'autre. Ce n'est pas toujours la même formule, plus concentrée.")],
    "Et toi ?", "Team eau de toilette<br>ou team extrait ?",
    flacons_slide=(3, "Les trois en vrai", [("lemale", "Le Male<br>Eau de toilette"), ("jadore", "J'adore<br>Eau de parfum"), ("hacivat", "Hacivat<br>Extrait")]))
P["16-pdj-9pm"] = pdj("ninepm", "Afnan · 2020", "9pm", "Lavande, pomme, cannelle, vanille", "Eau de parfum")
P["17-mat-rose"] = matiere("La rose", "La reine des fleurs", "rose", "50% 40%", "Quelles roses en parfumerie ?",
    "Deux grandes roses : la centifolia, ou rose de mai, cultivée en France et au Maroc, et la rose de Damas, en Bulgarie et en Turquie.",
    "Distillée, la rose de Damas donne une huile fraîche, presque citronnée. La centifolia donne une absolue plus chaude et miellée.",
    "On compose des parfums à la rose depuis l'Antiquité.",
    [("delina", "Parfums de Marly", "Delina"), ("coco", "Chanel", "Coco Mademoiselle")])
P["18-sel-mixtes"] = selection("3 parfums<br>à partager<br>à deux", [
    ("ckone", "Calvin Klein", "CK One", "Agrumes, thé vert, muscs", "Pensé pour elle et pour lui, dès 1994.", "1994 · Alberto Morillas"),
    ("colonia", "Acqua di Parma", "Colonia", "Agrumes, lavande, vétiver", "L'eau de Cologne qui a fondé la maison.", "1916"),
    ("redtob", "Mancera", "Red Tobacco", "Cannelle, safran, tabac, vanille", "Pour ceux qui aiment qu'on les remarque.", "2017")],
    "Vous partagez<br>lequel ?", "Dis-le nous<br>en commentaire.", sur="Spécial Noël")
P["19-pdj-hypnotic"] = pdj("hp", "Dior · 1998", "Hypnotic Poison", "Noix de coco, amande amère, vanille", "Annick Menardo", taille=104)
P["20-bio-polge"] = bio("Jacques<br>Polge", "f469-jacques-polge", "Parfumeur de Chanel de 1978 à 2015",
    ["Né en 1943 dans le Vaucluse.",
     "Après Givaudan Roure, il entre chez Chanel en 1978, où il succède à Henri Robert, le créateur du N°19 et de Cristalle.",
     "Son premier parfum pour la maison : Coco, en 1984. Suivront Allure, Coco Mademoiselle, Bleu de Chanel…"],
    None,
    [("coco", "Coco Mademoiselle", "Chanel · 2001"), ("bleu", "Bleu de Chanel", "Chanel · 2010")])
P["21-conseil-tester"] = conseil("Comment<br>bien tester<br>un parfum", [
    ("Commence par la mouillette", "Elle sert à faire un premier tri, sans saturer ta peau."),
    ("Puis passe à la peau", "Un parfum change au contact de ta peau. C'est là qu'il faut le juger."),
    ("Prends ton temps", "Les premières minutes ne montrent que les notes de tête. Attends au moins une heure avant de décider."),
    ("Trois maximum", "Au-delà, le nez sature et tout finit par sentir pareil."),
    ("Repose ton nez", "Entre deux essais, sens ton pull ou la peau de ton avant-bras.")],
    "Garde-le<br>pour plus tard", "Enregistre ce post<br>pour ta prochaine virée<br>en parfumerie.", couverture_fl=["erba", "hacivat", "aquauni"])
P["22-sel-arabes"] = selection("3 parfums<br>arabes<br>à offrir", [
    ("khamrah", "Lattafa", "Khamrah", "Cannelle, dattes, praline, vanille", "Chaud et gourmand, taillé pour l'hiver.", "2022"),
    ("yara", "Lattafa", "Yara", "Orchidée, fruits exotiques, vanille", "Doux et réconfortant. Il a lancé toute une ligne.", "2020"),
    ("asad", "Lattafa", "Asad", "Poivre noir, tabac, café, vanille", "Son nom veut dire « lion » en arabe.", "Eau de parfum")],
    "Ton préféré ?", "Toute notre sélection<br>de parfums arabes<br>est sur qosmi.be.", fin_droite="Parfums arabes", sur="Spécial Noël")
P["23-mat-santal"] = matiere("Le santal", "Le bois velouté", "santal", "50% 50%", "D'où vient le santal ?",
    "Un bois d'arbre originaire d'Asie, connu depuis 4 000 ans. L'Égypte ancienne l'utilisait déjà.",
    "Il vient aujourd'hui surtout d'Inde, mais aussi d'Australie ou du Sri Lanka. Devenu rare, il coûte de plus en plus cher.",
    "Peu puissant, mais d'une tenue remarquable : il donne du velouté à tout ce qu'il touche.",
    [("bleu", "Chanel", "Bleu de Chanel"), ("hp", "Dior", "Hypnotic Poison")])
P["24-pdj-hacivat"] = pdj("hacivat", "Nishane · 2017", "Hacivat", "Ananas, pamplemousse, patchouli, mousse de chêne", "Extrait de parfum")
P["25-anniv-goodgirl"] = anniv("10", "goodgirl", "Carolina Herrera · 2016 – 2026", "Good Girl", "Amande, café, tubéreuse, cacao", "Louise Turner")
P["26-bio-morillas"] = bio("Alberto<br>Morillas", "f142-alberto-morillas", "Parfumeur · né en 1950 à Séville",
    ["Il n'a jamais fait d'école de parfumerie.",
     "Étudiant aux Beaux-Arts de Genève, il entre chez Firmenich par hasard, au service chimie, et apprend seul en étudiant les matières premières.",
     "Premier grand succès : Must de Cartier, en 1981. En 2003, il reçoit le prix François Coty."],
    None,
    [("ckone", "CK One", "Calvin Klein · 1994"), ("lbh", "Light Blue pour Homme", "Dolce&Gabbana · 2007")])
P["27-conseil-peau"] = conseil("Pourquoi un<br>parfum ne sent<br>pas pareil sur toi<br>que sur les autres&nbsp;?", [
    ("Ta peau", "Sèche ou grasse, elle ne retient pas les notes de la même façon. Sur une peau sèche, le parfum s'évapore plus vite."),
    ("Ta température", "Une peau plus chaude diffuse davantage le parfum."),
    ("La saison", "Le froid freine la diffusion, la chaleur l'amplifie. Un même parfum peut changer d'une saison à l'autre."),
    ("Ton nez s'habitue", "Au bout de quelques minutes, tu ne sens plus ton propre parfum. Les autres, si. Inutile d'en remettre toute la journée.")],
    "Le bon réflexe", "Toujours tester<br>sur ta propre peau<br>avant d'acheter.")
P["28-pdj-erba"] = pdj("erba", "Xerjoff · Eau de parfum", "Erba Pura", "Bergamote, orange de Sicile, vanille, musc", "Collection Vibe")
P["29-mat-bergamote"] = matiere("La bergamote", "L'éclat des premières secondes", "bergamote", "50% 50%", "Qu'est-ce que la bergamote ?",
    "Un agrume, fruit du bergamotier, entre l'orange amère et le citron. Elle pousse surtout en Calabre, au sud de l'Italie.",
    "Douce, acidulée, légèrement amère : on la trouve surtout en note de tête, des colognes aux parfums les plus chauds.",
    "En 1925, Shalimar a été l'un des premiers parfums à en utiliser autant.",
    [("sauvage", "Dior", "Sauvage Parfum"), ("colonia", "Acqua di Parma", "Colonia")])
P["30-sel-derniere-minute"] = selection("3 cadeaux<br>qui plaisent<br>à tout le monde", [
    ("lemale", "Jean Paul Gaultier", "Le Male", "Lavande, cannelle, vanille", "Un classique depuis 1995, signé Francis Kurkdjian.", "1995"),
    ("lbh", "Dolce&Gabbana", "Light Blue pour Homme", "Pamplemousse, genièvre, romarin", "Frais et facile à porter.", "2007 · Alberto Morillas"),
    ("aquauni", "Maison Francis Kurkdjian", "Aqua Universalis Cologne Forte", "Bergamote, pois de senteur, musc", "Une odeur de propre, élégante, qui va à tout le monde.", "2021")],
    "Noël approche", "Commande sur qosmi.be<br>tant qu'il est temps.", fin_droite="qosmi.be", sur="Spécial Noël", taille_titre=88)

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
