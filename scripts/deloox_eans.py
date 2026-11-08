#!/usr/bin/env python3
"""Liste des EAN à relever chez Deloox : ceux déjà connus (config/deloox.json) + tous les formats qui ont une photo autorisée
(config/photos_*.json), c'est-à-dire les parfums qui sont ou peuvent être en ligne. Usage : python3 scripts/deloox_eans.py > eans.json"""
import glob, json, os
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
eans = set(json.load(open(os.path.join(RACINE, "config", "deloox.json")))["par_ean"])
for f in glob.glob(os.path.join(RACINE, "config", "photos_*.json")):
    if f.endswith("photos_cadrees.json"):
        continue
    eans |= {e.lstrip("0") for e in (json.load(open(f)).get("par_ean") or {}) if e.isdigit()}
print(json.dumps(sorted(eans)))
