"""TODO"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence, Optional

from .task import Task
from .utils import FileSystem, run_command


@dataclass(slots=True)
class TaskEngine:
    """TODO"""

    task: Task
    start_dir: Path
    desired_result: Task.Result = field(init=False)
    attempt_commands: list[list[str]] = field(init=False)
    cwd: Path = field(init=False)

    def __post_init__(self):
        self.desired_result = self.task.evaluate(self.start_dir)

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
        self.attempt_commands = []
        success = False
        while not success:
            print(self.cwd)
            # Don't worry about vetting input
            command = input("$ ").split()
            if not self._is_safe(command):
                continue
            is_result = self._run_command(command)
            if is_result is not None:
                if not is_result:
                    return False
                return True
        return success

    def _is_safe(self, command: Sequence[str]) -> bool:
        """TODO"""
        # Only checks paths, nothing more.
        for item in command[1:]:  # first may be an absolute path to an executable
            if item.startswith("/"):
                path = Path(item).resolve()
            else:
                path = (self.cwd / item).resolve()
            if not path.is_relative_to(self.start_dir):
                print(
                    f"Suspected path {item} goes outside workspace directory; rejecting command",
                    file=sys.stderr,
                )
                return False
        return True

    def _run_command(self, command: Sequence[str]) -> bool:
        """TODO"""
        result = run_command(command, self.cwd)
        self.cwd = result.new_cwd
        self.attempt_commands.append(list(command))
        if self.desired_result.stdout is not None and self.desired_result.stdout != result.stdout:
            return False
        if self.desired_result.stderr is not None and self.desired_result.stderr != result.stderr:
            return False
        if (
            self.desired_result.commands is not None
            and self.desired_result.commands != self.attempt_commands
        ):
            return False
        if (
            self.desired_result.fs is not None
            and self.desired_result.fs.find_diff(FileSystem.from_fs(self.start_dir)) is not None
        ):
            return False
        return True
