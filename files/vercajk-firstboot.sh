#!/bin/bash
set -euo pipefail
LOGFILE="/var/log/vercajk-firstboot.log"
exec > >(tee -a "$LOGFILE") 2>&1
echo "=== Vercajk first-boot provisioning started at $(date) ==="

if [ -z "${VERCAJK_USER:-}" ]; then
    TARGET_USER=$(getent group wheel | cut -d: -f4 | cut -d, -f1)
    if [ -z "$TARGET_USER" ]; then
        echo "ERROR: No user found in wheel group and VERCAJK_USER not set"
        exit 1
    fi
else
    TARGET_USER="$VERCAJK_USER"
fi

REPO_URL="https://github.com/nikromen/vercajk"
CLONE_DIR="/srv/shared-documents/git-repos/vercajk"

usermod -aG shared-documents "$TARGET_USER" 2>/dev/null || true
mkdir -p "$(dirname "$CLONE_DIR")"
if [ ! -d "$CLONE_DIR" ]; then
    git clone --recursive "$REPO_URL" "$CLONE_DIR"
else
    cd "$CLONE_DIR"
    git pull --ff-only
    git submodule update --init --recursive
fi

if ! git -C "$CLONE_DIR" verify-commit HEAD 2>/dev/null; then
    echo "WARNING: HEAD commit is not signed by a trusted GPG/SSH key"
    echo "ERROR: Please import the signing key into the keyring"
    exit 1
fi
chown -R :shared-documents "$CLONE_DIR"
su - "$TARGET_USER" -c "git config --global --add safe.directory $CLONE_DIR"

cat > /etc/vercajk.yaml << EOF
repo_path: $CLONE_DIR
EOF

# TODO: replace with vercajk CLI once it supports --user flag
ansible-galaxy collection install \
    -r "$CLONE_DIR/ansible/collections/requirements.yml"

ansible-playbook -i localhost, -c local \
    -e "target_user=$TARGET_USER" \
    "$CLONE_DIR/ansible/play_one_timers.yml"

ansible-playbook -i localhost, -c local \
    -e "target_user=$TARGET_USER" \
    "$CLONE_DIR/ansible/play_dotfiles.yml"

echo "=== Provisioning complete at $(date) ==="
rm -f /etc/vercajk-firstboot
systemctl disable vercajk-firstboot.service
rm -f /etc/systemd/system/vercajk-firstboot.service
rm -f /usr/local/bin/vercajk-firstboot.sh
systemctl daemon-reload
echo "=== Self-cleanup done ==="
