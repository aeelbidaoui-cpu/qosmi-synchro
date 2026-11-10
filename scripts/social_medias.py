#!/usr/bin/env python3
"""Plan B réseaux sociaux (10/11/2026) : Meta bloque l'accès développeur, donc les publications sont programmées
à la main dans Meta Business Suite. Pour pouvoir y charger les visuels, on les met dans Contenu → Fichiers de Shopify
(qosmi-social-<visuel>.jpg), accessibles sur https://qosmi.be/cdn/shop/files/qosmi-social-<visuel>.jpg.
Usage : social_medias.py social/lot1/lot1.json [autres lots…]"""
import json, os, sys, urllib.request, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def envoyer(s, chemin, nom):
    donnees = open(chemin, "rb").read()
    cible = s.gql("""mutation($i: [StagedUploadInput!]!) { stagedUploadsCreate(input: $i) { stagedTargets { url resourceUrl parameters { name value } } } }""",
                  {"i": [{"resource": "IMAGE", "filename": nom, "mimeType": "image/jpeg", "httpMethod": "POST"}]})["stagedUploadsCreate"]["stagedTargets"][0]
    limite = "----qosmi" + uuid.uuid4().hex
    corps = b"".join(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (limite, p["name"], p["value"])).encode()
                     for p in cible["parameters"])
    corps += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\nContent-Type: image/jpeg\r\n\r\n" % (limite, nom)).encode()
    corps += donnees + ("\r\n--%s--\r\n" % limite).encode()
    urllib.request.urlopen(urllib.request.Request(cible["url"], data=corps, method="POST",
                                                  headers={"Content-Type": "multipart/form-data; boundary=" + limite}), timeout=120).read()
    r = s.gql("""mutation($f: [FileCreateInput!]!) { fileCreate(files: $f) { files { id } userErrors { message } } }""",
              {"f": [{"originalSource": cible["resourceUrl"], "contentType": "IMAGE", "filename": nom, "alt": "Qosmi"}]})["fileCreate"]
    return r["userErrors"]


def main(lots):
    from shopify_api import Shopify
    s = Shopify()
    deja = set()
    c = None
    while True:
        d = s.gql("""query($c: String) { files(first: 250, after: $c, query: "filename:qosmi-social-*") { pageInfo { hasNextPage endCursor }
                     nodes { ... on MediaImage { image { url } } } } }""", {"c": c})["files"]
        for n in d["nodes"]:
            u = ((n.get("image") or {}).get("url") or "").split("?")[0]
            deja.add(u.rsplit("/", 1)[-1])
        if not d["pageInfo"]["hasNextPage"]:
            break
        c = d["pageInfo"]["endCursor"]
    faits = err = 0
    for lot in lots:
        dossier = os.path.dirname(os.path.join(RACINE, lot))
        for p in json.load(open(os.path.join(RACINE, lot), encoding="utf-8")):
            for img in p["img"]:
                nom = "qosmi-social-%s.jpg" % img
                if nom in deja:
                    continue
                e = envoyer(s, os.path.join(dossier, img + ".jpg"), nom)
                if e:
                    err += 1
                    print("  %s : %s" % (nom, e))
                else:
                    faits += 1
    print("Visuels réseaux sociaux : %d envoyés, %d déjà là, %d erreurs" % (faits, len(deja), err))


if __name__ == "__main__":
    main(sys.argv[1:] or ["social/lot1/lot1.json"])
