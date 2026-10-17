// Modèle des fiches : à copier dans <projet>/supports/fiche.typ, puis à adapter librement.
// Présentation validée par Papa (dictée CE2, octobre 2026). Voir references/fiches.md.
//
// Compilation, depuis la racine du projet :
//   typst compile --root . supports/bloc2.typ supports/bloc2.pdf
//   typst compile --root . --ppi 80 supports/bloc2.typ '/tmp/opencode/rendu/bloc2-{p}.png'
//
// Les extraits sont découpés à l'affichage dans les images de images_nb/, jamais modifiées.
// supports/lignes.json donne, pour chaque image : fichier, w, h, et pour chaque ligne du
// cahier [haut, bas, haut du corps, bas du corps], en pixels (voir scripts/lignes.py).
// Les coordonnées x des surlignages et ellipses sont en pixels de l'image (scripts/mots.py
// donne, pour chaque mot d'une ligne, le triplet (ligne, x0, x1) à recopier).

#let P = json("/supports/lignes.json")
#let largeur-manuscrit = 14.8cm

// ---------- Mise en page ----------

// Fiche enfant. Aucun corrigé, aucune note pour Papa.
#let presentation(titre: "", bloc: "", corps) = {
  set document(title: bloc + " · " + titre)
  set page(paper: "a4", margin: (x: 1.6cm, top: 1.3cm, bottom: 1.5cm),
    footer: context [
      #set text(size: 8pt, fill: luma(110))
      #bloc · #titre #h(1fr) #counter(page).display("1 / 1", both: true)
    ])
  set text(font: "DejaVu Sans", size: 11.5pt, lang: "fr")
  set par(leading: 0.45em, spacing: 0.65em)
  show heading.where(level: 1): it => block(below: 0.5em, text(size: 20pt, weight: "bold", it.body))
  show heading.where(level: 2): it => block(above: 0.8em, below: 0.5em, text(size: 15pt, weight: "bold", it.body))
  corps
}

// Guide Papa : document séparé (blocN_papa.typ).
#let notes(titre: "", bloc: "", corps) = {
  set document(title: bloc + " · Papa · " + titre)
  set page(paper: "a4", margin: 1.8cm,
    footer: context [#text(size: 8pt)[#bloc · Papa #h(1fr) #counter(page).display()]])
  set text(font: "DejaVu Sans", size: 10.5pt, lang: "fr")
  set par(leading: 0.5em, spacing: 0.7em)
  corps
}

// ---------- Manuscrit ----------

// Extrait du manuscrit, lignes `de` à `a` (incluses, numérotation de la transcription).
//   surligne : ((ligne, x0, x1), ...)  formes justes, grisées (exemples corrects)
//   entoure  : ((ligne, x0, x1), ...)  mots entourés (forme donnée, pas de recherche)
//   gris     : (ligne, ...)            lignes de contexte éclaircies
//   x-de / x-a : recadrage horizontal (cacher une faute hors sujet), même taille d'écriture
#let extrait(page, de, a, surligne: (), entoure: (), gris: (), largeur: largeur-manuscrit,
  x-de: 0, x-a: none) = {
  let p = P.at(page)
  let L = p.lignes
  let x-fin = if x-a == none { p.w } else { x-a }
  // l'échelle dépend de la largeur de la page entière : même taille d'écriture partout
  let s = largeur / p.w
  let y0 = L.at(de - 1).at(0)
  let y1 = L.at(a - 1).at(1)
  let largeur-cadre = (x-fin - x-de) * s
  block(breakable: false, above: 0.5em, below: 0.3em, inset: (left: 0.9cm), {
    box(width: largeur-cadre, height: (y1 - y0) * s, clip: true, stroke: 0.4pt + luma(190), {
      // largeur ET hauteur explicites : sinon typst centre verticalement l'image qui déborde
      place(top + left, dx: -x-de * s, dy: -y0 * s, image(p.fichier, width: p.w * s, height: p.h * s))
      for l in gris {
        let b = L.at(l - 1)
        place(top + left, dy: (b.at(0) - y0) * s,
          rect(width: largeur-cadre, height: (b.at(1) - b.at(0)) * s, fill: white.transparentize(30%)))
      }
      for (l, x0, x1) in surligne {
        let b = L.at(l - 1)
        place(top + left, dx: (x0 - x-de) * s, dy: (b.at(2) - 45 - y0) * s,
          rect(width: (x1 - x0) * s, height: (b.at(3) - b.at(2) + 90) * s, radius: 3pt,
            fill: luma(0).transparentize(84%)))
      }
      for (l, x0, x1) in entoure {
        let b = L.at(l - 1)
        // l'ellipse reste dans le cadre (sinon elle est coupée)
        let gauche = calc.max(x-de + 8, x0 - 30)
        let droite = calc.min(x-fin - 8, x1 + 30)
        let haut = calc.max(y0 + 8, b.at(2) - 60)
        let bas = calc.min(y1 - 8, b.at(3) + 60)
        place(top + left, dx: (gauche - x-de) * s, dy: (haut - y0) * s,
          ellipse(width: (droite - gauche) * s, height: (bas - haut) * s, stroke: 1.6pt + black))
      }
    })
  })
}

#let manuscrit(page, de, a, ..options) = extrait(page, de, a, ..options)

// Pouce vectoriel, lisible en noir et blanc (pas d'émoji).
#let pouce = image(bytes("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><g fill='white' stroke='black' stroke-width='3.5' stroke-linejoin='round' stroke-linecap='round'><path d='M22 53V29c7-5 13-13 14-23 0-3 8-3 9 4 1 6-1 12-3 16h12c6 0 7 4 6 8l-5 17c-1 4-4 6-9 6H30c-3 0-6-2-8-4Z'/><path d='M5 28h17v29H5Z'/><path d='M12 49h2'/></g></svg>"), format: "svg", width: 0.75cm)

// Légende, une seule fois en début de fiche.
#let legende() = [#box(width: 0.8cm, pouce) Les formes grisées sont bien écrites.]

// Exemple correct de son manuscrit : pouce + formes justes grisées (surligne:).
#let exemple(page, de, a, ..options) = block(breakable: false, {
  place(top + left, dy: 0.15cm, pouce)
  extrait(page, de, a, ..options)
})

// ---------- Blocs de la fiche ----------

// Règle ET son exemple d'application, sur le même fond gris léger.
#let regle(corps) = block(width: 100%, breakable: false, inset: 10pt, radius: 4pt,
  fill: luma(242), stroke: 0.7pt + luma(160), text(size: 12pt, corps))

// Exercice : bandeau gris avec identifiant et consigne courte, puis le contenu.
#let defi(id, consigne, corps) = block(breakable: false, {
  block(inset: (x: 7pt, y: 5pt), fill: luma(235), width: 100%, [*#id.* #consigne])
  corps
})

// Lignes pour écrire, sous l'extrait. Prévoir assez de lignes pour toutes les réponses.
#let reponse(n: 1, consigne: "") = block(breakable: false, above: 0.6em, {
  if consigne != "" { text(size: 10pt, fill: luma(80), consigne) }
  for i in range(n) {
    v(0.7cm)
    line(length: 100%, stroke: 0.6pt + luma(150))
  }
})

// Recherche : un extrait et ses lignes de réponse restent ensemble.
#let recherche(page, de, a, n: 1, consigne: "J'écris les mots corrigés :", ..options) = block(breakable: false)[
  #manuscrit(page, de, a, ..options)
  #reponse(n: n, consigne: consigne)
]

// Retouche rapide ou « tu ne pouvais pas savoir » : mots entourés, forme juste donnée.
#let retouche(page, de, a, mots, entoure: (), n: 1, consigne: "J'écris les mots corrigés :",
  ..options) = block(breakable: false)[
  #manuscrit(page, de, a, entoure: entoure, ..options)
  *À utiliser :* #mots
  #reponse(n: n, consigne: consigne)
]

// Tri juste / faute : numéro, extrait (mots à tester entourés), cases à cocher.
// Elle dit le test à voix haute et coche ; elle n'écrit que les corrections, à la fin.
#let tri(id, page, de, a, mots, ..options) = block(breakable: false, above: 0.4em, below: 0.4em,
  grid(columns: (0.6cm, 13.2cm, 1fr), align: (left + horizon, left, left + horizon),
    text(weight: "bold", size: 10pt)[#id],
    extrait(page, de, a, largeur: 12.3cm, entoure: mots, ..options),
    text(size: 11pt)[☐ juste \ ☐ faute]))

// Petite légende au-dessus d'un extrait (« Ta dictée · page 2 »).
#let source(t) = text(size: 9pt, fill: luma(90), t)

// Case à cocher pour une liste de fin de fiche.
#let case(t) = [☐ #t #linebreak()]
