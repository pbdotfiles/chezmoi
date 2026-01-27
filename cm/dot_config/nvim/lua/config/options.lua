-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

-- The setting below is necessary so that we can activate mini.files in ~/.config/nvim/lua/plugins/extras.lua
vim.g.lazyvim_check_order = false

-- Force Neovim to use a stable, isolated Python virtual environment
-- This prevents 'checkhealth' errors when system Python packages are too old
vim.g.python3_host_prog = vim.fn.expand("~/.local/share/nvim/venv/bin/python")

-- Use the system clipboard instead of the internal clipboard
vim.opt.clipboard = "unnamedplus"

-- Make undo persistent : can undo after closing/reopening neovim.
-- Place all undo files in a single directory, out of sight.
local undodir = vim.fn.expand("~/.local/state/nvim/undo")
if vim.fn.isdirectory(undodir) == 0 then
	vim.fn.mkdir(undodir, "p")
end
vim.opt.undodir = undodir
vim.opt.undofile = true
vim.opt.undolevels = 1000
vim.opt.undoreload = 10000

-- Always save files with Unix (LF) line endings
vim.opt.fileformat = "unix"
vim.opt.fileformats = "unix,dos"
