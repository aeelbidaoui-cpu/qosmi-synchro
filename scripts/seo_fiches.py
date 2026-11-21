#!/usr/bin/env python3
"""Textes des fiches plus utiles pour Google (demande d'Amine, 21/11/2026 : « on doit améliorer le référencement », « fait 2/3/4 »).

Appelé par site_synchro.textes() (action theme « textes-fiches ») sur les fiches EN LIGNE uniquement :
  1. Un paragraphe d'introduction rédigé à partir du profil vérifié du parfum (config/profils_parfums.json :
     notes, accords, saison, occasions, année, parfumeur). Avant, la partie visible de beaucoup de fiches tenait
     en une phrase identique d'une fiche à l'autre : Google les explore puis ne les indexe pas (« contenu trop mince »).
     Les fiches qui ont déjà une description rédigée (config/descriptions_parfums.json) gardent la leur.
  2. Un bloc « Dans le même esprit » : 4 parfums EN LIGNE aux accords et aux notes proches (liens internes,
     que Google suit pour découvrir et indexer les fiches). Jamais présentés comme copies ou équivalents.
  3. La méta-description Google se termine par la vraie promesse de livraison (offerte dès 2 articles).
  4. Titres et méta-descriptions écrits à la main pour les fiches déjà vues dans Google (config/seo_manuels.json),
     prioritaires sur tout le reste.
Rien n'est inventé : tout vient des profils déjà affichés sur les fiches, ou du fichier manuel.
"""
import html, json, os, re
from collections import defaultdict

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
MANUELS = os.path.join(RACINE, "config", "seo_manuels.json")

e = lambda x: html.escape(x, quote=False)  # noqa: E731


def seo_manuels():
    if not os.path.exists(MANUELS):
        return {}
    return json.load(open(MANUELS, encoding="utf-8")).get("fiches", {})


def joli(xs, et):
    xs = [x for x in xs if x]
    if not xs:
        return ""
    return xs[0] if len(xs) == 1 else "%s %s %s" % (", ".join(xs[:-1]), et, xs[-1])


TYPES = [  # (début du type dans le titre, FR avec article, NL, féminin ?)
    ("Eau de Parfum", "une eau de parfum", "een eau de parfum", True),
    ("Eau de Toilette", "une eau de toilette", "een eau de toilette", True),
    ("Eau de Cologne", "une eau de Cologne", "een eau de cologne", True),
    ("Eau Fraîche", "une eau fraîche", "een eau fraîche", True),
    ("Extrait de Parfum", "un extrait de parfum", "een extrait de parfum", False),
    ("Parfum", "un parfum", "een parfum", False),
]


def decouper(p):
    """« Jo Malone Wood Sage & Sea Salt — Eau de Cologne mixte » → nom court, type, genre."""
    t_fr = p["titre_fr"]
    tete, _, queue = t_fr.partition(" — ")
    marque = p.get("marque") or ""
    nom = tete[len(marque):].strip() if marque and tete.lower().startswith(marque.lower() + " ") else tete
    typ = next((x for x in TYPES if queue.startswith(x[0])), None)
    genre = "homme" if queue.endswith("pour homme") else "femme" if queue.endswith("pour femme") else \
        "mixte" if queue.endswith("mixte") else ""
    return nom, tete, typ, genre


def intro(p, prof, nl):
    from site_variantes import LIB
    i = 1 if nl else 0
    nom, complet, typ, genre = decouper(p)
    if not typ:
        return ""
    marque = p.get("marque") or ""
    lib = lambda cle, codes: [LIB[cle][c][i] for c in codes or [] if c in LIB[cle]]  # noqa: E731
    phrases = []
    a, pf = prof.get("a"), prof.get("pf") or []
    if nl:
        g = {"homme": " voor heren", "femme": " voor dames", "mixte": " (unisex)"}.get(genre, "")
        s = "%s is %s%s van %s" % (nom, typ[2], g, marque)
        if a:
            s += ", uitgebracht in %d" % a
        if pf:
            s += (" en gecreëerd door " if a else ", gecreëerd door ") + joli(pf, "en")
        phrases.append(s + ".")
    else:
        g = {"homme": " pour homme", "femme": " pour femme", "mixte": " mixte"}.get(genre, "")
        s = "%s est %s%s %s%s" % (nom, typ[1], g, "d'" if re.match(r"[aeiouyhAEIOUYÉÈH]", marque) and not marque.startswith(("H", "h")) else "de ", marque)
        if a:
            s += ", %s en %d" % ("sortie" if typ[3] else "sorti", a)
        if pf:
            s += (" et %s par " % ("signée" if typ[3] else "signé") if a else ", %s par " % ("signée" if typ[3] else "signé")) + joli(pf, "et")
        phrases.append(s + ".")
    ac, v = lib("ac", (prof.get("ac") or [])[:3]), lib("v", (prof.get("v") or [])[:2])
    if ac:  # certains accords sont des noms (rose, cuir, oud…) : liste, pas adjectif
        phrases.append(("Belangrijkste akkoorden: %s." if nl else "Accords dominants : %s.") % joli(ac, "en" if nl else "et"))
    if v:
        phrases.append(("Een geur met een %s karakter." if nl else "Un parfum au caractère %s.") % joli(v, "en" if nl else "et"))
    n = prof.get("nn" if nl else "nf") or {}
    # minuscule au début des notes, sauf sigles et, en néerlandais, adjectifs de lieu (« Bulgaarse roos », « Calabrische bergamot »)
    low = lambda xs: [x if x[:2].isupper() or (nl and re.match(r"[A-Z]\w+(s|sch|isch)e\b", x)) else x[:1].lower() + x[1:]  # noqa: E731
                      for x in (xs or [])][:3]
    t, c, f, plat = low(n.get("t")), low(n.get("c")), low(n.get("f")), low(n.get("n"))
    if t or c or f:
        if nl:
            bouts = (["het opent met %s" % joli(t, "en")] if t else []) + (["het hart bevat %s" % joli(c, "en")] if c else []) + \
                    (["de basis is %s" % joli(f, "en")] if f else [])
            phrases.append(joli(bouts, "en")[:1].upper() + joli(bouts, "en")[1:] + ".")
        else:
            bouts = (["il s'ouvre sur %s" % joli(t, "et")] if t else []) + (["son cœur mêle %s" % joli(c, "et")] if c else []) + \
                    (["le fond repose sur %s" % joli(f, "et")] if f else [])
            phrases.append(joli(bouts, "et")[:1].upper() + joli(bouts, "et")[1:] + ".")
    elif plat:
        phrases.append(("Belangrijkste noten: %s." if nl else "Notes principales : %s.") % joli(plat, "en" if nl else "et"))
    sais = [x for x in ("printemps", "ete", "automne", "hiver") if x in (prof.get("s") or [])]
    occ = lib("o", (prof.get("o") or [])[:3])
    if sais or occ:
        if nl:
            s = "Ideaal %s" % joli(["in de " + LIB["s"][x][1] for x in sais], "en") if sais and len(sais) < 4 else \
                "Draagbaar het hele jaar" if sais else "Ideaal"
            phrases.append(s + ((", voor " if sais else " voor ") + joli(occ, "en") if occ else "") + ".")
        else:
            pre = {"printemps": "au printemps", "ete": "en été", "automne": "en automne", "hiver": "en hiver"}
            s = "À porter surtout %s" % joli([pre[x] for x in sais], "et") if sais and len(sais) < 4 else \
                "À porter toute l'année" if sais else "Idéal"
            phrases.append(s + ((", pour " if sais else " pour ") + joli(occ, "et") if occ else "") + ".")
    return "<p>%s</p>" % e(" ".join(phrases))


def _cle_nom(p):
    return re.sub(r"[^a-z0-9]", "", decouper(p)[1].lower())


def similaires(vus, profils, n=4):
    """Pour chaque fiche : jusqu'à n fiches en ligne, même genre (ou mixte), au moins 2 accords en commun,
    autre parfum (pas une autre concentration du même), 2 fiches maximum de la même marque."""
    infos = {}
    par_accord = defaultdict(set)
    for p in vus:
        prof = profils.get(p["handle"])
        if not prof or not decouper(p)[2]:
            continue
        ac = set(prof.get("ac") or [])
        notes = {x.lower() for k in ("t", "c", "f", "n") for x in (prof.get("nf") or {}).get(k) or []}
        infos[p["handle"]] = (p, ac, notes, set(prof.get("s") or []), decouper(p)[3], _cle_nom(p))
        for a in ac:
            par_accord[a].add(p["handle"])
    res = {}
    for h, (p, ac, notes, sais, genre, nomc) in infos.items():
        cands = set()
        for a in ac:
            cands |= par_accord[a]
        scores = []
        for h2 in cands:
            if h2 == h:
                continue
            p2, ac2, notes2, sais2, genre2, nomc2 = infos[h2]
            if nomc2 == nomc or (genre and genre2 and genre != genre2 and "mixte" not in (genre, genre2)):
                continue
            ca = len(ac & ac2)
            if ca < 2:
                continue
            scores.append((-(3 * ca + len(notes & notes2) + (1 if sais & sais2 else 0)), p2["titre_fr"], h2))
        scores.sort()
        choix, par_marque, noms = [], defaultdict(int), set()
        for _, _, h2 in scores:
            p2 = infos[h2][0]
            if par_marque[p2.get("marque")] >= 2 or infos[h2][5] in noms:
                continue
            choix.append(p2)
            par_marque[p2.get("marque")] += 1
            noms.add(infos[h2][5])
            if len(choix) >= n:
                break
        if choix:
            res[h] = choix
    return res


def bloc_similaires(p, choix, nl):
    nom = decouper(p)[0]
    liens = ['<a href="%s/products/%s">%s</a>' % ("/nl" if nl else "", x["handle"], e(decouper(x)[1])) for x in choix]
    if nl:
        return '<div class="qk-desc-proches"><h3>In dezelfde sfeer</h3><p>Hou je van %s? Ontdek ook %s.</p></div>' % (e(nom), joli(liens, "en"))
    return '<div class="qk-desc-proches"><h3>Dans le même esprit</h3><p>Tu aimes %s ? Découvre aussi %s.</p></div>' % (e(nom), joli(liens, "et"))


FIN_FR = (("100 % authentique, livré partout en Belgique.", "100 % authentique, livraison offerte en Belgique dès 2 articles."),
          ("100 % authentique et neuf, livré partout en Belgique. Paiement Bancontact.",
           "100 % authentique et neuf. Livraison offerte en Belgique dès 2 articles."))
FIN_NL = (("100% origineel, geleverd in heel België.", "100% origineel, gratis levering in België vanaf 2 artikelen."),
          ("100% origineel en nieuw, geleverd in heel België. Betalen met Bancontact.",
           "100% origineel en nieuw. Gratis levering in België vanaf 2 artikelen."))


def nouvelle_meta(d, fins):
    for ancien, neuf in fins:
        if d.endswith(ancien):
            debut = d[:-len(ancien)].rstrip()
            place = 155 - len(neuf) - 1
            if len(debut) > place:  # on raccourcit la liste des notes plutôt que la promesse de livraison
                debut = debut[:place].rsplit(",", 1)[0].rstrip(" ,.:") + "."
            return (debut + " " + neuf).strip()
    return d


def enrichir(vus, journal=print):
    from site_variantes import profil_fi, descriptions_riches
    import site_soleluna as sl
    riches = descriptions_riches()
    profils = {}
    for p in vus:
        prof = profil_fi(sl.slug(p["titre_fr"])[:200])
        if prof:
            profils[p["handle"]] = prof
    proches = similaires(vus, profils)
    man = seo_manuels()
    n_intro = n_proches = n_man = 0
    for p in vus:
        prof = profils.get(p["handle"])
        if prof and sl.slug(p["titre_fr"])[:200] not in riches:
            i_fr, i_nl = intro(p, prof, False), intro(p, prof, True)
            if i_fr:
                p["desc_fr"], p["desc_nl"] = i_fr + p["desc_fr"], i_nl + p["desc_nl"]
                n_intro += 1
        if p["handle"] in proches:
            p["desc_fr"] += bloc_similaires(p, proches[p["handle"]], False)
            p["desc_nl"] += bloc_similaires(p, proches[p["handle"]], True)
            n_proches += 1
        if p.get("seo_desc_fr"):
            p["seo_desc_fr"] = nouvelle_meta(p["seo_desc_fr"], FIN_FR)
        if p.get("seo_desc_nl"):
            p["seo_desc_nl"] = nouvelle_meta(p["seo_desc_nl"], FIN_NL)
        m = man.get(re.sub(r"-\d+$", "", p["handle"])) or man.get(p["handle"])
        if m:
            for cle in ("seo_titre_fr", "seo_titre_nl", "seo_desc_fr", "seo_desc_nl"):
                if m.get(cle):
                    p[cle] = m[cle]
            n_man += 1
    journal("Fiches enrichies : introduction %d · « Dans le même esprit » %d · titres manuels %d (sur %d fiches en ligne)"
            % (n_intro, n_proches, n_man, len(vus)))
    return vus
