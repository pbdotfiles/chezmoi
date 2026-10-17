"""Repère les marques pâles isolées (traces d'encre accidentelles probables). Ne modifie rien.

Usage : python candidats.py images_nb/*.png --sortie /tmp/opencode/<projet>/3_taches

Écrit, pour chaque image :
- <sortie>/cand_<nom>.jpg : la page réduite de moitié, candidats encadrés et numérotés ;
- <sortie>/planche_<nom>_<k>.jpg : planche de vignettes agrandies, une par candidat,
  numérotées comme sur la page (24 vignettes au plus par planche) ;
- <sortie>/candidats.json : x, y, w, h en pixels de l'image.

Limites connues : ce repérage rate les vraies taches, noires et collées aux
lettres, et il signale aussi des accents ou des points légitimes. Il sert à
orienter l'œil : on regarde la page entière (cand_*.jpg) puis les planches, et on
ne zoome à part (zoomreg.py) que sur une trace précise.
"""
import argparse
import json
import os

import cv2
import numpy as np


def planches(g, cands, nom, sortie, par_planche=24, cote=260, colonnes=6):
    """Vignettes de `cote` px autour de chaque candidat, numérotées, en grille."""
    vignettes = []
    for k, (x, y, w, h, _) in enumerate(cands, 1):
        cx, cy = x + w // 2, y + h // 2
        d = max(110, w // 2 + 40, h // 2 + 40)
        X0, Y0 = max(cx - d, 0), max(cy - d, 0)
        crop = g[Y0:cy + d, X0:cx + d]
        v = cv2.cvtColor(cv2.resize(crop, (cote, cote)), cv2.COLOR_GRAY2BGR)
        s = cote / (2 * d)
        cv2.rectangle(v, (int((x - X0) * s) - 4, int((y - Y0) * s) - 4),
                      (int((x + w - X0) * s) + 4, int((y + h - Y0) * s) + 4), (0, 0, 255), 2)
        cv2.putText(v, str(k), (6, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        vignettes.append(cv2.copyMakeBorder(v, 3, 3, 3, 3, cv2.BORDER_CONSTANT, value=(160, 160, 160)))
    for p in range(0, len(vignettes), par_planche):
        lot = vignettes[p:p + par_planche]
        while len(lot) % colonnes:
            lot.append(np.full_like(lot[0], 255))
        rangs = [np.hstack(lot[i:i + colonnes]) for i in range(0, len(lot), colonnes)]
        cv2.imwrite(os.path.join(sortie, f"planche_{nom}_{p // par_planche + 1}.jpg"), np.vstack(rangs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--pale", type=float, default=70,
                    help="un tracé dont les 10 %% les plus sombres restent au-dessus de ce gris est 'pâle'")
    a = ap.parse_args()
    os.makedirs(a.sortie, exist_ok=True)
    out = {}
    for f in a.images:
        g = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
        ink = (g < 200).astype(np.uint8)
        ink = cv2.dilate(ink, np.ones((7, 7), np.uint8))  # regrouper les morceaux d'un même tracé
        n, lab, st, _ = cv2.connectedComponentsWithStats(ink)
        vis = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        cands = []
        for i in range(1, n):
            x, y, w, h, area = st[i]
            px = g[lab == i]
            core = px[px < 200]
            if len(core) < 30:
                continue
            p10 = np.percentile(core, 10)  # les vrais tracés ont un cœur noir
            if p10 > a.pale:
                cands.append((int(x), int(y), int(w), int(h), float(p10)))
        for k, (x, y, w, h, p) in enumerate(cands, 1):
            cv2.rectangle(vis, (x - 15, y - 15), (x + w + 15, y + h + 15), (0, 0, 255), 4)
            cv2.putText(vis, str(k), (x + w + 20, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
        name = os.path.splitext(os.path.basename(f))[0]
        cv2.imwrite(os.path.join(a.sortie, f"cand_{name}.jpg"), cv2.resize(vis, None, fx=0.5, fy=0.5))
        if cands:
            planches(g, cands, name, a.sortie)
        out[name] = cands
        print(name, len(cands), "candidats")
    json.dump(out, open(os.path.join(a.sortie, "candidats.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
