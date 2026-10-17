# Étape 2 : images imprimables

## Objectif

Pour chaque photo, une image `images_nb/<exercice>_p<N>.png` qui ressemble à une photocopie propre : redressée, recadrée sur le texte, en niveaux de gris, fond blanc, quadrillage et spirale effacés, écriture bien noire. Ces images seront imprimées et découpées en extraits dans les fiches : l'enfant y lira son propre manuscrit.

## Entrées

`photos/<exercice>/`, `AGENTS.md` (ordre des pages).

## Point de départ

`scripts/nettoyage.py` de la skill (lis sa docstring). Il a été mis au point sur un cahier Seyès à spirale, écrit à l'encre bleue. **Lance-le d'abord tel quel**, avec `--controle`, sur toutes les pages. N'adapte le script que si le contrôle ou la planche montre un vrai défaut ; dans ce cas, copie-le dans ton dossier temporaire et corrige ce défaut précis. Cas qui demandent une adaptation : encre noire ou crayon (le filtre « bleu » effacerait tout), feuille simple, photo de biais (redresser la perspective), éclairage très inégal, autre position de la spirale, tissu ou table visibles. Pas de série d'essais pour un rendu un peu plus joli.

## Règles

- **Tout le texte reste.** Ne jamais blanchir une zone qui contient de l'écriture. Mieux vaut un reste de spirale, d'ombre ou de quadrillage qu'une lettre, un accent ou un point coupé. (Une première version effaçait tout à droite de la spirale et coupait la fin des lignes : Papa préfère une spirale un peu moins propre.)
- Garde les niveaux de gris : un seuillage noir et blanc pur fait disparaître les traits pâles, les accents et les points.
- Garde les traces de travail de l'enfant : ratures, mots barrés, flèches, ajouts entre les lignes. Elles font partie du manuscrit.
- Ne retouche pas les taches d'encre accidentelles : c'est l'étape 3.
- Ne modifie jamais les photos d'origine.

## Vérifications

1. Lance le script avec `--controle` : l'encre de la photo absente de la sortie apparaît en rouge, et le nombre de pixels perdus près du texte est affiché. Il doit être nul ou s'expliquer (reflet de spirale contre une lettre). Regarde chaque image de contrôle.
2. Si du rouge apparaît près du texte, ou si une ligne semble coupée au bord, zoome sur ce bord seulement (photo et sortie côte à côte, dans une seule image).
3. Fais une planche de toutes les pages réduites : `/tmp/opencode/<projet>/2_images/planche.png`. Papa la regardera à la validation de la lecture.

Images : les aperçus, une image de contrôle par page, la planche, et quelques zooms de bords si besoin. Pas plus de 30 images dans la session ; assemble plusieurs vues dans une même image plutôt que de les ouvrir une à une. Ne rouvre pas une image déjà vue.

## Rapport final

Fichiers produits (nom, taille en pixels), adaptations faites au script et pourquoi, chiffres d'encre perdue par page, chemin de la planche, défauts restants visibles (restes de spirale, ombre, quadrillage pâle).

## Critères d'acceptation

- Une image par photo, au bon nom, dans `images_nb/`.
- Encre perdue près du texte nulle ou expliquée, pour chaque page.
- La planche existe.
