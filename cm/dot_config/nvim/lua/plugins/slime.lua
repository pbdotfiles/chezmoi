-- ============================================================================
-- Slime & REPL Configuration
--
-- Use `vim-slime` and `vim-slime-cells` plugins + tmux + ipython to reproduce
-- a Spyder-like experience in neovim.
--
-- `check_target` ensures we only send text to a pane running an approved process
-- (ipython, python, or sqlite3).
-- ============================================================================

local WHITELIST = { ipython = "python", python = "python", sqlite3 = "sqlite3" }

-- Returns target_type, blocked:
--   "python"       = safe, target is ipython or python
--   "sqlite3"      = safe, target is sqlite3
--   nil            = no config / tmux query failed (caller should fall back)
--   nil, true      = blocked (notification already fired, caller should abort)
local function check_target()
  local ok, config = pcall(vim.api.nvim_buf_get_var, 0, "slime_config")
  if not ok then
    ok, config = pcall(vim.api.nvim_get_var, "slime_default_config")
  end
  if not ok or not config or not config.target_pane then
    return nil
  end

  local target = config.target_pane
  local socket = config.socket_name or "default"
  local cmd = string.format("tmux -L %s display-message -p -t '%s' '#{pane_current_command}'", socket, target)
  local running_cmd = vim.fn.system(cmd):gsub("%s+", "")
  if vim.v.shell_error ~= 0 then
    return nil
  end

  for pattern, target_type in pairs(WHITELIST) do
    if running_cmd:match("^" .. pattern) then
      return target_type
    end
  end

  vim.notify("Slime Blocked: Pane is running '" .. running_cmd .. "'.", vim.log.levels.ERROR)
  return nil, true
end

local function safe_slime(plug_cmd)
  local _, blocked = check_target()
  if blocked then return "<Ignore>" end
  return plug_cmd
end

local function safe_slime_run_file()
  local target_type, blocked = check_target()
  if blocked then return end
  if not target_type then vim.cmd("%SlimeSend"); return end

  if target_type == "python" then
    local filepath = vim.fn.expand("%:p")
    if filepath == "" then
      vim.notify("Run File: buffer has no filename", vim.log.levels.WARN)
      return
    end
    if vim.bo.modified then
      vim.cmd("silent! write")
    end
    vim.fn["slime#send"]("%run -i " .. vim.fn.shellescape(filepath))
  else
    vim.cmd("%SlimeSend")
  end
end

return {
  {
    "jpalardy/vim-slime",
    init = function()
      vim.g.slime_target = "tmux"
      vim.g.slime_default_config = { socket_name = "default", target_pane = "{bottom-right}" }
      vim.g.slime_dont_ask_default = 0
      vim.g.slime_bracketed_paste = 1
      vim.g.slime_python_ipython = 1
    end,
    keys = {
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
        safe_slime_run_file,
        mode = "n",
        desc = "Run File (%run -i / raw)",
      },
    },
  },
  {
    "klafyvel/vim-slime-cells",
    dependencies = { "jpalardy/vim-slime" },
    ft = "python",
    init = function()
      vim.g.slime_cell_delimiter = [[#\s*%%]]
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
      { "[c", "<Plug>SlimeCellsPrev", desc = "Previous Cell" },
      { "]c", "<Plug>SlimeCellsNext", desc = "Next Cell" },
    },
  },
}
