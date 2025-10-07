#version=F42

keyboard --xlayouts='us','cz (qwerty)'
lang en_US.UTF-8

autopart
clearpart --none --initlabel

timezone Europe/Prague --utc

rootpw --plaintext fedora
user --name=nikromen --groups=wheel --password=fedora --plaintext --gecos="nikromen"

shutdown

%packages
@^custom-environment
hyprland
%end
