"""Donne la position x de chaque mot d'une ligne du manuscrit, pour griser ou entourer un mot dans une fiche.

Usage, depuis la racine du projet :
  python mots.py dictee_p4 6            mots de la ligne 6 de images_nb/dictee_p4.png
  python mots.py dictee_p4 6 7 12       plusieurs lignes
  python mots.py dictee_p4 6 --controle /tmp/opencode/<projet>/7_fiches/mots_p4_6.png

Le texte de la ligne est lu dans transcription/<exercice>.md (exercice = nom de la
page sans _p<N> ; section « ### Page N », ligne « 6. ... »). --texte "..." le remplace.
Les bandes viennent de supports/lignes.json (--lignes pour un autre chemin).

Sortie, une ligne par mot : numéro, mot, x0-x1, puis le triplet à copier dans
surligne: / entoure: de fiche.typ, et un niveau de confiance pour la ligne.

Méthode : dans le corps de la ligne (zone dense donnée par lignes.json, un peu
élargie), on redresse l'inclinaison de l'écriture, puis on repère les morceaux
d'encre séparés par des colonnes vides. Les morceaux sont répartis entre les mots
de la transcription, dans l'ordre, en coupant aux plus grands espaces : le
découpage colle donc toujours au nombre de mots transcrits. La ponctuation écrite
sans espace (« mot, ») reste avec son mot, même si elle est détachée sur le papier ;
séparée par une espace (« bureau : »), elle compte comme un mot. « l'artiste »
compte pour un mot.

Confiance :
- bonne   : les séparations sont nettes ; on utilise les x, vérifiés sur le rendu ;
- moyenne : probablement juste ; vérifie bien le placement sur le rendu de la fiche ;
- faible  : deux mots collés, un mot aux lettres très espacées, une ponctuation mal
            placée ; regarde l'image --controle de cette ligne (mots numérotés et
            règle graduée) et relève les x à la main. La liste brute des morceaux
            d'encre est aussi affichée.
"""
import argparse
import json
import os
import re
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def texte_ligne(transcription, page, ligne):
    """Texte de la ligne `ligne` de la section « ### Page `page` »."""
    cur = None
    for raw in open(transcription, encoding="utf-8"):
        m = re.match(r"^#{2,4}\s+\D*?(\d+)", raw)
        if m:
            cur = int(m.group(1))
            continue
        m = re.match(r"^\s*(\d+)\.\s+(.*)$", raw)
        if m and cur == page and int(m.group(1)) == ligne:
            return m.group(2)
    return None


def nettoyer(t):
    t = re.sub(r"<!--.*?-->", " ", t)
    t = re.sub(r"\{>>.*?<<\}", " ", t)              # commentaire CriticMarkup
    t = re.sub(r"\{==(.*?)==\}", r"\1", t)          # mot surligné : on garde le mot
    return t.split()


PONCTUATION = set(".,;:!?«»\"'()-–—…")


def est_ponctuation(mot):
    return all(c in PONCTUATION for c in mot)


def morceaux(gray, haut, bas, seuil_encre=160):
    """Morceaux d'encre séparés par des colonnes vides, après redressement de l'inclinaison.

    L'écriture penchée fait chevaucher les mots en projection verticale : on cherche
    l'inclinaison qui donne le plus de colonnes vides, puis on découpe. Renvoie
    [(x0, x1), ...] en coordonnées redressées, et pour chacun l'étendue x d'origine.
    """
    encre = (gray[haut:bas] < seuil_encre).astype(np.uint8) * 255
    h, w = encre.shape
    if not encre.any():
        return []
    pad = h  # place pour le cisaillement
    ym = h / 2
    meilleur = None
    for s in np.arange(-0.3, 1.01, 0.05):
        # x' = x + s * (y - ym) + pad : redresse une écriture penchée de pente s
        Mat = np.float32([[1, s, pad - s * ym], [0, 1, 0]])
        r = cv2.warpAffine(encre, Mat, (w + 2 * pad, h), flags=cv2.INTER_LINEAR) > 64
        prof = r.sum(0)
        nz = np.nonzero(prof)[0]
        vides = int((prof[nz[0]:nz[-1] + 1] == 0).sum())
        if meilleur is None or vides > meilleur[0]:
            meilleur = (vides, s, prof)
    _, s, prof = meilleur
    occupe = prof > 0
    runs, debut = [], None
    for i, v in enumerate(occupe):
        if v and debut is None:
            debut = i
        if not v and debut is not None:
            runs.append((debut, i - 1))
            debut = None
    if debut is not None:
        runs.append((debut, len(occupe) - 1))
    # étendue x d'origine de chaque morceau : pixels d'encre dont le x redressé y tombe
    ys, xs = np.nonzero(encre)
    xp = xs + s * (ys - ym) + pad
    out = []
    for r0, r1 in runs:
        sel = (xp >= r0 - 0.5) & (xp <= r1 + 0.5)
        if sel.any():
            out.append((r0, r1, int(xs[sel].min()), int(xs[sel].max())))
    return out


def decouper(gray, bande, mots_txt):
    """Répartit les morceaux d'encre entre les mots transcrits, dans l'ordre.

    Chaque mot reçoit des morceaux consécutifs ; on minimise la somme des espaces
    laissés à l'intérieur des mots (donc on coupe aux plus grands espaces). Deux
    préférences, pénalisées si elles ne sont pas tenues : un mot reçoit au moins un
    morceau de la taille d'une lettre, une ponctuation isolée (« : », « ! », « » »)
    ne reçoit que de petits morceaux. Une pénalité payée rend la confiance faible.
    """
    t, b, a, z = bande
    marge = int(0.25 * (z - a))
    M = morceaux(gray, max(a - marge, 0), min(z + marge, gray.shape[0]))
    n = len(mots_txt)
    if not M:
        return None, "aucune encre"
    if len(M) < n:
        return None, f"{len(M)} morceaux d'encre seulement pour {n} mots"
    petit = [m[1] - m[0] < 0.5 * (z - a) for m in M]
    large = [m[1] - m[0] > 1.2 * (z - a) for m in M]  # trop large même pour « ou »
    gap = [M[i + 1][0] - M[i][1] - 1 for i in range(len(M) - 1)]
    ponct = [est_ponctuation(w) for w in mots_txt]
    # un mot de une ou deux lettres (a, à, y, et) peut n'être qu'une petite marque
    court = [len([c for c in w if c not in PONCTUATION]) <= 2 for w in mots_txt]
    INF = float("inf")
    PENALITE = 10 * (z - a)
    # cout[j][i] : meilleur coût pour placer les j premiers mots sur les i premiers morceaux
    cout = [[INF] * (len(M) + 1) for _ in range(n + 1)]
    choix = [[None] * (len(M) + 1) for _ in range(n + 1)]
    cout[0][0] = 0
    for j in range(1, n + 1):
        for i in range(j, len(M) + 1):
            for k in range(j - 1, i):
                if cout[j - 1][k] == INF:
                    continue
                grands = sum(not p for p in petit[k:i])
                c = cout[j - 1][k] + sum(gap[k:i - 1])
                if (ponct[j - 1] and any(large[k:i])) or \
                        (not ponct[j - 1] and not court[j - 1] and not grands):
                    c += PENALITE
                if c < cout[j][i]:
                    cout[j][i], choix[j][i] = c, k
    bornes, i = [], len(M)
    for j in range(n, 0, -1):
        k = choix[j][i]
        bornes.append((k, i))
        i = k
    bornes.reverse()
    mots = [(min(m[2] for m in M[k:i]), max(m[3] for m in M[k:i])) for k, i in bornes]
    if cout[n][len(M)] >= PENALITE:
        return mots, ("faible (un mot n'a que de petites marques, ou une ponctuation isolée"
                      " contient un grand tracé : mots collés ou ponctuation mal placée)")
    if n == 1:
        return mots, "bonne"
    coupes = [gap[i - 1] for k, i in bornes[:-1]]
    # espaces internes, sauf ceux qui détachent une ponctuation collée (« doux . »)
    internes = [gap[x] for k, i in bornes for x in range(k, i - 1)
                if not petit[x] and not petit[x + 1]]
    mini, maxi = min(coupes), max(internes, default=0)
    r = mini / maxi if maxi else INF
    conf = "bonne" if r >= 1.5 and mini >= 5 else "moyenne" if r >= 1.15 else "faible"
    conf += f" (plus petit espace entre deux mots {mini} px, plus grand dans un mot {maxi} px)"
    return mots, conf


def controle(gray, bande, mots, sortie):
    """Bande de la ligne, mots numérotés, et une règle graduée en pixels de l'image."""
    t, b, a, z = bande
    regle = 70
    im = Image.new("RGB", (gray.shape[1], b - t + regle), "white")
    im.paste(Image.fromarray(gray[t:b]).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("DejaVuSans.ttf", 40)
    except OSError:
        f = ImageFont.load_default()
    for k, (x0, x1) in enumerate(mots, 1):
        couleur = (220, 0, 0) if k % 2 else (0, 90, 220)
        d.rectangle((x0, a - t - 10, x1, z - t + 10), outline=couleur, width=4)
        d.text((x0 + 4, 2), str(k), fill=couleur, font=f)
    y = b - t
    for x in range(0, gray.shape[1], 50):
        d.line((x, y, x, y + (25 if x % 100 == 0 else 12)), fill=(0, 140, 0), width=3)
        if x % 200 == 0:
            d.text((x + 4, y + 22), str(x), fill=(0, 140, 0), font=f)
    im = im.resize((im.width // 2, im.height // 2))
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    im.save(sortie)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", help="nom de l'image dans lignes.json, ex. dictee_p4")
    ap.add_argument("lignes_n", nargs="+", type=int, metavar="ligne")
    ap.add_argument("--lignes", default="supports/lignes.json")
    ap.add_argument("--transcription", default=None, help="défaut : transcription/<exercice>.md")
    ap.add_argument("--texte", default=None, help="texte de la ligne (une seule ligne)")
    ap.add_argument("--racine", default=".", help="racine du projet (celle de typst --root)")
    ap.add_argument("--controle", default=None, help="image de contrôle (une seule ligne)")
    a = ap.parse_args()

    P = json.load(open(a.lignes))
    if a.page not in P:
        sys.exit(f"{a.page} absent de {a.lignes}")
    p = P[a.page]
    m = re.match(r"^(.*)_p(\d+)$", a.page)
    if not m:
        sys.exit("nom de page attendu : <exercice>_p<N>")
    exercice, num = m.group(1), int(m.group(2))
    tr = a.transcription or os.path.join(a.racine, "transcription", exercice + ".md")
    gray = np.array(Image.open(os.path.join(a.racine, p["fichier"].lstrip("/"))).convert("L"))

    for l in a.lignes_n:
        if not 1 <= l <= len(p["lignes"]):
            print(f"{a.page} ligne {l} : absente de lignes.json ({len(p['lignes'])} lignes)\n")
            continue
        texte = a.texte if a.texte is not None else texte_ligne(tr, num, l)
        if texte is None:
            print(f"{a.page} ligne {l} : introuvable dans {tr}\n")
            continue
        mots_txt = nettoyer(texte)
        bande = p["lignes"][l - 1]
        mots, conf = decouper(gray, bande, mots_txt)
        print(f"{a.page} ligne {l} : « {' '.join(mots_txt)} »")
        if mots is None:
            print(f"  impossible : {conf} ; regarde --controle (morceaux d'encre numérotés)"
                  " et relève les x à la main\n")
            if a.controle:
                t, b, a_, z = bande
                marge = int(0.25 * (z - a_))
                M = morceaux(gray, max(a_ - marge, 0), min(z + marge, gray.shape[0]))
                controle(gray, bande, [(m[2], m[3]) for m in M], a.controle)
            continue
        for k, (w, (x0, x1)) in enumerate(zip(mots_txt, mots), 1):
            print(f"  {k:2d} {w:<20} x {x0}-{x1}   ({l}, {x0}, {x1})")
        print(f"  confiance : {conf}")
        if conf.startswith("faible"):
            t, b, a_, z = bande
            marge = int(0.25 * (z - a_))
            M = morceaux(gray, max(a_ - marge, 0), min(z + marge, gray.shape[0]))
            print("  morceaux d'encre (x) : " + ", ".join(f"{m[2]}-{m[3]}" for m in M))
        print()
        if a.controle:
            controle(gray, bande, mots, a.controle)


if __name__ == "__main__":
    main()
