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
