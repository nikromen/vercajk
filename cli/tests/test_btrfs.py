from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vercajk.core.btrfs import (
    SnapshotMeta,
    create_snapshot,
    delete_snapshot,
    get_snapshot_meta,
    is_btrfs,
    maybe_create_snapshot,
    revert_snapshot,
)
from vercajk.core.exceptions import VercajkSnapshotException


def _run_result(returncode: int = 0, stdout: str = "") -> MagicMock:
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    return result


class TestSnapshotMeta:
    def test_to_json_from_json_roundtrip(self, tmp_path: Path):
        meta = SnapshotMeta(commit="abc123", timestamp="2024-01-01T00:00:00", tags=["rpm"])
        path = tmp_path / "meta.json"
        path.write_text(meta.to_json())

        loaded = SnapshotMeta.from_json(path)
        assert loaded == meta

    def test_from_json_missing_tags_defaults_empty(self, tmp_path: Path):
        path = tmp_path / "meta.json"
        path.write_text('{"commit": "abc", "timestamp": "now"}')

        loaded = SnapshotMeta.from_json(path)
        assert loaded.tags == []


class TestIsBtrfs:
    def test_true_when_btrfs(self):
        with patch("vercajk.core.btrfs.subprocess.run", return_value=_run_result(0, "btrfs\n")):
            assert is_btrfs("/") is True

    def test_false_when_not_btrfs(self):
        with patch("vercajk.core.btrfs.subprocess.run", return_value=_run_result(0, "ext4\n")):
            assert is_btrfs("/") is False

    def test_false_when_command_fails(self):
        with patch("vercajk.core.btrfs.subprocess.run", return_value=_run_result(1, "")):
            assert is_btrfs("/") is False


class TestCreateSnapshot:
    def test_raises_if_root_not_btrfs(self, tmp_path: Path):
        with patch("vercajk.core.btrfs.is_btrfs", return_value=False):
            with pytest.raises(VercajkSnapshotException, match="not Btrfs"):
                create_snapshot(tmp_path)

    def test_creates_root_and_home_when_both_btrfs(self, tmp_path: Path):
        with (
            patch("vercajk.core.btrfs.is_btrfs", return_value=True),
            patch("vercajk.core.btrfs._ensure_snapshot_dirs"),
            patch("vercajk.core.btrfs._snapshot_exists", return_value=False),
            patch("vercajk.core.btrfs._create_snapshot") as mock_create,
            patch("vercajk.core.btrfs._get_git_commit", return_value="deadbeef"),
            patch("vercajk.core.btrfs.subprocess.run", return_value=_run_result(0)),
        ):
            meta = create_snapshot(tmp_path, tags=["rpm"])

        assert mock_create.call_count == 2
        assert meta.commit == "deadbeef"
        assert meta.tags == ["rpm"]

    def test_skips_home_when_home_not_btrfs(self, tmp_path: Path):
        def fake_is_btrfs(mountpoint="/"):
            return mountpoint == "/"

        with (
            patch("vercajk.core.btrfs.is_btrfs", side_effect=fake_is_btrfs),
            patch("vercajk.core.btrfs._ensure_snapshot_dirs"),
            patch("vercajk.core.btrfs._snapshot_exists", return_value=False),
            patch("vercajk.core.btrfs._create_snapshot") as mock_create,
            patch("vercajk.core.btrfs._get_git_commit", return_value="abc"),
            patch("vercajk.core.btrfs.subprocess.run", return_value=_run_result(0)),
        ):
            create_snapshot(tmp_path)

        assert mock_create.call_count == 1

    def test_deletes_existing_snapshot_first(self, tmp_path: Path):
        with (
            patch("vercajk.core.btrfs.is_btrfs", return_value=True),
            patch("vercajk.core.btrfs._ensure_snapshot_dirs"),
            patch("vercajk.core.btrfs._snapshot_exists", return_value=True),
            patch("vercajk.core.btrfs.delete_snapshot") as mock_delete,
            patch("vercajk.core.btrfs._create_snapshot"),
            patch("vercajk.core.btrfs._get_git_commit", return_value="abc"),
            patch("vercajk.core.btrfs.subprocess.run", return_value=_run_result(0)),
        ):
            create_snapshot(tmp_path)

        mock_delete.assert_called_once()

    def test_defaults_tags_to_empty_list(self, tmp_path: Path):
        with (
            patch("vercajk.core.btrfs.is_btrfs", return_value=True),
            patch("vercajk.core.btrfs._ensure_snapshot_dirs"),
            patch("vercajk.core.btrfs._snapshot_exists", return_value=False),
            patch("vercajk.core.btrfs._create_snapshot"),
            patch("vercajk.core.btrfs._get_git_commit", return_value="abc"),
            patch("vercajk.core.btrfs.subprocess.run", return_value=_run_result(0)),
        ):
            meta = create_snapshot(tmp_path)

        assert meta.tags == []


class TestDeleteSnapshot:
    def test_raises_if_no_snapshot_exists(self):
        with patch("vercajk.core.btrfs._snapshot_exists", return_value=False):
            with pytest.raises(VercajkSnapshotException, match="No vercajk snapshot"):
                delete_snapshot()

    def test_deletes_root_and_home(self):
        with (
            patch("vercajk.core.btrfs._snapshot_exists", return_value=True),
            patch("vercajk.core.btrfs._delete_snapshot") as mock_delete,
        ):
            delete_snapshot()

        assert mock_delete.call_count == 2


class TestGetSnapshotMeta:
    def test_returns_none_when_no_meta_file(self, tmp_path: Path):
        with patch("vercajk.core.btrfs._ROOT_SNAPSHOTS_DIR", tmp_path):
            assert get_snapshot_meta() is None

    def test_returns_meta_when_file_exists(self, tmp_path: Path):
        meta_path = tmp_path / "vercajk-pre.meta"
        meta_path.write_text(SnapshotMeta(commit="abc", timestamp="now", tags=[]).to_json())

        with patch("vercajk.core.btrfs._ROOT_SNAPSHOTS_DIR", tmp_path):
            meta = get_snapshot_meta()

        assert meta is not None
        assert meta.commit == "abc"

    def test_returns_none_on_corrupt_json(self, tmp_path: Path):
        meta_path = tmp_path / "vercajk-pre.meta"
        meta_path.write_text("not json")

        with patch("vercajk.core.btrfs._ROOT_SNAPSHOTS_DIR", tmp_path):
            assert get_snapshot_meta() is None


class TestRevertSnapshot:
    def test_raises_if_no_snapshot_exists(self):
        with patch("vercajk.core.btrfs._snapshot_exists", return_value=False):
            with pytest.raises(VercajkSnapshotException, match="No vercajk snapshot"):
                revert_snapshot()

    def test_success_path_returns_instructions(self):
        def fake_run(cmd, **kwargs):
            if "show" in cmd:
                return _run_result(0, "Subvolume ID: 257\nOther: stuff\n")
            if cmd[0] == "findmnt":
                return _run_result(0, "/dev/sda2[/subvol]\n")
            if "get-default" in cmd:
                return _run_result(0, "ID 5 gen 100 top level 5 path <FS_TREE>\n")
            return _run_result(0)

        with (
            patch("vercajk.core.btrfs._snapshot_exists", return_value=True),
            patch("vercajk.core.btrfs.subprocess.run", side_effect=fake_run),
        ):
            message = revert_snapshot()

        assert "257" in message
        assert "/dev/sda2" in message
        assert "Reboot" in message

    def test_raises_if_subvolume_id_not_found(self):
        def fake_run(cmd, **kwargs):
            return _run_result(0, "no useful output here\n")

        with (
            patch("vercajk.core.btrfs._snapshot_exists", return_value=True),
            patch("vercajk.core.btrfs.subprocess.run", side_effect=fake_run),
        ):
            with pytest.raises(VercajkSnapshotException, match="Could not determine"):
                revert_snapshot()


class TestMaybeCreateSnapshot:
    def test_noop_when_auto_snapshot_false(self, tmp_path: Path):
        with patch("vercajk.core.btrfs.create_snapshot") as mock_create:
            maybe_create_snapshot(tmp_path, [], auto_snapshot=False)
        mock_create.assert_not_called()

    def test_warns_when_not_btrfs(self, tmp_path: Path):
        with patch("vercajk.core.btrfs.is_btrfs", return_value=False):
            # Should not raise, just warn on stderr.
            maybe_create_snapshot(tmp_path, [], auto_snapshot=True)

    def test_creates_snapshot_when_possible(self, tmp_path: Path):
        meta = SnapshotMeta(commit="abc", timestamp="now", tags=[])
        with (
            patch("vercajk.core.btrfs.is_btrfs", return_value=True),
            patch("vercajk.core.btrfs.create_snapshot", return_value=meta) as mock_create,
        ):
            maybe_create_snapshot(tmp_path, ["rpm"], auto_snapshot=True)
        mock_create.assert_called_once_with(tmp_path, tags=["rpm"])

    def test_warns_on_snapshot_exception(self, tmp_path: Path):
        with (
            patch("vercajk.core.btrfs.is_btrfs", return_value=True),
            patch(
                "vercajk.core.btrfs.create_snapshot",
                side_effect=VercajkSnapshotException("boom"),
            ),
        ):
            # Should not propagate, just warn.
            maybe_create_snapshot(tmp_path, [], auto_snapshot=True)
