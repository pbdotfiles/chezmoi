# Terminal cheat sheet

Open with `keys`. Edit with `chezmoi edit ~/.config/cheatsheets/terminal.md`.

## Quick reference

### Jump around (shell)

| Key | Action |
|---|---|
| `z foo [bar]` | jump to best match from history |
| `zi` | pick from zoxide history |
| `z -` | back to previous folder |
| `Alt-C` | fuzzy cd into a subfolder |
| `cd **<Tab>` | fuzzy folder completion |
| `Ctrl-T` | fuzzy-insert a file path |
| `Ctrl-R` | fuzzy history |
| `Alt-y` / `yz` | open yazi |

### Command line

| Key | Action |
|---|---|
| `Alt-.` | insert last argument of previous command |
| `Ctrl-X Ctrl-E` | edit current command in nvim |
| `Ctrl-U` / `Ctrl-Y` | cut line / paste it back |

### Yazi

| Key | Action |
|---|---|
| `q` / `Q` | quit and cd here / quit, stay where you were |
| `h j k l` | move (`l` or `Enter` opens) |
| `z` / `Z` | jump with fzf / with zoxide |
| `g h` `g c` `g d` | home, `~/.config`, `~/Downloads` |
| `g Space` | type a path |
| `.` | toggle hidden files |
| `f` / `/` | filter list / find next match (`n`, `N`) |
| `s` / `S` | search names (fd) / contents (rg) |
| `Space` / `v` | select / visual select |
| `y` `x` `p` / `d` | copy, cut, paste / trash |
| `a` / `r` | create (end with `/` for a folder) / rename |
| `c c` / `c d` | copy file path / folder path |
| `;` | run a shell command here |
| `t t` / `1-9` | new tab / switch tab |
| `~` or `F1` | help (all keys) |

### tmux (prefix = `Ctrl-B`)

| Key | Action |
|---|---|
| `Ctrl-h/j/k/l` | move between panes (also across nvim splits) |
| `prefix c` `"` `%` | new window / split below / split right, in current folder |
| `prefix <` / `>` | move window left / right |
| `prefix r` | reload config |

---

## Details

### fzf `**<TAB>` trigger

Type `**` at the end of the current word, then TAB. Text *before* `**` sets the search root.

| You type | It searches |
|---|---|
| `z **<TAB>` / `cd **<TAB>` | directories, recursively from cwd |
| `z some/path/**<TAB>` | directories under `some/path` |
| `<any command> **<TAB>` | files + dirs |
| `ssh **<TAB>` | hosts from `~/.ssh/known_hosts` |
| `kill **<TAB>` | running processes (PIDs) |
| `export **<TAB>` | environment variable names |
| `unalias **<TAB>` | your aliases |

- `cd pushd rmdir` (and `z`/`cd` in your config) list dirs only; everything else lists files + dirs.
- Change the trigger: `export FZF_COMPLETION_TRIGGER='~~'`.

### zoxide extras

| Trigger | What it does |
|---|---|
| `z foo <TAB>` | same as `zi`, pre-filtered by `foo` |
| `z <TAB>` | plain directory prefix completion in cwd |
| `z` (alone) | `cd ~` |

- History is recorded by zoxide's prompt hook, and by yazi on every folder change.
- Tweak `zi`'s fzf: `export _ZO_FZF_OPTS='--height 60% --reverse --preview ...'`.

### Inside fzf

**Query syntax:**

| Pattern | Meaning |
|---|---|
| `foo bar` | fuzzy match both, in any order (AND) |
| `'foo` | exact (non-fuzzy) match |
| `^foo` / `foo$` | starts / ends with `foo` |
| `!foo` | exclude lines matching `foo` |
| `foo \| bar` | OR |
| `\ ` | a literal space |

Fragments match characters *in order* across the whole line (e.g. `ScoAgaMath` matches `Scolarité Agathe/CE2/Maths`).

**Keys:**

| Key | Action |
|---|---|
| `Ctrl-J` / `Ctrl-K` | move down / up |
| `Tab` / `Shift-Tab` | select / deselect (multi-select) |
| `Ctrl-U` / `Ctrl-W` | delete query / delete word |
| `Esc` / `Ctrl-C` | abort |

### Add fuzzy completion to your own command

```bash
_fzf_setup_completion path mycmd     # files + dirs
_fzf_setup_completion dir  mycmd     # dirs only
_fzf_setup_completion var  mycmd     # env vars
_fzf_setup_completion alias mycmd
_fzf_setup_completion host mycmd     # ssh hosts
_fzf_setup_completion proc mycmd     # processes
```
