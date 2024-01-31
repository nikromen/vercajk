if test $HOME/.config/fish/conf.d/aliases
    source $HOME/.config/fish/conf.d/aliases
end

if test $HOME/.config/fish/conf.d/variables
    source $HOME/.config/fish/conf.d/variables
end

if status is-interactive
    if test $HOME/.config/fish/functions/custom_interactive_functions.fish
        source $HOME/.config/fish/functions/custom_interactive_functions.fish
    end
end

if test $HOME/.config/fish/functions/custom_functions.fish
    source $HOME/.config/fish/functions/custom_functions.fish
end

if test $HOME/.config/fish/functions/call_in_bash_scripts.fish
    source $HOME/.config/fish/functions/call_in_bash_scripts.fish
end
