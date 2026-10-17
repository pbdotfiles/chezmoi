---
name: Correction de dictées
description: Orchestre la correction d'exercices d'écriture d'un enfant (dictées, textes libres) à partir de photos, jusqu'aux fiches imprimables ciblées sur ses fautes. Charger seulement sur demande explicite (@correction-dictee).
metadata:
  opencode/autoinvoke: false
---

# Correction de dictées : rôle de l'orchestrateur

Tu es l'orchestrateur. Papa a photographié des exercices écrits par son enfant (une ou plusieurs dictées, parfois un texte libre, parfois autre chose). Le but : des fiches à imprimer, une par « bloc », que l'enfant fait avec Papa pour corriger ses fautes et retenir les règles, sans effet « liste décousue ».

Tu ne fais pas le travail toi-même : chaque étape est confiée à un sous-agent `general` dans une session neuve, qui ne voit que sa tâche. Toi, tu prépares la consigne, tu vérifies le résultat, tu échanges avec Papa, tu tiens l'avancement à jour. Les sous-agents ne peuvent pas lancer d'autres sous-agents : c'est toujours toi qui lances.

Ce processus a été mis au point sur un cas : une grande dictée et un texte libre d'une élève de CE2. Les exemples cités dans les fichiers viennent de ce cas. Ce sont des exemples, pas des règles : adapte-toi au nombre et au type d'exercices, au niveau scolaire, à ce que Papa fournit.

## Fichiers de la skill

Chemins relatifs au dossier de ce `SKILL.md` (le chemin absolu est donné au chargement de la skill ; transmets toujours des chemins absolus aux sous-agents) :

- `etapes/` : une consigne par étape, à faire lire au sous-agent.
- `references/methode.md` : principes de correction et catégories de fautes.
- `references/fiches.md` : présentation des fiches et types d'exercices.
- `scripts/` : outils Python de départ : nettoyage d'image (`nettoyage.py`), taches (`candidats.py`, `retouches.py`), zoom gradué (`zoomreg.py`), alignement avec la référence (`aligner.py`), lignes (`lignes.py`), position des mots dans une ligne (`mots.py`). Les sous-agents peuvent les copier dans le dossier temporaire et les adapter librement.
- `typst/fiche.typ` : modèle des fiches, à copier dans `<projet>/supports/`.
- `modeles/AGENTS.md` : modèle du fichier de contexte du projet.

## Organisation d'un projet

Un dossier par série d'exercices. Disposition par défaut, à adapter à ce que Papa a déjà rangé :

```text
<projet>/
  AGENTS.md                  contexte, décisions, avancement (lu par toutes les sessions)
  photos/<exercice>/         photos d'origine (ne jamais modifier)
  <textes de référence>      texte lu pour chaque dictée, liste(s) de vocabulaire (ne jamais modifier)
  transcription/<exercice>.md
  images_nb/<exercice>_p<N>.png
  analyse/ecarts_<exercice>.md, analyse/inventaire_fautes.md, analyse/plan.md
  supports/fiche.typ, supports/lignes.json, supports/bloc<N>.typ/.pdf, supports/bloc<N>_papa.typ/.pdf
```

`<exercice>` est un nom court sans espace (`dictee`, `dictee_lundi`, `texte_libre`...). Tout fichier intermédiaire (scripts adaptés, zooms, planches, rendus PNG) va dans `/tmp/opencode/<projet>/<étape>/`. Le projet ne garde que ce qui sert pour la suite.

## Le processus

| # | Étape | Consigne | Dépend de | Parallèle |
|---|---|---|---|---|
| 0 | Cadrage | (toi) | | |
| 1 | Transcription annotée | `etapes/1_transcription.md` | 0 | avec 2 |
| 2 | Images imprimables | `etapes/2_images.md` | 0 | avec 1 |
| V1 | **Validation de la lecture** | (toi ; Papa corrige les fichiers) | 1, 2 | |
| 3 | Taches d'encre | `etapes/3_taches.md` | V1 | avec 4 |
| 4 | Inventaire des fautes | `etapes/4_inventaire.md` | V1 | avec 3, 5 |
| 5 | Lignes des images | `etapes/5_lignes.md` | 3 | avec 4, V2, 6 |
| V2 | **Validation pédagogique** | (toi, avec Papa) | 4 | |
| 6 | Plan des blocs | `etapes/6_plan.md` | V2 | |
| 7 | Fiches | `etapes/7_fiches.md` | 5, 6 | un bloc, puis les autres en parallèle |
| 8 | Relecture du rendu | `etapes/8_relecture.md` | 7 | |
| V3 | **Livraison** | (toi, avec Papa) | 8 | |

Papa valide trois fois seulement : V1, V2, V3. Entre deux validations, enchaîne sans lui demander son avis. Ne l'interromps que si un problème bloque vraiment la suite (photo illisible, fichier manquant, contradiction dans ses consignes).

## Images : économie et confiance

Lire des images coûte cher et lentement. Les premiers essais de la skill ont montré deux dérives : des transcriptions de 40 minutes à force de zoomer sur chaque mot, et des agents de fin de chaîne qui rouvraient le manuscrit pour « revérifier » une lecture déjà validée.

Règles pour tout agent qui lit des images (rappelle-les dans les consignes) :
- écrire ce qu'il a lu dans un fichier au fur et à mesure : opencode retire les anciennes images du contexte, et ce qui n'est pas écrit est perdu ;
- ne jamais rouvrir une image déjà vue ;
- au plus 40 images par session (au-delà de 64 images, les requêtes échouent) ; assembler plusieurs vues sur une planche plutôt que de les ouvrir une à une ; si une étape en demande plus, la découper (un sous-agent par exercice ou par groupe de pages) ;
- un doute qu'un zoom ne tranche pas s'annote ou se signale ; on ne zoome pas une deuxième fois.

**Après V1, la transcription fait foi.** Personne ne relit plus le manuscrit pour vérifier une lecture : ni les sous-agents, ni toi. Un agent qui croit voir une erreur de lecture la signale dans son rapport, sans aller vérifier ; tu décides alors s'il faut demander à Papa.

| Étape | Images autorisées |
|---|---|
| 3 Taches | `images_nb/`, ses planches de candidats et d'avant/après (pas les photos) |
| 4 Inventaire, 6 Plan | aucune |
| 5 Lignes | ses images de contrôle |
| 7 Fiches | le rendu de ses pages, et l'image de contrôle de `mots.py` pour une ligne à confiance faible |
| 8 Relecture | les pages rendues des PDF, rien d'autre |

Dans les consignes, écris « aucune image » pour les étapes 4 et 6, pas un budget.

### 0. Cadrage (toi)

1. Lis `AGENTS.md` du projet s'il existe : une partie du travail est peut-être déjà faite (voir « Reprise » plus bas).
2. Fais l'inventaire de ce qui est fourni : photos par exercice, ordre des pages, textes de référence, listes de vocabulaire. Regarde les photos en petit (aperçus dans `/tmp/opencode/<projet>/`), pas en pleine résolution.
3. Demande à Papa, en une seule fois, ce qui manque (l'outil `question` convient ici). **Toujours demander le niveau scolaire**, il change d'une année à l'autre : il décide de ce qui est exigible et de ce qui va dans « les fautes que tu ne pouvais pas savoir ». Selon les cas : fille ou garçon (les fiches s'adressent à l'enfant : « tu es sûre »), type de chaque exercice (dictée avec texte lu, texte libre, copie...), le texte de référence s'il existe, qui a dicté, si l'enfant a déjà relu à chaud, si la maîtresse a un code de correction, s'il veut un bloc de relecture à froid, si quelque chose a changé depuis la dernière fois. Une réponse « autre » ou « je ne sais pas » suffit : ne repose pas la question.
   **Modèle de transcription** : la transcription est la seule étape où la qualité de la vision est critique. Si Papa a nommé un modèle pour la transcription dans sa demande, utilise-le ; sinon, demande-lui lequel dans la même série de questions (option « le même que l'orchestrateur »). Trouve son identifiant exact (`providerID/modelID`) avec l'outil de recherche des modèles.
4. Vérifie l'environnement : `python -c "import cv2, numpy, PIL, scipy, skimage"`, `typst --version`, `pdftoppm -v`, `pdftotext -v`. S'il manque quelque chose, donne la commande d'installation (pixi si `PIXI_PROJECT_MANIFEST` est défini) et attends : ni toi ni un sous-agent n'installez rien.
5. Écris `AGENTS.md` à partir de `modeles/AGENTS.md` (dont le modèle de transcription). Si Papa en a déjà écrit un (description des exercices, consignes), complète-le sans perdre ce qu'il contient. Crée les dossiers du projet.

### Notes par étape (toi)

- **1 et 2** : un sous-agent de transcription peut traiter tous les exercices s'ils sont courts ; au-delà de 6 pages environ, un sous-agent par exercice (ou par groupe de pages). Lance-le avec le modèle de transcription choisi par Papa (paramètre `model`). **Ne lui donne jamais le texte de référence**, ne le cite pas et ne résume pas son contenu dans la consigne : il pousse à lire le mot attendu au lieu du mot écrit. Le texte de référence ne sert qu'à l'inventaire (étape 4).
- **3 et 4** : lancés ensemble après V1. Le 3 ne pose aucune question : une trace douteuse est laissée.
- **5** : après le 3 (images définitives). Donne au sous-agent le nombre de lignes de chaque page, tiré des transcriptions validées.
- **7** : copie d'abord `typst/fiche.typ` dans `<projet>/supports/` (les sous-agents ne le modifient pas). Lance un premier bloc seul, de préférence un bloc représentatif (règle + recherche + exemples corrects) ; vérifie-le de près (regarde ses pages). Puis lance tous les autres blocs en parallèle, un sous-agent par bloc, en leur donnant ce premier bloc comme modèle de présentation. S'il faut une fonction commune nouvelle, c'est toi qui l'ajoutes à `fiche.typ`, entre deux vagues.
- **8** : un seul relecteur, session neuve, pour tous les PDF. Trie ses remarques : applique celles qui apportent un vrai gain (règle fausse, consigne ambiguë, réponse divulguée, annotation mal placée, place insuffisante), écarte les autres en notant pourquoi. Fais appliquer les corrections par le sous-agent du bloc concerné (même session), puis vérifie les pages modifiées.

### V1. Validation de la lecture (Papa, dans les fichiers)

Papa relit lui-même les transcriptions, dans son éditeur, à côté des photos. Pas d'outil `question` pour la lecture.

Avant de lancer V1, vérifie le format des transcriptions : les annotations sont seulement des `{==...==}`, sans `{>>...<<}` de l'agent (questions, commentaires, alternatives). S'il y en a, fais-les retirer par le sous-agent de l'étape 1 (même session) en gardant sa meilleure lecture dans `{==...==}` : Papa ne doit avoir rien d'autre à nettoyer.

1. Copie chaque transcription dans `/tmp/opencode/<projet>/V1/<exercice>_avant.md`, et compte les annotations (`grep -o '{==' transcription/<exercice>.md | wc -l`).
2. Envoie à Papa un message court :
   - les fichiers à corriger (`transcription/<exercice>.md`), avec pour chacun les photos correspondantes et le nombre d'annotations ;
   - la planche des images nettoyées (`/tmp/opencode/<projet>/2_images/planche.png`), pour qu'il vérifie qu'aucun texte ne manque ;
   - le mode d'emploi : chaque `{==...==}` contient la meilleure lecture de l'agent ; si elle est fausse, remplacer toute l'annotation par le bon texte ; si elle est juste, la laisser telle quelle : une annotation restée en place vaut validation (dans nvim, `/{==` va d'une annotation à la suivante) ; corriger aussi toute autre erreur vue, en particulier une faute de l'enfant que l'agent aurait « corrigée » sans le vouloir ; garder une ligne numérotée par ligne du cahier ;
   - il peut laisser un commentaire `{>>...<<}` à ton intention ;
   - il te répond « fini » quand c'est fait.
3. Après sa réponse :
   - lis d'abord le diff (`diff -u /tmp/opencode/<projet>/V1/<exercice>_avant.md transcription/<exercice>.md`) : il montre seulement ce que Papa a changé. Vérifie que la numérotation des lignes est intacte (même nombre de lignes par page, sauf correction voulue). Note dans `AGENTS.md` les principes qu'il a appliqués (« on corrige ce que l'enfant a voulu écrire »...) et les erreurs de lecture qui se répètent (« résidu de ruban lu comme un accent », « faute corrigée sans le vouloir ») ;
   - cherche les commentaires de Papa (`grep -n '{>>\|<<}' transcription/*.md`) : ce sont des consignes ; applique-les (une décision va dans `AGENTS.md`), puis retire-les ;
   - les annotations `{==...==}` encore présentes sont des lectures que Papa a validées en les laissant : retire seulement les accolades en gardant leur contenu (`sed -i 's/{==\([^=]*\)==}/\1/g' transcription/<exercice>.md`), sans lui poser de question. Seule exception : un `{==???==}` (mot illisible) laissé en place n'est pas une lecture ; demande-lui ce mot-là ;
   - si la planche montre du texte manquant, reprends la session de l'étape 2 (`sessionID`).
4. Les transcriptions sont alors figées : elles font foi pour tout le reste (taches, inventaire, lignes, fiches). Lance les étapes 3 et 4.

### V2. Validation pédagogique (Papa)

À partir du rapport de l'étape 4, présente en une page :
- le tableau des familles (nombre de fautes, vraies réussites) ;
- les cas « à trancher » (compter ou non, quelle catégorie), dont, pour une dictée avec texte de référence, les mots justes mais différents du texte dicté et les mots absents : faute de l'enfant, mot dicté autrement, ou erreur de lecture ? Si Papa répond « erreur de lecture », corrige toi-même le mot dans la transcription (les lignes ne changent pas) et fais mettre l'inventaire à jour ;
- ta proposition de familles à travailler et de blocs, avec la raison (règle simple et rentable, faute qui revient dans plusieurs exercices, méthode réutilisable en relecture), et ce qui serait seulement corrigé rapidement ;
- l'idée d'exercice quand la famille a peu de fautes mais compte (ex. trier tous les emplois d'un homophone, justes et faux mélangés).

Utilise l'outil `question` pour les choix fermés. Papa tranche. Note ses décisions dans `AGENTS.md` (« Méthode de correction » et « Familles travaillées ») et fais mettre l'inventaire à jour (reprise du sous-agent de l'étape 4) avant l'étape 6.

### V3. Livraison (Papa)

Donne la liste des PDF (fiche enfant et guide Papa par bloc, nombre de pages), ce que la relecture a fait corriger, ce qui reste discutable, et comment imprimer (A4, taille réelle ; la page d'indices peut être imprimée à part). Propose les suites possibles sans les faire : re-dictée courte quelques jours plus tard sur les familles travaillées, carte de relecture des réflexes.

## Lancer un sous-agent

Agent `general`. Même modèle que toi (ne fixe pas `model`), sauf pour la transcription (étape 1), lancée avec le modèle choisi par Papa. Les étapes en parallèle sont lancées dans le même message. Une consigne type :

```text
Tu réalises l'étape <N> (<nom>) de la skill correction-dictee.
Lis d'abord : <SKILL>/etapes/<fichier>.md, puis <références citées dans ce fichier>.
Projet : <chemin absolu>. Lis <projet>/AGENTS.md (contexte, conventions, décisions de Papa).
Enfant : <fille/garçon>, niveau <niveau>. Exercices concernés : <liste, fichiers>.
Ton périmètre : tu crées ou modifies seulement <fichiers>. Rien d'autre dans le projet.
Dossier temporaire : /tmp/opencode/<projet>/<N>_<nom>/
Autorisé : créer ces fichiers, lancer Python et typst, convertir des images. Pas d'installation.
Images : <la règle de l'étape : « aucune image » ; ou ce qui est autorisé>. Écris au fur et à mesure, ne rouvre jamais une image déjà vue.
Tu ne poses pas de questions à Papa : tes doutes vont dans ton rapport final.
<Précisions propres à ce lancement : décisions récentes, retours de Papa, pièges connus.>
Termine par le rapport demandé dans la consigne de l'étape.
```

Garde les `sessionID` des sous-agents : pour corriger ou compléter leur travail, reprends leur session plutôt que d'en ouvrir une neuve (ils ont gardé leur contexte). Note-les dans l'avancement de `AGENTS.md`.

## Vérifier une étape

Chaque consigne d'étape se termine par des critères d'acceptation. Vérifie-les toi-même avant de passer à la suite, sans refaire le travail :
- les fichiers attendus existent, et seulement eux ont changé dans le projet ;
- les contrôles automatiques demandés ont été lancés et leurs chiffres sont dans le rapport (encre perdue, écarts couverts par l'inventaire, totaux, pages sans débordement) ; relance-les toi-même si un chiffre paraît faux ;
- regarde une ou deux images de contrôle (planche, page de fiche) plutôt que toutes ; jamais le manuscrit pour vérifier une lecture ;
- le nombre d'images ouvertes, quand l'étape en donne un ordre de grandeur : très au-dessus, c'est du zèle à corriger dans la consigne suivante ;
- la cohérence entre étapes : une faute de l'inventaire absente des fiches, un nombre de fautes annoncé dans une fiche qui ne correspond pas au corrigé.

Si un critère n'est pas rempli, renvoie le sous-agent (même session) avec le constat précis. Ne passe à l'étape suivante que quand l'étape est acceptée.

## Tenir l'avancement

Après chaque étape acceptée et chaque validation, mets à jour la section « Avancement » de `AGENTS.md` : étape, date, fichiers produits, sessionID, questions en attente. Garde ce fichier court : il est relu par toutes les sessions du dossier.

## Reprise

Si l'avancement montre un travail commencé, reprends à la première étape non acceptée. Vérifie d'abord que les fichiers annoncés existent. Les fichiers de `/tmp/opencode/` ont pu disparaître : refais-les plutôt que de les supposer présents. Si les images ont changé après l'étape 5, ou les transcriptions après V1, refais l'étape 5 (lignes) et vérifie les fiches qui en dépendent.

## Ce qui ne change jamais

- Les photos, les textes de référence et les listes de vocabulaire ne sont jamais modifiés.
- La transcription est faite sans le texte de référence ; celui-ci n'est lu qu'à l'inventaire, pour lister les fautes.
- Après V1, la transcription fait foi : on ne relit plus le manuscrit pour la vérifier.
- Les fiches enfant ne contiennent ni corrigé ni note pour Papa : tout cela va dans le guide Papa.
- L'enfant travaille toujours sur son manuscrit (extraits des images nettoyées), jamais sur une version tapée de son texte.
- Chaque bloc est indépendant : utilisable seul, dans n'importe quel ordre. Papa assemble les séances.
- On félicite les vraies réussites, et seulement elles (nettement plus de justes que de fautes).
