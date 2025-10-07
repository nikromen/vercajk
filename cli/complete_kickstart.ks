#version=F42
# This is a generated kickstart file for vercajk installation
# # No specific tags provided - full installation
# 
# Basic system configuration
keyboard --xlayouts='us','cz (qwerty)'
lang en_US.UTF-8

# Set locales
keyboard --xlayouts='us','cz (qwerty)'
lang en_US.UTF-8
timezone Europe/Prague --utc

# Disk partitioning - automatic
autopart
clearpart --none --initlabel

# Network configuration
network --hostname=vercajk-system --bootproto=dhcp --device=link --activate

# Boot loader configuration
bootloader --append="quiet console=tty0 console=ttyS0,115200n8 GRUB_DISABLE_OS_PROBER=false GRUB_TERMINAL_OUTPUT=console"

# Default user configuration
rootpw --plaintext fedora
user --name=nikromen --groups=wheel --password=fedora --plaintext --gecos="nikromen"

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

# Can stand on base desktop
@kde-desktop

# Development tools
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

# This tool itself
vercajk-cli

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
groupadd shared-documents
mkdir -p /srv/shared-documents
chown :shared-documents /srv/shared-documents
chmod 2770 /srv/shared-documents
setfacl -d -m g:shared-documents:rwx /srv/shared-documents
setfacl -m g:shared-documents:rwx /srv/shared-documents

# RPM Fusion
dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
dnf -y install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

dnf -y upgrade --refresh

# Enable required COPR repositories
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

# All the necessarry default desktop apps for nice desktop experience
flatpak install -y flathub \
    com.bitwarden.desktop \
    org.keepassxc.KeePassXC \
    com.github.tchx84.Flatseal \
    org.gnome.Firmware \
    com.gitlab.bitseater.meteo \
    dev.heppen.webapps \
    org.kde.ark \
    io.github.giantpinkrobots.flatsweep \
    org.kde.isoimagewriter \
    org.kde.kcalc \
    org.videolan.VLC \
    org.kde.gwenview \
    org.kde.okular \
    org.mozilla.firefox

# Configure VS Code repository
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

flatpak install -y flathub \
    rest.insomnia.Insomnia \
    io.podman_desktop.PodmanDesktop \
    io.qt.Designer \
    com.jgraph.drawio.desktop

# Install communication apps
flatpak install -y flathub \
    com.sindresorhus.Caprine \
    com.discordapp.Discord \
    org.signal.Signal \
    org.telegram.desktop \
    im.riot.Riot  # element

# Install multimedia apps
flatpak install -y flathub \
    com.spotify.Client \
    org.gimp.GIMP \
    com.github.johnfactotum.Foliate  # ebook reader

# Install games
flatpak install -y flathub \
    com.valvesoftware.Steam \
    org.prismlauncher.PrismLauncher \
    net.lutris.Lutris

# Install productivity apps
flatpak install -y flathub \
    org.libreoffice.LibreOffice \
    org.mozilla.Thunderbird

dnf -y copr enable nikromen/vercajk
dnf -y install vercajk

%end