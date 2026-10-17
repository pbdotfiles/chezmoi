<!-- Modèle : remplacer les <...>, supprimer les lignes inutiles. Garder ce fichier court : il est relu par toutes les sessions du dossier. -->
# Correction d'exercices d'écriture : <titre court>

Projet mené avec la skill `correction-dictee` (orchestrateur + sous-agents). Avant toute action, lire la section « Avancement ».

## Contexte
- Enfant : <fille/garçon> ; les fiches s'adressent à <elle/lui> au <féminin/masculin> (« tu es sûr<e> »). Niveau : <CE2, CM1...>. Date des exercices : <date>.
- <Qui a dicté, relecture à chaud faite ou non, code de correction de la maîtresse, autres précisions de Papa.>
- Modèle de la transcription (étape 1) : <providerID/modelID choisi par Papa, ou « celui de l'orchestrateur »>.

## Exercices
| Exercice | Type | Photos (ordre des pages) | Référence |
|---|---|---|---|
| <dictee> | dictée | `photos/dictee/` : <fichier p1>, <fichier p2>... | `<texte lu>.md` |
| <texte_libre> | texte libre | `photos/texte_libre/` : ... | aucune ; consigne : <...> |

Listes de vocabulaire : <fichier(s) ou aucune>.

## Fichiers du projet
- Sources (ne jamais modifier) : photos, textes de référence, listes de vocabulaire. Les textes de référence ne sont lus qu'à l'inventaire, jamais pour la transcription.
- `transcription/<exercice>.md` : texte final de l'enfant, fautes comprises ; une ligne numérotée = une ligne du cahier. Avant validation, les lectures incertaines y sont annotées en CriticMarkup (`{==meilleure lecture==}`). **Après validation par Papa, la transcription fait foi** : on ne relit plus le manuscrit pour la vérifier.
- `images_nb/<exercice>_p<N>.png` : images imprimables (taches effacées après validation : ne pas les régénérer sans refaire les retouches).
- `analyse/` : écarts avec la référence, inventaire des fautes, plan des blocs.
- `supports/` : `fiche.typ`, `lignes.json`, fiches enfant `bloc<N>` et guides `bloc<N>_papa` (typst et PDF).
- Fichiers temporaires : `/tmp/opencode/<projet>/`.

## Décisions de Papa
### Lecture
- On transcrit et on corrige ce que l'enfant a voulu écrire (ratures, ajouts, effacements = auto-corrections ; un résidu d'effacement n'est pas une faute).
- <Cas tranchés à la validation de la lecture : page:ligne, décision.>
- <Mots dictés autrement par Papa, erreurs de lecture découvertes à l'inventaire (validation pédagogique).>
### Méthode de correction
- <Ce qui ne compte pas, catégories ajoutées ou retirées, cas classés.>
### Familles travaillées et blocs
- <Bloc 1 : ... ; Bloc 2 : ... ; corrections rapides : ... ; laissé de côté : ...>

## Avancement
| Étape | État | Fichiers | Session |
|---|---|---|---|
| 0 Cadrage | fait <date> | AGENTS.md | |
| 1 Transcription | | | |
| 2 Images | | | |
| V1 Validation lecture | | | |
| 3 Taches | | | |
| 4 Inventaire | | | |
| 5 Lignes | | | |
| V2 Validation pédagogique | | | |
| 6 Plan | | | |
| 7 Fiches | | | |
| 8 Relecture | | | |
| V3 Livraison | | | |

Questions en attente : <aucune>
