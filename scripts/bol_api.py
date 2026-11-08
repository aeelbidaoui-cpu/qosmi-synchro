#!/usr/bin/env python3
"""Connexion à l'API officielle bol.com (Retailer API v10) pour la boutique Qosmi.

Accès :
  - serveur (GitHub Actions) : secrets du dépôt BOL_CLIENT_ID et BOL_CLIENT_SECRET ;
  - Mac : Client ID dans config/acces.json (BOL.client_id), secret dans le Trousseau (service « deway-bol »).
Le jeton (≈ 5 min) est redemandé automatiquement. Les pauses imposées par bol (429) sont respectées.

Usage : python3 scripts/bol_api.py --test   → vérifie la connexion (lecture seule)
"""
import base64, json, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
ACCES = os.path.join(RACINE, "config", "acces.json")
SERVICE = "deway-bol"
API = "https://api.bol.com"
ACCEPT = "application/vnd.retailer.v10+json"


def client_id():
    if os.environ.get("BOL_CLIENT_ID"):
        return os.environ["BOL_CLIENT_ID"].strip()
    try:
        with open(ACCES, encoding="utf-8") as f:
            return json.load(f)["BOL"]["client_id"]
    except (FileNotFoundError, KeyError):
        raise SystemExit("Accès bol absent : secrets BOL_CLIENT_ID / BOL_CLIENT_SECRET du dépôt (serveur) "
                         "ou « 9 - bol - Enregistrer la cle API » (Mac).")


def secret(cid):
    if os.environ.get("BOL_CLIENT_SECRET"):
        return os.environ["BOL_CLIENT_SECRET"].strip()
    r = subprocess.run(["security", "find-generic-password", "-s", SERVICE, "-a", cid, "-w"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("Secret bol absent du Trousseau : lancer « 9 - bol - Enregistrer la cle API ».")
    return r.stdout.strip()


class Bol:
    def __init__(self):
        self.cid = client_id()
        self.token, self.expire = None, 0
        self.appels = self.pauses = 0

    def _jeton(self):
        if self.token and time.time() < self.expire - 20:
            return self.token
        auth = base64.b64encode(("%s:%s" % (self.cid, secret(self.cid))).encode()).decode()
        req = urllib.request.Request("https://login.bol.com/token?grant_type=client_credentials", data=b"",
                                     method="POST", headers={"Authorization": "Basic " + auth,
                                                             "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)
        except urllib.error.HTTPError as e:
            raise SystemExit("Connexion bol refusée (%s) : vérifier le Client ID et le secret." % e.code)
        self.token = d["access_token"]
        self.expire = time.time() + int(d.get("expires_in", 299))
        return self.token

    def appel(self, methode, chemin, params=None, corps=None):
        url = API + chemin + ("?" + urllib.parse.urlencode(params) if params else "")
        donnees = json.dumps(corps).encode() if corps is not None else None
        for essai in range(8):
            h = {"Authorization": "Bearer " + self._jeton(), "Accept": ACCEPT}
            if donnees is not None:
                h["Content-Type"] = ACCEPT
            req = urllib.request.Request(url, data=donnees, method=methode, headers=h)
            try:
                self.appels += 1
                with urllib.request.urlopen(req, timeout=40) as r:
                    texte = r.read()
                    return json.loads(texte) if texte else {}
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                if e.code == 401:
                    self.token = None
                    continue
                if e.code == 429:
                    self.pauses += 1
                    time.sleep(min(max(int(e.headers.get("Retry-After") or 10), 1), 120))
                    continue
                if e.code >= 500:
                    time.sleep(3 * (essai + 1))
                    continue
                raise RuntimeError("%s %s → %s %s" % (methode, chemin, e.code, e.read().decode("utf-8", "replace")[:300]))
            except (urllib.error.URLError, TimeoutError):
                time.sleep(3 * (essai + 1))
        raise RuntimeError("%s %s : échec après plusieurs essais" % (methode, chemin))

    def get(self, chemin, params=None):
        return self.appel("GET", chemin, params)

    def post(self, chemin, corps):
        return self.appel("POST", chemin, corps=corps)

    def put(self, chemin, corps):
        return self.appel("PUT", chemin, corps=corps)

    def delete(self, chemin):
        return self.appel("DELETE", chemin)

    def statut(self, pid, tours=20):
        """Attend la fin d'un traitement bol (création d'offre, etc.)."""
        d = {}
        for _ in range(tours):
            d = self.get("/shared/process-status/%s" % pid) or {}
            if d.get("status") in ("SUCCESS", "FAILURE", "TIMEOUT"):
                return d
            time.sleep(3)
        return d


if __name__ == "__main__":
    if "--test" in sys.argv:
        b = Bol()
        b._jeton()
        print("Connexion bol : ok (jeton obtenu).")
