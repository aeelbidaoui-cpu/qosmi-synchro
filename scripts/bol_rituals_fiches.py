#!/usr/bin/env python3
"""Fiches bol des produits Rituals (demande d'Amine du 19/11/2026 : « pour les fiches Rituals sur bol, règle ceux qui
manquent des infos »). Rituals a autorisé l'usage des textes et photos de son site.

  python3 scripts/bol_rituals_fiches.py [--essai]

Cibles : nos offres Rituals que bol garde « niet te koop » faute de contenu (rapports/bol_invisibles.json, écrit par
bol_publier) :
  - « You are the first to sell this item » : la fiche n'existe pas chez bol → on la crée entièrement : catégorie bol
    (GPC Code, d'après la recommandation de bol sur le nom et la description), nom, description, marque, ingrédients
    (INCI), contenance, référence, fabricant (obligatoire RGPS) et photo officielle ;
  - « essential product information » / « missing content » : la fiche existe → on complète fabricant et ingrédients.
Les textes viennent de la fiche produit rituals.com/nl-be (bloc « productDetails ») : rien n'est inventé ; un attribut
dont on n'a pas la valeur sûre n'est pas envoyé.
Journal public : seulement des EAN, des noms d'attributs et des nombres (aucun prix).
"""
import collections
import concurrent.futures as cf
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
RAPPORTS = os.path.join(RACINE, "rapports")
SITE = "https://www.rituals.com"
AGENT = "Mozilla/5.0 (compatible; Qosmi-catalogue/1.0; +https://qosmi.be)"
MODELE = "https://productdatamodel.s-bol.com/v10/datamodel_v10_nl.json"
PREFIXE = "8719134"
CONTENU = ("4004", "3001")
# Fabricant (RGPS). Repli seulement : on reprend d'abord ce que bol affiche déjà sur les fiches Rituals existantes.
FABRICANT_REPLI = {"Manufacturer Name": "Rituals Cosmetics Enterprise B.V.",
                   "Manufacturer Address": "Keizersgracht 679, 1017 DV Amsterdam, Nederland",
                   "Manufacturer Email": "https://www.rituals.com/nl-be/contact"}


def lire(url, essais=3, timeout=60):
    for i in range(essais):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept-Language": "nl-BE,nl;q=0.9"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            time.sleep(2 + 3 * i)
    return None


def ean_de(code):
    s = PREFIXE + code[-5:]
    t = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(s))
    return s + str((10 - t % 10) % 10)


def flux(h):
    """Flux Next.js de la page (morceaux self.__next_f.push), décodé : c'est là que sont les blocs « productDetails »."""
    morceaux = []
    for m in re.finditer(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', h):
        try:
            morceaux.append(json.loads('"%s"' % m.group(1)))
        except Exception:
            pass
    return "".join(morceaux)


def champ(f, nom):
    m = re.search(r'"%s":\{"type":"(?:text|checkbox)","value":("(?:[^"\\]|\\.)*"|true|false)' % nom, f)
    if not m:
        return None
    val = json.loads(m.group(1))
    if isinstance(val, str) and re.fullmatch(r"\$[0-9a-z]+", val):  # texte long rangé à part dans le flux (« $d6 »)
        r = re.search(r"(?<![0-9a-z])%s:T([0-9a-f]+)," % re.escape(val[1:]), f)
        if not r:
            return None
        octets = f[r.end():].encode("utf-8")[:int(r.group(1), 16)]
        val = octets.decode("utf-8", "ignore")
    if isinstance(val, str):
        val = val.replace("\\n", "\n").strip()
    return val or None


def image_ok(url):
    """Vrai si l'adresse renvoie bien une image (bol refuse une photo introuvable : DOWNLOAD_FAILED_404)."""
    for i in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENT})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status == 200 and r.headers.get("Content-Type", "").startswith("image/") and len(r.read()) > 3000
        except urllib.error.HTTPError:
            return False
        except Exception:
            time.sleep(2)
    return False


def photo(code, h):
    """Photo officielle qui existe vraiment (19/11 : « product-pack » est introuvable pour ± 2 produits sur 3)."""
    cand = ["%s/assets/%s/packshot/product-pack?fmt=jpg&wid=1200" % (SITE, code),
            "%s/assets/%s/packshot/product?fmt=jpg&wid=1200" % (SITE, code)]
    for nom in dict.fromkeys(re.findall(r"rituals\.scene7\.com/is/image/rituals/(%s-[A-Za-z0-9_-]+)" % code, h)):
        cand.append("https://rituals.scene7.com/is/image/rituals/%s?fmt=jpg&wid=1200&hei=1200" % nom)
    return next((u for u in cand[:5] if image_ok(u)), None)


def page(url):
    """Données utiles d'une fiche rituals.com : nom, catégorie, textes, INCI, mises en garde."""
    code = (re.search(r"-(\d{6,8})\.html$", url) or [None, None])[1]
    h = lire(url)
    if not h or not code:
        return None
    u = h.replace('\\"', '"')
    f = flux(h) or u
    lds = []
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>([\s\S]*?)</script>', h):
        try:
            lds.append(json.loads(m.group(1)))
        except Exception:
            pass
    p = next((x for x in lds if isinstance(x, dict) and x.get("@type") == "Product"), {})
    bc = next((x for x in lds if isinstance(x, dict) and x.get("@type") == "BreadcrumbList"), None)
    paires = dict(re.findall(r'"tradeCode":"(\d{7})"[\s\S]{0,700}?"eanCode":"(\d{13})"', u))
    return {"code": code, "ean": paires.get(code) or ean_de(code), "url": url, "nom": (p.get("name") or "").strip(),
            "description_ld": (p.get("description") or "").strip(),
            "cat": " > ".join(i["item"]["name"] for i in bc["itemListElement"][1:-1]) if bc else "",
            "rituel": champ(f, "ancientRitual"), "titre": champ(f, "productTitle"), "texte": champ(f, "marketingUsps"),
            "usage": champ(f, "directionsForUse"), "contenu": champ(f, "boxContains"), "inci": inci_valide(champ(f, "inci")),
            "avertissement": champ(f, "warning"), "photo": photo(code, h)}


SANTE = re.compile(r"nachtrust|slaap|genees|geneeskunde|helend|heling|verlicht|pijn|stress|angst|immuun|therap|ontsteking|"
                   r"ziekte|klachten|medisch|anti-?bacteri|fluoriet|kristal|edelsteen|energie van de steen", re.I)


def sans_allegations(t):
    """Règle Qosmi : aucune allégation de santé. On retire les phrases du texte de la marque qui en contiennent."""
    if not t:
        return t
    phrases = re.split(r"(?<=[.!?])\s+", t)
    return " ".join(x for x in phrases if not SANTE.search(x)).strip()


def inci_valide(t):
    return t if t and t.count(",") >= 3 and len(t) >= 40 else None


def paragraphe(t):
    t = re.sub(r"\n{2,}", "\n\n", (t or "").strip())
    return "".join("<p>%s</p>" % html.escape(x.strip()).replace("\n", "<br>") for x in t.split("\n\n") if x.strip())


def description(d):
    corps = paragraphe("\n\n".join(sans_allegations(x) for x in (d["texte"] or d["description_ld"]).split("\n\n")))
    if d.get("usage"):
        corps += "<h3>Gebruik</h3>" + paragraphe(d["usage"])
    if d.get("contenu"):
        corps += "<h3>Inhoud verpakking</h3>" + paragraphe(d["contenu"])
    if d.get("avertissement"):
        corps += "<h3>Waarschuwing</h3>" + paragraphe(d["avertissement"])
    return corps[:10000]


def nom_bol(d):
    n = " ".join(d["nom"].split())
    return (n if n.lower().startswith("rituals") else "Rituals " + n)[:250]


def contenance(nom):
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(ml|g|kg|l|cl)\b", nom, re.I)
    if not m:
        return None
    unite = {"ml": "unece.unit.MLT", "g": "unece.unit.GRM", "kg": "unece.unit.KGM", "l": "unece.unit.LTR", "cl": "unece.unit.CLT"}
    return {"value": m.group(1).replace(",", "."), "unitId": unite[m.group(2).lower()]}


def v(x):
    return [{"value": x}]


def diagnostic():
    """Pourquoi bol bloque encore nos fiches Rituals : attributs obligatoires (niveau 0) de la catégorie absents de la
    fiche bol, et rapports d'envoi (champs refusés) des envois précédents gardés dans base/bol_rituals_envois.json."""
    from bol_api import Bol
    bol = Bol()
    inv = json.load(open(os.path.join(RAPPORTS, "bol_invisibles.json"), encoding="utf-8"))
    raisons = collections.defaultdict(list)
    for cle, eans in inv.items():
        for e in eans:
            raisons[str(e).zfill(13)].append(cle)
    cibles = sorted(e for e, r in raisons.items() if e.startswith(PREFIXE) and any(x.startswith(CONTENU) for x in r))
    print("Rituals bloquées : %d" % len(cibles), flush=True)
    print("Raisons :", dict(collections.Counter(x[:90] for e in cibles for x in raisons[e]).most_common(8)), flush=True)
    # texte complet de bol pour quelques offres (bol_invisibles.json le coupe à 80 caractères)
    raisons_longues = {}
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from bol_publier import offres_en_ligne
        en_ligne = offres_en_ligne(bol)
        for e in cibles[:8]:
            oid = (en_ligne.get(e) or en_ligne.get(e.lstrip("0")) or {}).get("offerId")
            o = bol.get("/retailer/offers/%s" % oid) if oid else {}
            raisons_longues[e] = [(r.get("code"), r.get("description")) for r in (o or {}).get("notPublishableReasons") or []]
    except Exception as ex:
        print("raisons longues : %s" % ex, flush=True)
    except Exception:
        pass
    modele = json.loads(lire(MODELE, timeout=300) or "{}")
    chunks = {c["id"]: c for c in modele.get("chunks", [])}
    manque, cats, attrs_vus = collections.Counter(), collections.Counter(), collections.Counter()
    ech = cibles[:80]
    for e in ech:
        f = bol.appel("GET", "/retailer/content/catalog-products/%s" % e, params={"language": "nl"}) or {}
        a = {x.get("id") for x in f.get("attributes") or []}
        gpc = str(f.get("gpc", {}).get("chunkId") if isinstance(f.get("gpc"), dict) else "") or next(
            ((x.get("values") or [{}])[0].get("value") for x in f.get("attributes") or [] if x.get("id") == "GPC Code"), None)
        attrs_vus[len(a)] += 0
        if not f:
            manque["(pas de fiche bol)"] += 1
            continue
        ch = chunks.get(str(gpc))
        cats[(ch or {}).get("name", "catégorie inconnue %s" % gpc)] += 1
        for x in (ch or {}).get("attributes", []):
            if x["enrichmentLevel"] == 0 and x["id"] not in a:
                manque[x["id"]] += 1
        if e == ech[0]:
            print("Exemple %s : clés de la fiche %s ; attributs %s" % (e, sorted(f.keys()), sorted(a)[:40]), flush=True)
        # 20/11 : photos publiées mais offres toujours 4004 → ce que bol montre vraiment sur la fiche et l'offre
        if ech.index(e) < 8:
            assets = bol.appel("GET", "/retailer/products/%s/assets" % e, params={"usage": "PRIMARY"}) or {}
            print("Détail %s : published=%s enrichment=%s gpc=%s photos=%s raisons=%s" % (
                e, json.dumps(f.get("published"), ensure_ascii=False)[:300], json.dumps(f.get("enrichment"), ensure_ascii=False)[:300],
                json.dumps(f.get("gpc"), ensure_ascii=False)[:200], json.dumps(assets, ensure_ascii=False)[:400],
                [(x, raisons_longues.get(e)) for x in raisons[e]][:3]), flush=True)
    # comparaison : quelques offres Rituals qui, elles, sont bien en vente
    try:
        bloquees = set(raisons)
        ok = [e for e in sorted(en_ligne) if str(e).zfill(13).startswith(PREFIXE) and str(e).zfill(13) not in bloquees][:4]
        print("Rituals en vente : %d" % len([e for e in en_ligne if str(e).zfill(13).startswith(PREFIXE) and str(e).zfill(13) not in bloquees]), flush=True)
        for e in ok:
            e = str(e).zfill(13)
            f = bol.appel("GET", "/retailer/content/catalog-products/%s" % e, params={"language": "nl"}) or {}
            assets = bol.appel("GET", "/retailer/products/%s/assets" % e, params={"usage": "PRIMARY"}) or {}
            print("En vente %s : published=%s enrichment=%s nb attributs=%d photos=%s" % (
                e, f.get("published"), json.dumps(f.get("enrichment")), len(f.get("attributes") or []), json.dumps(assets)[:300]), flush=True)
    except Exception as ex:
        print("comparaison : %s" % ex, flush=True)
    print("Échantillon %d : attributs obligatoires absents %s" % (len(ech), dict(manque.most_common(15))), flush=True)
    print("Catégories :", dict(cats.most_common(15)), flush=True)
    chemin = os.path.join(RACINE, "base", "bol_rituals_envois.json")
    if os.path.exists(chemin):
        envois = json.load(open(chemin, encoding="utf-8"))
        refus = collections.Counter()
        etats = collections.Counter()
        neuves = [e for e, x in envois.items() if x.get("nouvelle")]
        ordre = neuves[:40] + [e for e in envois if e not in neuves][:80]
        montre = False
        for e in ordre:
            v = envois[e]
            if not v.get("processStatusId"):
                continue
            st = bol.appel("GET", "/shared/process-status/%s" % v["processStatusId"]) or {}
            up = st.get("entityId")
            rep = bol.appel("GET", "/retailer/content/upload-report/%s" % up) if up else None
            etats[("nouvelle " if v.get("nouvelle") else "") + str((rep or {}).get("status") or st.get("status"))] += 1
            g = "[nouvelle] " if v.get("nouvelle") else ""
            if v.get("nouvelle") and not montre and rep:
                montre = True
                print("Rapport d'une fiche nouvelle : %s" % json.dumps({"status": rep.get("status"), "assets": rep.get("assets"),
                      "attributs": [(a.get("id"), a.get("status"), a.get("subStatus"), a.get("subStatusDescription")) for a in rep.get("attributes") or []]},
                      ensure_ascii=False)[:3000], flush=True)
            for at in (rep or {}).get("attributes") or []:
                if at.get("status") not in (None, "ACCEPTED", "PENDING"):
                    refus[g + "%s : %s" % (at.get("id"), "; ".join(sorted({str(m.get("violationCode") or m.get("message") or m)[:80] for m in at.get("subStatusMessages") or at.get("messages") or []})) or at.get("subStatus") or at.get("status"))] += 1
            for at in (rep or {}).get("assets") or []:
                if at.get("status") not in (None, "ACCEPTED", "PENDING"):
                    refus[g + "photo : %s" % (at.get("subStatus") or at.get("status"))] += 1
            if e == next(iter(envois)):
                print("Exemple de rapport : %s" % json.dumps(rep, ensure_ascii=False)[:1500], flush=True)
        print("Rapports d'envoi : %s" % dict(etats), flush=True)
        for k, n in refus.most_common(40):
            print("  refusé × %d : %s" % (n, k))


def main():
    if "--diag" in sys.argv:
        return diagnostic()
    essai = "--essai" in sys.argv
    photos = "--photos" in sys.argv
    inv = json.load(open(os.path.join(RAPPORTS, "bol_invisibles.json"), encoding="utf-8"))
    raisons = collections.defaultdict(list)
    for cle, eans in inv.items():
        for e in eans:
            raisons[str(e).zfill(13)].append(cle)
    cibles = {e: r for e, r in raisons.items() if e.startswith(PREFIXE) and any(x.startswith(CONTENU) for x in r)}
    nouveau = {e for e, r in cibles.items() if any("first to sell" in x for x in r)}
    print("Rituals : %d offres sans contenu suffisant chez bol (%d fiches à créer, %d à compléter)"
          % (len(cibles), len(nouveau), len(cibles) - len(nouveau)), flush=True)
    if not cibles:
        return

    plan = lire(SITE + "/nl-be/sitemap-nl-be.xml") or ""
    urls = sorted(set(u for u in re.findall(r"<loc>([^<]+)</loc>", plan) if re.search(r"/nl-be/.+-\d{6,8}\.html$", u)))
    par_ean = {}
    for u in urls:
        code = re.search(r"-(\d{6,8})\.html$", u).group(1)
        par_ean.setdefault(ean_de(code), u)
    a_lire = [par_ean[e] for e in cibles if e in par_ean]
    donnees = {}
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for d in ex.map(page, a_lire):
            if d:
                donnees[d["ean"]] = d
    print("Rituals : %d fiches rituals.com lues sur %d (%d sans page trouvée)" % (len(donnees), len(cibles), len(cibles) - len(a_lire)), flush=True)

    from bol_api import Bol
    bol = Bol()
    # fabricant : ce que bol affiche déjà sur les fiches Rituals existantes (le plus fréquent), sinon le repli
    vus = collections.Counter()
    for e in [x for x in cibles if x not in nouveau][:15]:
        f = bol.appel("GET", "/retailer/content/catalog-products/%s" % e, params={"language": "nl"}) or {}
        a = {x.get("id"): (x.get("values") or [{}])[0].get("value") for x in f.get("attributes") or []}
        if a.get("Manufacturer Name") and a.get("Manufacturer Address") and a.get("Manufacturer Email"):
            vus[(a["Manufacturer Name"], a["Manufacturer Address"], a["Manufacturer Email"])] += 1
    fab = dict(zip(("Manufacturer Name", "Manufacturer Address", "Manufacturer Email"), vus.most_common(1)[0][0])) if vus else FABRICANT_REPLI
    print("Fabricant : %s" % ("repris des fiches bol existantes" if vus else "repli (registre du commerce)"), flush=True)

    modele = json.loads(lire(MODELE, timeout=300) or "{}")
    chunks = {c["id"]: c for c in modele.get("chunks", [])}
    print("Modèle de données bol : %d catégories" % len(chunks), flush=True)

    stats, refus, envois = collections.Counter(), collections.Counter(), {}
    deja = set()
    if photos:  # 20/11 : ne renvoyer que les photos que bol n'a pas encore publiées (IMAGE_RATE_LIMITED, 404…)
        chemin = os.path.join(RACINE, "base", "bol_rituals_envois.json")
        prec = json.load(open(chemin, encoding="utf-8")) if os.path.exists(chemin) else {}
        for e, x in prec.items():
            if e not in cibles or not x.get("processStatusId"):
                continue
            st = bol.appel("GET", "/shared/process-status/%s" % x["processStatusId"]) or {}
            rep = bol.appel("GET", "/retailer/content/upload-report/%s" % st["entityId"]) if st.get("entityId") else None
            etat = [a.get("subStatus") for a in (rep or {}).get("assets") or []]
            if any(t in ("PUBLISHED", "IMAGE_FLAGGED_AS_DUPLICATE") for t in etat):
                deja.add(e)
                envois[e] = x
        print("Photos déjà publiées par bol : %d ; à renvoyer : %d" % (len(deja), len(cibles) - len(deja)), flush=True)
    for e in sorted(cibles):
        d = donnees.get(e)
        if not d:
            stats["sans page rituals.com"] += 1
            continue
        if photos:  # 19/11 : renvoi de la seule photo (vérifiée), espacé pour éviter IMAGE_RATE_LIMITED chez bol
            if e in deja:
                stats["photo déjà publiée"] += 1
                continue
            if not d.get("photo"):
                stats["sans photo trouvée sur rituals.com"] += 1
                continue
            stats["photo " + ("packshot" if "/assets/" in d["photo"] else "galerie")] += 1
            if essai:
                continue
            try:
                r = bol.appel("POST", "/retailer/content/products", corps={"language": "nl", "attributes": [{"id": "EAN", "values": v(e)}],
                                                                           "assets": [{"url": d["photo"], "labels": ["FRONT"]}]})
                envois[e] = {"processStatusId": (r or {}).get("processStatusId"), "nouvelle": e in nouveau, "attributs": ["EAN", "photo"]}
                stats["envoyées"] += 1
            except RuntimeError as ex:
                envois[e] = {"erreur": str(ex)[:300]}
                refus[str(ex)[:160]] += 1
                stats["refusées"] += 1
            time.sleep(10)
            continue
        attrs = [{"id": "EAN", "values": v(e)}] + [{"id": k, "values": v(x)} for k, x in fab.items()]
        assets = []
        # 19/11 soir : toutes les fiches bloquées reçoivent le jeu complet (catégorie reprise de la fiche bol si elle
        # existe déjà, sinon recommandée par bol), pas seulement le fabricant et les ingrédients.
        gpc = None
        if e not in nouveau:
            fb = bol.appel("GET", "/retailer/content/catalog-products/%s" % e, params={"language": "nl"}) or {}
            g = fb.get("gpc") or {}
            gpc = str(g.get("chunkId") or g.get("id") or g.get("code") or "") if isinstance(g, dict) else str(g or "")
            if not stats["exemple gpc"]:
                print("  gpc d'une fiche existante : %s" % json.dumps(g)[:200], flush=True)
                stats["exemple gpc"] += 1
            if gpc not in chunks:
                gpc = None
        if not d.get("inci") and any("Cosmetics" in x or "Ingredients" in x for x in cibles[e]):
            stats["cosmétique sans liste INCI sur rituals.com"] += 1
        if True:
            try:
                if gpc:
                    raise LookupError
                r = bol.appel("POST", "/retailer/content/chunk-recommendations",
                              corps={"productContents": [{"attributes": [{"id": "Name", "values": v(nom_bol(d))},
                                                                         {"id": "Description", "values": v(re.sub(r"<[^>]+>", " ", description(d))[:2000])}]}]})
                preds = sorted(((r or {}).get("recommendations") or [{}])[0].get("predictions") or [], key=lambda p: -p.get("probability", 0))
                gpc = next((p["chunkId"] for p in preds if str(p.get("chunkId")) in chunks), None)
            except LookupError:
                pass
            except RuntimeError as ex:
                if not stats["erreur recommandation"]:
                    print("  recommandation de catégorie : %s" % str(ex)[:300], flush=True)
                stats["erreur recommandation"] += 1
            if not gpc:
                stats["sans catégorie bol"] += 1
                continue
            ch = chunks[gpc]
            ids = {a["id"] for a in ch.get("attributes", [])}
            attrs += [{"id": "GPC Code", "values": v(gpc)}, {"id": "Name", "values": v(nom_bol(d))},
                      {"id": "Internal Reference", "values": v(d["code"])},
                      {"id": "Product Classification", "values": v(ch.get("name") or gpc)}]
            if "Description" in ids:
                attrs.append({"id": "Description", "values": v(description(d))})
            if "Brand" in ids:
                attrs.append({"id": "Brand", "values": v("Rituals")})
            cap = contenance(d["nom"])
            if cap and "Capacity" in ids:
                attrs.append({"id": "Capacity", "values": [cap]})
            if d.get("inci") and "Ingredients" in ids:
                attrs.append({"id": "Ingredients", "values": v(d["inci"])})
            assets = [{"url": d["photo"], "labels": ["FRONT"]}] if d.get("photo") else []
            if not assets:
                stats["sans photo trouvée sur rituals.com"] += 1
            stats["catégorie %s" % (ch.get("name") or gpc)] += 1
        corps = {"language": "nl", "attributes": attrs}
        if assets:
            corps["assets"] = assets
        if essai:
            stats["à envoyer"] += 1
            if stats["à envoyer"] <= 12:
                print("  essai %s · %s → %s · %s" % (e, d["cat"], [a["values"][0]["value"] for a in attrs if a["id"] in ("GPC Code", "Product Classification")],
                                                    ", ".join(a["id"] for a in attrs)), flush=True)
            continue
        try:
            r = bol.appel("POST", "/retailer/content/products", corps=corps)
            envois[e] = {"processStatusId": (r or {}).get("processStatusId"), "nouvelle": e in nouveau,
                         "attributs": [a["id"] for a in attrs]}
            stats["envoyées"] += 1
        except RuntimeError as ex:
            envois[e] = {"erreur": str(ex)[:300]}
            refus[str(ex)[:160]] += 1
            stats["refusées"] += 1

    # statut de traitement d'un échantillon (le rapport détaillé de bol n'arrive qu'après ± 1 h)
    if envois:
        ech = [x for x in envois.values() if x.get("processStatusId")][:20]
        st = collections.Counter((bol.statut(x["processStatusId"], tours=20) or {}).get("status") for x in ech)
        print("Traitement bol (échantillon de %d) : %s" % (len(ech), dict(st)), flush=True)
    os.makedirs(RAPPORTS, exist_ok=True)
    with open(os.path.join(RAPPORTS, "bol_rituals_fiches.json"), "w", encoding="utf-8") as f:
        json.dump(envois, f, ensure_ascii=False, indent=1)
    if envois:  # gardé d'un passage à l'autre (cache GitHub) pour lire ensuite les rapports d'envoi de bol
        with open(os.path.join(RACINE, "base", "bol_rituals_envois.json"), "w", encoding="utf-8") as f:
            json.dump(envois, f, ensure_ascii=False)
    for k, n in sorted(stats.items(), key=lambda kv: -kv[1]):
        print("  %-45s %5d" % (k, n))
    for k, n in refus.most_common(10):
        print("  refus × %d : %s" % (n, k))


if __name__ == "__main__":
    main()
