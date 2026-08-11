"""Testinfra tests for one_timers role."""

import pytest

TEST_USERS = ["testuser", "testuser2"]


@pytest.mark.parametrize("user", TEST_USERS)
def test_documents_dirs_exist(host, user):
    """Verify basic document directories are created for every target user."""
    dirs = ["work", "personal", "git", "rpm"]
    for d in dirs:
        path = host.file(f"/home/{user}/Documents/{d}")
        assert path.exists
        assert path.is_directory


@pytest.mark.parametrize("user", TEST_USERS)
def test_git_forge_dirs(host, user):
    """Verify git forge directories are created for every target user."""
    forges = ["github", "gitlab", "pagure", "distgit"]
    for forge in forges:
        path = host.file(f"/home/{user}/Documents/git/{forge}")
        assert path.exists
        assert path.is_directory


def test_firewall_ssh_allowed(host):
    """Verify SSH is allowed through firewall (machine-wide, runs once)."""
    cmd = host.run("firewall-cmd --list-services")
    if cmd.rc == 0:
        assert "ssh" in cmd.stdout


@pytest.mark.parametrize("user", TEST_USERS)
def test_tmux_plugin_dir(host, user):
    """Verify tmux plugin manager directory exists for every target user."""
    path = host.file(f"/home/{user}/.local/share/tmux/plugins/tpm")
    assert path.exists
    assert path.is_directory


@pytest.mark.parametrize("user", TEST_USERS)
def test_user_in_mock_group(host, user):
    """Verify every target user was added to the mock group."""
    cmd = host.run(f"id -nG {user}")
    assert cmd.rc == 0
    assert "mock" in cmd.stdout.split()
