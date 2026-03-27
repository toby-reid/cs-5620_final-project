"""TODO"""

import subprocess
from typing import Sequence, Optional


def run_student_code(command: Sequence[str]) -> tuple[bool, tuple[str, str]]:
    """TODO"""
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode == 0:
        return True, (result.stdout, result.stderr)
    return
