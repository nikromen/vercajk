dotfiles_dir := "ansible/roles/dotfiles/files/dotfiles"

# --- Testing ---

test:
    podman run --rm -v ./cli:/work:Z -w /work \
        registry.fedoraproject.org/fedora:latest \
        bash -c "dnf -y install python3-pip python3-devel && pip install poetry && poetry install --no-interaction && poetry run pytest --tb=short"

test-molecule role="dotfiles":
    podman run --rm --privileged \
        -v .:/work:Z -w /work \
        -v /run/podman/podman.sock:/run/podman/podman.sock \
        registry.fedoraproject.org/fedora:latest \
        bash -c "dnf -y install python3-pip podman ansible-core && pip install molecule molecule-podman ansible-lint testinfra && cd ansible/roles/{{role}} && molecule test"

# --- Submodule / repo management ---

pull:
    git pull --ff-only
    git submodule update --init --recursive

push:
    #!/usr/bin/env bash
    set -euo pipefail
    DOTFILES="{{dotfiles_dir}}"
    if [ -d "$DOTFILES/.git" ]; then
        cd "$DOTFILES"
        if [ -n "$(git status --porcelain)" ]; then
            echo "ERROR: dotfiles has uncommitted changes. Commit them first."
            exit 1
        fi
        UPSTREAM=$(git rev-parse @{u} 2>/dev/null || echo "")
        if [ -n "$UPSTREAM" ]; then
            LOCAL=$(git rev-parse @)
            if [ "$LOCAL" != "$UPSTREAM" ]; then
                echo "Pushing dotfiles submodule..."
                git push
            fi
        fi
        cd - >/dev/null
        if ! git diff --quiet "$DOTFILES"; then
            git add "$DOTFILES"
            git commit -m "update dotfiles submodule"
        fi
    fi
    git push

sync: pull push

commit msg:
    #!/usr/bin/env bash
    set -euo pipefail
    DOTFILES="{{dotfiles_dir}}"
    if [ -d "$DOTFILES/.git" ] && ! git diff --quiet "$DOTFILES"; then
        git add "$DOTFILES"
    fi
    git add -A
    git commit -m "{{msg}}"

dotfiles-commit msg:
    cd {{dotfiles_dir}} && git add -A && git commit -m "{{msg}}"

dotfiles-push:
    cd {{dotfiles_dir}} && git push

# --- Status / health ---

status:
    @echo "=== Main repo ==="
    @git status --short
    @echo ""
    @echo "=== Dotfiles submodule ==="
    @test ! -d {{dotfiles_dir}}/.git || (cd {{dotfiles_dir}} && git status --short)
    @echo ""
    @echo "=== Submodule sync ==="
    @git submodule status

check-health:
    #!/usr/bin/env bash
    set -euo pipefail
    DOTFILES="{{dotfiles_dir}}"
    OK=true
    if [ -d "$DOTFILES/.git" ]; then
        if [ -n "$(cd "$DOTFILES" && git status --porcelain)" ]; then
            echo "WARNING: dotfiles has uncommitted changes"
            OK=false
        fi
        cd "$DOTFILES"
        LOCAL=$(git rev-parse HEAD)
        REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "none")
        if [ "$REMOTE" != "none" ] && [ "$LOCAL" != "$REMOTE" ]; then
            echo "WARNING: dotfiles has unpushed commits"
            OK=false
        fi
        cd - >/dev/null
        EXPECTED=$(git ls-tree HEAD "$DOTFILES" | awk '{print $3}')
        ACTUAL=$(cd "$DOTFILES" && git rev-parse HEAD)
        if [ "$EXPECTED" != "$ACTUAL" ]; then
            echo "WARNING: submodule pointer out of date (run: just commit 'update dotfiles')"
            OK=false
        fi
    fi
    if [ -n "$(git status --porcelain)" ]; then
        echo "WARNING: main repo has uncommitted changes"
        OK=false
    fi
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "none")
    if [ "$REMOTE" != "none" ] && [ "$LOCAL" != "$REMOTE" ]; then
        echo "WARNING: main repo has unpushed commits"
        OK=false
    fi
    if $OK; then
        echo "All repos in good state."
    fi

# --- Hooks ---

install-hooks:
    pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type post-merge

# --- Kickstart / deployment ---

kickstart *ARGS:
    vercajk image kickstart {{ARGS}}

iso *ARGS:
    vercajk image iso {{ARGS}}
