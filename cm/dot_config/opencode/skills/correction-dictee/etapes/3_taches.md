# Étape 3 : taches d'encre

## Objectif

Effacer sur `images_nb/` les traces d'encre accidentelles (gouttes, traits de main qui glisse, bavures, points parasites, bouts de lettres d'une ligne coupée par le cadre). Elles gênent la lecture de l'enfant et peuvent passer pour de la ponctuation ou des accents.

Cette étape vient **après la validation de la lecture** : la transcription a été relue et corrigée par Papa, elle fait foi. C'est elle qui dit ce qui est un signe voulu.

## Entrées

`images_nb/` (étape 2), `transcription/` (validée : lettres, accents et ponctuation voulus), `AGENTS.md` (décisions de Papa à la validation de la lecture, par exemple « le ":" après nomades a bavé, le laisser »).

Tu n'as pas besoin des photos d'origine : ne les ouvre pas.

## Outils

Dans `scripts/` de la skill : `candidats.py` (repère les marques pâles isolées, produit la page annotée et des planches de vignettes numérotées), `retouches.py` (applique les effacements depuis un fichier JSON, produit une planche avant | après par image), `zoomreg.py` (zoom gradué en coordonnées de l'image, pour une trace précise). Copie-les dans ton dossier temporaire si tu les adaptes.

## La règle de décision

Pour chaque trace, regarde la transcription de la ligne :
- **la transcription ne l'explique pas** (ce n'est ni une lettre, ni un accent, ni un signe transcrit) et rien dans l'écriture ne peut l'expliquer : c'est une tache, **tu l'effaces** ;
- **la transcription l'explique** (le point, la virgule, l'accent transcrits à cet endroit), ou c'est une rature, un mot barré, une flèche, un ajout, une bavure d'un vrai signe : **tu la gardes** ;
- **le moindre doute** (elle pourrait être un bout de lettre, un accent, un signe) : **tu la laisses**. Une tache restée gêne peu ; un signe effacé fausse la fiche.

Tu ne poses aucune question à Papa et tu ne lui soumets aucune trace.

## Méthode

1. Lance `candidats.py` sur toutes les pages. Pour chaque page, regarde `cand_<page>.jpg` (page entière) puis ses planches de vignettes. Le repérage automatique rate les taches noires collées aux lettres : la page entière sert à les voir.
2. Écris les opérations dans un JSON de ton dossier temporaire (pas dans le projet), avec une courte description par opération. Relève les coordonnées sur les vignettes et dans `candidats.json` ; ne zoome à part (`zoomreg.py`) que pour une tache collée à une lettre.
3. Lance `retouches.py` : il garde l'image d'origine et repart toujours d'elle. Regarde la planche `verif_<page>.png` : la trace a disparu, aucune lettre voisine n'est entamée. Un rectangle « tombé à côté » se voit au chiffre d'encre restante qui ne baisse pas : corrige et relance.

Images : environ 3 par page (page annotée, planche de vignettes, planche avant | après), plus quelques zooms pour les taches collées aux lettres. Pas plus de 30 dans la session. Ne rouvre pas une image déjà vue.

## Rapport final

1. Traces effacées, par image : position (page, entre quelles lignes ou près de quel mot), nature.
2. Traces laissées par prudence, en une ligne chacune (pour information, pas de question).
3. Nombre d'images ouvertes.

## Critères d'acceptation

- Chaque retouche est vérifiée sur la planche avant | après ; aucune lettre touchée.
- Aucune trace expliquée par la transcription n'a été effacée.
- Les photos d'origine sont intactes.
