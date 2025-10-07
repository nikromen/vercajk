#version=F43
# This is a generated kickstart file for vercajk installation
{% if tags is defined and tags|length > 0 %}
# This kickstart includes the following tags: {{ tags }}
{% else %}
# No specific tags provided - full installation
{% endif %}

# Basic system configuration
keyboard --xlayouts='us','cz (qwerty)'
lang en_US.UTF-8

# Set locales
keyboard --xlayouts='us','cz (qwerty)'
lang en_US.UTF-8
timezone Europe/Prague --utc

# Disk partitioning - automatic
autopart
# WARNING: THIS WILL ERASE THE DRIVE!!!
clearpart --none --initlabel

# Default user configuration
rootpw --iscrypted
user --name=nikromen --groups=wheel --gecos="nikromen"

# Enable basic services
services --enabled="NetworkManager,sshd,firewalld,tuned"

# Run the Setup Agent on first boot
firstboot --disabled

# Reboot after installation
reboot

# Package selection
%packages

# Core system packages
@core
@hardware-support
glibc-langpack-en
glibc-langpack-cs
htop
lm_sensors
alacritty
fzf
cronie
btop
tree
stow
tmux
firewalld
neovim

{% if "desktop" in tags|default([]) or not tags|default([]) %}
@fonts
@networkmanager-submodules
@multimedia
fish
lua
openconnect
openvpn
fastfetch
tuned
tuned-ppd
flatpak
ocrmypdf
ffmpeg-free
adw-gtk3-theme
mediawriter
fontawesome-fonts

# Hyprland - base of the desktop
hyprland
rofi                    # launcher
wlogout                 # logout manager
pavucontrol             # audio +- control
wireplumber             # audio routing
polkit                  # authorization service
polkit-kde              # gui for polkit
playerctl               # media player control
blueman                 # bluetooth manager
brightnessctl           # screen brightness control
flameshot               # screenshot tool
copyq                   # copy server
# TODO: do I need this when I have copyq?
wl-clipboard            # clipboard manager for wayland
jq                      # json processor for my scripts
bc                      # calculator for my scripts
libnotify               # notification send/recv
waybar                  # static bar
hyprland-devel          # for plugins
network-manager-applet  # nmcli tray
SwayNotificationCenter  # another cool notification center
{% endif %}

# Can stand on base desktop
{% if "kde" in tags|default([]) or not tags|default([]) %}
@kde-desktop
{% endif %}

# Development tools
{% if "development_tools" in tags|default([]) or not tags|default([]) %}
# Container and virtualization
@container-management
@virtualization
docker-compose
podman-docker

# Development applications
valgrind
gdb
cppcheck
pre-commit
luarocks
cmake
make

# RPM and work related tools
@fedora-packager
copr-cli
packit
fedpkg
rpmdevtools

# Programming languages
gcc
gcc-c++
golang
rust
cargo

# Python development
python3-pip
python3-devel
krb5-devel
poetry

# VCS
git
git-subtree
git-filter-repo
{% endif %}

%end

# Post-installation scripts
%post
# Set locale variables
cat > /etc/locale.conf << EOF
LC_ADDRESS=cs_CZ.UTF-8
LC_NAME=cs_CZ.UTF-8
LC_MONETARY=cs_CZ.UTF-8
LC_TIME=cs_CZ.UTF-8
LC_NUMERIC=cs_CZ.UTF-8
LC_TELEPHONE=cs_CZ.UTF-8
LC_MEASUREMENT=cs_CZ.UTF-8
EOF

# Setup shared-documents directory for everyone in shared-documents group
{% if "multi_user" in tags|default([]) or not tags|default([]) %}
groupadd shared-documents
mkdir -p /srv/shared-documents
chown :shared-documents /srv/shared-documents
chmod 2770 /srv/shared-documents
setfacl -d -m g:shared-documents:rwx /srv/shared-documents
setfacl -m g:shared-documents:rwx /srv/shared-documents
{% endif %}

# RPM Fusion
dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
dnf -y install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

dnf -y upgrade --refresh

# Enable required COPR repositories
{% if "desktop" in tags|default([]) or not tags|default([]) %}
dnf -y copr enable che/nerd-fonts
dnf -y install nerd-fonts

# TODO: remove this once these are in fedora
dnf -y copr enable solopasha/hyprland
dnf -y install hyprsunset \  # blue light filter
    aylurs-gtk-shell \       # widgets
    swww \                   # wallpaper deamon
    hyprlock \               # lock deamon
    hypridle                 # idle daemon

# Ensure flatpak and flathub
dnf -y install flatpak
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
{% endif %}

# Configure VS Code repository
{% if "development_tools" in tags|default([]) or not tags|default([]) %}
rpm --import https://packages.microsoft.com/keys/microsoft.asc
cat > /etc/yum.repos.d/vscode.repo << EOF
[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
EOF

dnf -y copr enable phracek/PyCharm

# IDEs
dnf -y check-update || true
dnf -y install pycharm-community code
{% endif %}

# Setup the flatpak installation service for post-boot installation
# This will install all flatpak applications via ansible playbook
mkdir -p /etc/vercajk
cat > /etc/systemd/system/vercajk-flatpak.service << EOF
[Unit]
Description=Run flatpak installations via Ansible after first boot
After=network-online.target
Wants=network-online.target
ConditionPathExists=!/var/lib/vercajk/flatpak-installed

[Service]
Type=oneshot
ExecStart=/usr/bin/ansible-playbook -t flatpak /etc/vercajk/ansible/play_user.yml
ExecStartPost=/usr/bin/mkdir -p /var/lib/vercajk
ExecStartPost=/usr/bin/touch /var/lib/vercajk/flatpak-installed

[Install]
WantedBy=multi-user.target
EOF

# Enable the flatpak installation service
systemctl enable vercajk-flatpak.service

# This tool itself
{% if "vercajk" in tags|default([]) or not tags|default([]) %}
dnf -y copr enable nikromen/vercajk
dnf -y install vercajk-cli
{% endif %}

%end
