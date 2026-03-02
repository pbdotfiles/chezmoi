-- ============================================================================
-- Slime & REPL Configuration
--
-- Use `vim-slime` and `vim-slime-cells` plugins + tmux + ipython to reproduce
-- a Spyder-like experience in neovim.
--
-- The function `safe_slime` ensures we only send text to a pane that matches
-- either the "^ipython" or "^python" pattern.
-- ============================================================================

local function safe_slime(plug_cmd)
  -- Only send text via vim-slime if the target pane runs python.

  -- 1. Get the target pane from buffer-local or your global config
  local ok, config = pcall(vim.api.nvim_buf_get_var, 0, "slime_config")
  if not ok then
    ok, config = pcall(vim.api.nvim_get_var, "slime_default_config")
  end

  -- If no config exists yet, return the plug command so Slime can prompt you
  if not ok or not config or not config.target_pane then
    return plug_cmd
  end

  local target = config.target_pane
  local socket = config.socket_name or "default"

  -- 2. Query Tmux natively via Neovim
  local cmd = string.format("tmux -L %s display-message -p -t '%s' '#{pane_current_command}'", socket, target)
  local running_cmd = vim.fn.system(cmd):gsub("%s+", "")

  -- If tmux check fails (e.g., pane doesn't exist yet), let Slime handle the error naturally
  if vim.v.shell_error ~= 0 then
    return plug_cmd
  end

  -- 3. Whitelist
  local whitelist_patterns = { "^ipython", "^python" }

  for _, pattern in ipairs(whitelist_patterns) do
    if running_cmd:match(pattern) then
      return plug_cmd -- Safe to send!
    end
  end

  -- 4. Block send and warn
  vim.notify("Slime Blocked: Pane is running '" .. running_cmd .. "'.", vim.log.levels.ERROR)
  return "<Ignore>"
end

return {
  {
    "jpalardy/vim-slime",
    init = function()
      -- Tell slime to use tmux
      vim.g.slime_target = "tmux"

      -- Auto-target the pane to the right (so it doesn't prompt you every time)
      vim.g.slime_default_config = { socket_name = "default", target_pane = "{bottom-right}" }
      vim.g.slime_dont_ask_default = 0

      -- Enable bracketed paste so IPython handles indentation perfectly
      vim.g.slime_bracketed_paste = 1
      vim.g.slime_python_ipython = 1
    end,
    keys = {
      -- Standard visual send keymap
      {
        "<leader>rs",
        function()
          return safe_slime("<Plug>SlimeRegionSend")
        end,
        mode = "x",
        expr = true,
        desc = "Send Selection",
      },
      {
        "<leader>rl",
        function()
          return safe_slime("<Plug>SlimeLineSend")
        end,
        mode = "n",
        expr = true,
        desc = "Send Line",
      },
      {
        "<leader>rf",
        function()
          return safe_slime("<cmd>%SlimeSend<cr>")
        end,
        expr = true,
        desc = "Send Full File",
      },
    },
  },
  {
    "klafyvel/vim-slime-cells",
    dependencies = { "jpalardy/vim-slime" },
    ft = "python",
    init = function()
      vim.g.slime_cell_delimiter = [[#\s*%%]] -- Cell marker
    end,
    keys = {
      {
        "<leader>rc",
        function()
          return safe_slime("<Plug>SlimeCellsSend")
        end,
        expr = true,
        desc = "Send Cell",
      },
      {
        "<leader>rn",
        function()
          return safe_slime("<Plug>SlimeCellsSendAndGoToNext")
        end,
        expr = true,
        desc = "Send Cell & Next",
      },
      -- Cell navigation
      { "[c", "<Plug>SlimeCellsPrev", desc = "Previous Cell" },
      { "]c", "<Plug>SlimeCellsNext", desc = "Next Cell" },
    },
  },
}
