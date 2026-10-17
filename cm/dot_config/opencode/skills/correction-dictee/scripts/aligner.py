"""Aligne un texte de référence et la transcription de l'enfant, mot par mot.

Usage : python aligner.py reference.md transcription.md [> ecarts.md]

- reference.md : le texte lu (Markdown ; les titres `#` sont ignorés).
- transcription.md : format du projet. Sections `### Page N` (ou `### ... N`),
  puis une ligne du cahier par ligne numérotée `1. texte`. Tout le reste est ignoré.

Sortie : un tableau Markdown des écarts (page:ligne, attendu, écrit, type),
puis un résumé. Les signes de ponctuation sont des jetons à part.
Les apostrophes typographiques sont normalisées. La casse compte.

Il sert à l'inventaire, sur la transcription validée par Papa : chaque écart
y devient une faute, un écart accepté ou un cas à trancher. Les annotations
CriticMarkup éventuelles sont ignorées (le mot lu est gardé).
Si l'alignement déraille (mot répété, ligne sautée), le relancer sur des
morceaux plus courts.
"""
import difflib
import re
import sys

TOKEN = re.compile(r"[\wÀ-ÖØ-öø-ÿœŒæÆ'’-]+|[^\s\w]", re.UNICODE)


def norm(s):
    s = re.sub(r"<!--.*?-->", " ", s)
    s = re.sub(r"\{>>.*?<<\}", " ", s)          # commentaire CriticMarkup
    s = re.sub(r"\{==(.*?)==\}", r"\1", s)      # mot surligné : on garde le mot
    return s.replace("’", "'").replace("\u00a0", " ")


def tokens(text):
    out = []
    for t in TOKEN.findall(norm(text)):
        # "l'automne" -> "l'", "automne" ; "qu'un" -> "qu'", "un"
        m = re.match(r"^(\w+')(.+)$", t)
        if m:
            out += [m.group(1), m.group(2)]
        else:
            out.append(t)
    return out


def read_reference(path):
    text = []
    for line in open(path, encoding="utf-8"):
        if line.lstrip().startswith("#"):
            continue
        text.append(line)
    return tokens(" ".join(text))


def read_transcription(path):
    toks, where = [], []
    page = "?"
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^#{2,4}\s+\D*?(\d+)", line)
        if m:
            page = m.group(1)
            continue
        m = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if m:
            for t in tokens(m.group(2)):
                toks.append(t)
                where.append(f"p{page}:{m.group(1)}")
    return toks, where


def main(ref_path, tr_path):
    ref = read_reference(ref_path)
    kid, where = read_transcription(tr_path)
    sm = difflib.SequenceMatcher(a=ref, b=kid, autojunk=False)
    rows = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        loc = where[j1] if j1 < len(where) else (where[-1] if where else "?")
        if j2 - j1 > 0 and where[j1] != where[j2 - 1]:
            loc = f"{where[j1]}-{where[j2 - 1].split(':')[1]}"
        kind = {"replace": "remplacé", "delete": "oublié", "insert": "ajouté"}[op]
        rows.append((loc, " ".join(ref[i1:i2]), " ".join(kid[j1:j2]), kind))
    print("| Où | Attendu | Écrit | Type |")
    print("|---|---|---|---|")
    for loc, a, b, k in rows:
        print(f"| {loc} | {a or '∅'} | {b or '∅'} | {k} |")
    same = sum(b.size for b in sm.get_matching_blocks())
    print()
    print(f"Jetons référence : {len(ref)} ; jetons transcrits : {len(kid)} ; "
          f"identiques : {same} ; écarts : {len(rows)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
