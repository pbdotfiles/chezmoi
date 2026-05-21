-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

-- Escape terminal mode using '<C-x>'
vim.keymap.set("t", "<C-x>", "<C-\\><C-n>", { desc = "Exit terminal mode" })

-- diffview.nvim workflow
vim.keymap.set("n", "]g", "]c", { desc = "Next diff hunk" })
vim.keymap.set("n", "[g", "[c", { desc = "Prev diff hunk" })
-- vim.keymap.set("n", "<leader>gD", "<cmd>DiffviewClose<cr>", { desc = "Diffview Close" })

-- Command to run Ruff
vim.api.nvim_create_user_command("RuffCheck", function()
	vim.notify("Running Ruff on project...", vim.log.levels.INFO)
	local output = vim.fn.systemlist("ruff check . --output-format=concise")
	vim.fn.setqflist({}, " ", { title = "Ruff", lines = output, efm = "%f:%l:%c: %m" })
	vim.cmd("cwindow")
end, { desc = "Populate Quickfix with project-wide Ruff diagnostics" })

-- Command to run Pyright
vim.api.nvim_create_user_command("PyrightCheck", function()
	vim.notify("Running Pyright on project...", vim.log.levels.INFO)
	local output = vim.fn.systemlist("pyright")
	vim.fn.setqflist({}, " ", { title = "Pyright", lines = output, efm = "%*[ ]%f:%l:%c - %m,%-G%.%#" })
	vim.cmd("cwindow")
end, { desc = "Populate Quickfix with project-wide Pyright diagnostics" })
