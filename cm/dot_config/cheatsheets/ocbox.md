# ocbox cheat sheet

OpenCode with the agent confined to chosen folders (bubblewrap). Edit with `chezmoi edit ~/.config/cheatsheets/ocbox.md`.

## Quick reference

### Only this folder

```bash
ocbox -e none        # current folder (or its git repo) read-write, no other folder, no pixi env
```

Without `.envrc` or git repository, ocbox asks before sharing the folder (`ocbox -w .` skips the question).

### A project with its own rights

```bash
# <project>/.envrc
use pe p313                                      # pixi env, read-only
ocbox_ro ~/projects/sandbox/seeq_tutorial        # reference, read-only
ocbox_rw ~/projects/shared_lib                   # other folder, read-write
ocbox_ro data/raw                                # subfolder of the project, read-only
ocbox_hide .env secrets/                         # inaccessible (folders appear empty)
ocbox_env GOOGLE_CLOUD_PROJECT VERTEX_LOCATION   # variables to pass (API keys, ...)
```

```bash
direnv allow         # after every edit of .envrc
ocbox show           # check the rights
ocbox                # start, or join the server with the same rights
```

The `.envrc` folder is always read-write (unless listed in `ocbox_ro`). Underscore, not space: `ocbox_rw`, never `ocbox rw`. Variables needed everywhere (API keys): `~/.config/ocbox/env`.

### One-off additions

```bash
ocbox -r ~/some/reference     # read-only folder
ocbox -w ~/some/output        # read-write folder
ocbox -x secretfile           # hide a file or folder of the project
ocbox -e seeq312              # another pixi env (-e none: no env)
ocbox -E MY_API_KEY           # pass one variable
```

### Sessions

| Command | Action |
|---|---|
| `ocbox -c` | continue the last session |
| `ocbox -s <id>` | continue a given session |
| `ocbox` in a second pane | another session on the same server |
| `opencode` | vanilla, unsandboxed, sees all ocbox sessions |

### Wrong rights?

```bash
# quit the TUI, then
nvim .envrc && direnv allow
ocbox -c             # same conversation, new rights (new server)
```

### Housekeeping

| Command | Action |
|---|---|
| `ocbox show` | rights for this folder, server running or not |
| `ocbox shell` | bash in the same sandbox, to check what the agent sees |
| `ocbox ls` | running sandboxed servers and their TUIs |
| `ocbox stop <id>` / `--all` | stop servers: after a crash, or to restart after editing hidden files |

---

## Details

### Which folder is the project

1. The folder of the nearest `.envrc` (ignored if it is `~`),
2. else the root of the git repository,
3. else the current folder, after confirmation.

To limit a session to a subfolder of a repo, put an `.envrc` (even empty) in that subfolder.

### What the sandbox sees

| What | Access |
|---|---|
| The project and folders you list | as listed (read-only wins if listed both ways) |
| Subfolders listed in `ocbox_ro` / `ocbox_rw` | their own access, at any depth |
| Paths listed in `ocbox_hide` | folders: empty, read-only; files: "Permission denied" |
| Inside read-write folders: `.git/hooks`, `.git/config` (submodules too), `.envrc`, `.nvim.lua`, `.lazy.lua`, `.exrc` | read-only (4 levels deep; a missing `.git/hooks` is created) |
| The pixi env | read-only (read-write if listed with `ocbox_rw`: allows `pixi add`) |
| `/usr`, `/etc`, `/opt`, tools (`~/.local/bin`, `~/bin`, pixi, nvm), opencode, git settings | read-only |
| `~/.config/opencode` (without `service*.json`) | read-only |
| OpenCode history and state: all sessions, undo snapshots (copies of every project, `.env` included), provider credentials | read-write |
| Internet | open |
| Rest of `~`, `/mnt/c`, `/run` (WSL interop, Docker), other processes | hidden |
| `~` (except the above), `/tmp` | empty, in RAM, lost when the server stops |
| Environment | cleared: locale, CA bundles, proxies, `~/.config/ocbox/env` and `ocbox_env` variables only |

### Servers

- One server per set of rights and opencode version: same rights, same server; other rights, another server.
- A server stops when its last TUI closes, **interrupting a running agent task**. Changing `.envrc` never touches a running server.
- State and logs: `~/.local/state/ocbox/<id>/server.log` (removed 7 days after the server stops).
- Plugins cache: `~/.cache/ocbox/opencode` (separate from vanilla's).

### Sharing history with vanilla opencode

- Sessions of every server are in the same database: visible everywhere, at any time.
- Live updates are not shared between servers: a TUI on vanilla does not refresh while an ocbox server works on the same session, and the reverse.
- Never work on the same session in vanilla and ocbox at the same time. Same for two ocbox servers on one project (ocbox warns): they may also collide on undo snapshots.

### Gotchas

- A modified `.envrc` is blocked until `direnv allow`: ocbox refuses to start.
- Never call `ocbox` from an `.envrc`.
- Secrets in the project (`.env`, ...) are readable by the agent, unless listed in `ocbox_hide`.
- `ocbox_hide` takes exact paths that exist when the server starts (no patterns; created later: visible).
- A hidden or protected file replaced from outside while the server runs (saved by nvim, rewritten by git) loses its protection inside (hidden: readable again; read-only: writable): restart the server (`ocbox stop <id>`).
- Hidden or read-only paths cannot be deleted from inside ("Device or resource busy").
- Hidden tracked files look deleted or emptied to `git status` inside the sandbox: don't let the agent `git add -A`.
- Git commands writing `.git/config` fail (`git remote add`, `git push -u`).
- `pip install` fails in a read-only env; `pip install --user` vanishes when the server stops.
- Google Vertex needs its variables passed: `GOOGLE_CLOUD_*`, `VERTEX_LOCATION` (with `ocbox_env` or `-E`).
- Continuing an ocbox session in vanilla `opencode` runs it with full rights.
- `ocbox` refuses to share `/`, `~` or any folder above `~`.
