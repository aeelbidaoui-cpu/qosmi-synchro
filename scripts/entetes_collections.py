"""En-têtes de catégories Qosmi : 5 flacons alignés sur fond gris clair, même style que la bannière d'accueil."""
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageFilter, ImageChops

L, H = 2400, 1000
SOL_DEVANT, SOL_DERRIERE = 905, 845

REGLAGES = {"f_yves-saint-laurent-libre-eau-de-parfum-p.jpg": (232, 8), "h_jean-paul-gaultier-le-male-eau-de-toilet.jpg": (232, 8),
            "h_versace-eros-eau-de-parfum-pour-homme.jpg": (232, 8), "h_hugo-boss-boss-bottled-eau-de-parfum-pou.jpg": (232, 8)}  # fichier → (luminosité minimale du fond, écart de couleur maximal) pour les photos avec halo

def masque(im, nom=""):
    """Fond blanc relié aux bords → transparent ; le reste (y compris étiquettes blanches) → flacon."""
    rgb = im.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    seuil, ecart = REGLAGES.get(nom, (244, 255))
    blanc = lambda p: min(p) >= seuil and max(p) - min(p) <= ecart
    vu = bytearray(w * h)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            q.append((x, y))
    while q:
        x, y = q.popleft()
        i = y * w + x
        if vu[i] or not blanc(px[x, y]):
            continue
        vu[i] = 1
        if x > 0: q.append((x - 1, y))
        if x < w - 1: q.append((x + 1, y))
        if y > 0: q.append((x, y - 1))
        if y < h - 1: q.append((x, y + 1))
    m = Image.frombytes("L", (w, h), bytes(0 if v else 255 for v in vu))
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
    return m

def flacon(nom, hauteur, gris):
    brut = Image.open("src/" + nom)
    if brut.mode in ("RGBA", "LA", "P") and nom.endswith(".png"):  # déjà détouré (PNG transparent)
        brut = brut.convert("RGBA")
        im, m = Image.new("RGB", brut.size, (255, 255, 255)), brut.getchannel("A")
        im.paste(brut.convert("RGB"), (0, 0), m)
    else:
        im = Image.open("src/" + nom).convert("RGB")
        m = masque(im, nom)
    bb = m.point(lambda v: 255 if v > 20 else 0).getbbox()
    im, m = im.crop(bb), m.crop(bb)
    f = hauteur / im.height
    t = (round(im.width * f), hauteur)
    im, m = im.resize(t, Image.LANCZOS), m.resize(t, Image.LANCZOS)
    if f > 1.02:
        im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=int(30 + 40 * (f - 1)), threshold=2))
    im.putalpha(m)
    return im


def teinter(fl, fond_rgb, x, sol):
    """Les zones blanches du flacon (verre, reflets de la photo) prennent exactement la teinte du fond à cet endroit."""
    zone = fond_rgb.crop((x, sol - fl.height, x + fl.width, sol))
    rgb = ImageChops.multiply(fl.convert("RGB"), zone)
    rgb.putalpha(fl.getchannel("A"))
    return rgb

def fond():
    haut, bas = (238, 238, 237), (222, 222, 221)
    g = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1)
        g.putpixel((0, y), tuple(round(haut[i] + (bas[i] - haut[i]) * t) for i in range(3)))
    img = g.resize((L, H)).convert("RGBA")
    halo = Image.new("L", (L, H), 0)
    ImageDraw.Draw(halo).ellipse((L * 0.15, H * 0.05, L * 0.85, H * 1.05), fill=255)
    halo = halo.filter(ImageFilter.GaussianBlur(220))
    clair = Image.new("RGBA", (L, H), (246, 246, 245, 255))
    return Image.composite(clair, img, halo.point(lambda v: int(v * 0.55)))

def ombre(toile, x, sol, w):
    for largeur, haut, flou, force in ((0.90, 0.06, 14, 0.30), (1.25, 0.15, 48, 0.12)):
        m = Image.new("L", (L, H), 0)
        cx, ry, rx = x + w / 2, w * haut / 2, w * largeur / 2
        ImageDraw.Draw(m).ellipse((cx - rx, sol - ry, cx + rx, sol + ry * 0.8), fill=int(255 * force))
        m = m.filter(ImageFilter.GaussianBlur(flou))
        toile.paste(Image.new("RGBA", (L, H), (40, 40, 42, 255)), (0, 0), m)

def reflet(toile, fl, x, sol):
    h = int(fl.height * 0.2)
    r = fl.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, fl.width, h))
    grad = Image.new("L", (1, h))
    for y in range(h):
        grad.putpixel((0, y), int(255 * 0.12 * (1 - y / h) ** 2))
    r.putalpha(ImageChops.multiply(r.getchannel("A"), grad.resize((fl.width, h))))
    toile.alpha_composite(r.filter(ImageFilter.GaussianBlur(2)), (x, sol + 2))

def composer(flacons, chev, sortie):
    toile = fond()
    fond_rgb = toile.convert("RGB")
    fl = [(flacon(n, h, None), d) for n, h, d in flacons]
    lg = [f.width for f, _ in fl]
    total = sum(lg) - sum(min(lg[i], lg[i + 1]) * chev[i] for i in range(len(fl) - 1))
    x = (L - total) / 2
    places = []
    for i, (f, d) in enumerate(fl):
        places.append((f, int(round(x)), SOL_DEVANT if d else SOL_DERRIERE, d))
        if i + 1 < len(fl):
            x += f.width - min(f.width, fl[i + 1][0].width) * chev[i]
    for f, x, sol, d in sorted(places, key=lambda p: p[3]):
        ombre(toile, x, sol, f.width)
        reflet(toile, teinter(f, fond_rgb, x, sol), x, sol)
        f = teinter(f, toile.convert("RGB"), x, sol)  # les blancs prennent la teinte de ce qui est derrière (fond, ombre, flacon)
        toile.alpha_composite(f, (x, sol - f.height))
    rgb = toile.convert("RGB")
    rgb.save(sortie, quality=90, subsampling=0, optimize=True)
    print(sortie, "largeur flacons", int(total))

JEUX = {
 "parfums-femme": ([("f_carolina-herrera-good-girl-eau-de-parfum.jpg", 690, False), ("f_giorgio-armani-my-way-eau-de-parfum-pour.jpg", 600, True),
                    ("f_yves-saint-laurent-libre-eau-de-parfum-p.jpg", 720, False), ("f_viktor-rolf-flowerbomb-eau-de-parfum-pou.jpg", 560, True),
                    ("f_gucci-bloom-eau-de-parfum-pour-femme.jpg", 545, False)], [0.04, 0.04, 0.04, 0.04]),
 "parfums-homme": ([("h_hugo-boss-boss-bottled-eau-de-parfum-pou.jpg", 680, False), ("h_giorgio-armani-acqua-di-gio-eau-de-parfu.jpg", 600, True),
                    ("h_jean-paul-gaultier-le-male-eau-de-toilet.jpg", 760, False), ("h_paco-rabanne-1-million-eau-de-toilette-p.jpg", 600, True),
                    ("h_versace-eros-eau-de-parfum-pour-homme.jpg", 600, False)], [0.02, 0.02, 0.02, 0.02]),
 "journal-erba-pura": ([("j_erba_riklis.png", 760, True)], []),
 "journal-concentrations": ([("h_jean-paul-gaultier-le-male-eau-de-toilet.jpg", 700, True), ("h_giorgio-armani-acqua-di-gio-eau-de-parfu.jpg", 600, True),
                             ("n_nishane-ani-extrait-de-parfum-mixte.jpg", 600, True)], [-0.18, -0.18]),
 "niche": ([("n_parfums-de-marly-delina-eau-de-parfum-po.jpg", 620, False), ("n_xerjoff-xj-1861-naxos-eau-de-parfum-mixt.jpg", 650, True),
            ("n_initio-black-gold-project-oud-for-greatn.jpg", 550, False), ("n_tiziana-terenzi-kirke-extrait-de-parfum-.jpg", 520, True),
            ("n_nishane-ani-extrait-de-parfum-mixte.jpg", 560, False)], [-0.07, -0.07, -0.07, -0.07]),
}
if __name__ == "__main__":
    for k in (sys.argv[1:] or JEUX):
        composer(*JEUX[k], ("qosmi-%s.jpg" if k.startswith("journal") else "qosmi-entete-%s.jpg") % k)
