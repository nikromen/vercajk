function call_in_bash
    bash -c "source ~/.bash_profile; $argv[1] $argv[2..-1]; fish"
    exit
end
