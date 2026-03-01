return {
  {
    "dlyongemallo/diffview.nvim",
    cmd = { "DiffviewOpen", "DiffviewClose", "DiffviewToggle", "DiffviewFileHistory" },
    keys = {
      { "<leader>gT", "<cmd>DiffviewToggle<cr>", desc = "Diffview Toggle" },
      { "<leader>gD", "<cmd>DiffviewClose<cr>", desc = "Diffview Close" },
      { "<leader>gch", "<cmd>DiffviewFileHistory --follow %<cr>", desc = "File history" },
    },
    config = function()
      local actions = require("diffview.config").actions

      require("diffview").setup({
        enhanced_diff_hl = true,

        merge_tool = {
          layout = "diff3_mixed",
          disable_diagnostics = false,
          winbar_info = true,
        },

        keymaps = {
          view = {
            { "n", "<leader>gch", actions.conflict_choose("ours"), { desc = "Accept OURS" } },
            { "n", "<leader>gcl", actions.conflict_choose("theirs"), { desc = "Accept THEIRS" } },
            { "n", "<leader>gcb", actions.conflict_choose("base"), { desc = "Accept BASE" } },
            { "n", "<leader>gcn", actions.conflict_choose("none"), { desc = "Delete conflict" } },
            { "n", "<leader>gcH", actions.conflict_choose_all("ours"), { desc = "Accept ALL OURS" } },
            { "n", "<leader>gcL", actions.conflict_choose_all("theirs"), { desc = "Accept ALL THEIRS" } },
            { "n", "<leader>gcB", actions.conflict_choose_all("base"), { desc = "Accept ALL BASE" } },
          },
        },

        hooks = {
          diff_buf_read = function(bufnr, ctx)
            vim.opt_local.wrap = false
            vim.opt_local.foldenable = false
          end,
          diff_buf_win_enter = function(bufnr, winid, ctx)
            vim.wo[winid].foldmethod = "manual"
            vim.wo[winid].relativenumber = false
            vim.wo[winid].signcolumn = "no"
          end,
        },
      })
    end,
  },
}
