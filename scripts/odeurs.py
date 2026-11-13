#!/usr/bin/env python3
"""Recherche par odeurs (12/11/2026, idée d'un client, demande d'Amine).

Regroupe les notes brutes des parfums (config/descriptions_parfums.json, ~500 notes différentes) en ~60 odeurs
compréhensibles (FR + NL), rangées par famille, et produit l'index utilisé par :
  - la page /pages/odeurs (le client choisit jusqu'à 3 odeurs) ;
  - le bloc « Parfums aux notes proches » des fiches.
Chaque famille a aussi une odeur « toute la famille » (ex. « Tous les agrumes »).

Lancer seul pour voir la couverture :  python3 scripts/odeurs.py
"""
import json, os, re

ICI = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(os.path.dirname(ICI), "config", "descriptions_parfums.json")

# (id famille, FR, NL)
FAMILLES = [
    ("agrumes", "Agrumes", "Citrus"),
    ("fleurs", "Fleurs", "Bloemen"),
    ("fruits", "Fruits", "Fruit"),
    ("gourmand", "Gourmand", "Zoet & gourmand"),
    ("epices", "Épices", "Kruiden & specerijen"),
    ("bois", "Boisé", "Hout"),
    ("ambre", "Ambré & oriental", "Amber & oosters"),
    ("frais", "Frais & aromatique", "Fris & aromatisch"),
]
TOUT = {"agrumes": ("Tous les agrumes", "Alle citrus"), "fleurs": ("Toutes les fleurs", "Alle bloemen"),
        "fruits": ("Tous les fruits", "Alle fruit"), "gourmand": ("Tout le gourmand", "Alles zoet"),
        "epices": ("Toutes les épices", "Alle specerijen"), "bois": ("Tous les bois", "Alle houtgeuren"),
        "ambre": ("Tout l'ambré", "Alles amber"), "frais": ("Tout le frais", "Alles fris")}

# (id, famille, FR, NL, motifs regex sur la note en minuscules). Une note peut tomber dans plusieurs odeurs.
ODEURS = [
    ("bergamote", "agrumes", "Bergamote", "Bergamot", [r"bergamote"]),
    ("citron", "agrumes", "Citron", "Citroen", [r"citron(?!nier)", r"limette", r"yuzu", r"c[ée]drat", r"lits[ée]e"]),
    ("orange", "agrumes", "Orange & mandarine", "Sinaasappel & mandarijn",
     [r"\boranges?\b", r"mandarine", r"cl[ée]mentine", r"tangerine", r"bigarade", r"kumquat", r"petitgrain"]),
    ("pamplemousse", "agrumes", "Pamplemousse", "Grapefruit", [r"pamplemousse", r"pomelo"]),
    ("_agrumes", "agrumes", None, None, [r"agrumes", r"hesp[ée]rid"]),

    ("rose", "fleurs", "Rose", "Roos", [r"^(?!.*(poivre|bois de rose|pamplemousse|lotus|baies? roses?)).*\broses?\b", r"pomarose"]),
    ("jasmin", "fleurs", "Jasmin", "Jasmijn", [r"jasmin", r"sambac"]),
    ("fleur_oranger", "fleurs", "Fleur d'oranger & néroli", "Oranjebloesem & neroli", [r"fleur d'oranger", r"n[ée]roli"]),
    ("iris", "fleurs", "Iris", "Iris", [r"\biris\b"]),
    ("violette", "fleurs", "Violette", "Viooltje", [r"violette"]),
    ("tubereuse", "fleurs", "Tubéreuse", "Tuberoos", [r"tub[ée]reuse"]),
    ("ylang", "fleurs", "Ylang-ylang", "Ylang-ylang", [r"ylang"]),
    ("muguet", "fleurs", "Muguet", "Lelietje-van-dalen", [r"muguet"]),
    ("pivoine", "fleurs", "Pivoine", "Pioenroos", [r"pivoine"]),
    ("fleurs_blanches", "fleurs", "Fleurs blanches", "Witte bloemen",
     [r"fleurs blanches", r"gard[ée]nia", r"frangipan", r"tiar[ée]", r"magnolia", r"\blys\b", r"seringa", r"ch[èe]vrefeuille", r"lotus"]),
    ("geranium", "fleurs", "Géranium", "Geranium", [r"g[ée]ranium"]),
    ("heliotrope", "fleurs", "Héliotrope & poudré", "Heliotroop & poederig", [r"h[ée]liotrope", r"notes poudr[ée]es", r"mimosa", r"aldéhyde", r"ald[ée]hydes"]),
    ("orchidee", "fleurs", "Orchidée", "Orchidee", [r"orchid[ée]e"]),
    ("osmanthus", "fleurs", "Osmanthus", "Osmanthus", [r"osmanthus"]),
    ("_fleurs", "fleurs", None, None, [r"notes florales", r"^fleurs?$", r"accord floral", r"fleurs exotiques", r"freesia", r"œillet", r"narcisse", r"jonquille",
                                      r"cyclamen", r"jacinthe", r"lilas", r"camomille", r"immortelle", r"fleur de ", r"dahlia", r"souci", r"pois de senteur", r"aub[ée]pine"]),

    ("pomme", "fruits", "Pomme", "Appel", [r"\bpommes?\b(?! de)"]),
    ("poire", "fruits", "Poire", "Peer", [r"\bpoire\b"]),
    ("peche", "fruits", "Pêche & abricot", "Perzik & abrikoos", [r"p[êe]che\b", r"abricot", r"^nectar$", r"mirabelle"]),
    ("fruits_rouges", "fruits", "Fruits rouges", "Rood fruit",
     [r"fruits rouges", r"framboise", r"fraise", r"cerise", r"griotte", r"\bm[ûu]re\b", r"myrtille", r"groseille", r"baies sauvages", r"grenade"]),
    ("cassis", "fruits", "Cassis", "Zwarte bes", [r"cassis"]),
    ("tropical", "fruits", "Fruits exotiques", "Tropisch fruit",
     [r"ananas", r"mangue", r"passion", r"litchi", r"goyave", r"passiflore", r"pitaya", r"banane", r"tropicaux", r"fruit du dragon", r"kaki"]),
    ("prune", "fruits", "Prune & fruits secs", "Pruim & gedroogd fruit", [r"\bprune\b", r"dattes?", r"fruits secs", r"raisin", r"fruits confits"]),
    ("figue", "fruits", "Figue", "Vijg", [r"figu"]),
    ("melon", "fruits", "Melon & pastèque", "Meloen & watermeloen", [r"melon", r"past[èe]que"]),
    ("_fruits", "fruits", None, None, [r"notes fruit[ée]es", r"^fruits$", r"fruits (jaunes|m[ée]diterran)", r"coing", r"\bbaies?\b(?! ros)", r"rhubarbe"]),

    ("vanille", "gourmand", "Vanille", "Vanille", [r"vanill"]),
    ("tonka", "gourmand", "Fève tonka", "Tonkaboon", [r"tonka", r"coumarine"]),
    ("caramel", "gourmand", "Caramel & praliné", "Karamel & praliné",
     [r"caramel", r"pralin", r"\bsucres?\b", r"sucre roux", r"guimauve", r"barbe [àa] papa", r"confiture de lait", r"bonbon", r"notes sucr[ée]es",
      r"canne [àa] sucre", r"loukoum", r"chewing", r"sp[ée]culoos", r"biscuit", r"knafeh", r"tiramisu", r"tarte", r"s'mores"]),
    ("chocolat", "gourmand", "Chocolat & cacao", "Chocolade & cacao", [r"chocolat", r"cacao"]),
    ("cafe", "gourmand", "Café", "Koffie", [r"caf[ée]\b"]),
    ("miel", "gourmand", "Miel", "Honing", [r"\bmiel\b", r"cire d'abeille"]),
    ("amande", "gourmand", "Amande & noisette", "Amandel & hazelnoot", [r"amande", r"pistache", r"noisette", r"amaretto", r"ch[âa]taigne"]),
    ("coco", "gourmand", "Noix de coco", "Kokos", [r"coco\b"]),
    ("lait", "gourmand", "Lait & crème", "Melk & room", [r"\blait\b", r"lact[ée]", r"cr[èe]me", r"mascarpone", r"chantilly", r"kulfi"]),
    ("alcool", "gourmand", "Rhum & cognac", "Rum & cognac", [r"rhum", r"cognac", r"whisky", r"brandy", r"liqueur", r"bellini", r"absinthe"]),
    ("_gourmand", "gourmand", None, None, [r"gourmand", r"r[ée]glisse", r"cola"]),

    ("cannelle", "epices", "Cannelle", "Kaneel", [r"cannelle"]),
    ("cardamome", "epices", "Cardamome", "Kardemom", [r"cardamome"]),
    ("safran", "epices", "Safran", "Saffraan", [r"safran"]),
    ("poivre", "epices", "Poivre & baies roses", "Peper & roze bessen", [r"poivre", r"baies? roses?", r"piment"]),
    ("gingembre", "epices", "Gingembre", "Gember", [r"gingembre"]),
    ("muscade", "epices", "Muscade & clou de girofle", "Nootmuskaat & kruidnagel", [r"muscade", r"girofle", r"anis"]),
    ("_epices", "epices", None, None, [r"[ée]pices?", r"notes [ée]pic[ée]es", r"cumin", r"carvi", r"coriandre", r"curcuma", r"paprika", r"fenugrec"]),

    ("santal", "bois", "Santal", "Sandelhout", [r"santal"]),
    ("cedre", "bois", "Cèdre", "Ceder", [r"c[èe]dre(?!s? de l'atlas)", r"c[èe]dre"]),
    ("vetiver", "bois", "Vétiver", "Vetiver", [r"v[ée]tiver"]),
    ("patchouli", "bois", "Patchouli", "Patchoeli", [r"patchouli"]),
    ("oud", "bois", "Oud", "Oud", [r"\boud\b"]),
    ("bois_fumes", "bois", "Bois fumés", "Rokerig hout",
     [r"ga[ïi]ac", r"bouleau", r"\bcade\b", r"fum[ée]e", r"fum[ée]", r"poudre [àa] canon"]),
    ("mousse", "bois", "Mousse de chêne", "Eikenmos", [r"\bmousse", r"ch[êe]ne"]),
    ("_bois", "bois", None, None, [r"\bbois\b", r"bois[ée]", r"cashmeran", r"cachemire", r"akigalawood", r"nagarmotha", r"cypriol", r"papyrus",
                                  r"teck", r"[ée]b[èe]ne", r"palissandre", r"amyris", r"palo santo", r"clearwood", r"sycomore", r"orme", r"olivier"]),

    ("ambre", "ambre", "Ambre", "Amber", [r"ambre(?! gris)", r"ambroxa?n?", r"ambrox", r"labdanum", r"ciste", r"cetalox", r"ambrocénide", r"ambrofix"]),
    ("ambre_gris", "ambre", "Ambre gris", "Ambergris", [r"ambre gris"]),
    ("encens", "ambre", "Encens & myrrhe", "Wierook & mirre", [r"encens", r"oliban", r"myrrhe", r"[ée]l[ée]mi", r"copal", r"r[ée]sines?"]),
    ("baumes", "ambre", "Benjoin & baumes", "Benzoë & balsems", [r"benjoin", r"baume", r"styrax", r"opoponax", r"balsamique"]),
    ("musc", "ambre", "Musc", "Musk", [r"\bmuscs?\b", r"ambrette"]),
    ("cuir", "ambre", "Cuir", "Leer", [r"cuir", r"daim", r"castor[ée]um"]),
    ("tabac", "ambre", "Tabac", "Tabak", [r"tabac"]),
    ("_ambre", "ambre", None, None, [r"notes orientales", r"notes animales", r"notes balsamiques"]),

    ("lavande", "frais", "Lavande", "Lavendel", [r"lavand"]),
    ("menthe", "frais", "Menthe", "Munt", [r"menthe"]),
    ("sauge", "frais", "Sauge", "Salie", [r"sauge"]),
    ("herbes", "frais", "Romarin & herbes", "Rozemarijn & kruiden",
     [r"romarin", r"\bthym\b", r"basilic", r"estragon", r"origan", r"marjolaine", r"\bherbe\b", r"laurier", r"armoise", r"notes aromatiques",
      r"notes herbac[ée]es", r"hysope", r"verveine", r"myrte", r"fenouil", r"ang[ée]lique"]),
    ("marin", "frais", "Marin & salé", "Zee & zout",
     [r"marin", r"marine", r"aquatique", r"ozonique", r"\bsel\b", r"sal[ée]e?\b", r"algues", r"calone", r"eau de mer", r"min[ée]ral", r"aquozone", r"sable"]),
    ("vert", "frais", "Notes vertes", "Groene noten",
     [r"notes vertes", r"galbanum", r"feuilles? de violette", r"feuilles vertes", r"feuille de figuier", r"feuille de", r"feuilles de", r"herbe", r"foin",
      r"artichaut", r"ortie", r"gentiane", r"mat[ée]\b"]),
    ("the", "frais", "Thé", "Thee", [r"\bth[ée]\b"]),
    ("conifere", "frais", "Pin & genièvre", "Den & jeneverbes", [r"geni[èe]vre", r"\bpin\b", r"sapin", r"cypr[èe]s", r"thuya", r"eucalyptus"]),
    ("_frais", "frais", None, None, [r"notes solaires", r"\bfrais\b", r"fra[îi]ches?"]),
]

COMPILES = [(o[0], o[1], [re.compile(m) for m in o[4]]) for o in ODEURS]


def odeurs_de(note):
    n = note.lower().strip()
    return [oid for oid, _, motifs in COMPILES if any(m.search(n) for m in motifs)]


def construire_index():
    """Renvoie l'index : familles, odeurs (avec « toute la famille »), parfums {handle: "i,j,k|clés"}."""
    D = json.load(open(CONFIG, encoding="utf-8"))["parfums"] if os.path.exists(CONFIG) else {}
    # 13/11/2026 : notes des autres parfums du catalogue, tirées de Fragrance Index (config/notes_fi.json, scripts/fi_construire.py)
    fi = os.path.join(os.path.dirname(CONFIG), "notes_fi.json")
    if os.path.exists(fi):
        for h, v in json.load(open(fi, encoding="utf-8"))["parfums"].items():
            D.setdefault(h, v)
    liste = []  # odeurs affichées : [id, famille, fr, nl]
    for fid, ffr, fnl in FAMILLES:
        liste.append(["tout_" + fid, fid, TOUT[fid][0], TOUT[fid][1]])
        for oid, fam, fr, nl, _ in ODEURS:
            if fam == fid and fr:
                liste.append([oid, fam, fr, nl])
    rang = {o[0]: i for i, o in enumerate(liste)}
    fam_de = {o[0]: o[1] for o in ODEURS}
    parfums, compte = {}, {o[0]: 0 for o in liste}
    for h, d in D.items():
        n = d.get("notes_fr") or {}
        toutes, cles = set(), set()
        for k in ("tete", "coeur", "fond", "cle"):
            for note in n.get(k, []):
                for oid in odeurs_de(note):
                    ids = {"tout_" + fam_de[oid]} | ({oid} if not oid.startswith("_") else set())
                    toutes |= ids
                    if k == "cle":
                        cles |= ids
        if len(toutes) < 2:
            continue
        for x in toutes:
            compte[x] += 1
        parfums[h] = ",".join(str(rang[x]) for x in sorted(toutes, key=rang.get)) + "|" + ",".join(str(rang[x]) for x in sorted(cles, key=rang.get))
    return {"familles": [list(f) for f in FAMILLES], "odeurs": liste, "parfums": parfums}, compte


def fiches_en_ligne():
    """Fiches visibles sur la boutique (products.json public). Ensemble vide si la boutique ne répond pas."""
    import urllib.request
    h = set()
    try:
        for page in range(1, 60):
            r = json.load(urllib.request.urlopen(urllib.request.Request("https://qosmi.be/products.json?limit=250&page=%d" % page,
                                                                        headers={"User-Agent": "QosmiSynchro/1.0"}), timeout=30))
            if not r.get("products"):
                break
            h |= {x["handle"] for x in r["products"]}
    except Exception as e:
        print("fiches en ligne : %s" % e)
        return set()
    return h


def asset_js():
    idx, _ = construire_index()
    # 13/11/2026 : seulement les fiches en ligne (évite de proposer un parfum masqué : 404 côté navigateur)
    en_ligne = fiches_en_ligne()
    if len(en_ligne) > 500:
        idx["parfums"] = {h: v for h, v in idx["parfums"].items() if h in en_ligne}
    return ("/* Généré par scripts/odeurs.py (recherche par odeurs, 12/11/2026) : ne pas modifier à la main. */\n"
            "window.QK_ODEURS=" + json.dumps(idx, ensure_ascii=False, separators=(",", ":")) + ";\n")


if __name__ == "__main__":
    idx, compte = construire_index()
    D = json.load(open(CONFIG, encoding="utf-8"))["parfums"]
    print("parfums indexés :", len(idx["parfums"]), "/", len(D))
    for o in idx["odeurs"]:
        print("  %-20s %-32s %4d" % (o[1], o[2], compte[o[0]]))
    # notes non classées
    from collections import Counter
    c = Counter()
    for d in D.values():
        for k in ("tete", "coeur", "fond", "cle"):
            for note in (d.get("notes_fr") or {}).get(k, []):
                if not odeurs_de(note):
                    c[note.lower()] += 1
    print("notes non classées :", sum(c.values()), c.most_common(60))
    print("taille asset : %d ko" % (len(asset_js().encode()) // 1024))
