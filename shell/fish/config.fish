if status is-interactive
    # Commands to run in interactive sessions can go here
end


source ~/.config/shell/aliases


# every mym local thingy for fish starts with __loc_fish prefix


function fish_greeting
end


function __loc_fish_bind_bashes_bang_bang
    switch (commandline -t)[-1]
        case "!"
            commandline -t -- $history[1]
            commandline -f repaint
        case "*"
            commandline -i !
    end
end


function __loc_fish_git_branch
    set -l bryellow $(set_color bryellow)
    set -l normal $(set_color normal)
    set -l branch ""

    if [ "$(fish_git_prompt)" != "" ]
        set branch "$bryellow$(fish_git_prompt)$normal"
    end

    echo $branch
end


function __loc_fish_error_status
    set -l last_status $argv[1]
    set -l red $(set_color --bold red)
    set -l error_str \
        $(__fish_print_pipestatus "[" "]" "|" "$red" "$red" "$last_status")
    if [ "$error_str" != "" ]
        echo " $error_str"
    else
        echo ""
    end
end


function __loc_fish_concat_prompt
    set -l last_status $argv[1]
    set -l last_dir $argv[2]
    set -l newline_flag "false"

    set -l base "[$USER@$HOSTNAME $last_dir]"
    set -l git_branch "$(__loc_fish_git_branch)"
    set -l error_status "$(__loc_fish_error_status $last_status)"
    if [ $(string length --visible "$base$git_branch$error_status") -gt 44 ]
        set newline_flag "true"
    end

    echo -n "$base"
    echo -n "$git_branch"
    echo -n "$error_status"
    if [ $newline_flag = "true" ]
        echo " ↴"
    end
end


function fish_user_key_bindings
    bind "!" __loc_fish_bind_bashes_bang_bang
end


function fish_prompt
    set -l last_status "$pipestatus[-1]"
    set -l suffix "\$"

    set -l last_dir "~"
    if [ "$(pwd)" != "$HOME" ]
        set last_dir $(basename $(pwd))
    end

    __loc_fish_concat_prompt "$last_status" "$last_dir"
    echo "$suffix "
end
