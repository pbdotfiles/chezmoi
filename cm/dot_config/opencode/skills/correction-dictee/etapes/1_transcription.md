# Étape 1 : transcription annotée

## Objectif

Pour chaque exercice, un fichier `transcription/<exercice>.md` qui reproduit le **texte final** écrit par l'enfant, fautes comprises, ligne par ligne, avec tes lectures incertaines **annotées**. Papa relit ensuite ce fichier à côté des photos et corrige tout ce qu'il voit (validation de la lecture). Ton travail est une première lecture **rapide et fidèle** : annoter un doute ne coûte rien ; zoomer encore coûte du temps et, sur une écriture d'enfant, ne tranche souvent rien.

## Entrées

- `photos/<exercice>/` (ordre des pages : celui indiqué dans `AGENTS.md`, sinon l'ordre des noms de fichiers, à vérifier sur le contenu).
- `AGENTS.md` du projet (conventions, cas déjà tranchés).

**Pas de texte de référence.** Même si le texte dicté ou une liste de vocabulaire se trouve dans le dossier, ne l'ouvre pas. Savoir ce qui était attendu pousse à lire le mot attendu au lieu du mot écrit. Le texte de référence ne sert qu'à l'inventaire des fautes.

## La règle : fidélité à ce que l'enfant a écrit

Tu transcris ce que l'enfant a voulu écrire, **dans sa version finale** :
- **une faute est transcrite telle quelle** : « lesser », « touner », « coue », « q'un », « venire », « pleind », « sore », « contant » ;
- **une auto-correction claire donne la version corrigée** : un mot barré n'est pas transcrit ; un mot ajouté (au-dessus de la ligne, avec signe d'insertion) est transcrit à sa place ; sur du ruban correcteur ou une gomme, on transcrit ce qui est écrit par-dessus, et un résidu qui montre clairement une volonté d'effacer (bout d'accent, point à moitié couvert) est considéré comme effacé ;
- **les versions intermédiaires ne sont pas notées** : ni le mot barré, ni ce qu'il y avait sous le ruban.

**Le piège principal : écrire le mot juste à la place de la faute.** Tu reconnais le mot, et tu écris son orthographe correcte sans t'en rendre compte. Les essais de la skill en sont pleins : « laisser » pour « lesser », « déplaçait » pour « déplassait », « deviennent » pour « devienent », « appelle » pour « appèle », « attraction » pour « atraction », « Jennifer » pour « Jennyfer ». C'est l'erreur la plus grave : une faute effacée disparaît de l'inventaire et des fiches, et Papa a du mal à la voir, parce qu'un mot bien écrit n'attire pas l'œil.
- Transcris les **lettres que tu vois**, pas le mot que tu reconnais : doubles consonnes, terminaisons des verbes (`-e`, `-es`, `-ent`, `-ait`, `-aient`, `-é`, `-er`), `e` et `s` finaux, accents, apostrophes, majuscules.
- Un enfant de CE2 fait souvent une faute par ligne ou presque. **Une ligne que tu as transcrite sans aucune faute est suspecte** : relis-la lettre à lettre sur la bande que tu as déjà sous les yeux (pas de nouveau zoom).
- Les noms propres gardent l'orthographe de l'enfant, même si elle varie d'une ligne à l'autre : n'harmonise pas.
- Ne « normalise » rien d'autre non plus : majuscules manquantes, ponctuation absente ou en trop restent telles quelles. Accents sur les majuscules, apostrophes, guillemets : transcris ce que tu vois.

## Méthode : une seule passe

1. Fais un aperçu redressé et réduit de chaque page (`PIL.ImageOps.exif_transpose`) pour comprendre la mise en page : orientation, nombre de lignes, marges, flèches, ajouts.
2. Découpe la page en bandes horizontales de 4 à 5 lignes, avec un léger chevauchement, d'environ 1600 px de large : assez pour lire, pas plus. Lis chaque bande une fois, lettre par lettre.
3. **Au plus un zoom par bande** (`scripts/zoomreg.py`), et seulement pour un signe précis : accent, lettre finale, ponctuation. Si ce zoom ne tranche pas, annote ta meilleure lecture et passe à la suite. Jamais deux zooms sur le même endroit.
4. **Écris chaque page dans le fichier dès qu'elle est lue.** Ne garde pas la transcription « en tête » : opencode retire les anciennes images de ton contexte, et une page non écrite serait à relire.
5. **N'ouvre jamais deux fois la même image.** S'il te manque quelque chose, annote plutôt que de rouvrir.
6. Pas de relecture de contrôle contre l'image à la fin : c'est Papa qui relit.

Repères : environ 6 à 8 images et quelques minutes par page ; au plus 40 images dans toute la session (au-delà de 64, les requêtes échouent). Si tu approches ces chiffres, c'est que tu zoomes trop : annote.

## Annotations : une seule balise, ta meilleure lecture

Papa ouvre le fichier dans son éditeur, remplace par le bon texte chaque annotation dont la lecture est fausse, laisse en place celles dont la lecture est juste (l'orchestrateur retirera ensuite les accolades), et corrige au passage toute autre erreur qu'il voit. Il ne doit rien avoir d'autre à nettoyer : **pas de question, pas de commentaire, pas d'alternative** dans le fichier.

| Cas | Écriture |
|---|---|
| Mot incertain | `{==chevaux==}` (ta meilleure lecture, rien d'autre) |
| Signe incertain (virgule, point, accent...) | `septembre{==,==}` |
| Mot illisible (à n'utiliser que si tu n'as vraiment aucune lecture) | `{==???==}` |
| Marque que tu juges être une tache, un résidu | rien : ni transcrite, ni annotée |

- Annote chaque fois que tu hésites ; mieux vaut quinze annotations qu'un zoom de trop. Mais pas d'annotation sur un mot que tu lis sans hésiter.
- Les seuls commentaires du fichier sont les repères de structure, en HTML : changement de paragraphe `<!-- § 2 -->`, mot inséré `<!-- « ont » ajouté au-dessus de la ligne -->`, phrase déplacée `<!-- flèche : se lit après « ... » -->`. Courts, sans question.
- Une phrase déplacée par une flèche reste transcrite à sa ligne physique, avec le commentaire de flèche.

## Format

```markdown
## <Exercice> : transcription du texte de l'enfant

Texte final tel qu'écrit par l'enfant, fautes comprises. Une ligne numérotée = une ligne du cahier.

### Page 1 (`photos/<exercice>/<fichier>.jpg`)

1. Un matin de septembre, la maîtresse a
2. posé le journal du {==musé==} sur mon bureau :
```

- Une section `### Page N` par photo, lignes numérotées à partir de 1 sur chaque page, **une ligne numérotée par ligne d'écriture du cahier**, y compris pour un texte libre. Les fiches citeront « page 3, ligne 5 » et découperont les extraits avec ces numéros.
- Texte libre : un changement de paragraphe est indiqué par `<!-- § 2 -->` avant la ligne. Si l'exercice a une structure (une page de BD par paragraphe, une question par réponse), indique-la de la même façon.
- Plusieurs petites dictées sur une même page : un fichier par dictée, chaque fichier indiquant les pages et numéros de lignes du cahier.

## Ce que tu ne fais pas

Pas de correction, pas d'analyse des fautes, pas de modification des photos, pas de tableau des doutes ni de zooms à fournir : les annotations du fichier suffisent.

## Rapport final

1. Fichiers écrits, nombre de pages et de lignes par exercice.
2. Nombre d'annotations par exercice.
3. Observations utiles pour la suite : ratures et ruban correcteur fréquents, ajouts, flèches, texte coupé par le cadre de la photo, page qui semble manquer.
4. Nombre d'images ouvertes dans la session.

## Critères d'acceptation

- Un fichier par exercice, au format ci-dessus, chaque ligne du cahier présente une fois.
- Les incertitudes sont annotées seulement par `{==...==}`, accolades bien fermées ; aucun `{>>...<<}` dans le fichier.
- Les fautes de l'enfant sont transcrites telles quelles ; aucun texte de référence n'a été ouvert.
