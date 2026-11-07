#!/usr/bin/env python3
"""Envoie les images du bandeau d'accueil (assets/hero/*.jpg) dans les Fichiers Shopify (une seule fois par nom)."""
import os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
DOSSIER = os.path.join(os.path.dirname(ICI), "assets", "hero")


def main():
    from shopify_api import Shopify
    import photos_adp as pa
    s = Shopify()
    for nom in sorted(os.listdir(DOSSIER)):
        if nom.lower().endswith((".jpg", ".jpeg", ".png")):
            u = pa.adresse_fichier(s, nom) or pa.envoyer(s, os.path.join(DOSSIER, nom), alt="Qosmi")
            print("  %s → %s" % (nom, u or "échec"))


if __name__ == "__main__":
    main()
