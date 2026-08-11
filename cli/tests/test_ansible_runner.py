from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from vercajk.core.ansible import (
    AnsibleObj,
    apply_config_defaults,
    resolve_inventory,
    run_ansible_playbook,
    setup_ansible_cmd,
)
from vercajk.core.config import Config
from vercajk.core.exceptions import VercajkAnsibleException


class TestAnsibleObj:
    def test_defaults(self):
        obj = AnsibleObj()
        assert obj.verbose == ""
        assert obj.tags == []
        assert obj.skip_tags == []
        assert obj.users == []
        assert obj.extra_vars == {}


class TestApplyConfigDefaults:
    def test_fills_tags_from_config_when_empty(self, tmp_path: Path):
        config = Config(repo_path=tmp_path, tags=["desktop"], skip_tags=["games"])
        obj = AnsibleObj()
        apply_config_defaults(obj, config)
        assert obj.tags == ["desktop"]
        assert obj.skip_tags == ["games"]

    def test_explicit_cli_tags_override_config(self, tmp_path: Path):
        config = Config(repo_path=tmp_path, tags=["desktop"], skip_tags=["games"])
        obj = AnsibleObj(tags=["rpm"], skip_tags=["multimedia"])
        apply_config_defaults(obj, config)
        assert obj.tags == ["rpm"]
        assert obj.skip_tags == ["multimedia"]

    def test_target_users_default_from_config(self, tmp_path: Path):
        config = Config(repo_path=tmp_path, target_users=["alice", "bob"])
        obj = AnsibleObj()
        apply_config_defaults(obj, config)
        assert obj.extra_vars["target_users"] == ["alice", "bob"]

    def test_cli_users_override_config(self, tmp_path: Path):
        config = Config(repo_path=tmp_path, target_users=["alice", "bob"])
        obj = AnsibleObj(users=["carol"])
        apply_config_defaults(obj, config)
        assert obj.extra_vars["target_users"] == ["carol"]


class TestResolveInventory:
    def test_returns_inventory_path_under_repo(self, tmp_path: Path):
        assert resolve_inventory(tmp_path) == tmp_path / "inventory"


class TestSetupAnsibleCmd:
    def test_basic_command(self):
        obj = AnsibleObj()
        cmd = setup_ansible_cmd(obj)
        assert cmd == ["ansible-playbook", "-i", "localhost,", "-c", "local"]

    def test_with_verbose(self):
        obj = AnsibleObj(verbose="-vv")
        cmd = setup_ansible_cmd(obj)
        assert "-vv" in cmd

    def test_with_tags(self):
        obj = AnsibleObj(tags=["development_tools", "games"])
        cmd = setup_ansible_cmd(obj)
        assert "--tags=development_tools,games" in cmd

    def test_with_skip_tags(self):
        obj = AnsibleObj(skip_tags=["games"])
        cmd = setup_ansible_cmd(obj)
        assert "--skip-tags=games" in cmd

    def test_with_extra_vars_list(self):
        obj = AnsibleObj(extra_vars={"target_users": ["alice", "bob"]})
        cmd = setup_ansible_cmd(obj)
        assert "-e" in cmd
        assert 'target_users=["alice", "bob"]' in cmd

    def test_with_extra_vars_string(self):
        obj = AnsibleObj(extra_vars={"profile": "desktop"})
        cmd = setup_ansible_cmd(obj)
        assert "-e" in cmd
        assert "profile=desktop" in cmd

    def test_with_inventory(self, tmp_path: Path):
        obj = AnsibleObj()
        inv = tmp_path / "inventory"
        inv.write_text("[local]\nlocalhost\n")
        cmd = setup_ansible_cmd(obj, inventory=inv)
        assert "-i" in cmd
        assert str(inv) in cmd

    def test_without_inventory_uses_localhost(self):
        obj = AnsibleObj()
        cmd = setup_ansible_cmd(obj)
        assert "-i" in cmd
        assert "localhost," in cmd
        assert "-c" in cmd
        assert "local" in cmd

    def test_all_options(self, tmp_path: Path):
        obj = AnsibleObj(verbose="-v", tags=["rpm"], skip_tags=["games"])
        inv = tmp_path / "inventory"
        inv.write_text("[local]\nlocalhost\n")
        cmd = setup_ansible_cmd(obj, inventory=inv)
        assert cmd[0] == "ansible-playbook"
        assert "-i" in cmd
        assert "-v" in cmd
        assert "--tags=rpm" in cmd
        assert "--skip-tags=games" in cmd


class TestRunAnsiblePlaybook:
    def test_missing_playbook_raises(self, tmp_path: Path):
        with pytest.raises(VercajkAnsibleException, match="Playbook not found"):
            run_ansible_playbook(["ansible-playbook"], tmp_path / "nonexistent.yml")

    def test_successful_run(self, tmp_path: Path):
        playbook = tmp_path / "test.yml"
        playbook.write_text("---\n")
        with patch("subprocess.run") as mock_run:
            run_ansible_playbook(["ansible-playbook"], playbook)
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert call_args[-1] == str(playbook)
