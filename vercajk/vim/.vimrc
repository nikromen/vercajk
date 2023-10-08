syntax enable

set number relativenumber

set encoding=utf-8
set tabstop=4
set softtabstop=4
set shiftwidth=4
set autoindent
set colorcolumn=80
set laststatus=2
set eol
set hlsearch

set t_Co=256

" show trail spaces
set list
set listchars=trail:_

call plug#begin()
Plug 'itchyny/lightline.vim'
Plug 'preservim/nerdtree'
Plug 'Xuyuanp/nerdtree-git-plugin'
Plug 'Valloric/YouCompleteMe'
Plug 'luochen1990/rainbow'
Plug 'vim-syntastic/syntastic'
Plug 'puremourning/vimspector'
call plug#end()

" Start NERDTree. If a file is specified, move the cursor to its window.
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * NERDTree | if argc() > 0 || exists("s:std_in") | wincmd p | endif

" Start rainbow brackets
let g:rainbow_active = 1

" synastic configuration
set statusline+=%#warningmsg#
set statusline+=%{SyntasticStatuslineFlag()}
set statusline+=%*

let g:syntastic_always_populate_loc_list = 1
let g:syntastic_auto_loc_list = 1
let g:syntastic_check_on_open = 1
let g:syntastic_check_on_wq = 0

" vimstector config
let g:vimspector_enable_mappings = 'HUMAN'
