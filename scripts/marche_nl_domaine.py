#!/usr/bin/env python3
"""qosmi.nl = domaine du marché Pays-Bas, en néerlandais (25/11/2026, Amine : option 2, même boutique).
--etat : lecture seule (marchés, présences web, domaines). --appliquer : crée la présence web qosmi.nl
(langue par défaut nl, + fr et en) et la rattache au marché Pays-Bas."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import Shopify

s = Shopify()
Q = """{ shop { primaryDomain { id host } }
  domains: webPresences(first:20){ nodes{ id domain{ id host } subfolderSuffix defaultLocale{ locale } alternateLocales{ locale }
    markets(first:10){ nodes{ name } } } }
  markets(first:20){ nodes{ id name enabled webPresences(first:5){ nodes{ id domain{ host } subfolderSuffix } } } } }"""


def etat():
    try:
        d = s.gql(Q)
    except Exception as e:
        print("Requête complète refusée (%s), version courte" % e)
        d = s.gql("{ markets(first:20){ nodes{ id name enabled webPresences(first:5){ nodes{ id domain{ host } subfolderSuffix } } } } }")
    print(json.dumps(d, ensure_ascii=False, indent=1))
    return d


def domaine_nl():
    # Domaines de la boutique : on passe par la recherche de domaine connu
    for q in ['{ shop { domains { id host sslEnabled } } }']:
        try:
            for dm in s.gql(q)["shop"]["domains"]:
                print("domaine", dm)
                if dm["host"] == "qosmi.nl":
                    return dm["id"]
        except Exception as e:
            print("domains :", e)
    return None


def appliquer():
    d = etat()
    nl = [m for m in d["markets"]["nodes"] if m["name"] in ("Pays-Bas", "Netherlands", "Nederland")]
    if not nl:
        sys.exit("Marché Pays-Bas introuvable")
    nl = nl[0]
    for w in nl["webPresences"]["nodes"]:
        if (w.get("domain") or {}).get("host") == "qosmi.nl":
            print("Déjà en place : %s" % w["id"]); return
    dom = domaine_nl()
    if not dom:
        sys.exit("Domaine qosmi.nl introuvable dans la boutique")
    r = s.gql("""mutation($i: WebPresenceCreateInput!){ webPresenceCreate(input:$i){ webPresence{ id domain{ host } defaultLocale{ locale } }
              userErrors{ field message } } }""", {"i": {"domainId": dom, "defaultLocale": "nl", "alternateLocales": ["fr", "en"]}})
    print(json.dumps(r, ensure_ascii=False))
    wp = (r["webPresenceCreate"]["webPresence"] or {}).get("id")
    if not wp:
        sys.exit("Création de la présence web refusée")
    r = s.gql("""mutation($id: ID!, $i: MarketUpdateInput!){ marketUpdate(id:$id, input:$i){ market{ name webPresences(first:5){ nodes{ id domain{ host } } } }
              userErrors{ field message } } }""", {"id": nl["id"], "i": {"webPresencesToAdd": [wp]}})
    print(json.dumps(r, ensure_ascii=False))
    etat()


if __name__ == "__main__":
    appliquer() if "--appliquer" in sys.argv else (etat(), domaine_nl())
