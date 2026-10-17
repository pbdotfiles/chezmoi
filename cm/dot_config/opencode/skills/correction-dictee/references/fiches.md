# Fiches : présentation et types d'exercices

Présentation validée par Papa sur le premier cas, après plusieurs allers-retours. La suivre sauf décision contraire notée dans `AGENTS.md`.

## Deux documents par bloc

- **Fiche enfant** (`supports/bloc<N>.typ` → `.pdf`) : Papa l'imprime et la lit avec l'enfant. Elle s'adresse à l'enfant (« tu », accordé à son genre). **Aucune note pour Papa, aucune réponse, aucun corrigé**, même en marge.
- **Guide Papa** (`supports/bloc<N>_papa.typ` → `.pdf`) : la méthode, le corrigé de chaque exercice avec les repères page:ligne, ce qu'il faut dire et ne pas dire, les autres fautes visibles dans les extraits et leur famille, les réussites chiffrées. Court : une ou deux pages.

## Le manuscrit

- L'enfant lit **toujours son manuscrit** : des extraits des images de `images_nb/`, découpés par lignes (`extrait`, `manuscrit`). Jamais son texte retapé. Peuvent être tapés : les règles, les exemples inventés, les formes données.
- Un extrait contient assez de contexte pour comprendre la phrase : une ligne avant ou après si besoin, pas une page entière (sauf pour la relecture à froid, où les pages complètes non annotées viennent en premier).
- Un extrait présenté comme **correct** ne doit pas laisser voir, à côté du mot grisé, une faute que la même fiche fait chercher : recadre (`x-de`, `x-a`) ou choisis une autre ligne. Plus généralement, préfère les lignes sans autre faute.
- Les annotations doivent tomber exactement sur le bon mot : coordonnées x données par `scripts/mots.py` (à partir de `lignes.json` et de la transcription), vérifiées sur le rendu. Une ellipse ne doit pas être coupée par le bord du cadre.

## Les éléments de la fiche (modèle `typst/fiche.typ`)

- **Exemple correct** (`exemple`) : un pouce dessiné à côté de l'extrait, et seules les formes justes grisées (`surligne`). Une légende unique en début de fiche (« Les formes grisées sont bien écrites. »). Pas de « Bravo ! » répétés : ils allongent la page et poussent à ne pas tout lire. La fiche reste courte ; chaque phrase doit servir.
- **Règle** (`regle`) : fond gris léger. Elle contient **la règle et son exemple d'application**, de préférence tiré de son manuscrit, avec une phrase qui montre comment on applique la règle sur cet exemple.
- **Exercice** (`defi`) : bandeau gris avec un identifiant (A, B1...) et une consigne courte. Visuellement distinct des exemples corrects.
- **Réponses** (`reponse`, `recherche`) : lignes **sous l'extrait**, assez nombreuses pour toutes les réponses attendues (ou une consigne « deux par ligne »).
- **Indices** : sur la **dernière page**, « Un coup de pouce ? », un ou deux par exercice, gradués. Un indice aide à appliquer la méthode ; il ne donne ni le mot ni sa correction. Ce qui donne la réponse va dans le guide Papa.
- Fin de fiche possible : deux ou trois cases à cocher « mon réflexe de relecture ».

## Guidage de la recherche

- Donne **le nombre de fautes pour un groupe d'extraits** (« Trouve 4 erreurs de terminaison dans ces extraits »), jamais par ligne : par ligne, c'est trop guidé.
- La consigne **ne désigne pas le mot** (« vérifie le nom après chaque » donne la réponse) : ces repères vont dans les indices.
- Ne fais chercher que ce que la règle ou la méthode permet de trouver. Sinon, **pas de devinette** : le mot est entouré (`retouche`), la forme juste est donnée, l'enfant la recopie. C'est le cas des mots à retenir, des corrections rapides et des « fautes que tu ne pouvais pas savoir ».
- Un exercice ne mélange pas deux difficultés quand la règle donnée n'en couvre qu'une (premier cas : « écoutés » glissé dans un exercice é/er, alors que le test vendu/vendre ne dit rien du `s`).

## Types d'exercices

Varier. Le seul « trouve la faute dans cet extrait » finit par lasser et ne fait pas réfléchir de la même façon.

- **Recherche dans un groupe d'extraits** : N fautes de la famille dans plusieurs extraits, avec la règle à côté.
- **Tri juste / faute** (`tri`) : tous les emplois d'une difficulté dans ses textes, justes et faux mélangés (premier cas : 18 son/sont, ce/se dont 2 faux). Pour chacun, elle dit le test à voix haute (« mon regard » marche → son) et coche juste ou faute ; elle n'écrit que les corrections, à la fin. Inverser au hasard ne marche plus, puisque presque tout est juste : elle doit appliquer le test. Chaque emploi juste validé est une réussite.
- **Comparaison** : le même mot ou la même règle, réussi à un endroit, raté à un autre (« chaque instrument joue » / « chaque animales semblent »). L'enfant explique la différence et corrige.
- **Mots à retenir** : mots entourés, forme donnée, à recopier ; regroupés par habitude (« mon e en trop »).
- **« Tu ne pouvais pas savoir »** : mots entourés, forme juste et explication courte, sur le ton « moi aussi je me serais trompé ».
- **Reformulation** (texte libre) : réécrire une phrase maladroite ou des paroles avec leur ponctuation, sans recopier tout le paragraphe.
- **Relecture à froid** : pages complètes non annotées ; puis, si besoin, les étourderies non trouvées avec un réflexe de relecture (« je relis en me disant la phrase »).
- **Réussites** : une page ou un encadré d'exemples corrects de choses difficiles.

## Indépendance des blocs

Chaque fiche est utilisable seule, dans n'importe quel ordre : pas de « comme au bloc 3 », pas de faute supposée déjà corrigée. Un mot qui porte aussi une faute d'une autre famille reste tel quel dans l'extrait ; la fiche ne fait chercher que la sienne ; le guide Papa signale l'autre.

## Justesse des règles

Une règle fausse apprise à un enfant coûte plus cher qu'une faute. Chaque règle est formulée **dans son domaine de validité**, et ses exemples la prouvent vraiment. Fausses généralisations relevées dans le premier cas :
- « avec il / elle, le verbe finit par -t » (faux pour le premier groupe : elle joue) ; dire plutôt : « au présent, premier groupe : -e ; pour les autres verbes, je vérifie : elle dit, elle prend » ;
- « devant deux consonnes, jamais d'accent » ; restreindre à la consonne double usuelle (belle, appelle) ;
- « avec avoir, jamais d'accord » ; ne pas en faire une règle, expliquer le cas ;
- « toute négation a deux mots » ; restreindre aux exemples (ne... pas, ne... personne) ;
- « concourir » ne fait pas entendre le `s` de « concours » ; « pas de mot de la famille trouvé, donc pas de lettre muette » est un raisonnement faux ;
- un test de remplacement doit marcher sur la phrase donnée (« ce » devant un nom ne se remplace pas par « cela »).

## Mise en page et vérification

- A4, noir et blanc, police sans empattement, pas d'émoji (pouce dessiné en SVG).
- Un exercice (consigne, extrait, lignes de réponse) ne se coupe pas entre deux pages ; aucun bloc insécable plus haut qu'une page ; pas de page presque vide.
- Compiler avec `typst compile --root . supports/bloc<N>.typ supports/bloc<N>.pdf`, rendre chaque page en PNG dans le dossier temporaire (`--ppi 80`), **regarder chaque page** : débordements, ellipses coupées, surlignage sur le bon mot, place pour écrire, lisibilité du manuscrit.
- `pdftotext supports/bloc<N>.pdf -` ne doit contenir aucune réponse ni mention destinée à Papa.
