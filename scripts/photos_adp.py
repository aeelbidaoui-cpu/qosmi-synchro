#!/usr/bin/env python3
"""Acqua di Parma : envoi des photos officielles (accord de la marque du 05/11/2026) dans les Fichiers Shopify.

Le site acquadiparma.com refuse que Shopify vienne chercher les photos lui-même. Amine les a téléchargées
dans son navigateur le 07/11/2026 ; elles sont dans assets/photos_adp/ (21 photos, 2400 × 2400).
Ce script les envoie dans les Fichiers Shopify (une seule fois : un fichier déjà présent est repris tel quel),
puis remplace dans config/photos_acquadiparma.json l'adresse du site par l'adresse Shopify de la photo,
et écrit la correspondance dans rapports/theme/adp_cdn.json.
"""
import json, os, sys, time, urllib.request, uuid

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.dirname(ICI)
DOSSIER = os.path.join(RACINE, "assets", "photos_adp")


def adresse_fichier(s, nom):
    n = s.gql("query($q: String!) { files(first: 20, query: $q) { nodes { ... on MediaImage { fileStatus image { url } } } } }",
              {"q": "filename:%s" % nom})["files"]["nodes"]
    for x in n:
        if x.get("fileStatus") == "READY" and x.get("image"):
            u = x["image"]["url"].split("?")[0]
            if u.rsplit("/", 1)[-1] == nom:  # la recherche Shopify trouve aussi les noms qui commencent pareil
                return u
    return None


def envoyer(s, chemin, alt="Acqua di Parma"):
    nom = os.path.basename(chemin)
    cible = s.gql("""mutation($i: [StagedUploadInput!]!) { stagedUploadsCreate(input: $i) { stagedTargets { url resourceUrl parameters { name value } } userErrors { message } } }""",
                  {"i": [{"resource": "IMAGE", "filename": nom, "mimeType": "image/jpeg", "httpMethod": "POST"}]})["stagedUploadsCreate"]["stagedTargets"][0]
    limite = "----qosmi" + uuid.uuid4().hex
    corps = b"".join(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (limite, p["name"], p["value"])).encode()
                     for p in cible["parameters"])
    corps += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\nContent-Type: image/jpeg\r\n\r\n" % (limite, nom)).encode()
    corps += open(chemin, "rb").read() + ("\r\n--%s--\r\n" % limite).encode()
    urllib.request.urlopen(urllib.request.Request(cible["url"], data=corps, method="POST",
                                                  headers={"Content-Type": "multipart/form-data; boundary=" + limite}), timeout=120).read()
    f = s.gql("""mutation($f: [FileCreateInput!]!) { fileCreate(files: $f) { files { id } userErrors { field message } } }""",
              {"f": [{"originalSource": cible["resourceUrl"], "contentType": "IMAGE", "filename": nom, "alt": alt}]})["fileCreate"]
    if f["userErrors"]:
        print("  refus Shopify :", nom, f["userErrors"])
        return None
    for _ in range(40):
        time.sleep(3)
        u = adresse_fichier(s, nom)
        if u:
            return u
    return None


def main():
    from shopify_api import Shopify
    s = Shopify()
    chemin_conf = os.path.join(RACINE, "config", "photos_acquadiparma.json")
    conf = json.load(open(chemin_conf, encoding="utf-8"))
    sortie = {}
    for src in sorted(set(conf["par_ean"].values())):
        nom = "qosmi-adp-" + src.rsplit("/", 1)[1]
        chemin = os.path.join(DOSSIER, nom)
        if src.startswith("https://cdn.shopify.com"):
            continue
        if not os.path.exists(chemin):
            print("  photo absente du dépôt :", nom)
            continue
        u = adresse_fichier(s, nom) or envoyer(s, chemin)
        print("  %s → %s" % (nom, u or "échec"))
        if u:
            sortie[src] = u
    conf["par_ean"] = {e: sortie.get(u, u) for e, u in conf["par_ean"].items()}
    json.dump(conf, open(chemin_conf, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    os.makedirs(os.path.join(RACINE, "rapports", "theme"), exist_ok=True)
    json.dump(sortie, open(os.path.join(RACINE, "rapports", "theme", "adp_cdn.json"), "w"), indent=1)
    shutil_copy = os.path.join(RACINE, "rapports", "theme", "photos_acquadiparma.json")
    json.dump(conf, open(shutil_copy, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("Photos Acqua di Parma dans les Fichiers Shopify : %d" % len(sortie))


if __name__ == "__main__":
    main()
