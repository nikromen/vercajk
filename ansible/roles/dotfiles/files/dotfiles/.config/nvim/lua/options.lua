vim.cmd('syntax enable')

-- relative numbering
vim.opt.number = true
vim.opt.relativenumber = true

vim.opt.encoding = 'utf-8'
vim.opt.colorcolumn = '100'
vim.opt.laststatus = 2
vim.opt.eol = true

vim.opt.scrolloff = 8

vim.opt.updatetime = 50

vim.opt.swapfile = false
vim.opt.backup = false
vim.opt.undodir = os.getenv("HOME") .. "/.cache/nvim/undodir"
vim.opt.undofile = true

vim.opt.termguicolors = true

vim.opt.autowrite = true

-- spacing
vim.opt.tabstop = 4
vim.opt.softtabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true

vim.opt.autoindent = true
vim.opt.smartindent = true

vim.opt.fixeol = true

-- search
vim.opt.hlsearch = true
vim.opt.termguicolors = true

-- listchars
vim.opt.list = true
vim.opt.listchars = { tab = '» ', trail = '_', extends = '…', precedes = '…', nbsp = '␣' }

-- vimspector config
vim.g.vimspector_enable_mappings = 'HUMAN'

-- disable netrw at the very start of your init.lua
vim.g.loaded_netrw = 1
vim.g.loaded_netrwPlugin = 1

-- optionally enable 24-bit colour
vim.opt.termguicolors = true

vim.g.mapleader = " "
