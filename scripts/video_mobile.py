#!/usr/bin/env python3
"""Vidéo d'accueil pour téléphone (26/11/2026, vitesse) : version portrait 720x1280 (~0,6 Mo) de la vidéo d'ambiance,
recadrée comme elle s'affiche sur téléphone (72 % vers la droite). Envoyée dans Contenu → Fichiers sous le nom
qosmi-hero-mobile.mp4 ; le thème (theme_rk.py, réglage video_mobile de qk-hero) la montre à la place de la 4K (7 Mo)."""
import os, sys, time, urllib.request, uuid

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
NOM = "qosmi-hero-mobile.mp4"


def main():
    from shopify_api import Shopify
    s = Shopify()
    deja = s.gql("query($q: String!) { files(first: 3, query: $q) { nodes { id fileStatus } } }", {"q": "filename:%s" % NOM})["files"]["nodes"]
    if deja:
        print("  %s déjà là (%s)" % (NOM, deja[0]["fileStatus"]))
    else:
        donnees = open(os.path.join(os.path.dirname(ICI), "media", NOM), "rb").read()
        r = s.gql("""mutation($i: [StagedUploadInput!]!) { stagedUploadsCreate(input: $i) { stagedTargets { url resourceUrl parameters { name value } } userErrors { message } } }""",
                  {"i": [{"resource": "VIDEO", "filename": NOM, "mimeType": "video/mp4", "httpMethod": "POST", "fileSize": str(len(donnees))}]})["stagedUploadsCreate"]
        if r["userErrors"]:
            sys.exit("stagedUploadsCreate : %s" % r["userErrors"])
        cible = r["stagedTargets"][0]
        limite = "----qosmi" + uuid.uuid4().hex
        corps = b"".join(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (limite, p["name"], p["value"])).encode()
                         for p in cible["parameters"])
        corps += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\nContent-Type: video/mp4\r\n\r\n" % (limite, NOM)).encode()
        corps += donnees + ("\r\n--%s--\r\n" % limite).encode()
        urllib.request.urlopen(urllib.request.Request(cible["url"], data=corps, method="POST",
                                                      headers={"Content-Type": "multipart/form-data; boundary=" + limite}), timeout=300).read()
        r = s.gql("""mutation($f: [FileCreateInput!]!) { fileCreate(files: $f) { files { id fileStatus } userErrors { field message } } }""",
                  {"f": [{"originalSource": cible["resourceUrl"], "contentType": "VIDEO", "filename": NOM,
                          "alt": "Ingrédients de parfum en mouvement : agrumes, rose, figue, vanille"}]})["fileCreate"]
        print("  %s : %d Ko envoyés, %s" % (NOM, len(donnees) // 1024, r["userErrors"] or r["files"][0]["fileStatus"]))
    for _ in range(40):
        f = s.gql("""query($q: String!) { files(first: 3, query: $q) { nodes { fileStatus fileErrors { message }
                     ... on Video { sources { url height mimeType } } } } }""", {"q": "filename:%s" % NOM})["files"]["nodes"]
        if f and f[0]["fileStatus"] in ("READY", "FAILED"):
            print("  contrôle %s : %s" % (NOM, f[0]))
            return
        time.sleep(15)
    print("  contrôle %s : toujours en traitement" % NOM)


if __name__ == "__main__":
    main()
