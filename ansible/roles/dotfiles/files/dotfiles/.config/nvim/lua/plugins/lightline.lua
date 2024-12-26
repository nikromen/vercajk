return {
    {
        "itchyny/lightline.vim",
        config = function()
            vim.g.lightline = {
                active = {
                    left = {
                        { "mode", "paste" },
                        { "gitbranch", "readonly", "filename", "modified" }
                    },
                    right = {
                        { "lineinfo" },
                        { "percent" },
                        { "fileencoding", "filetype" }
                    }
                },
                component_function = {
                    gitbranch = "FugitiveHead",
                }
            }
        end
    }
}
