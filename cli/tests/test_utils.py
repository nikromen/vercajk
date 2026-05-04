from __future__ import annotations

from pathlib import Path

from vercajk.core.utils import find_fst_number_in_str, get_temporary_dir, streaming_copy


class TestFindFstNumberInStr:
    def test_finds_number(self):
        assert find_fst_number_in_str("fedora-42-x86") == 42

    def test_finds_first_number(self):
        assert find_fst_number_in_str("test-1-2-3") == 1

    def test_no_number_returns_none(self):
        assert find_fst_number_in_str("no-numbers-here") is None

    def test_empty_string(self):
        assert find_fst_number_in_str("") is None


class TestGetTemporaryDir:
    def test_creates_and_cleans_up(self):
        with get_temporary_dir() as tmp:
            assert tmp.exists()
            assert tmp.is_dir()
        assert not tmp.exists()

    def test_with_permissions(self):
        with get_temporary_dir(permissions=0o755) as tmp:
            mode = tmp.stat().st_mode & 0o777
            assert mode == 0o755


class TestStreamingCopy:
    def test_copies_file(self, tmp_path: Path):
        src = tmp_path / "source.bin"
        dst = tmp_path / "dest.bin"
        content = b"hello world" * 1000
        src.write_bytes(content)

        streaming_copy(src, dst)
        assert dst.read_bytes() == content

    def test_copies_large_file_in_chunks(self, tmp_path: Path):
        src = tmp_path / "large.bin"
        dst = tmp_path / "large_copy.bin"
        content = b"x" * (1024 * 1024)  # 1MB
        src.write_bytes(content)

        streaming_copy(src, dst, chunk_size=4096)
        assert dst.read_bytes() == content
