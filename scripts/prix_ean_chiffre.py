#!/usr/bin/env python3
"""Prix de vente, coût d'achat et stock de variantes par EAN, sortie CHIFFRÉE (27/11/2026 : liste « target price »
pour un fournisseur). Le dépôt est public : le coût d'achat ne doit jamais apparaître en clair dans les journaux.
Clé publique RSA dans la variable CLE_PUBLIQUE (PEM) ; sortie : clé AES chiffrée RSA + données chiffrées AES, en base64."""
import base64, json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import Shopify
s = Shopify()
Q = """query($q: String!) { productVariants(first: 10, query: $q) { nodes { title barcode price inventoryQuantity
  inventoryItem { unitCost { amount } } product { title status } } } }"""
out = {}
for ean in (os.environ.get("EANS") or "").replace(",", " ").split():
    q = "barcode:%s OR barcode:0%s" % (ean.lstrip("0"), ean.lstrip("0"))
    out[ean] = [{"t": v["product"]["title"], "v": v["title"], "st": v["product"]["status"], "p": v["price"],
                 "q": v["inventoryQuantity"], "c": ((v["inventoryItem"] or {}).get("unitCost") or {}).get("amount")}
                for v in s.gql(Q, {"q": q})["productVariants"]["nodes"]]
d = tempfile.mkdtemp()
pub, cle, data = (os.path.join(d, x) for x in ("pub.pem", "cle.bin", "data.bin"))
open(pub, "w").write(os.environ["CLE_PUBLIQUE"].replace("\\n", "\n"))
open(cle, "wb").write(os.urandom(32))
open(data + ".json", "w").write(json.dumps(out))
subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-in", data + ".json", "-out", data, "-pass", "file:" + cle], check=True)
ck = subprocess.run(["openssl", "pkeyutl", "-encrypt", "-pubin", "-inkey", pub, "-in", cle], check=True, capture_output=True).stdout
os.remove(data + ".json")
print("EANS %d" % len(out))
print("CLE " + base64.b64encode(ck).decode())
print("DATA " + base64.b64encode(open(data, "rb").read()).decode())
