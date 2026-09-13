set nocompatible
set title
set hidden
set number
set ambiwidth=double
set selection=exclusive
set virtualedit=onemore
set whichwrap=b,s,h,l,<,>,[,]
set incsearch
set ttimeout
set ttimeoutlen=50

inoremap <C-j> <C-o>

function! MyMode()
  let m = mode(1)

  " Insert Normal モードはすべて "i"
  if m =~# '^ni'
    return 'i'
  endif

  " Operator-pending はすべて "no"
  if m =~# '^no'
    return 'no'
  endif

  " Select モードはすべて "s"
  if m =~# '^[sS]' || m ==# "\<C-s>"
    return 's'
  endif

  " Visual モードはすべて "v"
  if m =~# '^[vV]' || m ==# "\<C-v>"
    return 'v'
  endif

  " その他はそのまま
  return m
endfunction

let &titlestring = "%f - vim [%{MyMode()}]"

augroup UpdateTitle
  autocmd!
  autocmd ModeChanged * let &titlestring = &titlestring | redraw
augroup END
