#!/usr/bin/env python3
"""Fiches produit bol incomplètes (demande d'Amine du 09/11/2026).

bol rend invisibles certaines de nos offres parce que la FICHE PRODUIT (commune à tous les vendeurs) est incomplète :
ingrédients, contenu « cosmétiques », informations essentielles, adresse fournisseur.

--envoyer : envoie à bol les compléments de config/bol_contenu.json (ingrédients INCI, fabricant officiel) ;
            les numéros d'envoi sont gardés dans rapports/bol_contenu_envois.json.
Le résultat réel se voit quelques heures plus tard avec l'action « contenu-diag » (les raisons d'invisibilité disparaissent).

--diag : pour chaque EAN concerné (rapports/bol_invisibles.json, écrit par bol_publier.py), lit la fiche bol
         (GET /retailer/content/catalog-products/{ean}) et écrit rapports/bol_contenu_diag.json :
         attributs présents, attributs vides, raisons d'invisibilité. Rien n'est envoyé à bol.

Règle d'Amine : l'adresse fournisseur est TOUJOURS celle de Deway BV, jamais celle du fournisseur réel.
"""
import json, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
RAPPORTS = os.path.join(RACINE, "rapports")
CONTENU = ("4004", "3001")  # informations essentielles / attributs (ingrédients, cosmétiques, adresse fournisseur)


def diag():
    from bol_api import Bol
    inv = json.load(open(os.path.join(RAPPORTS, "bol_invisibles.json"), encoding="utf-8"))
    raisons = {}
    for cle, eans in inv.items():
        for e in eans:
            raisons.setdefault(e, []).append(cle)
    cibles = sorted(e for e, r in raisons.items() if any(x.startswith(CONTENU) for x in r))
    print("EAN avec un problème de fiche : %d" % len(cibles))
    bol = Bol()
    from bol_publier import offres_en_ligne
    offres = offres_en_ligne(bol)
    out = {}
    for e in cibles:
        o = offres.get(e.lstrip("0")) or {}
        completes = []
        if o.get("offerId"):
            completes = (bol.appel("GET", "/retailer/offers/%s" % o["offerId"]) or {}).get("notPublishableReasons") or []
        ean = e.zfill(13)
        fiche = None
        for params in ({"language": "nl"}, None):
            try:
                fiche = bol.appel("GET", "/retailer/content/catalog-products/%s" % ean, params=params)
            except RuntimeError as ex:
                fiche = {"erreur": str(ex)[:300]}
            if fiche:
                break
        out[ean] = {"raisons": raisons[e], "raisons_completes": completes, "fiche": fiche}
        attrs = (fiche or {}).get("attributes") or []
        print("%s : %d attributs · %s" % (ean, len(attrs), " | ".join(r[:40] for r in raisons[e])))
    os.makedirs(RAPPORTS, exist_ok=True)
    with open(os.path.join(RAPPORTS, "bol_contenu_diag.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("Rapport : rapports/bol_contenu_diag.json (%d fiches, %d appels)" % (len(out), bol.appels))


PAYS_NL = {"France": "Frankrijk", "Italie": "Italië", "Espagne": "Spanje", "Belgique": "België", "Allemagne": "Duitsland",
           "Pays-Bas": "Nederland", "Suisse": "Zwitserland", "Royaume-Uni": "Verenigd Koninkrijk", "Slovaquie": "Slowakije",
           "Émirats arabes unis": "Verenigde Arabische Emiraten", "États-Unis": "Verenigde Staten", "Pologne": "Polen",
           "Luxembourg": "Luxemburg", "Monaco": "Monaco", "Autriche": "Oostenrijk", "Turquie": "Turkije"}


def attributs(f):
    """Attributs bol à compléter pour une fiche (seulement ce qui est sûr)."""
    out = []
    if f.get("inci") and f.get("inci_statut") in ("trouve", "partiel", "existant_complet"):
        out.append({"id": "Ingredients", "values": [{"value": f["inci"].strip()}]})
    if f.get("fabricant_nom") and f.get("fabricant_adresse"):
        a = f["fabricant_adresse"]
        if a.get("rue") and a.get("ville") and a.get("pays"):
            ligne = "%s %s, %s %s, %s" % (a["rue"], a.get("numero", ""), a.get("code_postal", ""), a["ville"], PAYS_NL.get(a["pays"], a["pays"]))
            out.append({"id": "Manufacturer Name", "values": [{"value": f["fabricant_nom"].strip()}]})
            out.append({"id": "Manufacturer Address", "values": [{"value": " ".join(ligne.split()).replace(" ,", ",")}]})
            if f.get("fabricant_email"):
                out.append({"id": "Manufacturer Email", "values": [{"value": f["fabricant_email"].strip()}]})
    return out


def envoyer(essai=False):
    from bol_api import Bol
    fiches = json.load(open(os.path.join(RACINE, "config", "bol_contenu.json"), encoding="utf-8"))["fiches"]
    bol = None if essai else Bol()
    envois = {}
    for f in fiches:
        attrs = attributs(f)
        if not attrs:
            print("%s : rien de sûr à envoyer (%s)" % (f["ean"], f.get("inci_statut")))
            continue
        corps = {"language": "nl", "attributes": [{"id": "EAN", "values": [{"value": f["ean"].zfill(13)}]}] + attrs}
        if essai:
            print("%s : %s" % (f["ean"], ", ".join(a["id"] for a in attrs)))
            continue
        try:
            r = bol.appel("POST", "/retailer/content/products", corps=corps)
            pid = (r or {}).get("processStatusId")
            st = bol.statut(pid, tours=60) if pid else {}
            envois[f["ean"]] = {"processStatusId": pid, "statut": st.get("status"), "uploadId": st.get("entityId"),
                                "message": st.get("errorMessage"), "attributs": [a["id"] for a in attrs]}
            print("%s : envoyé (%s)" % (f["ean"], ", ".join(a["id"] for a in attrs)))
        except RuntimeError as ex:
            envois[f["ean"]] = {"erreur": str(ex)[:300]}
            print("%s : REFUS %s" % (f["ean"], str(ex)[:200]))
    if not essai:
        os.makedirs(RAPPORTS, exist_ok=True)
        with open(os.path.join(RAPPORTS, "bol_contenu_envois.json"), "w", encoding="utf-8") as fh:
            json.dump(envois, fh, ensure_ascii=False, indent=1)
        print("%d fiches envoyées à bol" % sum(1 for v in envois.values() if "processStatusId" in v))


def rapport(chemin=None):
    from bol_api import Bol
    bol = Bol()
    envois = json.load(open(chemin or os.path.join(RAPPORTS, "bol_contenu_envois.json"), encoding="utf-8"))
    for ean, v in envois.items():
        if not v.get("processStatusId"):
            continue
        st = bol.appel("GET", "/shared/process-status/%s" % v["processStatusId"]) or {}
        up = st.get("entityId")
        rep = bol.appel("GET", "/retailer/content/upload-report/%s" % up) if up else None
        v["statut"] = st.get("status")
        v["rapport"] = rep
        print("%s : %s %s" % (ean, st.get("status"), json.dumps(rep, ensure_ascii=False)[:600] if rep else ""))
    os.makedirs(RAPPORTS, exist_ok=True)
    with open(os.path.join(RAPPORTS, "bol_contenu_envois.json"), "w", encoding="utf-8") as fh:
        json.dump(envois, fh, ensure_ascii=False, indent=1)

# ---------- complément automatique (09/11/2026) ----------
BLOQUANTS = ("2006", "2002", "3000", "2003")  # marque interdite, produit bloqué, droits de vente : rien à faire côté fiche


def cle_marque(s):
    import re, unicodedata
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\b(professionals?|parfums?|perfumes?|paris|cosmetics?|the|de|by|new york|london|milano|fragrances?|beauty|laboratoires?)\b", " ", s)
    return " ".join(s.split())


def fabricant_pour(marque, nom, table):
    """Fabricant (config/bol_fabricants.json) d'après la marque de la fiche bol, sinon d'après le début du nom du produit."""
    k = cle_marque(marque)
    if k in table:
        return table[k]
    for kk, v in table.items():
        if k and kk and (k.startswith(kk + " ") or kk.startswith(k + " ") or k in [cle_marque(a) for a in v.get("alias", [])]):
            return v
    nk = cle_marque(nom)
    for kk in sorted(table, key=len, reverse=True):
        if kk and (nk == kk or nk.startswith(kk + " ")):
            return table[kk]
    return None


def nettoyer_inci(v):
    """Liste d'ingrédients refusée par bol : on enlève le préfixe (« Ingredients: ») et les mentions ajoutées par d'autres
    vendeurs ; on ne renvoie la liste que si elle ressemble à une vraie liste INCI."""
    import re
    if not v:
        return None
    t = re.sub(r"^\s*(ingr[eé]di[eë]nt(s|en)?|inci|composition|samenstelling|zutaten)\s*[:：-]\s*", "", v.strip(), flags=re.I)
    t = re.split(r"[\"'“”‘’]{1,3}\s*Houd er rekening mee|Houd er rekening mee|Please note|Veuillez noter", t)[0]
    t = re.sub(r"\s+", " ", t).strip(" .;'\"“”")
    if re.search(r"does not apply|niet van toepassing|n/a", t, re.I) or t.count(",") < 4 or len(t) < 40:
        return None
    vus, items = set(), []
    for x in (i.strip() for i in t.split(",")):
        if x and x.lower() not in vus:
            vus.add(x.lower()); items.append(x)
    if items[-1].split(" ")[-1].lower() in ("benzyl", "ethylhexyl", "butyl", "sodium", "alcohol", "hexyl", "methyl"):
        return None  # liste tronquée : on ne la renvoie pas
    t = ", ".join(items)
    return t + ("." if not t.endswith(".") else "")


def auto(essai=False):
    """Après --diag : complète tout seul les fiches bloquées pour « informations essentielles » (fabricant, d'après la
    marque) et « adresse fabricant incorrecte », et nettoie les listes d'ingrédients refusées pour leur mise en forme.
    Ce qui ne peut pas être complété automatiquement est listé dans rapports/bol_contenu_auto.json."""
    diag_ = json.load(open(os.path.join(RAPPORTS, "bol_contenu_diag.json"), encoding="utf-8"))
    table = json.load(open(os.path.join(RACINE, "config", "bol_fabricants.json"), encoding="utf-8"))["marques"]
    manuel = {f["ean"].zfill(13): f for f in json.load(open(os.path.join(RACINE, "config", "bol_contenu.json"), encoding="utf-8"))["fiches"]}
    try:
        decisions = json.load(open(os.path.join(RACINE, "base", "bol_decisions.json"), encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        decisions = {}
    a_envoyer, sans_fabricant, inci_a_chercher = {}, {}, []
    for ean, v in diag_.items():
        textes = [(str(r.get("code")), r.get("description") or "") for r in v.get("raisons_completes") or []]
        if not textes or any(c in BLOQUANTS for c, _ in textes):
            continue
        fiche = v.get("fiche") or {}
        attrs = {a.get("id"): (a.get("values") or [{}])[0].get("value") for a in fiche.get("attributes") or []}
        marque = next((p.get("name") for p in fiche.get("parties", []) if p.get("role") == "BRAND"), "")
        d = decisions.get(ean.lstrip("0")) or decisions.get(ean) or {}
        nom = d.get("nom") or attrs.get("Title") or ""
        marque = marque or d.get("marque") or ""
        envoi = []
        if any(c == "4004" and "essential" in t for c, t in textes) or any("Supplier address" in t for c, t in textes):
            f = manuel.get(ean) if manuel.get(ean, {}).get("fabricant_nom") else fabricant_pour(marque, nom, table)
            if f:
                envoi += [a for a in attributs(dict(f, inci=None)) if a["id"].startswith("Manufacturer")]
            else:
                sans_fabricant.setdefault(marque or nom.split(" ")[0], []).append([ean, nom])
        inci_manuel = (manuel.get(ean) or {}).get("inci") if (manuel.get(ean) or {}).get("inci_statut") in ("trouve", "partiel") else None
        if inci_manuel and any("(Ingredients)" in t or "missing content (Cosmetics)" in t for _, t in textes):
            envoi.append({"id": "Ingredients", "values": [{"value": inci_manuel.strip()}]})
        elif any("(Ingredients)" in t for _, t in textes):
            propre = nettoyer_inci(attrs.get("Ingredients"))
            if propre and propre != attrs.get("Ingredients"):
                envoi.append({"id": "Ingredients", "values": [{"value": propre}]})
            else:
                inci_a_chercher.append([ean, nom, (attrs.get("Ingredients") or "")[:120]])
        if any("missing content (Cosmetics)" in t for _, t in textes) and not attrs.get("Ingredients") and not inci_manuel:
            inci_a_chercher.append([ean, nom, ""])
        if envoi:
            a_envoyer[ean] = envoi
    print("Fiches à compléter automatiquement : %d · marques sans fabricant connu : %d (%d produits) · listes INCI à chercher : %d"
          % (len(a_envoyer), len(sans_fabricant), sum(len(x) for x in sans_fabricant.values()), len(inci_a_chercher)))
    envois = {}
    if not essai and a_envoyer:
        from bol_api import Bol
        bol = Bol()
        for ean, attrs in a_envoyer.items():
            corps = {"language": "nl", "attributes": [{"id": "EAN", "values": [{"value": ean.zfill(13)}]}] + attrs}
            try:
                r = bol.appel("POST", "/retailer/content/products", corps=corps)
                envois[ean] = {"processStatusId": (r or {}).get("processStatusId"), "attributs": [a["id"] for a in attrs]}
            except RuntimeError as ex:
                envois[ean] = {"erreur": str(ex)[:300]}
        print("%d fiches envoyées à bol, %d refus" % (sum(1 for v in envois.values() if v.get("processStatusId")), sum(1 for v in envois.values() if "erreur" in v)))
    with open(os.path.join(RAPPORTS, "bol_contenu_auto.json"), "w", encoding="utf-8") as fh:
        json.dump({"envois": envois, "a_envoyer": {k: [a["id"] for a in v] for k, v in a_envoyer.items()},
                   "sans_fabricant": sans_fabricant, "inci_a_chercher": inci_a_chercher}, fh, ensure_ascii=False, indent=1)


def images():
    """Essai (09/11/2026) : les offres « 4004 informations essentielles manquantes » sont presque toutes sur des fiches bol
    non publiées (published=false). On envoie la photo Qosmi (photo autorisée, recadrée) comme image principale (FRONT)."""
    from bol_api import Bol
    bol = Bol()
    imgs = json.load(open(os.path.join(RACINE, "config", "bol_images.json"), encoding="utf-8"))
    envois = {}
    for ean, url in imgs.items():
        corps = {"language": "nl", "attributes": [{"id": "EAN", "values": [{"value": ean.zfill(13)}]}],
                 "assets": [{"url": url, "labels": ["FRONT"]}]}
        try:
            r = bol.appel("POST", "/retailer/content/products", corps=corps)
            envois[ean] = {"processStatusId": (r or {}).get("processStatusId"), "attributs": ["FRONT"]}
        except RuntimeError as ex:
            envois[ean] = {"erreur": str(ex)[:300]}
    print("%d images envoyées, %d refus" % (sum(1 for v in envois.values() if v.get("processStatusId")), sum(1 for v in envois.values() if "erreur" in v)))
    os.makedirs(RAPPORTS, exist_ok=True)
    with open(os.path.join(RAPPORTS, "bol_contenu_envois.json"), "w", encoding="utf-8") as fh:
        json.dump(envois, fh, ensure_ascii=False, indent=1)
    import time
    time.sleep(240)
    rapport()


def offres_test():
    """Contrôle : opérateur économique lié aux offres bloquées 4004 vs offres visibles, et détail de 3 offres."""
    from bol_api import Bol
    from bol_publier import offres_en_ligne
    bol = Bol()
    inv = json.load(open(os.path.join(RACINE, "config", "bol_invisibles_controle.json"), encoding="utf-8"))
    k4 = {e.lstrip("0") for k, v in inv.items() if k.startswith("4004 For") for e in v}
    tous_inv = {e.lstrip("0") for v in inv.values() for e in v}
    offres = offres_en_ligne(bol)
    import collections
    c = collections.Counter()
    for e, o in offres.items():
        grp = "4004" if e in k4 else ("visible" if e not in tous_inv else "autre")
        c[(grp, bool(o.get("eo")))] += 1
    print("offres par groupe (groupe, opérateur lié) :", dict(c))
    ex = [e for e in offres if e in k4][:2] + [e for e in offres if e not in tous_inv][:1]
    for e in ex:
        print("=====", e, json.dumps(bol.appel("GET", "/retailer/offers/%s" % offres[e]["offerId"]), ensure_ascii=False)[:1500])


if __name__ == "__main__":
    if "--images" in sys.argv:
        images()
        sys.exit(0)
    if "--offres-test" in sys.argv:
        offres_test()
        sys.exit(0)
    if "--envoyer" in sys.argv:
        envoyer(essai="--essai" in sys.argv)
        sys.exit(0)
    if "--rapport" in sys.argv:
        i = sys.argv.index("--rapport")
        rapport(os.path.join(RACINE, sys.argv[i + 1]) if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith("-") else None)
        sys.exit(0)
    if "--diag" in sys.argv:
        diag()
        if "--auto" in sys.argv:
            auto(essai="--essai" in sys.argv)
    elif "--auto" in sys.argv:
        auto(essai="--essai" in sys.argv)
    else:
        print(__doc__)
