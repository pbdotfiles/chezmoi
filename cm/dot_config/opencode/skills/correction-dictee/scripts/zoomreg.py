"""Extrait une zone d'image avec des graduations tous les 50 px (repérage des coordonnées).

Usage : python zoomreg.py image.png x0 y0 x1 y1 sortie.png [--echelle 2]

Les graduations portent les coordonnées de l'image entière : on peut les
recopier telles quelles dans une retouche ou dans un surlignage de fiche.
"""
import argparse

import cv2

ap = argparse.ArgumentParser()
ap.add_argument("image")
ap.add_argument("x0", type=int)
ap.add_argument("y0", type=int)
ap.add_argument("x1", type=int)
ap.add_argument("y1", type=int)
ap.add_argument("sortie")
ap.add_argument("--echelle", type=float, default=1.0)
a = ap.parse_args()

x0, y0, x1, y1 = a.x0, a.y0, a.x1, a.y1
g = cv2.imread(a.image, cv2.IMREAD_GRAYSCALE)[y0:y1, x0:x1]
v = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
for x in range((x0 // 50 + 1) * 50, x1, 50):
    c = (0, 0, 255) if x % 100 == 0 else (0, 180, 255)
    cv2.line(v, (x - x0, 0), (x - x0, 12), c, 2)
    if x % 100 == 0:
        cv2.putText(v, str(x), (x - x0 + 2, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, c, 1)
for y in range((y0 // 50 + 1) * 50, y1, 50):
    c = (0, 0, 255) if y % 100 == 0 else (0, 180, 255)
    cv2.line(v, (0, y - y0), (12, y - y0), c, 2)
    if y % 100 == 0:
        cv2.putText(v, str(y), (14, y - y0 + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, c, 1)
if a.echelle != 1.0:
    v = cv2.resize(v, None, fx=a.echelle, fy=a.echelle, interpolation=cv2.INTER_NEAREST)
cv2.imwrite(a.sortie, v)
