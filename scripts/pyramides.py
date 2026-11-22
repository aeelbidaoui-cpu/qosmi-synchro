"""2e image des parfums : la pyramide olfactive en photos, dans le style Qosmi (22/11/2026, demande d'Amine, version B).

Trois cartes blanches qui s'élargissent vers le bas (tête, cœur, fond), chaque note en photo ronde avec son nom.
Une note sans photo dans config/pyramide_photos.json passe en texte (« et aussi : … ») sous les photos.

    python3 scripts/pyramides.py --apercu HANDLE [HANDLE…]   → rapports/pyramides/<handle>.jpg (sans Shopify)
    python3 scripts/pyramides.py --poser [--limite N]        → crée / met à jour la 2e image des fiches actives

Sur la fiche : métachamps qosmi.pyramide_media (identifiant du média, gardé par site_synchro.entree_complete) et
qosmi.pyramide_hash (contenu dessiné : une fiche n'est refaite que si ses notes, son nom ou ce dessin changent).
"""
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(RACINE, "config")
RAPPORTS = os.path.join(RACINE, "rapports")
CACHE = os.path.join(RAPPORTS, "pyramides_photos")
POLICE = os.path.join(RACINE, "social", "polices", "Jost.ttf")
LOGO = os.path.join(RACINE, "assets", "qosmi-logo.png")
VERSION_DESSIN = "b1"

W = 2000
FOND, NOIR, GRIS, BLANC, FILET = (244, 244, 244), (17, 17, 17), (128, 128, 128), (255, 255, 255), (230, 230, 230)
ETAGES = [("t", "tete", "Notes de tête", 0.50, 4), ("c", "coeur", "Notes de cœur", 0.72, 5), ("f", "fond", "Notes de fond", 0.94, 6)]
CONCENTRATIONS = r"(Extrait de Parfum|Eau de Parfum|Eau de Toilette|Eau de Cologne|Eau Fraîche|Parfum|Extrait|Elixir|Cologne)"


def police(style, taille):
    f = ImageFont.truetype(POLICE, taille)
    f.set_variation_by_name(style)
    return f


# ------------------------------------------------------------------ notes → photos
def _photos():
    with open(os.path.join(CONFIG, "pyramide_photos.json"), encoding="utf-8") as fh:
        d = json.load(fh)
    return d["photos"], d.get("alias", {})


PHOTOS, ALIAS = _photos()
CLES = sorted(PHOTOS, key=len, reverse=True)


def cle(note):
    n = note.strip().lower().replace("’", "'")
    n = re.sub(r"^(accord|absolu|essence|huile) (de |d')", "", n)
    if n in ALIAS:
        return ALIAS[n]
    if n in PHOTOS:
        return n
    for k in CLES:
        if n.startswith(k + " ") or n.startswith(k + "'"):
            return k
    for a in sorted(ALIAS, key=len, reverse=True):
        if n.startswith(a + " "):
            return ALIAS[a]
    return None


def photo(k):
    os.makedirs(CACHE, exist_ok=True)
    chemin = os.path.join(CACHE, PHOTOS[k] + ".jpg")
    if not os.path.exists(chemin):
        url = "https://images.unsplash.com/%s?w=600&h=600&fit=crop&crop=entropy&q=85&fm=jpg" % PHOTOS[k]
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; QosmiSynchro/1.0)"})
        with urllib.request.urlopen(req, timeout=60) as r:
            donnees = r.read()
        with open(chemin, "wb") as fh:
            fh.write(donnees)
    return chemin


def notes_parfum(handle, profils, descriptions):
    """{'t': [...], 'c': [...], 'f': [...]} — notes vérifiées (descriptions) d'abord, sinon profil."""
    d = (descriptions.get(handle) or {}).get("notes_fr") or {}
    if any(d.get(x) for x in ("tete", "coeur", "fond")):
        return {"t": d.get("tete") or [], "c": d.get("coeur") or [], "f": d.get("fond") or []}
    nf = (profils.get(handle) or {}).get("nf") or {}
    return {x: nf.get(x) or [] for x in ("t", "c", "f")}


def joli(n):
    n = n.strip()
    return n[:1].upper() + n[1:]


# ------------------------------------------------------------------ dessin
def centre(d, t, y, fo, c=NOIR, sp=0, x0=0, w0=W):
    w = sum(d.textlength(ch, font=fo) for ch in t) + sp * (len(t) - 1)
    x = x0 + (w0 - w) / 2
    for ch in t:
        d.text((x, y), ch, font=fo, fill=c)
        x += d.textlength(ch, font=fo) + sp


def coupe(d, texte, fo, largeur, maxl=2):
    mots, lignes, cur = texte.split(), [], ""
    for m in mots:
        t = (cur + " " + m).strip()
        if d.textlength(t, font=fo) > largeur and cur:
            lignes.append(cur)
            cur = m
        else:
            cur = t
    lignes.append(cur)
    if len(lignes) > maxl:
        lignes = lignes[:maxl]
        while d.textlength(lignes[-1] + "…", font=fo) > largeur and " " in lignes[-1]:
            lignes[-1] = lignes[-1].rsplit(" ", 1)[0]
        lignes[-1] += "…"
    return lignes


def ombre(im, box, r):
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle(box, r, fill=55)
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    im.paste(Image.new("RGB", im.size, (0, 0, 0)), (0, 12), sh)


def rond(chemin, dia):
    ph = Image.open(chemin).convert("RGB")
    s = min(ph.size)
    ph = ph.crop(((ph.width - s) // 2, (ph.height - s) // 2, (ph.width + s) // 2, (ph.height + s) // 2))
    ph = ph.resize((dia, dia), Image.LANCZOS)
    m = Image.new("L", (dia * 4, dia * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, dia * 4 - 1, dia * 4 - 1), fill=255)
    return ph, m.resize((dia, dia), Image.LANCZOS)


def etages(notes):
    """Par étage : (libellé, largeur, [(nom, clé photo)], [noms sans photo]). Étages vides retirés."""
    out, vus = [], set()  # une même photo ne revient pas deux fois sur l'image (jasmin / jasmin sambac)
    for x, _, lib, larg, cap in ETAGES:
        avec, sans = [], []
        for n in notes.get(x) or []:
            k = cle(n)
            if k and k not in vus and len(avec) < cap:
                vus.add(k)
                avec.append((joli(n), k))
            elif not k or k not in vus:
                sans.append(joli(n))
        if avec or sans:
            out.append((lib, larg, avec, sans))
    if len(out) == 1:  # une seule liste de notes : pas de tête / cœur / fond
        out[0] = ("Notes principales", 0.94, out[0][2], out[0][3])
    return out


def entete(marque, nom, typ):
    im = Image.new("RGB", (W, W), FOND)
    d = ImageDraw.Draw(im)
    logo = Image.open(LOGO).convert("RGBA")
    lw = 330
    logo = logo.resize((lw, int(logo.size[1] * lw / logo.size[0])), Image.LANCZOS)
    im.paste(logo, ((W - lw) // 2, 100), logo)
    centre(d, marque.upper(), 250, police("Regular", 38), GRIS, sp=12)
    fo_nom = police("Medium", 88)
    while d.textlength(nom, font=fo_nom) > W - 240 and fo_nom.size > 50:
        fo_nom = police("Medium", fo_nom.size - 4)
    centre(d, nom, 300, fo_nom)
    centre(d, typ, 412, police("Light", 42), GRIS)
    return im, d


def dessiner(marque, nom, typ, notes):
    et = etages(notes)
    if not et or not any(a for _, _, a, _ in et):
        return None
    im, d = entete(marque, nom, typ)
    dia, gap = 180, 64
    fo_note, fo_lab, fo_plus = police("Regular", 34), police("Medium", 29), police("Light", 31)
    hauteurs = []
    for lib, larg, avec, sans in et:
        hauteurs.append(70 + (dia + 18 + 2 * 40 if avec else 0) + (48 if sans else 0) + 26)
    gap_v = 24
    total = sum(hauteurs) + gap_v * (len(et) - 1)
    y = 500 + max(0, (1440 - total) // 2)
    for (lib, larg, avec, sans), h in zip(et, hauteurs):
        w = W * larg
        x = (W - w) / 2
        box = (x, y, x + w, y + h)
        ombre(im, box, 40)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle(box, 40, fill=BLANC)
        centre(d, lib.upper(), y + 30, fo_lab, GRIS, sp=9)
        yy = y + 80
        if avec:
            n = len(avec)
            xx = (W - (n * dia + (n - 1) * gap)) / 2
            for nom_note, k in avec:
                ph, m = rond(photo(k), dia)
                im.paste(ph, (int(xx), int(yy)), m)
                d = ImageDraw.Draw(im)
                d.ellipse((xx - 3, yy - 3, xx + dia + 3, yy + dia + 3), outline=FILET, width=3)
                for i, l in enumerate(coupe(d, nom_note, fo_note, dia + gap - 14)):
                    centre(d, l, yy + dia + 16 + i * 40, fo_note, NOIR, x0=xx - gap / 2, w0=dia + gap)
                xx += dia + gap
            yy += dia + 18 + 2 * 40
        if sans:
            t = ("Et aussi : " if avec else "") + ", ".join(sans)
            l = coupe(d, t, fo_plus, w - 120, maxl=1)[0]
            centre(d, l, yy + 4, fo_plus, GRIS)
        y += h + gap_v
    return im


# 22/11/2026 (Amine) : parfum sans notes connues → 2e image « 100 % authentique » au lieu de la pyramide
ENGAGEMENTS = [("Parfum original de la marque", "Jamais d'imitation ni de contretype"),
               ("Livraison suivie", "En Belgique et dans 8 autres pays d'Europe"),
               ("Livraison offerte dès 2 articles", "En Belgique, aux Pays-Bas et au Luxembourg"),
               ("Paiement sécurisé", "Paiement chiffré, confirmation par e-mail")]


def coche(d, cx, cy, r, ep=5):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=NOIR, width=ep)
    d.line([(cx - r * 0.42, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.34), (cx + r * 0.45, cy - r * 0.3)],
           fill=NOIR, width=ep + 1, joint="curve")


def dessiner_authentique(marque, nom, typ):
    im, d = entete(marque, nom, typ)
    box = (170, 540, W - 170, 1860)
    ombre(im, box, 48)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, 48, fill=BLANC)
    # sceau
    cx, cy = W // 2, 740
    d.ellipse((cx - 150, cy - 150, cx + 150, cy + 150), outline=NOIR, width=4)
    d.ellipse((cx - 130, cy - 130, cx + 130, cy + 130), outline=FILET, width=2)
    centre(d, "100 %", cy - 58, police("Medium", 72))
    centre(d, "AUTHENTIQUE", cy + 32, police("Medium", 22), GRIS, sp=5)
    centre(d, "Le vrai parfum, tout simplement", 925, police("Light", 44), GRIS)
    fo_t, fo_s = police("Medium", 44), police("Light", 34)
    larg = max(max(d.textlength(t, font=fo_t), d.textlength(u, font=fo_s)) for t, u in ENGAGEMENTS)
    x0 = int((W - (larg + 110)) / 2)  # bloc centré : coche + textes
    y = 1060
    for titre_e, sous in ENGAGEMENTS:
        coche(d, x0 + 34, y + 38, 34)
        d.text((x0 + 110, y), titre_e, font=fo_t, fill=NOIR)
        d.text((x0 + 110, y + 58), sous, font=fo_s, fill=GRIS)
        y += 180
    return im


def separer_titre(titre, marque):
    t = titre.strip()
    if marque and t.lower().startswith(marque.lower()):
        t = t[len(marque):].strip(" -–")
    if " — " in t:  # titres de la boutique : « Aventus — Eau de Parfum pour homme »
        nom, typ = t.split(" — ", 1)
        return nom.strip(), typ.strip()
    m = re.search(CONCENTRATIONS, t)
    if m and m.start() > 0:
        return t[:m.start()].strip(" -–—,"), t[m.start():].strip()
    return t, ""


def empreinte(marque, nom, typ, notes):
    brut = json.dumps([VERSION_DESSIN, marque, nom, typ, notes, {k: PHOTOS[k] for k in sorted(PHOTOS)}],
                      ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(brut.encode("utf-8")).hexdigest()[:16]


def charger():
    with open(os.path.join(CONFIG, "profils_parfums.json"), encoding="utf-8") as fh:
        profils = json.load(fh)["parfums"]
    with open(os.path.join(CONFIG, "descriptions_parfums.json"), encoding="utf-8") as fh:
        descriptions = json.load(fh).get("parfums") or {}
    return profils, descriptions


# ------------------------------------------------------------------ Shopify
Q_FICHES = """query($apres: String) { products(first: 100, after: $apres, query: "status:active") {
  pageInfo { hasNextPage endCursor }
  nodes { id handle title vendor productType
    media(first: 12) { nodes { id } }
    pm: metafield(namespace: "qosmi", key: "pyramide_media") { value }
    ph: metafield(namespace: "qosmi", key: "pyramide_hash") { value } } } }"""
M_STAGE = """mutation($i: [StagedUploadInput!]!) { stagedUploadsCreate(input: $i) {
  stagedTargets { url resourceUrl parameters { name value } } userErrors { message } } }"""
M_FICHIER = """mutation($f: [FileCreateInput!]!) { fileCreate(files: $f) { files { id fileStatus } userErrors { message } } }"""
M_LIER = """mutation($f: [FileUpdateInput!]!) { fileUpdate(files: $f) { files { id } userErrors { message } } }"""
M_ORDRE = """mutation($id: ID!, $m: [MoveInput!]!) { productReorderMedia(id: $id, moves: $m) { job { id } mediaUserErrors { message } } }"""
M_META = """mutation($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) { userErrors { message } } }"""
M_SUPPR = """mutation($ids: [ID!]!) { fileDelete(fileIds: $ids) { deletedFileIds userErrors { message } } }"""


def televerser(s, nom_fichier, donnees, alt):
    cible = s.gql(M_STAGE, {"i": [{"resource": "IMAGE", "filename": nom_fichier, "mimeType": "image/jpeg",
                                    "httpMethod": "POST", "fileSize": str(len(donnees))}]})["stagedUploadsCreate"]
    if cible["userErrors"]:
        raise RuntimeError(cible["userErrors"])
    t = cible["stagedTargets"][0]
    limite = "----qosmi%d" % int(time.time() * 1000)
    corps = b""
    for p in t["parameters"]:
        corps += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (limite, p["name"], p["value"])).encode()
    corps += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\nContent-Type: image/jpeg\r\n\r\n"
              % (limite, nom_fichier)).encode() + donnees + ("\r\n--%s--\r\n" % limite).encode()
    req = urllib.request.Request(t["url"], data=corps, method="POST",
                                 headers={"Content-Type": "multipart/form-data; boundary=" + limite})
    urllib.request.urlopen(req, timeout=120).read()
    f = s.gql(M_FICHIER, {"f": [{"originalSource": t["resourceUrl"], "contentType": "IMAGE", "alt": alt,
                                  "filename": nom_fichier}]})["fileCreate"]
    if f["userErrors"]:
        raise RuntimeError(f["userErrors"])
    fid = f["files"][0]["id"]
    for _ in range(40):
        st = s.gql("query($id: ID!) { node(id: $id) { ... on MediaImage { fileStatus } } }", {"id": fid})["node"]
        if st and st.get("fileStatus") == "READY":
            return fid
        if st and st.get("fileStatus") == "FAILED":
            raise RuntimeError("fichier refusé par Shopify")
        time.sleep(3)
    raise RuntimeError("fichier pas prêt après 2 minutes")


def poser(limite=0, seules=None):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from shopify_api import Shopify
    s = Shopify()
    profils, descriptions = charger()
    fiches, apres = [], None
    while True:
        d = s.gql(Q_FICHES, {"apres": apres})["products"]
        fiches += d["nodes"]
        if not d["pageInfo"]["hasNextPage"]:
            break
        apres = d["pageInfo"]["endCursor"]
    faits = sautes = sans_notes = err = authentiques = 0
    for p in fiches:
        if seules and p["handle"] not in seules:
            continue
        notes = notes_parfum(p["handle"], profils, descriptions)
        nom, typ = separer_titre(p["title"], p["vendor"])
        im = None
        if any(notes.values()) and any(a for _, _, a, _ in etages(notes)):
            sorte = "pyramide"
        elif (p.get("productType") or "").startswith("Parfums") or (p.get("productType") or "") == "Testeurs":
            sorte, notes = "authentique", {"authentique": [t for t, _ in ENGAGEMENTS]}
        else:
            sans_notes += 1
            continue
        h = empreinte(p["vendor"], nom, typ, notes)
        ancien = (p.get("pm") or {}).get("value")
        medias = [m["id"] for m in p["media"]["nodes"]]
        if ancien in medias and (p.get("ph") or {}).get("value") == h:
            sautes += 1
            continue
        if sorte == "pyramide":
            im = dessiner(p["vendor"], nom or p["title"], typ, notes)
        else:
            im = dessiner_authentique(p["vendor"], nom or p["title"], typ)
            authentiques += 1
        tampon = io.BytesIO()
        im.save(tampon, "JPEG", quality=90, optimize=True)
        try:
            alt = ("Pyramide olfactive de %s %s" if sorte == "pyramide" else "%s %s, parfum 100 %% authentique") % (p["vendor"], nom)
            fid = televerser(s, "pyramide-%s-%s.jpg" % (p["handle"][:90], h[:6]), tampon.getvalue(), alt)
            r = s.gql(M_LIER, {"f": [{"id": fid, "referencesToAdd": [p["id"]]}]})["fileUpdate"]
            if r["userErrors"]:
                raise RuntimeError(r["userErrors"])
            if medias:  # 2e position, derrière la photo du produit
                s.gql(M_ORDRE, {"id": p["id"], "m": [{"id": fid, "newPosition": "1"}]})
            s.gql(M_META, {"m": [
                {"ownerId": p["id"], "namespace": "qosmi", "key": "pyramide_media", "type": "single_line_text_field", "value": fid},
                {"ownerId": p["id"], "namespace": "qosmi", "key": "pyramide_hash", "type": "single_line_text_field", "value": h}]})
            if ancien and ancien != fid:
                s.gql(M_SUPPR, {"ids": [ancien]})
            faits += 1
            if faits <= 3 or faits % 50 == 0:
                print("  pyramide posée : %s (%d)" % (p["handle"], faits), flush=True)
        except Exception as e:  # une fiche en échec n'arrête pas les autres
            err += 1
            print("  erreur %s : %s" % (p["handle"], str(e)[:200]), flush=True)
        if limite and faits >= limite:
            break
    print("Pyramides : %d posées (dont %d « 100 %% authentique »), %d déjà à jour, %d hors parfums sans notes, "
          "%d erreurs (sur %d fiches actives)." % (faits, authentiques, sautes, sans_notes, err, len(fiches)))


def apercu(handles):
    profils, descriptions = charger()
    sortie = os.path.join(RAPPORTS, "pyramides")
    os.makedirs(sortie, exist_ok=True)
    for h in handles:
        notes = notes_parfum(h, profils, descriptions)
        mots = h.split("-")
        marque = mots[0].capitalize()
        titre = " ".join(m.capitalize() for m in mots[1:])
        titre = re.sub(r"\bEau De\b", "Eau de", titre).replace(" Pour ", " pour ")
        nom, typ = separer_titre(titre, "")
        im = dessiner(marque, nom, typ.lower().capitalize() if typ else "", notes)
        if im is None:
            im = dessiner_authentique(marque, nom, typ.lower().capitalize() if typ else "")
        im.save(os.path.join(sortie, h + ".jpg"), quality=90)
        print("%s → %s" % (h, os.path.join(sortie, h + ".jpg")))


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--apercu" in a:
        apercu([x for x in a if not x.startswith("--")])
    elif "--poser" in a:
        lim = int(a[a.index("--limite") + 1]) if "--limite" in a else 0
        seules = set(os.environ.get("PYRAMIDES_FICHES", "").split()) or None
        poser(lim, seules)
    else:
        print(__doc__)
