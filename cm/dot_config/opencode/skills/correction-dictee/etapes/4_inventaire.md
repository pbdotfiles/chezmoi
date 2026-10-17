# Étape 4 : inventaire des fautes et des réussites

## Objectif

`analyse/inventaire_fautes.md` : toutes les fautes de tous les exercices, rangées par famille, avec leur emplacement, et les réussites chiffrées. C'est la référence de tout ce qui suit : plan, fiches, guides Papa. Puis une proposition de familles à travailler, que l'orchestrateur présentera à Papa.

Lis d'abord `references/methode.md` de la skill : catégories, définitions, critère de vraie réussite.

## Entrées

`transcription/` (validée par Papa), textes de référence, listes de vocabulaire s'il y en a, `AGENTS.md` (niveau scolaire, décisions de Papa : ce qui compte, ce qui ne compte pas, cas tranchés à la validation de la lecture).

Le texte de référence n'a été vu par personne avant toi : c'est à cette étape seulement qu'il sert, pour lister les fautes. Il ne sert jamais à corriger la transcription.

**La transcription validée fait foi.** Tu travailles sur du texte : n'ouvre aucune image (photos, `images_nb/`, zooms d'autres étapes). Si un passage te semble mal lu, mets-le dans « À trancher » ; ne va pas vérifier sur l'image.

## Méthode

1. **Exercice avec texte de référence** (dictée, copie) : lance `scripts/aligner.py <référence> transcription/<exercice>.md`. Si l'alignement déraille (mot répété, ligne sautée), découpe et relance. Écris le résultat, nettoyé, dans `analyse/ecarts_<exercice>.md` : un tableau Où (page:ligne) / Attendu / Écrit / Type. Chaque écart devient une ou plusieurs fautes, ou un écart accepté. Le texte de référence permet de trouver des fautes qu'une simple relecture ne voit pas : un mot juste mais qui n'est pas celui dicté (« cherche » pour « cherchait »), un mot oublié ou répété. Classe-les en « Déconcentration » (voir `references/methode.md`), et mets **aussi** chacun d'eux dans « À trancher », avec la question « faute de l'enfant, mot dicté autrement, ou erreur de lecture ? » : seul Papa le sait (dans le premier cas, « Le peintre » pour « Ce peintre » était une erreur de lecture).
2. **Exercice sans référence** (texte libre, dictée dont Papa n'a pas le texte) : fais deux passes complètes, mot par mot, ligne par ligne : orthographe, accords, conjugaison, homophones, ponctuation, majuscules, tournures orales. Écris la forme attendue pour chaque faute. Une faute oubliée ici disparaît de tout le reste (le premier inventaire avait oublié « và »). Pour une dictée sans référence, reconstitue le texte attendu à partir du sens, et mets dans « À trancher » les passages où plusieurs textes étaient possibles.
3. Range chaque faute dans une famille. Un mot à deux fautes va dans deux familles, avec un renvoi.
4. Pour chaque famille, **compte aussi les justes** (mêmes règles, même type de mot, dans tous les exercices) : c'est ce qui décide s'il y a une vraie réussite à dire d'abord, ou seulement un point d'appui.
5. Croise avec les listes de vocabulaire : pour chaque mot de la liste mal écrit, indique la semaine ou la liste, et s'il est mal mémorisé ou si c'est sa grammaire qui manque.
6. Repère les habitudes transversales et les comparaisons utiles (le même mot ou la même règle réussi à un endroit, raté à un autre : « chaque instrument joue » et « chaque animales semblent »).
7. Vérifie chaque règle que tu écris : elle doit être juste dans son domaine, et ses exemples doivent la prouver (« concourir » ne fait pas entendre le `s` de « concours » : ce n'est pas un exemple de la méthode de la lettre muette).

## Format

```markdown
## Inventaire des fautes et des réussites

Sources : ... Niveau : ...
Repères : `D p3:5` = <exercice>, page 3, ligne 5 (définir une lettre par exercice).

### Vue d'ensemble
| # | Famille | <exercice 1> | <exercice 2> | Total |

### 1. <Famille>
**À dire d'abord :** <vraie réussite, chiffres> (seulement si nettement plus de justes que de fautes)
<La règle ou l'astuce en une ou deux phrases.>
| Où | Écrit | Attendu | Remarque |
Remarques : points d'appui, chiffres justes/faux quand ce n'est pas une réussite, renvois.

### Déconcentration / Les fautes que tu ne pouvais pas savoir / L'écrit n'est pas l'oral
### Écarts acceptés (non comptés)
### Réussites à féliciter
### Mots de la liste mal écrits (mal mémorisés / grammaire)
### À trancher
| Où | Écrit | Question pour Papa | Classement proposé |
```

## Contrôles automatiques (obligatoires)

Écris un petit script dans ton dossier temporaire et mets ses résultats dans ton rapport (pour un exercice sans référence, seul le second contrôle s'applique) :
- chaque écart de `analyse/ecarts_*.md` est repris dans l'inventaire (comme faute, écart accepté ou cas à trancher) : aucun écart orphelin ;
- les totaux de la vue d'ensemble sont égaux au nombre de lignes des tableaux de chaque famille.

## Proposition pour la validation pédagogique (dans ton rapport, pas dans le fichier)

- Les familles que tu proposes de travailler, regroupées en blocs (une ou deux familles par bloc, une famille courte peut en accompagner une plus longue), avec la raison de chaque choix.
- Pour chaque bloc, l'idée d'exercice principale (voir `references/fiches.md`, « Types d'exercices »).
- Ce qui serait seulement corrigé rapidement, et ce qui serait laissé de côté.
- Faut-il un bloc de relecture à froid, un bloc texte libre séparé.

## Rapport final

Chemin du fichier, tableau de la vue d'ensemble, résultats des contrôles, liste « À trancher », proposition ci-dessus, points où tu as hésité.

## Critères d'acceptation

- `analyse/ecarts_<exercice>.md` existe pour chaque exercice avec texte de référence, et correspond à la transcription validée.
- Aucun écart orphelin, totaux justes (contrôle lancé).
- Aucune image ouverte.
- Chaque « À dire d'abord » est chiffré et respecte le critère de vraie réussite.
- Les catégories et décisions de `AGENTS.md` sont appliquées.
