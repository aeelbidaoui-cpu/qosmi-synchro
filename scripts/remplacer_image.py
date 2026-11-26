#!/usr/bin/env python3
"""26/11/2026 (vitesse) : remplace le contenu d'une image de Contenu → Fichiers par la version de media/<nom>, en gardant le
même fichier (même nom, mêmes liens dans le thème). Première utilisation : qosmi-decor-coffret-noel.jpg, adoucie (grain
retiré) pour passer d'environ 480 Ko à 210 Ko sur téléphone."""
import os, sys, time, urllib.request, uuid

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)


def main(nom):
    from shopify_api import Shopify
    s = Shopify()
    f = s.gql("query($q: String!) { files(first: 5, query: $q) { nodes { id fileStatus ... on MediaImage { image { url } } } } }",
              {"q": "filename:%s" % nom})["files"]["nodes"]
    if not f:
        sys.exit("fichier %s introuvable" % nom)
    donnees = open(os.path.join(os.path.dirname(ICI), "media", nom), "rb").read()
    cible = s.gql("""mutation($i: [StagedUploadInput!]!) { stagedUploadsCreate(input: $i) { stagedTargets { url resourceUrl parameters { name value } } userErrors { message } } }""",
                  {"i": [{"resource": "IMAGE", "filename": nom, "mimeType": "image/jpeg", "httpMethod": "POST"}]})["stagedUploadsCreate"]["stagedTargets"][0]
    limite = "----qosmi" + uuid.uuid4().hex
    corps = b"".join(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (limite, p["name"], p["value"])).encode() for p in cible["parameters"])
    corps += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\nContent-Type: image/jpeg\r\n\r\n" % (limite, nom)).encode()
    corps += donnees + ("\r\n--%s--\r\n" % limite).encode()
    urllib.request.urlopen(urllib.request.Request(cible["url"], data=corps, method="POST",
                                                  headers={"Content-Type": "multipart/form-data; boundary=" + limite}), timeout=120).read()
    r = s.gql("""mutation($f: [FileUpdateInput!]!) { fileUpdate(files: $f) { files { id fileStatus } userErrors { field message } } }""",
              {"f": [{"id": f[0]["id"], "originalSource": cible["resourceUrl"]}]})["fileUpdate"]
    print("  %s : %d Ko envoyés, %s" % (nom, len(donnees) // 1024, r["userErrors"] or r["files"][0]["fileStatus"]))
    for _ in range(20):
        time.sleep(6)
        g = s.gql("query($q: String!) { files(first: 5, query: $q) { nodes { id fileStatus ... on MediaImage { image { url width height } } } } }",
                  {"q": "filename:%s" % nom})["files"]["nodes"]
        if g and g[0]["fileStatus"] in ("READY", "FAILED"):
            print("  contrôle :", g[0]); return
    print("  contrôle : toujours en traitement")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "qosmi-decor-coffret-noel.jpg")
