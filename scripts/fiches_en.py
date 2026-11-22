#!/usr/bin/env python3
"""Version anglaise des fiches (22/11/2026, Amine : version anglaise du site, « fait le 5 »).

Ajoute à chaque fiche préparée (site_variantes.produit + seo_fiches.enrichir) : titre_en, type_en, desc_en,
seo_titre_en, seo_desc_en. Tout est construit à partir des mêmes données vérifiées que le français (profil du parfum,
description vérifiée : notes, famille, année, parfumeurs), avec les notes traduites dans config/notes_en.json.
Les paragraphes rédigés à la main en français (descriptions vérifiées) ne sont pas traduits : la fiche anglaise
reprend leurs faits (famille, notes, année, parfumeurs). Rien n'est inventé.
Appelé par site_synchro.textes() (action theme « textes-fiches »), puis site_variantes.traduire(..., locale="en")."""
import html, json, os, re

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
e = lambda x: html.escape(x, quote=False)  # noqa: E731
_NOTES = None

GENRE_EN = {"homme": "for men", "femme": "for women", "mixte": "unisex", "enfant": "for children"}
CAT_EN = {"Parfums femme": "Women's fragrances", "Parfums homme": "Men's fragrances", "Parfums mixtes": "Unisex fragrances",
          "Parfums enfants": "Children's fragrances", "Parfums": "Fragrances", "Coffrets": "Gift sets", "Testeurs": "Testers",
          "Cheveux": "Hair care", "Déodorants": "Deodorants", "Homme": "Men's grooming", "Maquillage": "Make-up",
          "Soins du visage": "Face care", "Soins du corps": "Body care", "Solaires et autobronzants": "Sun care and self-tanners",
          "Maison": "Home fragrance"}
LIB_EN = {
    "s": {"printemps": "spring", "ete": "summer", "automne": "autumn", "hiver": "winter"},
    "t": {"legere": "light", "moyenne": "moderate", "longue": "long", "journee": "all day", "lendemain": "until the next day"},
    "si": {"discret": "subtle", "modere": "moderate", "fort": "strong", "tres_fort": "very strong"},
    "o": {"quotidien": "every day", "bureau": "the office", "rdv": "a date", "diner": "a dinner", "soiree": "evenings out",
          "mariage": "a wedding", "sport": "sport", "vacances": "holidays", "chic": "a smart event", "detente": "relaxing"},
    "v": {"cozy": "cosy", "sensual": "sensual", "elegant": "elegant", "energetic": "energetic", "romantic": "romantic",
          "calm": "calming", "playful": "playful", "fresh": "fresh", "bold": "bold", "mysterious": "mysterious"},
    "ac": {"aldehyde": "aldehydic", "amande": "almond", "ambre": "amber", "animal": "animalic", "aquatique": "aquatic",
           "aromatique": "aromatic", "balsamique": "balsamic", "alcool": "boozy", "caramel": "caramel", "chocolat": "chocolate",
           "cannelle": "cinnamon", "agrumes": "citrus", "coco": "coconut", "cafe": "coffee", "terreux": "earthy", "floral": "floral",
           "frais": "fresh", "epice_frais": "fresh spicy", "fruite": "fruity", "gourmand": "gourmand", "vert": "green",
           "miel": "honey", "iris": "iris", "jasmin": "jasmine", "lacte": "milky", "lavande": "lavender", "cuir": "leather",
           "mousse": "mossy", "muguet": "lily of the valley", "musque": "musky", "noisette": "nutty", "oud": "oud",
           "ozonique": "ozonic", "patchouli": "patchouli", "peche": "peach", "pistache": "pistachio", "poudre": "powdery",
           "rose": "rose", "fume": "smoky", "epice_doux": "soft spicy", "sucre": "sweet", "the": "tea", "tabac": "tobacco",
           "tropical": "tropical", "tubereuse": "tuberose", "vanille": "vanilla", "violette": "violet",
           "epice_chaud": "warm spicy", "fleurs_blanches": "white flowers", "boise": "woody", "fleurs_jaunes": "yellow flowers"},
}
SOINS_EN = None


def joli(xs, et="and"):
    xs = [x for x in xs if x]
    if not xs:
        return ""
    return xs[0] if len(xs) == 1 else "%s %s %s" % (", ".join(xs[:-1]), et, xs[-1])


def dico():
    global _NOTES
    if _NOTES is None:
        f = os.path.join(RACINE, "config", "notes_en.json")
        _NOTES = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {"notes": {}, "familles": {}}
    return _NOTES


def note(n):
    """Note FR -> EN ; inconnue : on la garde telle quelle (souvent un nom propre ou une molécule)."""
    t = dico()["notes"].get(n.strip().lower())
    return t if t else n.strip()


def notes(xs):
    return [note(x) for x in (xs or []) if x]


def soins_en():
    global SOINS_EN
    if SOINS_EN is None:
        import site_soleluna as sl
        SOINS_EN = {fr: en.title().replace("'S", "'s") for en, (fr, nl) in sl.SOINS.items()}
        SOINS_EN.update({"Lait corporel": "Body Lotion", "Brume parfumée": "Body Mist", "Après-rasage": "Aftershave"})
    return SOINS_EN


def titre_en(t_fr):
    """« Creed Aventus — Eau de Parfum pour homme » -> « Creed Aventus — Eau de Parfum for men »."""
    tete, sep, queue = t_fr.partition(" — ")
    if not sep:
        return t_fr
    q = queue
    q = re.sub(r"\bpour femme\b", "for women", q)
    q = re.sub(r"\bpour homme\b", "for men", q)
    q = re.sub(r"\bpour enfants?\b", "for children", q)
    if re.search(r" mixte\b", q) and not q.startswith("coffret"):
        q = "Unisex " + re.sub(r" mixte\b", "", q)
    q = re.sub(r"\bmixte\b", "unisex", q)
    q = re.sub(r"^coffret\b", "gift set", q)
    for fr, en in sorted(soins_en().items(), key=lambda x: -len(x[0])):
        if q.startswith(fr):
            q = en + q[len(fr):]
            break
    return "%s — %s" % (tete, q)


def formats(p):
    vols, testeur, abime = [], False, False
    for v in p.get("variantes") or []:
        f = v.get("format_fr") or ""
        base = f.split(" – ")[0].split(" · ")[0]
        if base and base != "Taille unique" and base not in vols:
            vols.append(base)
        testeur |= " – testeur" in f
        abime |= " – boîte abîmée" in f
    return vols, testeur, abime


def intro_profil(p, prof, nom, typ, genre, marque):
    ph = []
    s = "%s is %s %s%s by %s" % (nom, "an" if typ[0][:1] in "AEIOU" else "a", typ[0],
                                 {"homme": " for men", "femme": " for women", "mixte": " (unisex)"}.get(genre, ""), marque)
    if prof.get("a"):
        s += ", launched in %d" % prof["a"]
    if prof.get("pf"):
        s += (" and created by " if prof.get("a") else ", created by ") + joli(prof["pf"])
    ph.append(s + ".")
    ac = [LIB_EN["ac"][c] for c in (prof.get("ac") or [])[:3] if c in LIB_EN["ac"]]
    if ac:
        ph.append("Main accords: %s." % joli(ac))
    v = [LIB_EN["v"][c] for c in (prof.get("v") or [])[:2] if c in LIB_EN["v"]]
    if v:
        ph.append("A fragrance with a %s character." % joli(v))
    n = prof.get("nf") or {}
    t, c, f, plat = notes(n.get("t"))[:3], notes(n.get("c"))[:3], notes(n.get("f"))[:3], notes(n.get("n"))[:3]
    if t or c or f:
        b = (["it opens with %s" % joli(t)] if t else []) + (["the heart blends %s" % joli(c)] if c else []) + \
            (["the base rests on %s" % joli(f)] if f else [])
        x = joli(b)
        ph.append(x[:1].upper() + x[1:] + ".")
    elif plat:
        ph.append("Main notes: %s." % joli(plat))
    sais = [LIB_EN["s"][x] for x in ("printemps", "ete", "automne", "hiver") if x in (prof.get("s") or [])]
    occ = [LIB_EN["o"][c] for c in (prof.get("o") or [])[:3] if c in LIB_EN["o"]]
    if sais or occ:
        s = ("Best worn in %s" % joli(sais) if sais and len(sais) < 4 else "Wearable all year round" if sais else "Ideal")
        ph.append(s + ((", for " if sais else " for ") + joli(occ) if occ else "") + ".")
    return "<p>%s</p>" % e(" ".join(ph))


def intro_riche(r, nom, typ, genre, marque):
    ph = []
    s = "%s is %s%s by %s" % (nom, ("an " if typ[0][:1] in "AEIOU" else "a ") + typ[0] if typ else "a fragrance",
                              {"homme": " for men", "femme": " for women", "mixte": " (unisex)"}.get(genre, ""), marque)
    if r.get("annee"):
        s += ", launched in %d" % r["annee"]
    if r.get("parfumeurs"):
        s += (" and created by " if r.get("annee") else ", created by ") + joli(r["parfumeurs"])
    ph.append(s + ".")
    fam = dico()["familles"].get(r.get("famille_fr") or "")
    if fam:
        ph.append("Olfactory family: %s." % fam.lower())
    n = r.get("notes_fr") or {}
    t, c, f = notes(n.get("tete"))[:4], notes(n.get("coeur"))[:4], notes(n.get("fond"))[:4]
    if t or c or f:
        b = (["it opens with %s" % joli(t)] if t else []) + (["the heart blends %s" % joli(c)] if c else []) + \
            (["the base rests on %s" % joli(f)] if f else [])
        x = joli(b)
        ph.append(x[:1].upper() + x[1:] + ".")
    k = notes(n.get("cle"))[:3]
    if k:
        ph.append("Signature notes: %s." % joli(k))
    return "<p>%s</p>" % e(" ".join(ph))


def bloc_profil(prof):
    m = []
    n = prof.get("nf") or {}
    lignes = [("Top notes", n.get("t")), ("Heart notes", n.get("c")), ("Base notes", n.get("f")), ("Notes", n.get("n"))]
    lignes = ["<strong>%s:</strong> %s" % (k, e(", ".join(notes(v)))) for k, v in lignes if v]
    if lignes:
        m.append("<h3>Fragrance notes</h3><p>%s</p>" % "<br>".join(lignes))
    f = []
    if prof.get("ac"):
        f.append("Olfactory family: " + ", ".join(LIB_EN["ac"][c] for c in prof["ac"] if c in LIB_EN["ac"]))
    if prof.get("v"):
        f.append("Mood: " + ", ".join(LIB_EN["v"][c] for c in prof["v"] if c in LIB_EN["v"]))
    if prof.get("s"):
        f.append("Best season: " + ", ".join(LIB_EN["s"][c] for c in prof["s"] if c in LIB_EN["s"]))
    if prof.get("t") in LIB_EN["t"]:
        f.append("Longevity: " + LIB_EN["t"][prof["t"]])
    if prof.get("si") in LIB_EN["si"]:
        f.append("Sillage: " + LIB_EN["si"][prof["si"]])
    if prof.get("o"):
        f.append("Ideal for: " + ", ".join(LIB_EN["o"][c] for c in prof["o"] if c in LIB_EN["o"]))
    if prof.get("a"):
        f.append("Launched in %d" % prof["a"])
    if prof.get("pf"):
        f.append(("Perfumer: " if len(prof["pf"]) == 1 else "Perfumers: ") + ", ".join(prof["pf"]))
    if f:
        m.append("<p>%s.</p>" % e(". ".join(f)))
    return '<div class="qk-desc-profil">%s</div>' % "".join(m) if m else ""


def coupe(d, n=155):
    return d if len(d) <= n else d[:n - 3].rsplit(" ", 1)[0] + "…"


def seo_titre(t):
    t = t.replace(" — ", " ")
    if len(t) <= 60:
        return t
    t2 = re.sub(r" (for (men|women|children)|unisex)$", "", t).replace(" Unisex ", " ")
    if len(t2) <= 60:
        return t2
    t3 = t2.replace("Eau de Parfum", "EDP").replace("Eau de Toilette", "EDT")
    return t3 if len(t3) <= 60 else t3[:61].rsplit(" ", 1)[0]


def completer(vus, journal=print):
    from seo_fiches import decouper
    from site_variantes import profil_fi, descriptions_riches
    import site_soleluna as sl
    riches = descriptions_riches()
    n = 0
    for p in vus:
        t_en = titre_en(p["titre_fr"])
        p["titre_en"] = t_en
        p["type_en"] = CAT_EN.get(p.get("type_fr"), p.get("type_fr"))
        nom, tete, typ, genre = decouper(p)
        marque = p.get("marque") or ""
        cle = sl.slug(p["titre_fr"])[:200]
        prof, riche = profil_fi(cle), riches.get(cle)
        morceaux, notes_seo = [], []
        if riche and typ:
            morceaux.append(intro_riche(riche, nom, typ, genre, marque))
            nr = riche.get("notes_fr") or {}
            notes_seo = notes([x for k in ("tete", "coeur", "fond", "cle") for x in nr.get(k) or []])[:3]
        elif prof and typ:
            morceaux.append(intro_profil(p, prof, nom, typ, genre, marque))
        if prof:
            nf = prof.get("nf") or {}
            notes_seo = notes_seo or notes([x for k in ("t", "c", "f", "n") for x in nf.get(k) or []])[:3]
        vols, testeur, abime = formats(p)
        if typ:
            b = "%s %s by %s, %s." % (typ[0], nom, marque, "a unisex fragrance" if genre == "mixte" else
                                      ("a fragrance " + GENRE_EN[genre]) if genre in GENRE_EN else "a fragrance")
        else:
            b = "%s by %s." % (t_en.split(" — ")[0][len(marque):].strip() or t_en, marque)
        if len(vols) > 1:
            b += " Available in %s." % joli(vols)
        elif vols and typ:
            b += " %s bottle." % vols[0]
        if p.get("teintes"):
            b += " Several shades available."
        if testeur:
            b += " “Tester” size: the same product as the one sold in shops, in simple packaging, often without a cap."
        if abime:
            b += " “Damaged box” size: the original box is damaged, the product itself is brand-new and intact."
        b += " Genuine, brand-new product. Delivered in Belgium and 8 other European countries."
        morceaux.append("<p>%s</p>" % e(b))
        if prof:
            morceaux.append(bloc_profil(prof))
        choix = p.get("_proches") or []
        if choix:
            liens = ['<a href="/en/products/%s">%s</a>' % (x["handle"], e(decouper(x)[1])) for x in choix]
            morceaux.append('<div class="qk-desc-proches"><h3>In the same spirit</h3><p>Love %s? Discover %s too.</p></div>'
                            % (e(nom), joli(liens)))
        p["desc_en"] = "".join(morceaux)
        p["seo_titre_en"] = seo_titre(t_en)
        nm = t_en.replace(" — ", ", ")
        fin = "100% authentic, delivered in 9 European countries."
        p["seo_desc_en"] = coupe("%s. Notes: %s. %s" % (nm, ", ".join(notes_seo), fin)
                                 if notes_seo else "%s%s. %s" % (nm, (", " + joli(vols)) if vols else "", fin))
        n += 1
    journal("Fiches en anglais préparées : %d" % n)
    return vus
