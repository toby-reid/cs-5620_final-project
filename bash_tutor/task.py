"""Contains the structure for an individual task."""

from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path
from typing import Any, Optional

from .skill import Skill
from .utils import ENCODING, CommandResult, FileSystem, run_command


@dataclass(frozen=True, slots=True, kw_only=True)
class Task:
    """Structure for an individual task."""

    class ResultCheck(StrEnum):
        """Represents one of the checks that can be made to ensure a solution is correct."""
        STDOUT = auto()
        STDERR = auto()
        EXACT_COMMAND = auto()
        FILE_SYSTEM = auto()

    @dataclass(slots=True, kw_only=True)
    class Result:
        """Represents the desired results, if that thing should be checked."""
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
    def from_json[TaskT](cls: type[TaskT], object: dict[str, Any]) -> Optional[TaskT]:
        """
        Attempts to generate this object from a JSON-type object.

        Parameters:
            object (dict[str, Any]): The JSON-like object whose keys match this class's keys

        Returns:
            instance (TaskT | None): An instance of this class, if the input JSON is valid
        """
        try:
            # Note: this simplistic method will keep strings/ints, not convert to enum
            return cls(**object)
        except TypeError as e:
            print(f"Invalid JSON task provided: {object}\n  ({e})")
            return None

    def evaluate(self, start_dir: Path) -> Result:
        """
        Determines the desired results for this task, based on the checks that should be made.

        Parameters:
            start_dir (Path): The directory from which this task will be started

        Returns:
            result (Result): Desired results for this task
        """
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
