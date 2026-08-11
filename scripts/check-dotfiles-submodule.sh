#!/usr/bin/env bash
#
# Usage: check-dotfiles-submodule.sh <uncommitted|unpushed|pointer|remote>
set -euo pipefail

DOTFILES="ansible/roles/dotfiles/files/dotfiles"
DOTFILES_URL="https://github.com/nikromen/dotfiles.git"
ACTION="${1:?usage: $0 <uncommitted|unpushed|pointer|remote>}"

# "remote" only needs the recorded git tree entry, not a local checkout of
# the submodule (relevant in CI, which never inits submodules), so it's
# handled before the checkout guard below.
if [ "$ACTION" = "remote" ]; then
    EXPECTED=$(git ls-tree HEAD "$DOTFILES" | awk '{print $3}')
    ACTUAL=$(git ls-remote "$DOTFILES_URL" refs/heads/main | awk '{print $1}')
    if [ -n "$EXPECTED" ] && [ "$EXPECTED" != "$ACTUAL" ]; then
        echo "dotfiles submodule pointer is not tracking tip of main. Run: just pull && just commit '<msg>'"
        exit 1
    fi
    exit 0
fi

if [ ! -e "$DOTFILES/.git" ]; then
    exit 0
fi

case "$ACTION" in
    uncommitted)
        if [ -n "$(cd "$DOTFILES" && git status --porcelain)" ]; then
            echo "dotfiles has uncommitted changes. Run: just dotfiles-commit '<msg>'"
            exit 1
        fi
        ;;
    unpushed)
        LOCAL=$(cd "$DOTFILES" && git rev-parse HEAD)
        REMOTE=$(cd "$DOTFILES" && git rev-parse "@{u}" 2>/dev/null || echo "")
        if [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
            echo "dotfiles has unpushed commits. Run: just dotfiles-push"
            exit 1
        fi
        ;;
    pointer)
        EXPECTED=$(git ls-tree HEAD "$DOTFILES" | awk '{print $3}')
        if [ -n "$EXPECTED" ]; then
            ACTUAL=$(cd "$DOTFILES" && git rev-parse HEAD)
            if [ "$EXPECTED" != "$ACTUAL" ]; then
                echo "submodule pointer out of date. Run: just commit '<msg>'"
                exit 1
            fi
        fi
        ;;
    *)
        echo "unknown action: $ACTION" >&2
        exit 2
        ;;
esac
