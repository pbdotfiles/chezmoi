-- Autocmds are automatically loaded on the VeryLazy event
-- Default autocmds that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/autocmds.lua
-- Add any additional autocmds here

-- Fix: Disable LazyVim's forced spell checking for markdown/text
vim.api.nvim_create_autocmd("FileType", {
  pattern = { "markdown", "text", "gitcommit" },
  callback = function()
    -- We delete the group that forces spell=true
    pcall(vim.api.nvim_del_augroup_by_name, "lazyvim_wrap_spell")
    -- Then we explicitly turn it off for the current buffer
    vim.opt_local.spell = false
  end,
})
