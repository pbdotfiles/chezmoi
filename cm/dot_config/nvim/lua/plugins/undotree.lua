return {
  "jiaoshijie/undotree",
  dependencies = "nvim-lua/plenary.nvim",
  keys = {
    {
      "<leader>uu",
      function()
        require("undotree").toggle()
      end,
      desc = "Toggle Undotree",
    },
  },
  opts = {
    float_diff = true, -- shows diff in a floating window
    layout = "left_bottom",
    position = "left",
    ignore_filetype = { "undotree", "undotreeDiff", "qf", "TelescopePrompt", "spectre_panel", "tsplayground" },
  },
}
