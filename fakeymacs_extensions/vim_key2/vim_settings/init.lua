vim.opt.title = true
vim.opt.hidden = true
vim.opt.number = true
vim.opt.ambiwidth = "double"
vim.opt.selection = "exclusive"
vim.opt.virtualedit = "onemore"
vim.opt.whichwrap = "b", "s", "h", "l", "<", ">", "[", "]"
vim.opt.incsearch = true

vim.keymap.set("i", "<C-j>", "<C-o>")

vim.api.nvim_create_autocmd("VimLeave", {
  callback = function()
    os.execute("echo -ne '\\033]0;\\007'")
  end,
})

local function MyMode()
  local m = vim.fn.mode(1)

  -- Insert Normal モードはすべて "i"
  if m:match("^ni") then
    return "i"
  end

  -- Operator-pending はすべて "no"
  if m:match("^no") then
    return "no"
  end

  -- Select モードはすべて "s"
  if m == "s" or m == "S" or m == "\19" then  -- \19 = CTRL-S
    return "s"
  end

  -- Visual モードはすべて "v"
  if m == "v" or m == "V" or m == "\22" then  -- \22 = CTRL-V
    return "v"
  end

  return m
end

_G.MyMode = MyMode

vim.opt.titlestring = "%f - nvim [%{v:lua.MyMode()}]"

vim.api.nvim_create_autocmd({"ModeChanged"}, {
  callback = function()
    vim.opt.titlestring = vim.opt.titlestring:get()
    vim.cmd("redraw")
  end,
})
