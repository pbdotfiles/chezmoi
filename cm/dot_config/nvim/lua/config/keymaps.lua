-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

-- Escape terminal mode using '<C-x>'
vim.keymap.set("t", "<C-x>", "<C-\\><C-n>", { desc = "Exit terminal mode" })

-- diffview.nvim workflow
vim.keymap.set("n", "]g", "]c", { desc = "Next diff hunk" })
vim.keymap.set("n", "[g", "[c", { desc = "Prev diff hunk" })
-- vim.keymap.set("n", "<leader>gD", "<cmd>DiffviewClose<cr>", { desc = "Diffview Close" })
