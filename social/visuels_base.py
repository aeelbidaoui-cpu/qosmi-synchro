"""Qosmi — 5 publications d'exemple (09/11/2026). Rendu HTML → PNG 1080×1350 (format portrait Instagram/Facebook)."""
import os, html
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ICI, "out")
os.makedirs(OUT, exist_ok=True)
J = "file://" + ICI + "/jost/files/jost-latin-%s-normal.woff2"
FL = "file://" + ICI + "/fl/%s.png"
NOIR, GRIS, DOUX = "#111111", "#f4f4f4", "#6b6b6b"

BASE = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:J;font-weight:300;src:url({J % 300})}}
@font-face{{font-family:J;font-weight:400;src:url({J % 400})}}
@font-face{{font-family:J;font-weight:500;src:url({J % 500})}}
@font-face{{font-family:J;font-weight:600;src:url({J % 600})}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;font-family:J;color:{NOIR};-webkit-font-smoothing:antialiased}}
.p{{position:relative;width:1080px;height:1350px;overflow:hidden;padding:76px 80px;display:flex;flex-direction:column}}
.haut{{display:flex;justify-content:space-between;align-items:center;font-size:24px;letter-spacing:.22em;text-transform:uppercase;font-weight:500}}
.logo{{letter-spacing:.42em;font-weight:500;font-size:26px}}
.sur{{font-size:24px;letter-spacing:.2em;text-transform:uppercase;color:{DOUX};font-weight:500}}
.t{{text-transform:uppercase;font-weight:500;letter-spacing:.01em;line-height:1.02}}
.notes{{font-size:30px;font-weight:300;letter-spacing:.02em}}
.bas{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;font-size:22px;letter-spacing:.2em;text-transform:uppercase;color:{DOUX};font-weight:500}}
.fl{{position:absolute;left:50%;transform:translateX(-50%);filter:drop-shadow(0 30px 28px rgba(0,0,0,.13))}}
.sol{{position:absolute;left:50%;transform:translateX(-50%);border-radius:50%;background:radial-gradient(closest-side,rgba(0,0,0,.16),rgba(0,0,0,0))}}
.num{{font-size:30px;font-weight:500;letter-spacing:.15em}}
.dots{{display:flex;gap:10px}}.dots i{{display:block;width:10px;height:10px;border-radius:50%;background:#cfcfcf}}.dots i.on{{background:currentColor}}
</style></head><body>"""


def page(contenu, fond=GRIS, couleur=NOIR):
    return BASE + f'<div class="p" style="background:{fond};color:{couleur}">{contenu}</div></body></html>'


def flacon(nom, h, bas, x="50%"):
    """Flacon détouré posé sur une ombre douce ; h = hauteur en px, bas = distance au bas de la page."""
    return (f'<div class="sol" style="left:{x};bottom:{bas - 18}px;width:{int(h * .62)}px;height:46px"></div>'
            f'<img class="fl" src="{FL % nom}" style="left:{x};bottom:{bas}px;height:{h}px">')


def points(n, i):
    return '<div class="dots">' + "".join('<i class="on"></i>' if k == i else "<i></i>" for k in range(n)) + "</div>"


def bas(gauche="qosmi.be", droite=""):
    return f'<div class="bas"><span>{gauche}</span><span>{droite}</span></div>'


S = {}

# ---------- 1. Parfum du jour : Delina ----------
S["1-parfum-du-jour"] = [page(f"""
<div class="haut"><span>Le parfum du jour</span><span class="logo">QOSMI</span></div>
{flacon('delina', 700, 430)}
<div style="margin-top:auto;position:relative">
  <div class="sur">Parfums de Marly · 2017</div>
  <div class="t" style="font-size:132px;margin:14px 0 22px">Delina</div>
  <div class="notes">Rhubarbe, litchi, rose de Damas, vanille</div>
  <div style="height:34px"></div>
  {bas('qosmi.be', 'Eau de parfum')}
</div>""")]

# ---------- 2. Carrousel : 3 parfums pour les soirs d'hiver ----------
HIVER = [("lostcherry", "Tom Ford", "Lost Cherry", "Cerise noire, amande amère, fève tonka",
          "Une cerise macérée dans sa liqueur. Gourmand, mais jamais sage.", "2018 · Louise Turner"),
         ("angels", "By Kilian", "Angels' Share", "Cognac, cannelle, praline",
          "Le nom vient de la « part des anges » : ce qui s'évapore des fûts de cognac.", "2020 · Benoist Lapouza"),
         ("blackorchid", "Tom Ford", "Black Orchid", "Cassis, jasmin, patchouli, vanille",
          "Le tout premier parfum de Tom Ford. Il fête ses 20 ans cette année.", "2006 · Pierre Négrin")]
n = len(HIVER) + 2
car = [page(f"""
<div class="haut"><span class="sur" style="color:inherit">La sélection</span><span class="logo">QOSMI</span></div>
<div class="t" style="font-size:96px;margin-top:70px;position:relative">3 parfums<br>pour les soirs<br>d'hiver</div>
{flacon('lostcherry', 470, 190, '24%')}{flacon('angels', 400, 190, '52%')}{flacon('blackorchid', 470, 190, '79%')}
<div style="margin-top:auto;position:relative;display:flex;justify-content:space-between;align-items:center">{points(n, 0)}<span class="sur">Glisse →</span></div>""")]
for i, (f, marque, nom, notes, phrase, info) in enumerate(HIVER, 1):
    car.append(page(f"""
<div class="haut"><span class="num">0{i}</span><span class="logo">QOSMI</span></div>
{flacon(f, 640 if f != 'angels' else 540, 470)}
<div style="margin-top:auto;position:relative">
  <div class="sur">{marque}</div>
  <div class="t" style="font-size:96px;margin:12px 0 18px">{html.escape(nom)}</div>
  <div class="notes" style="font-weight:400">{notes}</div>
  <div class="notes" style="font-size:27px;color:{DOUX};margin-top:12px;line-height:1.35">{html.escape(phrase)}</div>
  <div style="height:30px"></div>
  <div style="display:flex;justify-content:space-between;align-items:center">{points(n, i)}<span class="sur" style="font-size:20px">{info}</span></div>
</div>"""))
car.append(page(f"""
<div class="haut"><span></span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0;position:relative">
  <div class="t" style="font-size:104px">Ton préféré ?</div>
  <div class="notes" style="font-size:40px;margin-top:30px;line-height:1.4">Dis-nous 1, 2 ou 3<br>en commentaire.</div>
</div>
<div style="position:relative;display:flex;justify-content:space-between;align-items:flex-end">{points(n, n - 1)}<span class="sur">Les trois sur qosmi.be</span></div>""",
                fond=NOIR, couleur="#ffffff"))
S["2-carrousel-hiver"] = car

# ---------- 3. Carrousel conseil : faire tenir son parfum ----------
GESTES = [("Hydrate d'abord", "Une crème neutre, sans parfum, juste avant. Sur une peau sèche, le parfum s'évapore plus vite."),
          ("Vise les points chauds", "Poignets, cou, creux des coudes, derrière les oreilles. La chaleur de la peau diffuse le parfum."),
          ("Ne frotte pas", "Frotter les poignets écrase les notes de tête. Vaporise, puis laisse sécher tout seul."),
          ("Pense à l'écharpe", "Un nuage sur un vêtement tient souvent plus longtemps que sur la peau. Évite la soie et les tissus clairs."),
          ("Range-le bien", "À l'abri de la lumière et de la chaleur. La salle de bain est le pire endroit pour un flacon.")]
n = len(GESTES) + 2
cons = [page(f"""
<div class="haut"><span class="sur" style="color:inherit">Le conseil</span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0;position:relative">
  <div class="t" style="font-size:100px">5 gestes<br>pour que ton<br>parfum tienne<br>plus longtemps</div>
</div>
<div style="display:flex;justify-content:space-between;align-items:center">{points(n, 0)}<span class="sur">Glisse →</span></div>""", fond="#ffffff")]
for i, (titre, texte) in enumerate(GESTES, 1):
    cons.append(page(f"""
<div class="haut"><span></span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0">
  <div style="font-size:300px;font-weight:300;line-height:.9;letter-spacing:-.02em">0{i}</div>
  <div class="t" style="font-size:76px;margin:46px 0 30px">{html.escape(titre)}</div>
  <div class="notes" style="font-size:38px;line-height:1.42;max-width:860px">{html.escape(texte)}</div>
</div>
<div style="display:flex;justify-content:space-between;align-items:center">{points(n, i)}<span class="sur">Le conseil Qosmi</span></div>""",
                     fond="#ffffff" if i % 2 else GRIS))
cons.append(page(f"""
<div class="haut"><span></span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0">
  <div class="t" style="font-size:96px">Garde-le<br>pour plus tard</div>
  <div class="notes" style="font-size:40px;margin-top:30px;line-height:1.4">Enregistre ce post,<br>et envoie-le à la personne<br>qui se parfume toujours trop tôt.</div>
</div>
<div style="display:flex;justify-content:space-between;align-items:flex-end">{points(n, n - 1)}<span class="sur">qosmi.be</span></div>""",
                 fond=NOIR, couleur="#ffffff"))
S["3-carrousel-conseil"] = cons

# ---------- 4. Matière première : l'oud ----------
MAT = "file://" + ICI + "/mat/%s.jpg"
S["4-matiere-oud"] = [page(f"""
<img src="{MAT % 'oud'}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 62%">
<div class="haut" style="position:relative"><span>Matière première</span><span class="logo">QOSMI</span></div>
<div style="position:relative;margin-top:60px">
  <div class="t" style="font-size:170px">L'oud</div>
  <div class="sur" style="color:{NOIR};margin-top:18px">Le bois des dieux</div>
</div>
<div style="margin-top:auto;position:relative;display:flex;justify-content:space-between;align-items:center">{points(3, 0)}<span class="sur" style="color:{NOIR}">Glisse →</span></div>"""),
page(f"""
<div class="haut"><span class="sur" style="color:inherit">D'où vient l'oud ?</span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0">
  <div class="notes" style="font-size:46px;line-height:1.36;font-weight:400">Une résine que l'arbre Aquilaria, des forêts tropicales d'Asie, fabrique pour se défendre quand un champignon l'attaque.</div>
  <div class="notes" style="font-size:34px;margin-top:40px;line-height:1.45;color:{DOUX}">Le bois devient sombre, lourd et très parfumé. Boisé, fumé, presque animal.</div>
  <div style="margin-top:56px;padding-top:30px;border-top:1px solid #d9d9d9">
    <div class="sur">Le saviez-vous</div>
    <div class="notes" style="font-size:36px;margin-top:12px">« Al-oud » veut dire « le bois » en arabe.</div>
  </div>
</div>
<div style="display:flex;justify-content:space-between;align-items:center">{points(3, 1)}<span class="sur">Matière première</span></div>""", fond="#ffffff"),
page(f"""
<div class="haut"><span class="sur" style="color:inherit">À sentir</span><span class="logo">QOSMI</span></div>
{flacon('oudwood', 700, 450)}
<div style="margin-top:auto;position:relative">
  <div class="sur">Tom Ford · 2007</div>
  <div class="t" style="font-size:104px;margin:12px 0 18px">Oud Wood</div>
  <div class="notes">Oud, santal, vétiver, fève tonka</div>
  <div style="height:30px"></div>
  <div style="display:flex;justify-content:space-between;align-items:center">{points(3, 2)}<span class="sur">qosmi.be</span></div>
</div>""")]

# ---------- 5. Anniversaire : Coco Mademoiselle, 25 ans ----------
S["5-anniversaire-coco"] = [page(f"""
<div class="haut"><span>Joyeux anniversaire</span><span class="logo">QOSMI</span></div>
<div style="position:relative;margin-top:40px">
  <div style="font-size:330px;font-weight:300;line-height:.86;letter-spacing:-.03em">25</div>
  <div class="t" style="font-size:54px;margin-top:4px">ans</div>
</div>
{flacon('coco', 600, 560, '70%')}
<div style="margin-top:auto;position:relative">
  <div class="sur">Chanel · 2001 – 2026</div>
  <div class="t" style="font-size:96px;margin:12px 0 18px">Coco<br>Mademoiselle</div>
  <div class="notes">Orange, rose, jasmin, patchouli</div>
  <div style="height:30px"></div>
  {bas('qosmi.be', 'Jacques Polge')}
</div>""", fond="#ffffff")]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
    for nom, slides in S.items():
        for k, h in enumerate(slides, 1):
            f = os.path.join(OUT, "%s-%d.html" % (nom, k))
            open(f, "w").write(h)
            pg.goto("file://" + f)
            pg.wait_for_timeout(250)
            pg.screenshot(path=os.path.join(OUT, "%s-%d.jpg" % (nom, k)), type="jpeg", quality=93)
            os.remove(f)
    b.close()
print("ok", sum(len(v) for v in S.values()), "visuels")
