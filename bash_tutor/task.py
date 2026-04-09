"""Contains the structure for an individual task."""

from copy import deepcopy
from dataclasses import dataclass, field
from enum import StrEnum, auto
from pathlib import Path
from typing import Any, Optional

from .skill import Skill
from .utils import Color, CommandResult, FileSystem, print_color, run_command


@dataclass(frozen=True, slots=True, kw_only=True)
class Task:
    """Structure for an individual task."""

    class JsonKey(StrEnum):
        """Represents a valid JSON key, which is directly mapped into the Task object."""

        PROMPT = auto()
        HINTS = auto()
        SOLUTION = auto()
        RESULT_CHECKS = auto()
        SKILLS = auto()
        COMMAND_LIMIT = auto()

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
    result_checks: set[ResultCheck] = field(default_factory=lambda: set(Task.ResultCheck))
    skills: Optional[set[Skill]] = None  # will actually be string, not enum
    command_limit: Optional[int] = None

    @classmethod
    def from_json(cls, name: str, object: dict[str, Any]) -> Optional["Task"]:
        """
        Attempts to generate this object from a JSON-type object.

        Parameters:
            object (dict[str, Any]): The JSON-like object whose keys match this class's keys

        Returns:
            instance (Task | None): An instance of this class, if the input JSON is valid
        """
        json_object = deepcopy(object)
        try:
            if cls.JsonKey.RESULT_CHECKS in json_object:
                json_object[cls.JsonKey.RESULT_CHECKS] = {
                    cls.ResultCheck(check) for check in json_object[cls.JsonKey.RESULT_CHECKS]
                }
            if cls.JsonKey.SKILLS in json_object and json_object[cls.JsonKey.SKILLS] is not None:
                json_object[cls.JsonKey.SKILLS] = {
                    Skill(skill) for skill in json_object[cls.JsonKey.SKILLS]
                }
            return cls(name=name, **json_object)
        except (KeyError, TypeError) as e:
            print_color(f"Invalid task provided (e): {object}", Color.YELLOW)
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
