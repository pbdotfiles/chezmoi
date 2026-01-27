-- EDITOR.LUA: For CONFIGURING the behavior, UI, and 'opts' of plugins.
-- Use this file for tweaks (e.g., completion keys, picker settings, UI changes).
-- NOT for activating major feature bundles (use extras.lua) or general
-- Neovim-wide settings like indentation or paths (use options.lua).

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
