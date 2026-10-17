# Étape 5 : lignes des images

## Objectif

`supports/lignes.json` : pour chaque image de `images_nb/`, la position de chaque ligne d'écriture, **numérotée comme dans la transcription**. Les fiches s'en servent pour découper les extraits du manuscrit (« page 2, lignes 3 à 5 »), placer les surlignages, et trouver la position des mots (`scripts/mots.py`). Une ligne décalée et un extrait montre la mauvaise phrase.

Les images doivent être définitives (après les taches). Si elles changent ensuite, cette étape est à refaire.

## Outil

`scripts/lignes.py` de la skill (lis sa docstring). Donne-lui le nombre de lignes attendu par image, lu dans `transcription/` (`--attendu dictee_p1=12 ...`) : il cherche alors le réglage qui donne ce nombre. Avec `--controle`, il dessine les bandes numérotées sur chaque image.

## Méthode

1. Lance le script sur toutes les images, sortie `supports/lignes.json`, contrôle dans ton dossier temporaire.
2. Regarde chaque image de contrôle. Pour chaque ligne, vérifie que la bande porte le bon numéro (compare le premier mot avec la transcription), qu'elle contient les jambages et les accents sans mordre franchement sur la ligne voisine.
3. Corrige à la main dans le JSON ce qui ne va pas : ligne manquante (ligne très courte ou très pâle), deux lignes fusionnées, fausse ligne (flèche, rature, ajout entre deux lignes). Un ajout écrit entre deux lignes (mot inséré) doit tomber dans la bande de la ligne où il se lit, si possible.
4. Relance le contrôle après correction, et regarde seulement les pages corrigées.

Images : seulement les images de contrôle (une par page, plus une par page corrigée), et au besoin un zoom sur un cas limite. Tu ne lis pas le manuscrit : la transcription validée fait foi, tu t'en sers pour compter et repérer les lignes. Ne rouvre pas une image déjà vue.

## Rapport final

Nombre de lignes par image (et nombre attendu), corrections manuelles faites, cas limites (ajout entre deux lignes, ligne coupée par le cadre), nombre d'images ouvertes.

## Critères d'acceptation

Pour chaque image, autant de lignes que dans la transcription, dans le même ordre, vérifiées sur l'image de contrôle.
