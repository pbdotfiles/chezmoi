-- EXTRAS.LUA: For ACTIVATING LazyVim feature bundles (via 'import') ONLY.
-- Use this file to toggle major modules (e.g., Markdown support, Mini-files).
-- DO NOT use this for general plugin configuration; put your behavior tweaks
-- (keymaps, plugin options, etc.) in editor.lua or other plugin files instead.

return {
	{ import = "lazyvim.plugins.extras.editor.mini-files" }, -- Activate mini-files
	{ import = "lazyvim.plugins.extras.lang.markdown" }, -- Activate markdown preview

	-- Override : disable markdownlint
	{
		"mfussenegger/nvim-lint",
		opts = {
			linters_by_ft = {
				markdown = {}, -- Override to have NO linters for markdown
			},
		},
	},
}
