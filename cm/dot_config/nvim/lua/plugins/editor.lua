return {
  {
    "folke/snacks.nvim",
    opts = {
      picker = {
        sources = {
          files = {
            hidden = true, -- Enable hidden files
            ignored = false, -- Keep gitignored files hidden (set to true to show them)
          },
        },
      },
    },
  },
}
