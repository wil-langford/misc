version 6.0
if &cp | set nocp | endif
let s:cpo_save=&cpo
set cpo&vim
nmap gx <Plug>NetrwBrowseX
nnoremap <silent> <Plug>NetrwBrowseX :call netrw#NetrwBrowseX(expand("<cWORD>"),0)
let &cpo=s:cpo_save
unlet s:cpo_save
set backspace=2
set fileencodings=ucs-bom,utf-8,default,latin1
set helplang=en
set modelines=0
set window=0
" vim: set ft=vim :

" My stuff is below -Wil
syntax on
set background=dark

set autoindent
set smartindent
set tabstop=4
set shiftwidth=4
set smarttab
set expandtab
set softtabstop=4

set guifont=DejaVu\ Sans\ Mono:h15

if has("autocmd")
  au BufReadPost * if line("'\"") > 0 && line("'\"") <= line("$")
    \| exe "normal g'\"" | endif
endif

set foldmethod=indent
set foldnestmax=2
set foldlevel=1
