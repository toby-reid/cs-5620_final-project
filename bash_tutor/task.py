"""TODO"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .utils import ENCODING


@dataclass(frozen=True, slots=True, kw_only=True)
class Task:
    """TODO"""

    name: str
    prompt: str
    hints: list[str]
    solution: list[list[str]]

    @staticmethod
    def from_json(object: dict[str, Any]) -> Optional["Task"]:
        """TODO"""
        # for the sake of demo, we'll skip validation
        try:
            return Task(**object)
        except TypeError:
            print(f"Invalid JSON task provided: {object}")
            return None

    def evaluate(student_command: list[str]) -> bool:
        """TODO"""



def load_tasks(tasks_file: Path) -> list[Task]:
    """TODO"""

    with tasks_file.open('r', encoding=ENCODING) as file:
        # Again, skip validation for the sake of time
        tasks_json: list[dict[str, Any]] = json.load(file)
    tasks = [Task.from_json(task) for task in tasks_json]
    return [task for task in tasks if task is not None]
