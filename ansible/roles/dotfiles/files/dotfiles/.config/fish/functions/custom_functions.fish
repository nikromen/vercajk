function call_in_bash
    if test -f ~/.bash_profile
        exec bash -c "source ~/.bash_profile; $argv[1] $argv[2..-1]; exec fish"
    else
        exec bash -c "$argv[1] $argv[2..-1]; exec fish"
    end
end
