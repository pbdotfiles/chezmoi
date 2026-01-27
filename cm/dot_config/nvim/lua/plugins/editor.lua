return {
	{
		"folke/snacks.nvim",
		optional = true,
		opts = {
			picker = {
				sources = {
					files = {
						hidden = true, -- Enable hidden files
						ignored = false, -- Keep gitignored files hidden (set to true to show them)
					},
					grep = {
						hidden = true,
						ignored = false,
					},
				},
			},
		},
	},
	{
		"saghen/blink.cmp",
		optional = true,
		opts = {
			keymap = {
				preset = "default",
				["<CR>"] = { "fallback" }, -- This disables Enter for completion
			},
		},
	},
}
