#!/usr/bin/env python3
"""Prix et stock d'EAN chez nos grossistes branchés sur le serveur (SoleLuna, liste « bons plans », Wholesale-Fragrances).
27/11/2026 (Amine : « chez qui c'est le moins cher »). Sortie CHIFFRÉE : le dépôt est public, aucun prix d'achat ni nom
de fournisseur ne doit apparaître en clair dans les journaux. Variables : EANS, CLE_PUBLIQUE (PEM RSA)."""
import base64, json, os, subprocess, sys, tempfile, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_synchro as ss
import site_soleluna as sl
import site_variantes as sv

eans = [e.strip().lstrip("0") for e in (os.environ.get("EANS") or "").replace(",", " ").split() if e.strip()]
res, notes = {e: [] for e in eans}, []

def chercher(nom, octets):
    txt = octets.decode("utf-8-sig", "replace").replace("\r\n", "\n").replace("\r", "\n")
    lignes = txt.split("\n")
    entete = lignes[0] if lignes else ""
    for l in lignes[1:]:
        for e in eans:
            if e in l:
                res[e].append({"source": nom, "entete": entete[:400], "ligne": l[:600]})

try:
    ss.listes_serveur()
    chercher("SoleLuna", open(sl.SOURCE, "rb").read())
except Exception as ex:
    notes.append("SoleLuna : %s" % ex)
if os.path.exists(sv.TRISTA):
    chercher("Bons plans (2e grossiste)", open(sv.TRISTA, "rb").read())
else:
    notes.append("liste bons plans absente")
url = os.environ.get("WF_URL", "").strip()
if url:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ss.AGENT}), timeout=180) as r:
            chercher("Wholesale-Fragrances", r.read())
    except Exception as ex:
        notes.append("WF : %s" % ex)

d = tempfile.mkdtemp()
pub, cle, data = (os.path.join(d, x) for x in ("pub.pem", "cle.bin", "data.bin"))
open(pub, "w").write(os.environ["CLE_PUBLIQUE"].replace("\\n", "\n"))
open(cle, "wb").write(os.urandom(32))
open(data + ".json", "w").write(json.dumps({"res": res, "notes": notes}))
subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-in", data + ".json", "-out", data, "-pass", "file:" + cle], check=True)
ck = subprocess.run(["openssl", "pkeyutl", "-encrypt", "-pubin", "-inkey", pub, "-in", cle], check=True, capture_output=True).stdout
os.remove(data + ".json")
print("EANS %d · trouvés %d" % (len(eans), sum(1 for v in res.values() if v)))
print("CLE " + base64.b64encode(ck).decode())
print("DATA " + base64.b64encode(open(data, "rb").read()).decode())
