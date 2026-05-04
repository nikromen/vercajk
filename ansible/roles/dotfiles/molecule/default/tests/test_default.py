"""Testinfra tests for dotfiles role."""


def test_bashrc_exists(host):
    """Verify .bashrc exists for the test user."""
    f = host.file("/home/testuser/.bashrc")
    assert f.exists
    assert f.mode == 0o600


def test_bashrc_sources_custom_profile(host):
    """Verify .bashrc sources the custom bash profile."""
    f = host.file("/home/testuser/.bashrc")
    assert f.exists
    assert "custom_bash_profile_merged" in f.content_string
