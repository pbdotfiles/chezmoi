set showmode
set clipboard+=unnamed
set cursorline
set ignorecase
set smartcase
set number relativenumber
set scrolloff=12

if executable('tmux')
	augroup Yank
		autocmd!
		autocmd TextYankPost * if v:event.operator is 'y' && v:event.regname is '' | call system('tmux', 'load-buffer', '-') | endif
	augroup end
endif

