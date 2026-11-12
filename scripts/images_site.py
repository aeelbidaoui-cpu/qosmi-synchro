#!/usr/bin/env python3
"""Images du site fournies par Amine (13/11/2026, générées avec Gemini) : assets/site/*.jpg.
Envoyées dans Contenu → Fichiers sous le même nom (une seule fois), puis utilisées par le thème (shopify://shop_images/<nom>)
et les pages (adresse CDN, champ {img_<nom sans qosmi- ni .jpg>} dans scripts/site_pages_contenu.py).

  python3 scripts/images_site.py      # envoie les images manquantes et affiche leurs adresses
"""
import glob, os, sys, time, urllib.request, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
DOSSIER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "site")


def _fichier(s, nom):
    n = s.gql("query($q: String!) { files(first: 3, query: $q) { nodes { id fileStatus ... on MediaImage { image { url } } } } }",
              {"q": "filename:%s" % nom})["files"]["nodes"]
    return n[0] if n else None


def envoyer(s, chemin):
    nom = os.path.basename(chemin)
    if _fichier(s, nom):
        return
    donnees = open(chemin, "rb").read()
    cible = s.gql("""mutation($i: [StagedUploadInput!]!) { stagedUploadsCreate(input: $i) { stagedTargets { url resourceUrl parameters { name value } } userErrors { message } } }""",
                  {"i": [{"resource": "IMAGE", "filename": nom, "mimeType": "image/jpeg", "httpMethod": "POST"}]})["stagedUploadsCreate"]["stagedTargets"][0]
    limite = "----qosmi" + uuid.uuid4().hex
    corps = b"".join(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (limite, p["name"], p["value"])).encode()
                     for p in cible["parameters"])
    corps += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\nContent-Type: image/jpeg\r\n\r\n" % (limite, nom)).encode()
    corps += donnees + ("\r\n--%s--\r\n" % limite).encode()
    urllib.request.urlopen(urllib.request.Request(cible["url"], data=corps, method="POST",
                                                  headers={"Content-Type": "multipart/form-data; boundary=%s" % limite}), timeout=120).read()
    r = s.gql("mutation($f: [FileCreateInput!]!) { fileCreate(files: $f) { files { id } userErrors { message } } }",
              {"f": [{"originalSource": cible["resourceUrl"], "contentType": "IMAGE", "filename": nom,
                      "alt": nom.replace("qosmi-", "").replace(".jpg", "").replace("-", " ")}]})["fileCreate"]
    if r["userErrors"]:
        raise SystemExit("%s : %s" % (nom, r["userErrors"]))
    print("  %s envoyée" % nom)


def urls(s, attendre=True):
    """{nom: adresse CDN} des images de assets/site (les envoie si besoin)."""
    out = {}
    for chemin in sorted(glob.glob(os.path.join(DOSSIER, "*.jpg"))):
        nom = os.path.basename(chemin)
        envoyer(s, chemin)
        for _ in range(30 if attendre else 1):
            f = _fichier(s, nom)
            if f and f.get("image") and f["image"].get("url"):
                out[nom] = f["image"]["url"]
                break
            time.sleep(3)
    return out


if __name__ == "__main__":
    from shopify_api import Shopify
    for nom, u in urls(Shopify()).items():
        print("OK", nom, u)
