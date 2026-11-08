"""Logos de marques : recadre le blanc autour, ajoute une marge, enregistre en JPG pour le site (assets/hero)."""
import json, re, sys, unicodedata, os
from PIL import Image, ImageChops
D = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/claude/qosmi-synchro"
def handleize(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")
garde = json.load(open(os.path.join(D, "garde.json")))  # {marque: id fragrantica}
conf = {"source": "Logos des marques relevés sur Fragrantica (fimgs.net) le 08/11/2026, vérifiés un par un (propres, bonne marque) ; demande d'Amine du 08/11/2026.", "par_marque": {}}
for m, i in garde.items():
    im = Image.open(os.path.join(D, "brut", "%s.jpg" % i))
    if im.mode in ("P", "RGBA", "LA"):
        im = im.convert("RGBA"); fond = Image.new("RGBA", im.size, (255, 255, 255, 255)); fond.alpha_composite(im); im = fond
    im = im.convert("RGB")
    coin = im.getpixel((2, 2))
    diff = ImageChops.difference(im, Image.new("RGB", im.size, coin)).convert("L").point(lambda v: 255 if v > 18 else 0)
    bb = diff.getbbox() or (0, 0) + im.size
    im = im.crop(bb)
    m_px = int(max(im.size) * 0.08)
    t = Image.new("RGB", (im.width + 2 * m_px, im.height + 2 * m_px), coin)
    t.paste(im, (m_px, m_px))
    slug = handleize(m)
    t.save(os.path.join(REPO, "assets", "hero", "qosmi-logo-marque-%s.jpg" % slug), quality=93)
    conf["par_marque"][m] = {"slug": slug, "fichier": "qosmi-logo-marque-%s.jpg" % slug, "source": "https://fimgs.net/mdimg/dizajneri/o.%s.jpg" % i, "taille": list(t.size)}
json.dump(conf, open(os.path.join(REPO, "config", "logos_marques.json"), "w"), ensure_ascii=False, indent=1)
print(len(conf["par_marque"]), "logos")
