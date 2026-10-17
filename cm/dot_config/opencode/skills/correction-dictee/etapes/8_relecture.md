# Étape 8 : relecture du rendu

## Objectif

Relire les PDF comme ils seront imprimés, avec un œil neuf, et dire ce qui gênerait l'enfant ou Papa. Tu ne refais pas l'analyse des fautes, tu ne relis pas le manuscrit et tu ne vérifies pas le processus : tu juges le rendu. Tu ne modifies aucun fichier du projet.

## Entrées

`supports/bloc*.pdf` et `supports/bloc*_papa.pdf`. Tu peux consulter `references/fiches.md` de la skill (présentation attendue), et `transcription/` ou `analyse/inventaire_fautes.md` (du texte) pour comprendre une page.

**Tu n'ouvres que les pages rendues des PDF.** Pas les photos, pas `images_nb/`, pas de recadrage du manuscrit, pas de calcul de coordonnées. La transcription a été validée par Papa : elle fait foi. Si, sur une page, l'écriture de l'enfant te semble dire autre chose que ce que la fiche suppose, ou si une annotation te semble mal placée, note-le comme question dans ton rapport, sans aller vérifier.

## Méthode

Rends chaque page en PNG (`pdftoppm -r 100 -png`) dans ton dossier temporaire et lis-les toutes, une fois chacune. Si tu ne peux pas voir les images, dis-le d'emblée : une lecture par `pdftotext` ne vaut pas une relecture du rendu.

Lis chaque fiche enfant deux fois (deux lectures de la même page vue une seule fois) :
- **comme l'enfant** (niveau indiqué) : comprend-elle chaque consigne sans aide ? sait-elle où écrire, combien de réponses ? un exemple « correct » montre-t-il une faute ? une règle est-elle trop longue, un mot trop difficile ? une page trop chargée ?
- **comme un adulte exigeant** : chaque règle imprimée est-elle juste, sans fausse généralisation ? les exemples prouvent-ils la règle ? une consigne ou un indice donne-t-il la réponse ? le nombre annoncé correspond-il à ce qu'on voit ? un renvoi à un autre bloc ? une annotation sur le mauvais mot, coupée, ou qui cache l'écriture ?

Puis lis chaque guide Papa : est-il clair, utilisable pendant la séance, cohérent avec la fiche ?

## Rapport final

Problèmes classés en **important** (gêne réelle ou règle fausse) et **mineur** (confort). Pour chacun : PDF, page, constat précis, conséquence pour l'enfant, proposition minimale. Distingue les certitudes des questions. Ne propose pas de changement sans vrai gain, et n'invente pas de défaut pour remplir : « rien d'important » est une réponse valable. Indique ce que tu as examiné et comment (images ou texte), et le nombre d'images ouvertes.
