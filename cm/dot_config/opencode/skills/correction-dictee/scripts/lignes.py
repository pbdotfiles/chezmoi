"""Repère les lignes d'écriture sur les images imprimables, pour les extraits des fiches.

Usage : python lignes.py images_nb/*.png --sortie supports/lignes.json --controle /tmp/opencode/lignes

Pour chaque image, écrit dans lignes.json :
  "nom": {"fichier": "/images_nb/nom.png", "w": W, "h": H,
          "lignes": [[haut, bas, haut_du_corps, bas_du_corps], ...]}
- haut / bas : bande de la ligne (découpe d'un extrait) ;
- haut_du_corps / bas_du_corps : zone où l'encre est dense (sert à placer
  surlignages et ellipses). Coordonnées en pixels de l'image.
La numérotation doit correspondre à celle de la transcription (ligne 1 = ligne 1).

Méthode : profil horizontal de l'encre, lissé ; les bandes au-dessus d'un seuil
sont des corps de ligne ; les limites sont prises à mi-chemin entre deux corps.
Points de vigilance (à vérifier sur les images de contrôle, et à corriger à la
main dans le JSON si besoin) :
- une ligne très courte ou très pâle peut manquer (ajuster --seuil) ;
- deux lignes serrées, ou des jambages longs (f, g, p), peuvent fusionner ;
- une flèche, une rature ou un ajout entre deux lignes peut créer une fausse ligne ;
- le nombre de lignes trouvé est affiché : le comparer à la transcription.
"""
import argparse
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import uniform_filter1d


def corps(gray, seuil=0.08, lissage=25, min_h=30):
    ink = (gray < 128).sum(1).astype(float)
    s = uniform_filter1d(ink, lissage)
    on = s > s.max() * seuil
    runs, start = [], None
    for i, v in enumerate(on):
        if v and start is None:
            start = i
        if not v and start is not None:
            runs.append((start, i))
            start = None
    if start is not None:
        runs.append((start, len(on)))
    return [r for r in runs if r[1] - r[0] > min_h]


def chercher(gray, attendu, seuil, lissage):
    """Essaie plusieurs réglages pour trouver le nombre de lignes attendu."""
    if attendu is None:
        return corps(gray, seuil, lissage), (seuil, lissage)
    meilleur = None
    for lis in (25, 15, 11, 7):
        for sv in (0.08, 0.05, 0.12, 0.15, 0.2, 0.25, 0.3, 0.35):
            r = corps(gray, sv, lis)
            if len(r) == attendu:
                return r, (sv, lis)
            if meilleur is None or abs(len(r) - attendu) < abs(len(meilleur[0]) - attendu):
                meilleur = (r, (sv, lis))
    return meilleur


def bandes(cores, H):
    """Bandes de découpe : à mi-chemin entre deux corps, sans englober un grand blanc."""
    if not cores:
        return []
    hauteur = float(np.median([z - a for a, z in cores]))
    if len(cores) > 1:
        pas = float(np.median([cores[i + 1][0] - cores[i][0] for i in range(len(cores) - 1)]))
    else:
        pas = 2.5 * hauteur
    marge = max(0.6 * (pas - hauteur), 0.3 * hauteur)  # jambages et accents
    out = []
    for i, (a, z) in enumerate(cores):
        top = (cores[i - 1][1] + a) // 2 if i > 0 else 0
        bot = (z + cores[i + 1][0]) // 2 if i < len(cores) - 1 else H
        top = max(top, int(a - marge))
        bot = min(bot, int(z + marge))
        out.append([int(max(top, 0)), int(min(bot, H)), int(a), int(z)])
    return out


def controle(path, lignes, dossier):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("DejaVuSans.ttf", 60)
    except OSError:
        f = ImageFont.load_default()
    for k, (t, b, a, z) in enumerate(lignes, 1):
        d.rectangle((0, t, im.width - 1, b), outline=(255, 0, 0), width=4)
        d.rectangle((0, a, 40, z), fill=(0, 160, 255))
        d.text((50, t + 5), str(k), fill=(255, 0, 0), font=f)
    im = im.resize((im.width // 3, im.height // 3))
    os.makedirs(dossier, exist_ok=True)
    im.save(os.path.join(dossier, os.path.basename(path)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--controle", default=None)
    ap.add_argument("--seuil", type=float, default=0.08)
    ap.add_argument("--attendu", nargs="*", default=[],
                    help="nombre de lignes attendu par image, ex. dictee_p1=12 (tiré de la transcription)")
    ap.add_argument("--prefixe", default="/images_nb/",
                    help="chemin des images vu depuis la racine typst (--root)")
    a = ap.parse_args()
    data = {}
    if os.path.exists(a.sortie):
        data = json.load(open(a.sortie))
    attendu = {k: int(v) for k, v in (x.split("=") for x in a.attendu)}
    for p in a.images:
        g = np.array(Image.open(p).convert("L"))
        H, W = g.shape
        name = os.path.splitext(os.path.basename(p))[0]
        n = attendu.get(name)
        cores, reglage = chercher(g, n, a.seuil, 25)
        L = bandes(cores, H)
        data[name] = {"fichier": a.prefixe + os.path.basename(p), "w": W, "h": H, "lignes": L}
        alerte = "" if n is None or n == len(L) else f"  ATTENTION : {n} attendues, à corriger à la main"
        print(f"{name}: {len(L)} lignes (seuil={reglage[0]}, lissage={reglage[1]}){alerte}")
        if a.controle:
            controle(p, L, a.controle)
    # une ligne par ligne d'écriture, lisible et facile à corriger à la main
    s = "{\n" + ",\n".join(
        f'  "{k}": {{\n    "fichier": "{v["fichier"]}", "w": {v["w"]}, "h": {v["h"]},\n    "lignes": [\n'
        + ",\n".join("      " + json.dumps(l) for l in v["lignes"]) + "\n    ]\n  }"
        for k, v in data.items()) + "\n}\n"
    os.makedirs(os.path.dirname(a.sortie) or ".", exist_ok=True)
    open(a.sortie, "w").write(s)


if __name__ == "__main__":
    main()
