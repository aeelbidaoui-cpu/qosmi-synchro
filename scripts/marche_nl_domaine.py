#!/usr/bin/env python3
"""qosmi.nl = domaine du marché Pays-Bas, en néerlandais (25/11/2026, Amine : option 2, même boutique).
26/11/2026 (Amine : « qosmi.fr […] je veux que quelqu'un qui cherche qosmi.fr voie aussi le catalogue comme les
hollandais ») : même chose pour qosmi.fr → marché France, en français. Variable DOMAINE=qosmi.fr (par défaut qosmi.nl).
--etat : lecture seule (marchés, présences web, domaines). --appliquer : crée la présence web du domaine
(langue par défaut du pays, + les autres langues) et la rattache au marché du pays."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import Shopify

s = Shopify()
PAYS = {
    "qosmi.nl": {"marches": ("Pays-Bas", "Netherlands", "Nederland"), "langue": "nl", "autres": ["fr", "en"]},
    "qosmi.fr": {"marches": ("France",), "langue": "fr", "autres": ["nl", "en"]},
}
DOMAINE = os.environ.get("DOMAINE") or "qosmi.nl"
CONF = PAYS[DOMAINE]
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


def domaine_nl():  # (nom gardé) : identifiant Shopify du domaine DOMAINE
    # Domaines de la boutique : on passe par la recherche de domaine connu
    for q in ['{ shop { domains { id host sslEnabled } } }']:
        try:
            for dm in s.gql(q)["shop"]["domains"]:
                print("domaine", dm)
                if dm["host"] == DOMAINE:
                    return dm["id"]
        except Exception as e:
            print("domains :", e)
    return None


def appliquer():
    d = etat()
    nl = [m for m in d["markets"]["nodes"] if m["name"] in CONF["marches"]]
    if not nl:
        sys.exit("Marché %s introuvable" % CONF["marches"][0])
    nl = nl[0]
    for w in nl["webPresences"]["nodes"]:
        if (w.get("domain") or {}).get("host") == DOMAINE:
            print("Déjà en place : %s" % w["id"]); return
    dom = domaine_nl()
    if not dom:
        sys.exit("Domaine %s introuvable dans la boutique (à connecter d'abord dans Paramètres → Domaines)" % DOMAINE)
    r = s.gql("""mutation($i: WebPresenceCreateInput!){ webPresenceCreate(input:$i){ webPresence{ id domain{ host } defaultLocale{ locale } }
              userErrors{ field message } } }""", {"i": {"domainId": dom, "defaultLocale": CONF["langue"], "alternateLocales": CONF["autres"]}})
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
