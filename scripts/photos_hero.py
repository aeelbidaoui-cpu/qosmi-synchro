#!/usr/bin/env python3
"""Envoie les images et vidéos du bandeau d'accueil (assets/hero/) dans les Fichiers Shopify (une seule fois par nom)."""
import os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
DOSSIER = os.path.join(os.path.dirname(ICI), "assets", "hero")


def video(s, chemin):
    """Vidéo (mp4) : envoi + attente du traitement par Shopify ; renvoie l'identifiant (gid://shopify/Video/…)."""
    import time, urllib.request, uuid
    nom = os.path.basename(chemin)
    q = "query($q: String!) { files(first: 20, query: $q) { nodes { ... on Video { id filename fileStatus } } } }"
    for x in s.gql(q, {"q": "filename:%s" % nom})["files"]["nodes"]:
        if x.get("filename") == nom and x.get("fileStatus") == "READY":
            return x["id"]
    taille = os.path.getsize(chemin)
    cible = s.gql("""mutation($i: [StagedUploadInput!]!) { stagedUploadsCreate(input: $i) { stagedTargets { url resourceUrl parameters { name value } } userErrors { message } } }""",
                  {"i": [{"resource": "VIDEO", "filename": nom, "mimeType": "video/mp4", "fileSize": str(taille), "httpMethod": "POST"}]})["stagedUploadsCreate"]["stagedTargets"][0]
    limite = "----qosmi" + uuid.uuid4().hex
    corps = b"".join(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (limite, p["name"], p["value"])).encode()
                     for p in cible["parameters"])
    corps += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\nContent-Type: video/mp4\r\n\r\n" % (limite, nom)).encode()
    corps += open(chemin, "rb").read() + ("\r\n--%s--\r\n" % limite).encode()
    urllib.request.urlopen(urllib.request.Request(cible["url"], data=corps, method="POST",
                                                  headers={"Content-Type": "multipart/form-data; boundary=" + limite}), timeout=300).read()
    f = s.gql("""mutation($f: [FileCreateInput!]!) { fileCreate(files: $f) { files { id } userErrors { message } } }""",
              {"f": [{"originalSource": cible["resourceUrl"], "contentType": "VIDEO", "filename": nom, "alt": "Qosmi"}]})["fileCreate"]
    if f["userErrors"]:
        print("  refus Shopify :", f["userErrors"])
        return None
    vid = f["files"][0]["id"]
    for _ in range(60):
        time.sleep(5)
        st = s.gql("query($id: ID!) { node(id: $id) { ... on Video { fileStatus } } }", {"id": vid})["node"]["fileStatus"]
        if st in ("READY", "FAILED"):
            print("  vidéo", st)
            break
    return vid


def main():
    from shopify_api import Shopify
    import photos_adp as pa
    s = Shopify()
    for nom in sorted(os.listdir(DOSSIER)):
        if nom.lower().endswith((".jpg", ".jpeg", ".png")):
            u = pa.adresse_fichier(s, nom) or pa.envoyer(s, os.path.join(DOSSIER, nom), alt="Qosmi")
            print("  %s → %s" % (nom, u or "échec"))
        elif nom.lower().endswith(".mp4"):
            print("  %s → %s" % (nom, video(s, os.path.join(DOSSIER, nom)) or "échec"))


if __name__ == "__main__":
    main()
