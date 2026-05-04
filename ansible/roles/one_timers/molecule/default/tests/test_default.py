"""Testinfra tests for one_timers role."""


def test_documents_dirs_exist(host):
    """Verify basic document directories are created."""
    dirs = ["work", "personal", "git", "rpm"]
    for d in dirs:
        path = host.file(f"/home/testuser/Documents/{d}")
        assert path.exists
        assert path.is_directory


def test_git_forge_dirs(host):
    """Verify git forge directories are created."""
    forges = ["github", "gitlab", "pagure", "distgit"]
    for forge in forges:
        path = host.file(f"/home/testuser/Documents/git/{forge}")
        assert path.exists
        assert path.is_directory


def test_firewall_ssh_allowed(host):
    """Verify SSH is allowed through firewall."""
    cmd = host.run("firewall-cmd --list-services")
    if cmd.rc == 0:
        assert "ssh" in cmd.stdout


def test_tmux_plugin_dir(host):
    """Verify tmux plugin manager directory exists."""
    path = host.file("/home/testuser/.local/share/tmux/plugins/tpm")
    assert path.exists
    assert path.is_directory
