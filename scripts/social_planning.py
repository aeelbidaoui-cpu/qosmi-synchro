#!/usr/bin/env python3
"""Calendrier des réseaux sociaux à deux publications par jour (demande d'Amine du 18/11/2026 : « tu vas poster 2x par jour »).

Toutes les publications pas encore publiées sont redatées à partir de « debut » (config/social.json « planning »), sur les
créneaux « heures » (12:30 et 18:30, heure de Bruxelles), dans l'ordre des lots de « ordre ». Les publications liées à
une date (Noël, réveillon, Nouvel An, Saint-Valentin, printemps…) gardent la date fixée dans « fixes » (créneau du soir).

  python3 scripts/social_planning.py --essai   # montre le nouveau calendrier
  python3 scripts/social_planning.py           # l'écrit dans les fichiers des lots
"""
import datetime as dt, json, os, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(RACINE, "config", "social.json"), encoding="utf-8"))
PL = CFG["planning"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def main():
    essai = "--essai" in sys.argv
    faites = set(json.load(open(os.path.join(RACINE, "social", "publie.json"), encoding="utf-8")))
    heures = CFG["heures"]
    soir = heures[-1]
    lots = {c: json.load(open(os.path.join(RACINE, c), encoding="utf-8")) for c in CFG["lots"]}
    fixes = PL.get("fixes", {})
    attente = []
    for c in PL["ordre"]:
        attente += [p for p in sorted(lots[c], key=lambda p: (p["iso"], p.get("heure", ""))) if p["id"] not in faites]
    pris = {(d, soir) for d in fixes.values()}
    libres = [p for p in attente if p["id"] not in fixes]
    places = {}
    jour = dt.date.fromisoformat(PL["debut"])
    i = 0
    while i < len(libres):
        for hm in heures:
            if i < len(libres) and (jour.isoformat(), hm) not in pris:
                places[libres[i]["id"]] = (jour, hm)
                i += 1
        jour += dt.timedelta(days=1)
    for pid, d in fixes.items():
        places[pid] = (dt.date.fromisoformat(d), soir)
    for c, lot in lots.items():
        for p in lot:
            if p["id"] in places:
                d, hm = places[p["id"]]
                p["iso"], p["heure"] = d.isoformat(), hm
                p["date"] = "%s %d %s" % (JOURS[d.weekday()], d.day, MOIS[d.month - 1])
        if not essai:
            json.dump(lot, open(os.path.join(RACINE, c), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tout = sorted((v[0].isoformat(), v[1], k) for k, v in places.items())
    for d, hm, k in tout:
        print(d, hm, k + ("  (date fixe)" if k in fixes else ""))
    libres_fin = max(places[p["id"]][0] for p in libres) if libres else None
    print("%d publications à venir, deux par jour jusqu'au %s, puis seulement les dates fixes (dernière : %s)"
          % (len(tout), libres_fin, tout[-1][0] if tout else "-"))


if __name__ == "__main__":
    main()
