## WezTerm

Place `wezterm.lua` (from this folder) at:

```
%USERPROFILE%\.wezterm.lua
```

This gives you:
- JetBrainsMono Nerd Font, size 11
- Tokyo Night color scheme (matches Neovim + Kitty)
- No title bar (window is still resizable by dragging edges)
- OSC 52 clipboard read+write — makes `p` in Neovim work from the Windows clipboard through tmux/WSL
- Default shell: WSL distribution `ulz`

---

## WSL config

Put this in /etc/wsl.conf

```
[boot]
systemd=true    (or false, I'm not sure if this is the reason the process gets killed)

[user]
default=paul

[interop]
appendWindowsPath = false
```
