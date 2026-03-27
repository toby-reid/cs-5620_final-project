"""TODO"""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence, Optional

from .task import Task


@dataclass(slots=True)
class TaskEngine:
    """TODO"""

    task: Task
    start_dir: Path
    cwd: Path = field(init=False)

    def run(self, max_attempts: Optional[int] = None) -> bool:
        """TODO"""
        attempts = 0
        while max_attempts is None or attempts < max_attempts:
            if self._run():
                return True
            attempts += 1
        return False

    def _run(self) -> bool:
        """TODO"""
        self.cwd = self.start_dir
        success = False
        while not success:
            print(self.cwd)
            # Don't worry about vetting input
            command = self._sanitize(input("$ ").split())


    @staticmethod
    def _sanitize(command: Sequence[str]) -> Sequence[str]:
        """TODO"""
        # Only fixes paths, nothing more.
        for item in command:
            path = Path(item).resolve()
            if # TODO: check if path will go outside of the cwd...

    def _run_command(self, command: Sequence[str]) -> bool:
        """TODO"""
        result = subprocess.run(command, shell=True, cwd=self.cwd, capture_output=True, check=False, text=True, )
