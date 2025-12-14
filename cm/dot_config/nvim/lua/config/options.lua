-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

-- The setting below is necessary so that we can activate mini.files in ~/.config/nvim/lua/plugins/extras.lua
vim.g.lazyvim_check_order = false

-- Force Neovim to use a stable, isolated Python virtual environment
-- This prevents 'checkhealth' errors when system Python packages are too old
vim.g.python3_host_prog = vim.fn.expand("~/.local/share/nvim/venv/bin/python")
