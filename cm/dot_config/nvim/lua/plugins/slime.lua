local VALID_TARGETS = {
  "^ipython",
  "^python",
  "^sqlite3",
}

local function is_target_safe()
  local ok, config = pcall(vim.api.nvim_buf_get_var, 0, "slime_config")
  if not ok then
    ok, config = pcall(vim.api.nvim_get_var, "slime_default_config")
  end

  if not ok or not config or not config.target_pane then
    return true
  end

  local target = config.target_pane
  local socket = config.socket_name or "default"
  local cmd = string.format("tmux -L %s display-message -p -t '%s' '#{pane_current_command}'", socket, target)
  local running_cmd = vim.fn.system(cmd):gsub("%s+", "")

  if vim.v.shell_error ~= 0 then
    return true
  end

  for _, pattern in ipairs(VALID_TARGETS) do
    if running_cmd:match(pattern) then
      return true
    end
  end

  vim.notify("Slime Blocked: Pane is running '" .. running_cmd .. "'.", vim.log.levels.ERROR)
  return false
end

local function safe_slime_expr(plug_cmd)
  return is_target_safe() and plug_cmd or "<Ignore>"
end

return {
  {
    "jpalardy/vim-slime",
    init = function()
      vim.g.slime_target = "tmux"
      vim.g.slime_default_config = { socket_name = "default", target_pane = "{bottom-right}" }
      vim.g.slime_dont_ask_default = 0
      vim.g.slime_bracketed_paste = 1
      vim.g.slime_python_ipython = 0
    end,
    keys = {
      {
        "<leader>rs",
        function()
          return safe_slime_expr("<Plug>SlimeRegionSend")
        end,
        mode = "x",
        expr = true,
        desc = "Send Selection",
      },
      {
        "<leader>rl",
        function()
          return safe_slime_expr("<Plug>SlimeLineSend")
        end,
        mode = "n",
        expr = true,
        desc = "Send Line",
      },
      {
        "<leader>rf",
        function()
          if is_target_safe() then
            vim.cmd("%SlimeSend")
          end
        end,
        mode = "n",
        desc = "Send Full File",
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
          return safe_slime_expr("<Plug>SlimeCellsSend")
        end,
        expr = true,
        desc = "Send Cell",
      },
      {
        "<leader>rn",
        function()
          return safe_slime_expr("<Plug>SlimeCellsSendAndGoToNext")
        end,
        expr = true,
        desc = "Send Cell & Next",
      },
      { "[c", "<Plug>SlimeCellsPrev", desc = "Previous Cell" },
      { "]c", "<Plug>SlimeCellsNext", desc = "Next Cell" },
    },
  },
}
