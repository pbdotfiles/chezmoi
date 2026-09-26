# Fuzzy navigation cheat sheet

For fzf 0.73.1 + zoxide 0.9.9, configured in `~/.bash_aliases`.

## Mental model: 3 ways to invoke fzf

1. **The universal trigger `**` + TAB** — inline, works on the command line for *any* command.
2. **Global key widgets** — `Ctrl-T`, `Ctrl-R`, `Alt-C`.
3. **Command-specific** — `z`/`zi` (zoxide), which mix frecency and fzf.

---

## 1. The universal trigger: `**<TAB>`

Type `**` at the end of the current word, then TAB. Text *before* `**` sets the search root.

| You type | It searches |
|---|---|
| `z **<TAB>` | directories, recursively from cwd |
| `cd **<TAB>` | same (because `alias cd=z`) |
| `z some/path/**<TAB>` | directories under `some/path` |
| `<any command> **<TAB>` | files + dirs |

- **Dir-only vs files+dirs**: `cd pushd rmdir` (and `z`/`cd` in your config) list dirs only; everything else defaults to files+dirs.
- **Change the trigger**: `export FZF_COMPLETION_TRIGGER='~~'` (default `**`).

### Special kinds (fzf built-ins)

| You type | It searches |
|---|---|
| `ssh **<TAB>` | hosts from `~/.ssh/known_hosts` |
| `kill **<TAB>` | running processes (PIDs) |
| `export **<TAB>` | environment variable names |
| `unalias **<TAB>` | your aliases |

---

## 2. zoxide (`z`) — frecency + fzf

| Trigger | What it does |
|---|---|
| `z foo bar<Enter>` | jump by frecency, no UI (terms match path segments) |
| `zi` | full fzf UI over your whole zoxide database |
| `z foo <TAB>` | same as `zi`, pre-filtered by `foo` |
| `z <TAB>` | plain directory prefix completion in cwd |
| `z **<TAB>` | fzf recursive dir walker from cwd |
| `z -` | jump to previous directory |
| `z` (alone) | `cd ~` |

- History is recorded automatically by zoxide's `PROMPT_COMMAND` hook.
- Tweak `zi`'s fzf: `export _ZO_FZF_OPTS='--height 60% --reverse --preview ...'`.

---

## 3. Global key widgets

| Key | What it does |
|---|---|
| `Ctrl-T` | fzf picker of **files + dirs** from cwd (via `fd`), **multi-select** |
| `Ctrl-R` | fzf **history** search |
| `Alt-C` | fzf **directory** picker + `cd` (from cwd) |

---

## 4. Inside the fzf window

**Query syntax** (extended-search mode is on by default):

| Pattern | Meaning |
|---|---|
| `foo bar` | fuzzy match both, in any order (AND) |
| `'foo` | exact (non-fuzzy) match |
| `^foo` | line starts with `foo` (exact) |
| `foo$` | line ends with `foo` (exact) |
| `!foo` | exclude lines matching `foo` |
| `foo \| bar` | OR |
| `\ ` | a literal space |

Fragments match characters *in order* across the whole line, skipping everything in between (e.g. `ScoAgaMath` matches `Scolarité Agathe/CE2/Maths`).

**Keys** (fzf defaults):

| Key | Action |
|---|---|
| `Enter` | accept |
| `Esc` / `Ctrl-C` | abort |
| `Ctrl-J` / `Ctrl-K` | move down / up (= arrows) |
| `PgUp` / `PgDn` | page |
| `Ctrl-A` / `Ctrl-E` | start / end of query |
| `Ctrl-U` / `Ctrl-W` | delete line / delete word |
| `Ctrl-Y` | yank (paste) |
| `Ctrl-D` | delete char (aborts if query empty) |
| `Ctrl-L` | clear screen |
| `Tab` / `Shift-Tab` | select / deselect (when multi-select is on) |
| `Alt-B` / `Alt-F` | word left / right |

---

## 5. Add fuzzy completion to your own command

```bash
_fzf_setup_completion path mycmd     # files + dirs
_fzf_setup_completion dir  mycmd     # dirs only
_fzf_setup_completion var  mycmd     # env vars
_fzf_setup_completion alias mycmd
_fzf_setup_completion host mycmd     # ssh hosts
_fzf_setup_completion proc mycmd     # processes
```
