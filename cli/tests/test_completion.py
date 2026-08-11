from __future__ import annotations

import os
from unittest.mock import patch

from click.testing import CliRunner

from vercajk.cli.base import vercajk_cli


class TestCompletionCommand:
    def setup_method(self):
        self.runner = CliRunner()

    def test_explicit_bash_shell(self):
        result = self.runner.invoke(vercajk_cli, ["completion", "--shell", "bash"])
        assert result.exit_code == 0
        assert "_VERCAJK_COMPLETE=bash_source vercajk" in result.output

    def test_explicit_fish_shell(self):
        result = self.runner.invoke(vercajk_cli, ["completion", "--shell", "fish"])
        assert result.exit_code == 0
        assert "_VERCAJK_COMPLETE=fish_source vercajk | source" in result.output

    def test_explicit_zsh_shell(self):
        result = self.runner.invoke(vercajk_cli, ["completion", "--shell", "zsh"])
        assert result.exit_code == 0
        assert "zsh_source" in result.output

    def test_autodetects_from_shell_env_var(self):
        with patch.dict(os.environ, {"SHELL": "/usr/bin/fish"}):
            result = self.runner.invoke(vercajk_cli, ["completion"])
        assert result.exit_code == 0
        assert "fish_source" in result.output

    def test_falls_back_to_bash_for_unknown_shell(self):
        with patch.dict(os.environ, {"SHELL": "/usr/bin/tcsh"}):
            result = self.runner.invoke(vercajk_cli, ["completion"])
        assert result.exit_code == 0
        assert "bash_source" in result.output

    def test_invalid_shell_choice_rejected(self):
        result = self.runner.invoke(vercajk_cli, ["completion", "--shell", "tcsh"])
        assert result.exit_code != 0
