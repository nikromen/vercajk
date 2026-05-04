"""Btrfs snapshot management for system rollback."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import click

from vercajk.core.exceptions import VercajkSnapshotException

_SNAPSHOT_NAME = "vercajk-pre"
_ROOT_SNAPSHOTS_DIR = Path("/.snapshots")
_HOME_SNAPSHOTS_DIR = Path("/home/.snapshots")


@dataclass
class SnapshotMeta:
    commit: str
    timestamp: str
    tags: list[str]

    def to_json(self) -> str:
        return json.dumps(
            {"commit": self.commit, "timestamp": self.timestamp, "tags": self.tags},
            indent=2,
        )

    @classmethod
    def from_json(cls, path: Path) -> SnapshotMeta:
        data = json.loads(path.read_text())
        return cls(
            commit=data["commit"],
            timestamp=data["timestamp"],
            tags=data.get("tags", []),
        )


def is_btrfs(mountpoint: str = "/") -> bool:
    """Check if the given mountpoint is on a Btrfs filesystem."""
    result = subprocess.run(
        ["findmnt", "-n", "-o", "FSTYPE", "--target", mountpoint],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and "btrfs" in result.stdout.strip()


def _get_git_commit(repo_path: Path) -> str:
    """Get the current short git commit hash."""
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def _ensure_snapshot_dirs() -> None:
    """Create snapshot directories if they don't exist."""
    for d in (_ROOT_SNAPSHOTS_DIR, _HOME_SNAPSHOTS_DIR):
        subprocess.run(["sudo", "mkdir", "-p", str(d)], check=True)


def _snapshot_exists() -> bool:
    """Check if a vercajk snapshot currently exists."""
    root_snap = _ROOT_SNAPSHOTS_DIR / _SNAPSHOT_NAME
    return root_snap.exists()


def _delete_snapshot(snapshots_dir: Path, name: str) -> None:
    """Delete a single Btrfs subvolume snapshot."""
    snap_path = snapshots_dir / name
    meta_path = snapshots_dir / f"{name}.meta"

    if snap_path.exists():
        subprocess.run(
            ["sudo", "btrfs", "subvolume", "delete", str(snap_path)],
            check=True,
        )
    if meta_path.exists():
        subprocess.run(["sudo", "rm", "-f", str(meta_path)], check=True)


def _create_snapshot(source: str, snapshots_dir: Path, name: str) -> None:
    """Create a read-only Btrfs snapshot."""
    dest = snapshots_dir / name
    subprocess.run(
        ["sudo", "btrfs", "subvolume", "snapshot", "-r", source, str(dest)],
        check=True,
    )


def create_snapshot(repo_path: Path, tags: list[str] | None = None) -> SnapshotMeta:
    """Create a pre-update snapshot of root and home subvolumes.

    Deletes any existing vercajk snapshot first (single-snapshot pattern).
    """
    if not is_btrfs("/"):
        raise VercajkSnapshotException("Root filesystem is not Btrfs. Snapshots require Btrfs.")

    _ensure_snapshot_dirs()

    if _snapshot_exists():
        delete_snapshot()

    _create_snapshot("/", _ROOT_SNAPSHOTS_DIR, _SNAPSHOT_NAME)

    if is_btrfs("/home"):
        _create_snapshot("/home", _HOME_SNAPSHOTS_DIR, _SNAPSHOT_NAME)

    meta = SnapshotMeta(
        commit=_get_git_commit(repo_path),
        timestamp=datetime.now(timezone.utc).isoformat(),
        tags=tags or [],
    )
    meta_path = _ROOT_SNAPSHOTS_DIR / f"{_SNAPSHOT_NAME}.meta"
    subprocess.run(
        ["sudo", "tee", str(meta_path)],
        input=meta.to_json(),
        text=True,
        check=True,
        stdout=subprocess.DEVNULL,
    )

    return meta


def delete_snapshot() -> None:
    """Delete the existing vercajk snapshot (root + home)."""
    if not _snapshot_exists():
        raise VercajkSnapshotException("No vercajk snapshot exists to delete.")

    _delete_snapshot(_ROOT_SNAPSHOTS_DIR, _SNAPSHOT_NAME)
    _delete_snapshot(_HOME_SNAPSHOTS_DIR, _SNAPSHOT_NAME)


def get_snapshot_meta() -> SnapshotMeta | None:
    """Get metadata of the current snapshot, or None if no snapshot exists."""
    meta_path = _ROOT_SNAPSHOTS_DIR / f"{_SNAPSHOT_NAME}.meta"
    if not meta_path.exists():
        return None
    try:
        return SnapshotMeta.from_json(meta_path)
    except (json.JSONDecodeError, KeyError):
        return None


def revert_snapshot() -> str:
    """Set the snapshot as the default subvolume for next boot.

    Returns instructions for the user (reboot required).
    """
    if not _snapshot_exists():
        raise VercajkSnapshotException("No vercajk snapshot exists to revert to.")

    root_snap = _ROOT_SNAPSHOTS_DIR / _SNAPSHOT_NAME

    result = subprocess.run(
        ["sudo", "btrfs", "subvolume", "show", str(root_snap)],
        capture_output=True,
        text=True,
        check=True,
    )

    subvol_id = None
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("Subvolume ID:"):
            subvol_id = stripped.split(":")[-1].strip()
            break

    if not subvol_id:
        raise VercajkSnapshotException("Could not determine subvolume ID of the snapshot.")

    device = (
        subprocess.run(
            ["findmnt", "-n", "-o", "SOURCE", "--target", "/"],
            capture_output=True,
            text=True,
            check=True,
        )
        .stdout.strip()
        .split("[")[0]
    )

    prev_default = subprocess.run(
        ["btrfs", "subvolume", "get-default", "/"],
        capture_output=True,
        text=True,
    )
    prev_id = "5"
    if prev_default.returncode == 0:
        parts = prev_default.stdout.strip().split()
        if len(parts) >= 2 and parts[1].isdigit():
            prev_id = parts[1]

    subprocess.run(
        ["sudo", "btrfs", "subvolume", "set-default", subvol_id, device],
        check=True,
    )

    return (
        f"Default subvolume set to snapshot (ID {subvol_id}).\n"
        "Reboot to complete the rollback.\n"
        "After reboot, the system will be in the pre-update state.\n"
        "To return to normal boot, run:\n"
        f"  sudo btrfs subvolume set-default {prev_id} {device}"
    )


def maybe_create_snapshot(
    repo_path: Path,
    tags: list[str],
    auto_snapshot: bool,
) -> None:
    """Create a pre-update Btrfs snapshot if requested and possible."""
    if not auto_snapshot:
        return

    if not is_btrfs("/"):
        click.echo("Warning: Root is not Btrfs, skipping snapshot.", err=True)
        return

    click.echo("Creating pre-update snapshot...")
    try:
        meta = create_snapshot(repo_path, tags=tags)
        click.echo(f"  Snapshot created (commit: {meta.commit})")
    except VercajkSnapshotException as e:
        click.echo(f"Warning: Snapshot failed: {e}", err=True)
