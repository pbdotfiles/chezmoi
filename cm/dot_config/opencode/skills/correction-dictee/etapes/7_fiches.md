# Étape 7 : fiches d'un bloc

## Objectif

Pour le bloc qui t'est confié : `supports/bloc<N>.typ` et `.pdf` (fiche enfant), `supports/bloc<N>_papa.typ` et `.pdf` (guide Papa). Rien d'autre.

Lis d'abord `references/fiches.md` (présentation, types d'exercices, justesse des règles) et `references/methode.md` de la skill. Si l'orchestrateur te donne une fiche déjà faite comme modèle, suis sa présentation.

## Entrées

`analyse/plan.md` (ton bloc), `analyse/inventaire_fautes.md`, `transcription/`, `supports/lignes.json`, `supports/fiche.typ` (copié par l'orchestrateur), `AGENTS.md`. Les images de `images_nb/` sont utilisées par typst ; tu n'as pas à les ouvrir.

## Règles de travail

- Tu ne modifies que les quatre fichiers de ton bloc. Pas `fiche.typ`, pas `lignes.json`, pas les images, pas l'inventaire : d'autres agents travaillent en même temps. S'il te faut une fonction de plus, définis-la en haut de ton `bloc<N>.typ`. Si `lignes.json` ou l'inventaire te semblent faux, signale-le dans ton rapport.
- Suis le plan. Si une partie du plan ne marche pas sur la page (exemple qui montre une autre faute, extrait trop long, règle douteuse), adapte et explique pourquoi dans ton rapport.
- **La transcription validée fait foi.** Tu ne relis pas le manuscrit pour vérifier une lecture ou une faute. Si, sur ton rendu, un extrait semble contredire la transcription, signale-le dans ton rapport sans aller vérifier.
- Recompte : le nombre de fautes annoncé dans chaque consigne doit être égal au nombre de corrections du guide Papa pour cet exercice.

## Position des mots à griser ou entourer

Lance `scripts/mots.py` depuis la racine du projet (lis sa docstring) :

```text
python <skill>/scripts/mots.py dictee_p4 6 12
```

Il lit le texte de chaque ligne dans la transcription et donne, pour chaque mot, sa position x et le triplet à recopier dans `surligne:` ou `entoure:` (`(6, 1320, 1570)`). Pour griser plusieurs mots qui se suivent, prends le x0 du premier et le x1 du dernier.

- Confiance **bonne** ou **moyenne** : utilise les x tels quels ; tu vérifies sur le rendu.
- Confiance **faible** (mots collés, ponctuation mal placée) : relance la ligne avec `--controle <dossier temporaire>/mots_<page>_<ligne>.png`. Cette image montre seulement la ligne, les mots numérotés et une règle graduée : relève les x corrects dessus. C'est la seule image du manuscrit que tu ouvres.

## Vérification

1. Compile les deux documents depuis la racine du projet (`typst compile --root . ...`).
2. Rends chaque page en PNG dans ton dossier temporaire et regarde **chaque page** : annotations sur le bon mot, ellipses entières, exemples corrects sans faute visible de la même fiche, place pour écrire, sauts de page, lisibilité. Après une correction, ne regarde que les pages modifiées.
3. Vérifie avec `pdftotext` que la fiche enfant ne contient ni réponse ni note pour Papa.
4. Relis chaque règle et chaque indice en te demandant : est-ce vrai en dehors de cet exemple ? un indice donne-t-il la réponse ?

Images : les pages rendues de tes deux PDF, et les images `--controle` des lignes à confiance faible. Rien d'autre. Ne rouvre pas une page déjà vue si elle n'a pas changé.

## Rapport final

Fichiers créés et nombre de pages de chaque PDF ; exercices (identifiant, type, nombre de fautes) ; écarts avec le plan et pourquoi ; points incertains (position de mot relevée à la main, règle à formulation délicate, problème vu dans `lignes.json`, l'inventaire ou la transcription).

## Critères d'acceptation

- Quatre fichiers, deux PDF compilés, toutes les pages regardées.
- Nombres annoncés = corrigé du guide Papa.
- Aucune réponse dans la fiche enfant, aucun renvoi à un autre bloc.
