#!/bin/bash
set -euo pipefail
LOGFILE="/var/log/vercajk-firstboot.log"
exec > >(tee -a "$LOGFILE") 2>&1
echo "=== Vercajk first-boot provisioning started at $(date) ==="

# Comma-separated string -> YAML list, e.g. "alice,bob" -> ["alice", "bob"].
to_yaml_list() {
    local csv="$1"
    if [ -z "$csv" ]; then
        echo "[]"
        return
    fi
    local items=()
    IFS=',' read -ra items <<< "$csv"
    local out="["
    local first=true
    for item in "${items[@]}"; do
        if [ "$first" = true ]; then first=false; else out+=", "; fi
        out+="\"$item\""
    done
    out+="]"
    echo "$out"
}

if [ -z "${VERCAJK_USERS:-}" ]; then
    echo "ERROR: VERCAJK_USERS not set (comma-separated list of users to provision)"
    exit 1
fi
TARGET_USERS="$VERCAJK_USERS"

REPO_URL="https://github.com/nikromen/vercajk"
CLONE_DIR="/srv/shared-documents/git-repos/vercajk"

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

cat > /etc/vercajk.yaml << EOF
repo_path: $CLONE_DIR
target_users: $(to_yaml_list "$TARGET_USERS")
tags: $(to_yaml_list "${VERCAJK_TAGS:-}")
skip_tags: $(to_yaml_list "${VERCAJK_SKIP_TAGS:-}")
EOF

ansible-galaxy collection install \
    -r "$CLONE_DIR/ansible/collections/requirements.yml"


vercajk ansible one-timers
vercajk ansible dotfiles

echo "=== Provisioning complete at $(date) ==="
rm -f /etc/vercajk-firstboot
systemctl disable vercajk-firstboot.service
rm -f /etc/systemd/system/vercajk-firstboot.service
rm -f /usr/local/bin/vercajk-firstboot.sh
systemctl daemon-reload
echo "=== Self-cleanup done ==="
