return {
    {
        "nvim-telescope/telescope-ui-select.nvim",
    },
    {
        "nvim-telescope/telescope.nvim",
        dependencies = { "nvim-lua/plenary.nvim" },
        config = function()
            require("telescope").setup({
                extensions = {
                    ["ui-select"] = {
                        require("telescope.themes").get_dropdown({}),
                    },
                },
                pickers = {
                    find_files = {
                        find_command = { 'rg', '--files', '--iglob', '!.git', '--hidden' },
                    },
                    grep_string = {
                        additional_args = {'--hidden'}
                    },
                    live_grep = {
                        additional_args = {'--hidden'}
                    },
                },
            })
            local builtin = require("telescope.builtin")
            vim.keymap.set("n", "<C-p>", builtin.find_files, { desc = "Find Files" })
            vim.keymap.set("n", "<C-f>", builtin.live_grep, { desc = "Live Grep" })
            vim.keymap.set("n", "<leader>ft", builtin.help_tags, { desc = "Find Help Tags" })
            vim.keymap.set("n", "<leader>fgc", builtin.git_commits, { desc = "Find Git Commits" })
            vim.keymap.set("n", "<leader>fgs", builtin.git_stash, { desc = "Find Git Stash" })
            require("telescope").load_extension("ui-select")
        end,
    },
}
