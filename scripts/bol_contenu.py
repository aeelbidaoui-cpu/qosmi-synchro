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


def rapport():
    from bol_api import Bol
    bol = Bol()
    envois = json.load(open(os.path.join(RAPPORTS, "bol_contenu_envois.json"), encoding="utf-8"))
    for ean, v in envois.items():
        if not v.get("processStatusId"):
            continue
        st = bol.appel("GET", "/shared/process-status/%s" % v["processStatusId"]) or {}
        up = st.get("entityId")
        rep = bol.appel("GET", "/retailer/content/upload-report/%s" % up) if up else None
        v["statut"] = st.get("status")
        v["rapport"] = rep
        print("%s : %s %s" % (ean, st.get("status"), json.dumps(rep, ensure_ascii=False)[:300] if rep else ""))
    with open(os.path.join(RAPPORTS, "bol_contenu_envois.json"), "w", encoding="utf-8") as fh:
        json.dump(envois, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    if "--envoyer" in sys.argv:
        envoyer(essai="--essai" in sys.argv)
        sys.exit(0)
    if "--rapport" in sys.argv:
        rapport()
        sys.exit(0)
    if "--diag" in sys.argv:
        diag()
    else:
        print(__doc__)
