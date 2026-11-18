#!/usr/bin/env python3
"""Qosmi — visuels du lot n°6 « Le bon parfum pour chaque moment » : mêmes gabarits que le lot n°5 (visuels_lot5.py).

  python3 social/legendes_lot6.py && QOSMI_ACTIFS_LOT5=… python3 social/visuels_lot6.py [id …]
"""
import json, os, sys
from PIL import Image
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import legendes_lot5 as L5  # noqa: E402
import legendes_lot6 as L6  # noqa: E402
import visuels_lot5 as V  # noqa: E402


class Donnees:
    """Ce que les gabarits du lot 5 attendent (P, SIG, années, notes), pour les parfums du lot 6."""
    P = L6.P
    SIG = {}
    concentration = staticmethod(L5.concentration)

    @staticmethod
    def annee(cle):
        return (L5.PROFILS.get(L6.P[cle][0]) or {}).get("a")

    @staticmethod
    def notes(cle, nl=False, n=4):
        sauve = L5.P
        L5.P = L6.P
        try:
            return L5.notes(cle, nl, n)
        finally:
            L5.P = sauve


V.L5 = Donnees
V.T["fr"].update(sur="Le bon moment", src="Profil · Fragrance Index")
V.T["nl"].update(sur="Het juiste moment", src="Profiel · Fragrance Index")
OUT = os.path.join(ICI, "lot6")


def main():
    lot = json.load(open(os.path.join(OUT, "lot6.json"), encoding="utf-8"))
    src = {p["id"]: p for p in L6.L}
    seul = sys.argv[1:]
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        pg = nav.new_page(viewport={"width": 1080, "height": 1350})
        for q in lot:
            if seul and q["id"] not in seul:
                continue
            p = dict(src[q["id"]], langue=q["langue"])
            m = L6.MOMENT.get(p.get("moment"))
            if p["type"] == "pdj":
                Donnees.SIG[p["parfums"][0]] = m
            elif p["type"] == "sel":
                p["sig"] = {c: m for c in p["parfums"]}
            pages = {"pdj": V.pdj, "sel": V.sel, "conseil": V.conseil}[p["type"]](p)
            assert len(pages) == len(q["img"]), q["id"]
            for nom, h in zip(q["img"], pages):
                f = os.path.join(OUT, nom + ".html")
                open(f, "w", encoding="utf-8").write(h)
                pg.goto("file://" + f)
                pg.wait_for_timeout(150)
                png = os.path.join(OUT, nom + ".png")
                pg.screenshot(path=png)
                Image.open(png).convert("RGB").save(os.path.join(OUT, nom + ".jpg"), quality=90)
                os.remove(png)
                os.remove(f)
            print(q["id"], len(pages))
        nav.close()


if __name__ == "__main__":
    main()
