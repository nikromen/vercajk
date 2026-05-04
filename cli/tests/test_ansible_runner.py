from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from vercajk.core.ansible import AnsibleObj, run_ansible_playbook, setup_ansible_cmd
from vercajk.core.exceptions import VercajkAnsibleException


class TestAnsibleObj:
    def test_defaults(self):
        obj = AnsibleObj()
        assert obj.verbose == ""
        assert obj.tags == []
        assert obj.skip_tags == []


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
