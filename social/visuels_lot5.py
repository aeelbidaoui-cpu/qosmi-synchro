#!/usr/bin/env python3
"""Qosmi — visuels du lot n°5 « Tendances » (1080 × 1350, même style que les lots 1 à 4 : police Jost, fond gris clair).

Les visuels sont dans la langue de la publication (champ « langue » de social/lot5/lot5.json).
Il faut, dans le dossier ACTIFS (variable d'environnement QOSMI_ACTIFS_LOT5) :
  - fl/<handle>.png : flacons détourés, tirés des photos des fiches Qosmi ;
  - package/files/jost-latin-<poids>-normal.woff2 : police Jost (paquet npm @fontsource/jost).

  python3 social/legendes_lot5.py && QOSMI_ACTIFS_LOT5=… python3 social/visuels_lot5.py
"""
import html, json, os, sys
from PIL import Image
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import legendes_lot5 as L5  # noqa: E402

ACTIFS = os.environ.get("QOSMI_ACTIFS_LOT5", "")
OUT = os.path.join(ICI, "lot5")
J = "file://" + ACTIFS + "/package/files/jost-latin-%s-normal.woff2"
FL = ACTIFS + "/fl/%s.png"
NOIR, GRIS, DOUX = "#111111", "#f4f4f4", "#6b6b6b"
e = html.escape

T = {"fr": {"sur": "La tendance", "glisse": "Glisse →", "src": "Fragrance Index · nov. 2026", "fin1": "Tous sur qosmi.be",
            "fin2": "Lien en bio pour commander", "conseil": "Le conseil", "fin_conseil": "D'autres conseils<br>chaque semaine"},
     "nl": {"sur": "De trend", "glisse": "Swipe →", "src": "Fragrance Index · nov. 2026", "fin1": "Alles op qosmi.be",
            "fin2": "Link in bio om te bestellen", "conseil": "Het advies", "fin_conseil": "Elke week<br>nieuwe tips"}}

BASE = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:J;font-weight:300;src:url({J % 300})}}
@font-face{{font-family:J;font-weight:400;src:url({J % 400})}}
@font-face{{font-family:J;font-weight:500;src:url({J % 500})}}
@font-face{{font-family:J;font-weight:600;src:url({J % 600})}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;font-family:J;color:{NOIR};-webkit-font-smoothing:antialiased}}
.p{{position:relative;width:1080px;height:1350px;overflow:hidden;padding:76px 80px;display:flex;flex-direction:column}}
.haut{{position:relative;z-index:2;display:flex;justify-content:space-between;align-items:center;font-size:24px;letter-spacing:.22em;text-transform:uppercase;font-weight:500}}
.logo{{letter-spacing:.42em;font-weight:500;font-size:26px}}
.sur{{font-size:24px;letter-spacing:.2em;text-transform:uppercase;color:{DOUX};font-weight:500}}
.t{{text-transform:uppercase;font-weight:500;letter-spacing:.01em;line-height:1.02}}
.notes{{font-size:32px;font-weight:300;letter-spacing:.02em;line-height:1.35}}
.chip{{display:inline-block;background:{NOIR};color:#fff;font-size:24px;letter-spacing:.14em;text-transform:uppercase;font-weight:500;padding:12px 20px}}
.src{{font-size:20px;letter-spacing:.16em;text-transform:uppercase;color:{DOUX};font-weight:500;margin-top:12px}}
.bas{{margin-top:auto;position:relative;display:flex;justify-content:space-between;align-items:center;font-size:22px;letter-spacing:.2em;text-transform:uppercase;color:{DOUX};font-weight:500}}
.fl{{position:absolute;filter:drop-shadow(0 30px 28px rgba(0,0,0,.14))}}
.sol{{position:absolute;border-radius:50%;background:radial-gradient(closest-side,rgba(0,0,0,.16),rgba(0,0,0,0))}}
.num{{font-size:30px;font-weight:500;letter-spacing:.15em}}
.dots{{display:flex;gap:10px}}.dots i{{display:block;width:10px;height:10px;border-radius:50%;background:#cfcfcf}}.dots i.on{{background:currentColor}}
</style></head><body>"""

TAILLES = {}


def taille(h):
    if h not in TAILLES:
        TAILLES[h] = Image.open(FL % h).size
    return TAILLES[h]


def page(contenu, fond=GRIS, couleur=NOIR):
    return BASE + f'<div class="p" style="background:{fond};color:{couleur}">{contenu}</div></body></html>'


def flacon(h, haut_max, larg_max, bas, cx=540):
    """Flacon détouré centré sur cx, posé sur une ombre douce."""
    w, hh = taille(h)
    k = min(haut_max / hh, larg_max / w)
    W, H = int(w * k), int(hh * k)
    return (f'<div class="sol" style="left:{cx - int(W * .55)}px;bottom:{bas - 20}px;width:{int(W * 1.1)}px;height:46px"></div>'
            f'<img class="fl" src="file://{FL % h}" style="left:{cx - W // 2}px;bottom:{bas}px;width:{W}px;height:{H}px">')


def rangee(handles, haut, larg_tot, bas, gap=26):
    """Plusieurs flacons côte à côte, même hauteur, réduits pour tenir dans la largeur."""
    ws = [taille(h)[0] * haut / taille(h)[1] for h in handles]
    k = min(1, (larg_tot - gap * (len(handles) - 1)) / sum(ws))
    x = 540 - (sum(ws) * k + gap * (len(handles) - 1)) / 2
    out = ""
    for h, w in zip(handles, ws):
        out += flacon(h, haut * k, w * k + 1, bas, cx=int(x + w * k / 2))
        x += w * k + gap
    return out


def points(n, i):
    return '<div class="dots">' + "".join('<i class="on"></i>' if k == i else "<i></i>" for k in range(n)) + "</div>"


def taille_nom(nom):
    n = len(nom)
    return 132 if n <= 10 else 108 if n <= 15 else 88 if n <= 20 else 72


def bloc_parfum(cle, lg, sig=None):
    h, marque, nom = L5.P[cle]
    an = L5.annee(cle)
    nt = L5.notes(cle, nl=(lg == "nl"))
    return f"""<div style="margin-top:auto;position:relative">
  <div class="sur">{e(marque)}{' · %s' % an if an else ''}</div>
  <div class="t" style="font-size:{taille_nom(nom)}px;margin:14px 0 22px">{e(nom)}</div>
  {f'<div class="notes">{e(nt)}</div>' if nt else ''}
</div>"""


def chip(cle, lg, sig=None):
    s = (sig or {}).get(cle) or L5.SIG.get(cle) or ("", "")
    s = s[1] if lg == "nl" else s[0]
    if not s:
        return ""
    return f'<div style="position:relative;z-index:2;margin-top:34px"><span class="chip">{e(s)}</span><div class="src">{T[lg]["src"]}</div></div>'


def pdj(p):
    lg = p["langue"]
    cle = p["parfums"][0]
    return [page(f"""
<div class="haut"><span>{T[lg]['sur']}</span><span class="logo">QOSMI</span></div>
{chip(cle, lg)}
{flacon(L5.P[cle][0], 640, 720, 455)}
{bloc_parfum(cle, lg)}
<div class="bas" style="margin-top:34px"><span>qosmi.be</span><span>{L5.concentration(L5.P[cle][0])}</span></div>""")]


def sel(p):
    lg = p["langue"]
    cles = p["parfums"]
    n = len(cles) + 2
    titre = p["couv"][1 if lg == "nl" else 0]
    ch = p.get("chip")
    ch = f'<div style="margin-top:30px"><span class="chip">{e(ch[1] if lg == "nl" else ch[0])}</span><div class="src">{T[lg]["src"]}</div></div>' if ch else ""
    out = [page(f"""
<div class="haut"><span>{T[lg]['sur']}</span><span class="logo">QOSMI</span></div>
<div style="margin-top:70px;position:relative;z-index:2"><div class="t" style="font-size:96px">{titre}</div>{ch}</div>
{rangee([L5.P[c][0] for c in cles], 470 if len(cles) <= 3 else 420, 940, 175)}
<div class="bas">{points(n, 0)}<span style="color:{NOIR}">{T[lg]['glisse']}</span></div>""")]
    for i, c in enumerate(cles, 1):
        out.append(page(f"""
<div class="haut"><span class="num">{i:02d}</span><span class="logo">QOSMI</span></div>
{chip(c, lg, p.get('sig'))}
{flacon(L5.P[c][0], 600, 700, 470)}
{bloc_parfum(c, lg)}
<div class="bas" style="margin-top:34px">{points(n, i)}<span>{L5.concentration(L5.P[c][0])}</span></div>"""))
    out.append(fin(lg, n))
    return out


def fin(lg, n, texte=None, sur=None):
    return page(f"""
<div class="haut"><span>{sur or T[lg]['sur']}</span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0;text-align:center">
  <div class="t" style="font-size:96px">{texte or T[lg]['fin1']}</div>
  <div class="notes" style="margin-top:34px;font-size:36px">{T[lg]['fin2']}</div>
</div>
<div class="bas" style="color:#9a9a9a">{points(n, n - 1)}<span>{T[lg]['src']}</span></div>""", fond=NOIR, couleur="#ffffff")


def conseil(p):
    lg = p["langue"]
    n = len(p["slides"]) + 2
    out = [page(f"""
<div class="haut"><span>{T[lg]['conseil']}</span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0"><div class="t" style="font-size:110px">{p['couv'][1 if lg == 'nl' else 0]}</div></div>
<div class="bas">{points(n, 0)}<span style="color:{NOIR}">{T[lg]['glisse']}</span></div>""", fond="#ffffff")]
    for i, s in enumerate(p["slides"], 1):
        titre, texte = (s[2], s[3]) if lg == "nl" else (s[0], s[1])
        out.append(page(f"""
<div class="haut"><span class="num">{i:02d}</span><span class="logo">QOSMI</span></div>
<div style="margin:auto 0">
  <div class="t" style="font-size:{92 if len(titre) <= 16 else 76}px">{e(titre)}</div>
  <div class="notes" style="font-size:40px;margin-top:40px;line-height:1.45">{e(texte)}</div>
</div>
<div class="bas">{points(n, i)}<span>QOSMI.BE</span></div>""", fond=GRIS if i % 2 else "#ffffff"))
    out.append(fin(lg, n, T[lg]["fin_conseil"], T[lg]["conseil"]))
    return out


def main():
    if not ACTIFS:
        sys.exit("QOSMI_ACTIFS_LOT5 manquant (dossier des flacons détourés et de la police)")
    lot = json.load(open(os.path.join(OUT, "lot5.json"), encoding="utf-8"))
    seul = sys.argv[1:]
    src = {p["id"]: p for p in L5.L}
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        pg = nav.new_page(viewport={"width": 1080, "height": 1350})
        for q in lot:
            if seul and q["id"] not in seul:
                continue
            p = dict(src[q["id"]], langue=q["langue"])
            pages = {"pdj": pdj, "sel": sel, "conseil": conseil}[p["type"]](p)
            assert len(pages) == len(q["img"]), q["id"]
            for nom, h in zip(q["img"], pages):
                f = os.path.join(OUT, nom + ".html")
                open(f, "w", encoding="utf-8").write(h)
                pg.goto("file://" + f)
                pg.wait_for_timeout(150)
                png = os.path.join(OUT, nom + ".png")
                pg.screenshot(path=png)
                Image.open(png).convert("RGB").save(os.path.join(OUT, nom + ".jpg"), quality=90)
                os.remove(png)
                os.remove(f)
            print(q["id"], len(pages))
        nav.close()


if __name__ == "__main__":
    main()
