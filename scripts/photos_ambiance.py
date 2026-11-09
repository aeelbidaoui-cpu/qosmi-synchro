#!/usr/bin/env python3
"""Photos d'ambiance du site (validées par Amine le 09/11/2026) : 8 photos gratuites Unsplash (licence Unsplash :
usage commercial libre), envoyées dans Contenu → Fichiers sous le nom qosmi-ambiance-<n>.jpg, recadrées en 4:5.
Utilisées par la section qk-ambiance (scripts/theme_rk.py)."""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PHOTOS = {  # n : (identifiant Unsplash, description)
    1: ("1784924247174-e8e52265a013", "Flacons de parfum posés sur un journal"),
    2: ("1615634260167-c8cdede054de", "Flacons de parfum alignés, en lumière douce"),
    3: ("1784183972601-17a1b00ea05e", "Main qui vaporise un parfum"),
    4: ("1622618991746-fe6004db3a47", "Flacons de parfum dorés dans la lumière"),
    5: ("1778434505577-28b8e26384f2", "Pivoine blanche dans un petit flacon de verre"),
    6: ("1760920250029-36af9369a0bb", "Flacon de parfum sur une fourrure blanche"),
    7: ("1783431412504-dba295fdee4e", "Reflets dorés d'un flacon de parfum"),
    8: ("1761659760494-32b921a2449f", "Flacon de parfum posé sur une surface couverte de gouttes"),
}


def main():
    from shopify_api import Shopify
    s = Shopify()
    for n, (pid, alt) in PHOTOS.items():
        nom = "qosmi-ambiance-%d.jpg" % n
        deja = s.gql("query($q: String!) { files(first: 3, query: $q) { nodes { id fileStatus } } }", {"q": "filename:%s" % nom})["files"]["nodes"]
        if deja:
            print("  %s déjà là (%s)" % (nom, deja[0]["fileStatus"]))
            continue
        url = "https://images.unsplash.com/photo-%s?w=1600&h=2000&fit=crop&crop=entropy&q=82&fm=jpg" % pid
        r = s.gql("""mutation($f: [FileCreateInput!]!) { fileCreate(files: $f) { files { id fileStatus } userErrors { field message } } }""",
                  {"f": [{"originalSource": url, "contentType": "IMAGE", "filename": nom, "alt": alt}]})["fileCreate"]
        print("  %s : %s" % (nom, r["userErrors"] or r["files"][0]["fileStatus"]))
    time.sleep(20)
    for n in PHOTOS:
        nom = "qosmi-ambiance-%d.jpg" % n
        f = s.gql("""query($q: String!) { files(first: 3, query: $q) { nodes { fileStatus fileErrors { message }
                     ... on MediaImage { image { url width height } } } } }""", {"q": "filename:%s" % nom})["files"]["nodes"]
        print("  contrôle %s : %s" % (nom, f[0] if f else "absent"))


if __name__ == "__main__":
    main()
