"""Nettoyage d'une photo de cahier pour impression noir et blanc.

Usage : python nettoyage.py photo.jpg sortie.png [--controle dossier]

Point de départ validé sur un cahier Seyès à spirale, écrit à l'encre bleue.
À adapter librement (autre encre, crayon, feuille simple, photo de biais...).

Principe :
- le canal rouge sépare l'encre bleue (rouge faible) du quadrillage violet clair
  (rouge élevé) ; on compense l'éclairage en divisant par un fond estimé ;
- on ne garde que ce qui est bleu (élimine spirale, ombres, tissu) ;
- on blanchit ce qui est hors de la feuille ;
- RÈGLE : ne jamais blanchir une zone qui contient de l'écriture. Mieux vaut
  un reste de spirale ou d'ombre qu'une lettre coupée. Les tracés d'encre qui
  partent de la feuille sont toujours protégés, même s'ils débordent sur la
  spirale ou sur le bord.

Avec --controle, écrit dossier/<nom>_controle.png (réduit au tiers) : l'encre de
la photo qui a disparu de la sortie est en rouge. Le script affiche les pixels
d'encre perdus près du texte (doit être 0) et isolés (reflets probables, à
regarder sur l'image de contrôle).
"""
import argparse
import os

import cv2
import numpy as np
from PIL import Image, ImageOps


def load(path):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return np.array(im)


def paper_hull(rgb):
    """Enveloppe de la feuille (trous remplis), non rognée."""
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    v, s = hsv[..., 2], hsv[..., 1]
    m = ((v > 150) & (s < 90)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((61, 61), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    big = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    m = (lab == big).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    full = np.zeros_like(m)
    cv2.drawContours(full, cnts, -1, 255, -1)
    return full


def clean(rgb, lo=0.45, hi=0.75, gamma=1.0):
    r = rgb[..., 0].astype(np.float32)
    b = rgb[..., 2].astype(np.float32)
    # fond = maximum local lissé (efface encre et lignes fines)
    bg = cv2.dilate(r, np.ones((31, 31), np.uint8))
    bg = cv2.GaussianBlur(bg, (0, 0), 25)
    ratio = np.clip(r / np.maximum(bg, 1), 0, 1)
    dark = 1 - np.clip((ratio - lo) / (hi - lo), 0, 1) ** gamma
    # ne garder que ce qui est bleu (encre)
    blue = np.clip((b - r - 8) / 25, 0, 1)
    blue = cv2.dilate(blue, np.ones((5, 5), np.uint8))
    blue = cv2.GaussianBlur(blue, (0, 0), 1.5)
    out = 1 - dark * blue
    return (out * 255).astype(np.uint8)


def ink_mask(rgb):
    """Encre franche sur la photo (bleu foncé)."""
    r = rgb[..., 0].astype(int)
    b = rgb[..., 2].astype(int)
    return (r < 110) & (b - r > 30)


def spiral_x(rgb, band=0.15, frac=0.12):
    """Abscisse de début de la spirale (bord droit), ou None."""
    r = rgb[..., 0].astype(int)
    b = rgb[..., 2].astype(int)
    neutral_dark = (r < 120) & (np.abs(b - r) < 20)
    col = neutral_dark.mean(axis=0)
    W = rgb.shape[1]
    x0 = int(W * (1 - band))
    hits = np.nonzero(col[x0:] > frac)[0]
    return x0 + hits.min() - 40 if len(hits) else None


def bottom_y(rgb):
    """Début d'un bord inférieur hors feuille (tissu, table), ou None."""
    dark_rows = (rgb[..., 0] < 120).mean(axis=1)
    H = rgb.shape[0]
    y0 = int(H * 0.85)
    band = dark_rows[y0:] > 0.5
    # exiger 30 lignes sombres consécutives (une ligne d'écriture dense ne suffit pas)
    run = np.convolve(band.astype(int), np.ones(30, int), mode="valid")
    hits = np.nonzero(run == 30)[0]
    return y0 + hits.min() - 30 if len(hits) else None


def crop_to_ink(gray, margin=120):
    ink = gray < 128
    ink = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    ys, xs = np.nonzero(ink)
    H, W = gray.shape
    y0, y1 = max(ys.min() - margin, 0), min(ys.max() + margin, H)
    x0, x1 = max(xs.min() - margin, 0), min(xs.max() + margin, W)
    return y0, y1, x0, x1


def process(src, dst, controle=None):
    rgb = load(src)
    hull = paper_hull(rgb)
    inner = cv2.erode(hull, np.ones((41, 41), np.uint8))  # feuille sans son bord
    keep = inner > 0
    sx = spiral_x(rgb)
    if sx is not None:
        keep[:, sx:] = False
    by = bottom_y(rgb)
    if by is not None:
        keep[by:, :] = False

    g = clean(rgb)

    # Protection de l'écriture : on regroupe l'encre de la photo par voisinage
    # (un point reste rattaché à son mot). Tout groupe qui touche la zone gardée
    # est conservé entier, même s'il déborde sur la spirale ou sur le bord.
    ink = ink_mask(rgb) & (hull > 0)
    if by is not None:
        ink[by:, :] = False
    groups = cv2.dilate(ink.astype(np.uint8) | (g < 200).astype(np.uint8), np.ones((25, 25), np.uint8))
    n, lab, _, _ = cv2.connectedComponentsWithStats(groups, connectivity=8)
    touching = np.unique(lab[keep & (g < 200)])
    protect = np.isin(lab, touching[touching > 0])

    g[~(keep | protect)] = 255

    y0, y1, x0, x1 = crop_to_ink(g)
    out = g[y0:y1, x0:x1]
    Image.fromarray(out).save(dst, optimize=True, dpi=(300, 300))

    # Contrôle : encre de la photo devenue blanche. "proche" = à moins de 80 px
    # d'une écriture conservée (lettre ou ponctuation coupée : à corriger) ;
    # "isolée" = loin de tout texte (souvent un reflet de spirale : à regarder).
    full = np.full_like(g, 255)
    full[y0:y1, x0:x1] = out
    lost = ink & (full > 200)
    lost = cv2.morphologyEx(lost.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    near = cv2.dilate((full < 128).astype(np.uint8), np.ones((161, 161), np.uint8)) > 0
    print(f"{dst} {out.shape} spirale={sx} bas={by} "
          f"encre_perdue_proche={int((lost & near).sum())} px encre_perdue_isolee={int((lost & ~near).sum())} px")
    if controle:
        os.makedirs(controle, exist_ok=True)
        vis = cv2.cvtColor(full, cv2.COLOR_GRAY2RGB)
        vis[cv2.dilate(lost.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0] = (255, 0, 0)
        name = os.path.splitext(os.path.basename(dst))[0]
        Image.fromarray(vis).resize((vis.shape[1] // 3, vis.shape[0] // 3)).save(
            os.path.join(controle, f"{name}_controle.png"))
    return int((lost & near).sum())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--controle", default=None)
    a = ap.parse_args()
    process(a.src, a.dst, a.controle)
