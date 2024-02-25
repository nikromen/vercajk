import os
import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional


@contextmanager
def get_temporary_dir(permissions: Optional[int] = None) -> Iterator[Path]:
    temp_dir = Path(tempfile.mkdtemp())
    if permissions:
        os.chmod(temp_dir, permissions)
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


def find_fst_number_in_str(string: str) -> Optional[int]:
    pattern = r"\d+"
    match = re.search(pattern, string)
    if match:
        return int(match[0])
    return None


def get_mime(path: Path) -> str:
    process = subprocess.run(
        ["file", "-b", "--mime-type", str(path)], capture_output=True, text=True
    )
    return process.stdout.split()[-1].strip()
