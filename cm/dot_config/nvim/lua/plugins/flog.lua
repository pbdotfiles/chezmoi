return {
	{
		"rbong/vim-flog",
		lazy = true,
		cmd = { "Flog", "Flogsplit", "Floggit" },
		dependencies = { "tpope/vim-fugitive" },
		keys = {
			{ "<leader>gF", "<cmd>Flog -all<cr>", desc = "Git Flog" },
		},
		init = function()
			vim.g.flog_enable_extended_chars = 1
			vim.g.flog_permanent_default_opts = { max_count = 5000 }
		end,
		config = function()
			local function get_hash()
				local commit = vim.fn["flog#floggraph#commit#GetAtLine"](vim.fn.line("."))
				return commit and commit.hash or nil
			end

			vim.api.nvim_create_autocmd("FileType", {
				pattern = "floggraph",
				callback = function()
					local opts = { buffer = true, silent = true }

					-- View what this single commit introduced
					vim.keymap.set("n", "<C-f>", function()
						local hash = get_hash()
						if hash then
							vim.cmd("DiffviewOpen " .. hash .. "^!")
						end
					end, vim.tbl_extend("force", opts, { desc = "View commit in Diffview" }))

					-- Diff this commit against your working directory
					vim.keymap.set("n", "<C-d>", function()
						local hash = get_hash()
						if hash then
							vim.cmd("DiffviewOpen " .. hash)
						end
					end, vim.tbl_extend("force", opts, { desc = "Diff commit vs workdir" }))
				end,
			})
		end,
	},
}
