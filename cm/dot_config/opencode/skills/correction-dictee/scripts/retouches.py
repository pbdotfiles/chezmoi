"""Efface des traces d'encre accidentelles sur les images imprimables, puis montre avant/après.

Usage : python retouches.py operations.json --avant /tmp/opencode/taches/avant

operations.json (à écrire dans /tmp/opencode, pas dans le projet) :
{
  "images_nb/dictee_p1.png": [
    ["rect", 1505, 1415, 1560, 1485, "goutte au-dessus de époque"],
    ["pale", 985, 1050, 1025, 1192, 60, "trait pâle au-dessus de plante"],
    ["line", 1535, 2405, 1590, 2455, 18, "faux accent sur personnage"]
  ]
}
- rect x0 y0 x1 y1        : blanchit toute la zone ;
- pale x0 y0 x1 y1 seuil  : blanchit seulement les pixels plus clairs que le seuil
                            (garde le cœur noir des lettres qui traversent la zone) ;
- line x0 y0 x1 y1 épaisseur : blanchit un trait.
Le dernier élément texte (description) est facultatif.

Le script repart toujours de la copie « avant » si elle existe (relancer après
correction des coordonnées ne cumule pas les retouches). Il écrit, pour chaque
opération, <avant>/../verif_<nom>_<k>.png : zone avant | après, agrandie, et pour
chaque image une planche <avant>/../verif_<nom>.png qui les regroupe toutes,
numérotées : on regarde la planche pour vérifier qu'aucune lettre voisine n'a été
touchée. Il affiche aussi l'encre restante dans chaque zone (0 = zone complètement
blanchie ; un rectangle tombé à côté de la tache se voit ainsi tout de suite).
"""
import argparse
import json
import os
import shutil

import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("operations")
    ap.add_argument("--avant", required=True, help="dossier où garder les images avant retouche")
    a = ap.parse_args()
    os.makedirs(a.avant, exist_ok=True)
    verif = os.path.dirname(os.path.abspath(a.avant))
    ops_all = json.load(open(a.operations))
    for f, ops in ops_all.items():
        name = os.path.splitext(os.path.basename(f))[0]
        orig = os.path.join(a.avant, os.path.basename(f))
        if not os.path.exists(orig):
            shutil.copy(f, orig)
        before = cv2.imread(orig, cv2.IMREAD_GRAYSCALE)
        g = before.copy()
        vues = []
        for k, op in enumerate(ops, 1):
            op = [x for x in op if not isinstance(x, str) or x in ("rect", "pale", "line")]
            kind, x0, y0, x1, y1, *p = op
            if kind == "rect":
                g[y0:y1, x0:x1] = 255
            elif kind == "pale":
                roi = g[y0:y1, x0:x1]
                roi[roi > p[0]] = 255
            elif kind == "line":
                cv2.line(g, (x0, y0), (x1, y1), 255, int(p[0]))
            # vérification visuelle et numérique
            xa, xb = sorted((x0, x1))
            ya, yb = sorted((y0, y1))
            m = 60
            X0, Y0 = max(xa - m, 0), max(ya - m, 0)
            X1, Y1 = min(xb + m, g.shape[1]), min(yb + m, g.shape[0])
            av = before[Y0:Y1, X0:X1]
            ap_ = g[Y0:Y1, X0:X1]
            sep = np.full((av.shape[0], 8), 128, np.uint8)
            vis = np.hstack([av, sep, ap_])
            vis = cv2.resize(vis, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
            cv2.imwrite(os.path.join(verif, f"verif_{name}_{k}.png"), vis)
            vues.append((k, vis))
            reste = int((g[ya:yb, xa:xb] < 200).sum())
            avant = int((before[ya:yb, xa:xb] < 200).sum())
            print(f"{name} #{k} {kind}: encre dans la zone {avant} -> {reste} px")
        cv2.imwrite(f, g)
        if vues:
            planche(vues, os.path.join(verif, f"verif_{name}.png"))
            print(f"{name}: planche avant | après dans {os.path.join(verif, f'verif_{name}.png')}")


def planche(vues, sortie, hauteur=240, largeur_max=1800):
    """Toutes les vues avant | après d'une image, numérotées, sur une seule planche."""
    rangs, rang, w = [], [], 0
    for k, v in vues:
        s = hauteur / v.shape[0]
        v = cv2.resize(v, (max(int(v.shape[1] * s), 1), hauteur))
        v = cv2.cvtColor(v, cv2.COLOR_GRAY2BGR)
        cv2.putText(v, str(k), (6, 28), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        v = cv2.copyMakeBorder(v, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=(0, 160, 0))
        if rang and w + v.shape[1] > largeur_max:
            rangs.append(rang)
            rang, w = [], 0
        rang.append(v)
        w += v.shape[1]
    rangs.append(rang)
    L = max(sum(v.shape[1] for v in r) for r in rangs)
    lignes = []
    for r in rangs:
        ligne = np.hstack(r)
        lignes.append(cv2.copyMakeBorder(ligne, 0, 0, 0, L - ligne.shape[1],
                                         cv2.BORDER_CONSTANT, value=(255, 255, 255)))
    cv2.imwrite(sortie, np.vstack(lignes))


if __name__ == "__main__":
    main()
