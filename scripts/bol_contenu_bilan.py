#!/usr/bin/env python3
"""Bilan des offres Qosmi invisibles sur bol pour raison de CONTENU (24/11/2026, Amine : « complète ce que bol demande »).
Lecture seule. Pour chaque offre en ligne : raisons de non-publication (GET offre) ; pour celles liées au contenu
(codes 4004 / 3001), lecture de la fiche bol et liste des attributs vides ou demandés.
Sortie : rapports/bol_contenu_bilan.json (EAN, titre, marque, raisons, attributs manquants) — aucun prix, aucun fournisseur."""
import collections, json, os, sys
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)


def valeurs(fiche):
    out = {}
    for a in (fiche or {}).get("attributes") or []:
        vs = [v.get("value") for v in a.get("values") or [] if v.get("value") not in (None, "")]
        out[a.get("id")] = vs
    return out


def main():
    from bol_api import Bol
    from bol_publier import offres_en_ligne
    bol = Bol()
    en_ligne = offres_en_ligne(bol)
    raisons_tot = collections.Counter()
    cibles = {}
    for i, (e, o) in enumerate(en_ligne.items()):
        det = bol.get("/retailer/offers/%s" % o["offerId"]) or {}
        rs = det.get("notPublishableReasons") or []
        for r in rs:
            raisons_tot["%s %s" % (r.get("code"), (r.get("description") or "")[:90])] += 1
        if any(str(r.get("code")) in ("4004", "3001") for r in rs):
            cibles[e] = [("%s %s" % (r.get("code"), r.get("description") or "")) for r in rs]
        if i % 500 == 0:
            print("  %d offres lues" % i, flush=True)
    print("Offres en ligne : %d · avec au moins une raison : %d" % (len(en_ligne), sum(1 for _ in raisons_tot)))
    for k, n in raisons_tot.most_common(40):
        print("  %5d × %s" % (n, k))
    manque = collections.Counter()
    out = {}
    for e, rs in cibles.items():
        fiche = None
        try:
            fiche = bol.appel("GET", "/retailer/content/catalog-products/%s" % e.zfill(13), params={"language": "nl"})
        except RuntimeError as ex:
            fiche = {"erreur": str(ex)[:200]}
        v = valeurs(fiche)
        titre = (v.get("Name") or v.get("Title") or [""])[0]
        marque = (v.get("Brand") or [""])[0]
        vides = sorted(k for k, x in v.items() if not x)
        cles = ["Ingredients", "Manufacturer Name", "Manufacturer Address", "Manufacturer Email", "Description",
                "Product Classification", "Content Volume", "Chunk ID", "Image"]
        absents = [k for k in cles if k not in v or not v.get(k)]
        for k in set(vides) | set(absents):
            manque[k] += 1
        out[e] = {"titre": titre, "marque": marque, "raisons": rs, "vides": vides, "absents": absents,
                  "attributs_presents": sorted(k for k, x in v.items() if x), "erreur": (fiche or {}).get("erreur")}
    print("\nFiches avec problème de contenu : %d" % len(out))
    print("Attributs vides ou absents (sur ces fiches) :")
    for k, n in manque.most_common(40):
        print("  %5d × %s" % (n, k))
    os.makedirs(os.path.join(RACINE, "rapports"), exist_ok=True)
    json.dump(out, open(os.path.join(RACINE, "rapports", "bol_contenu_bilan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
