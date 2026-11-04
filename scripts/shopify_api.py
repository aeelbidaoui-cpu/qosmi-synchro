#!/usr/bin/env python3
"""Connexion à la boutique Shopify Qosmi (Admin API GraphQL).

Accès : app créée dans le Dev Dashboard de Shopify, installée sur la boutique.
  - domaine de la boutique et Client ID : config/acces.json → SHOPIFY.boutique / SHOPIFY.client_id
  - Client secret : Trousseau macOS, service « deway-shopify »
Le jeton (valable 24 h) est redemandé automatiquement par « client credentials ».

Usage : python3 scripts/shopify_api.py --test   → vérifie la connexion (lecture seule)
"""
import json, os, subprocess, sys, time, urllib.parse, urllib.request, urllib.error

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
ACCES = os.path.join(RACINE, "config", "acces.json")
SERVICE = "deway-shopify"
VERSION = "2026-07"


def acces():
    if os.environ.get("SHOPIFY_CLIENT_ID"):  # serveur (GitHub Actions) : accès dans les « Secrets » du dépôt
        return os.environ["SHOPIFY_BOUTIQUE"], os.environ["SHOPIFY_CLIENT_ID"]
    try:
        with open(ACCES, encoding="utf-8") as f:
            d = json.load(f)["SHOPIFY"]
        return d["boutique"], d["client_id"]
    except (FileNotFoundError, KeyError):
        raise SystemExit("Accès Shopify absent : lancer « 14 - Shopify - Enregistrer l'acces ».")


def secret(cid):
    if os.environ.get("SHOPIFY_CLIENT_SECRET"):
        return os.environ["SHOPIFY_CLIENT_SECRET"]
    r = subprocess.run(["security", "find-generic-password", "-s", SERVICE, "-a", cid, "-w"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("Secret Shopify absent du Trousseau : lancer « 14 - Shopify - Enregistrer l'acces ».")
    return r.stdout.strip()


class Shopify:
    def __init__(self):
        self.boutique, self.cid = acces()
        self.jeton, self.expire = None, 0

    def _jeton(self):
        if self.jeton and time.time() < self.expire - 300:
            return self.jeton
        corps = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": self.cid,
                                        "client_secret": secret(self.cid)}).encode()
        req = urllib.request.Request("https://%s/admin/oauth/access_token" % self.boutique, data=corps,
                                     headers={"Content-Type": "application/x-www-form-urlencoded",
                                              "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)
        except urllib.error.HTTPError as e:
            raise SystemExit("Connexion Shopify refusée (%s) : %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))
        self.jeton = d["access_token"]
        self.expire = time.time() + int(d.get("expires_in", 86400))
        return self.jeton

    def gql(self, requete, variables=None):
        corps = json.dumps({"query": requete, "variables": variables or {}}).encode()
        for essai in range(6):
            req = urllib.request.Request("https://%s/admin/api/%s/graphql.json" % (self.boutique, VERSION), data=corps,
                                         headers={"Content-Type": "application/json",
                                                  "X-Shopify-Access-Token": self._jeton()})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    d = json.load(r)
            except urllib.error.HTTPError as e:
                if e.code in (429, 502, 503, 504):
                    time.sleep(2 * (essai + 1))
                    continue
                if e.code == 401:
                    self.jeton = None
                    continue
                raise RuntimeError("Shopify %s : %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))
            if d.get("errors") and any("THROTTLED" in json.dumps(x) for x in d["errors"]):
                time.sleep(2 * (essai + 1))
                continue
            if d.get("errors"):
                raise RuntimeError("Shopify : %s" % json.dumps(d["errors"])[:500])
            return d["data"]
        raise RuntimeError("Shopify : trop d'essais")


def test():
    s = Shopify()
    d = s.gql("""{ shop { name myshopifyDomain currencyCode primaryDomain { host } plan { displayName } }
                  locations(first: 10) { nodes { id name isActive } }
                  products(first: 1) { nodes { id } } }""")
    sh = d["shop"]
    print("Connexion OK : boutique « %s » (%s), devise %s, formule %s" % (sh["name"], sh["myshopifyDomain"],
                                                                   sh["currencyCode"], sh["plan"]["displayName"]))
    print("Domaine principal : %s" % sh["primaryDomain"]["host"])
    print("Lieux de stock : %s" % ", ".join(l["name"] for l in d["locations"]["nodes"]))
    print("Produits déjà présents : %s" % ("oui" if d["products"]["nodes"] else "aucun"))
    try:
        loc = s.gql("{ shopLocales { locale primary published } }")["shopLocales"]
        print("Langues : %s" % ", ".join("%s%s" % (l["locale"], " (principale)" if l["primary"] else "") for l in loc))
    except RuntimeError as e:
        print("Langues : accès pas encore accordé (%s)" % ("read_locales" if "read_locales" in str(e) else str(e)[:120]))
        print("  → Admin Shopify → Paramètres → Applications → Qosmi catalogue : accepter la mise à jour des autorisations.")

if __name__ == "__main__":
    if "--test" in sys.argv:
        test()
