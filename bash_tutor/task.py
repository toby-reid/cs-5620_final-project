"""TODO"""

import json
from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path
from typing import Any, Optional

from .skill import Skill
from .utils import ENCODING, CommandResult, FileSystem, run_command


@dataclass(frozen=True, slots=True, kw_only=True)
class Task:
    """TODO"""

    class ResultCheck(StrEnum):
        """TODO"""
        STDOUT = auto()
        STDERR = auto()
        EXACT_COMMAND = auto()
        FILE_SYSTEM = auto()

    @dataclass(slots=True, kw_only=True)
    class Result:
        """TODO"""
        stdout: Optional[str] = None
        stderr: Optional[str] = None
        commands: Optional[list[list[str]]] = None
        fs: Optional[FileSystem] = None

    name: str
    prompt: str
    hints: list[str]
    solution: list[list[str]]
    result_checks: list[ResultCheck] = list(ResultCheck)  # will be str, not enum
    skills: Optional[list[Skill]] = None  # will actually be string, not enum
    command_limit: Optional[int] = None

    @classmethod
    def from_json(cls, object: dict[str, Any]) -> Optional["Task"]:
        """TODO"""
        try:
            # Note: this simplistic method will keep strings/ints, not convert to enum
            return Task(**object)
        except TypeError as e:
            print(f"Invalid JSON task provided: {object}\n  ({e})")
            return None

    def evaluate(self, start_dir: Path) -> Result:
        """TODO"""
        cmd_results: list[CommandResult] = []
        cwd = start_dir
        for command in self.solution:
            cmd_result = run_command(command, cwd=cwd)
            cmd_results.append(cmd_result)
            cwd = cmd_result.new_cwd
        result = Task.Result()
        if Task.ResultCheck.STDOUT in self.result_checks:
            result.stdout = cmd_results[-1].stdout
        if Task.ResultCheck.STDERR in self.result_checks:
            result.stderr = cmd_results[-1].stderr
        if Task.ResultCheck.EXACT_COMMAND in self.result_checks:
            result.commands = self.solution
        if Task.ResultCheck.FILE_SYSTEM in self.result_checks:
            result.fs = FileSystem.from_fs(start_dir)
        return result


def load_tasks(tasks_file: Path) -> list[Task]:
    """TODO"""

    with tasks_file.open('r', encoding=ENCODING) as file:
        # Again, skip validation for the sake of time
        tasks_json: list[dict[str, Any]] = json.load(file)
    tasks = [Task.from_json(task) for task in tasks_json]
    return [task for task in tasks if task is not None]
