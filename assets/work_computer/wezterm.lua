local wezterm = require("wezterm")
local config = wezterm.config_builder()

config.front_end = "WebGpu"

-- =============================================================================
-- Default program
-- =============================================================================

config.default_prog = { "wsl.exe", "--distribution", "ulz" }

-- =============================================================================
-- Font
-- =============================================================================

config.font = wezterm.font("FiraCode Nerd Font Mono")
config.font_size = 11.0

-- =============================================================================
-- Color scheme (Tokyo Night — matches kitty + Neovim)
-- =============================================================================

config.colors = {
	foreground = "#c0caf5",
	background = "#1a1b26",
	cursor_bg = "#c0caf5",
	cursor_fg = "#1a1b26",
	cursor_border = "#c0caf5",
	selection_fg = "#c0caf5",
	selection_bg = "#283457",
	ansi = {
		"#15161e", -- black
		"#f7768e", -- red
		"#9ece6a", -- green
		"#e0af68", -- yellow
		"#7aa2f7", -- blue
		"#bb9af7", -- magenta
		"#7dcfff", -- cyan
		"#a9b1d6", -- white
	},
	brights = {
		"#414868", -- bright black
		"#f7768e", -- bright red
		"#9ece6a", -- bright green
		"#e0af68", -- bright yellow
		"#7aa2f7", -- bright blue
		"#bb9af7", -- bright magenta
		"#7dcfff", -- bright cyan
		"#c0caf5", -- bright white
	},
	indexed = {
		[16] = "#ff9e64", -- orange
		[17] = "#db4b4b", -- dark red
	},
	tab_bar = {
		background = "#15161e",
		active_tab = {
			bg_color = "#7aa2f7",
			fg_color = "#16161e",
			intensity = "Normal",
			underline = "None",
			italic = false,
			strikethrough = false,
		},
		inactive_tab = {
			bg_color = "#292e42",
			fg_color = "#545c7e",
		},
		inactive_tab_hover = {
			bg_color = "#2f3549",
			fg_color = "#7aa2f7",
		},
		new_tab = {
			bg_color = "#15161e",
			fg_color = "#545c7e",
		},
		new_tab_hover = {
			bg_color = "#15161e",
			fg_color = "#7aa2f7",
		},
	},
}

-- =============================================================================
-- Background opacity
-- =============================================================================

config.window_background_opacity = 0.98

-- =============================================================================
-- Window chrome
-- Remove the title bar but keep the resize border so the window is still
-- resizable by dragging the edges. RESIZE is the cleanest option on Windows.
-- =============================================================================

config.window_decorations = "RESIZE"

-- =============================================================================
-- Tab bar
-- =============================================================================

config.use_fancy_tab_bar = false -- use the retro (flat) tab bar, consistent with the color table above
config.tab_bar_at_bottom = false
config.hide_tab_bar_if_only_one_tab = false
config.show_new_tab_button_in_tab_bar = true

-- =============================================================================
-- Window padding
-- =============================================================================

config.window_padding = {
	left = 0,
	right = 0,
	top = 0,
	bottom = 0,
}

-- =============================================================================
-- Clipboard
-- OSC 52 read+write — the main reason to use WezTerm over Windows Terminal.
-- This makes "p" in Neovim (inside tmux over WSL) paste from the Windows
-- clipboard, which Windows Terminal cannot do.
-- No explicit config needed: WezTerm enables OSC 52 by default.
-- =============================================================================

-- =============================================================================
-- Miscellaneous
-- =============================================================================

config.audible_bell = "Disabled"
config.window_close_confirmation = "NeverPrompt"
config.check_for_updates = false

return config
