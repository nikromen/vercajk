from __future__ import annotations

from pathlib import Path

from vercajk.core.fish_converter import convert_scripts, convert_variables


class TestConvertVariables:
    def test_generates_variables_file(self, tmp_path: Path, tmp_repo: Path):
        bash_dir = tmp_repo / "dotfiles" / ".config" / "bash"
        bash_dir.mkdir(parents=True, exist_ok=True)
        (bash_dir / "variables").write_text('FOO="bar"\nBAZ=qux\n# comment\nINVALID_LINE\n')

        convert_variables(bash_dir, tmp_path)

        output = tmp_path / "variables" / "variables.fish"
        assert output.exists()
        content = output.read_text()
        assert "set -gx FOO bar" in content
        assert "set -gx BAZ qux" in content
        assert "INVALID_LINE" not in content
        assert "comment" not in content

    def test_no_variables_file_does_nothing(self, tmp_path: Path, tmp_repo: Path):
        bash_dir = tmp_repo / "dotfiles" / ".config" / "bash"
        bash_dir.mkdir(parents=True, exist_ok=True)
        convert_variables(bash_dir, tmp_path)
        assert not (tmp_path / "variables").exists()

    def test_empty_variables_file(self, tmp_path: Path, tmp_repo: Path):
        bash_dir = tmp_repo / "dotfiles" / ".config" / "bash"
        bash_dir.mkdir(parents=True, exist_ok=True)
        (bash_dir / "variables").write_text("")

        convert_variables(bash_dir, tmp_path)

        output = tmp_path / "variables" / "variables.fish"
        assert output.exists()
        assert output.read_text() == ""


class TestConvertScripts:
    def test_no_scripts_file_does_nothing(self, tmp_path: Path, tmp_repo: Path):
        bash_dir = tmp_repo / "dotfiles" / ".config" / "bash"
        bash_dir.mkdir(parents=True, exist_ok=True)
        convert_scripts(bash_dir, tmp_path)
        assert not (tmp_path / "call_in_bash_scripts.fish").exists()

    def test_generates_fish_wrappers(self, tmp_path: Path, tmp_repo: Path):
        bash_dir = tmp_repo / "dotfiles" / ".config" / "bash"
        bash_dir.mkdir(parents=True, exist_ok=True)
        (bash_dir / "custom_scripts").write_text(
            "#!/bin/bash\nmy_func() { echo hello; }\nanother() { echo world; }\n"
        )

        convert_scripts(bash_dir, tmp_path)

        output = tmp_path / "call_in_bash_scripts.fish"
        assert output.exists()
        content = output.read_text()
        assert "function my_func" in content
        assert "function another" in content
        assert "call_in_bash" in content

    def test_skips_underscore_functions(self, tmp_path: Path, tmp_repo: Path):
        bash_dir = tmp_repo / "dotfiles" / ".config" / "bash"
        bash_dir.mkdir(parents=True, exist_ok=True)
        (bash_dir / "custom_scripts").write_text(
            "#!/bin/bash\n_private() { :; }\npublic() { :; }\n"
        )

        convert_scripts(bash_dir, tmp_path)

        output = tmp_path / "call_in_bash_scripts.fish"
        assert output.exists()
        content = output.read_text()
        assert "_private" not in content
        assert "function public" in content
