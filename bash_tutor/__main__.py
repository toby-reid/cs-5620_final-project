"""TODO"""

import json
from pathlib import Path
from typing import Any

from .task import Task
from .utils import ENCODING


def load_tasks(tasks_file: Path) -> list[Task]:
    """
    Loads tasks from a given JSON file.

    Parameters:
        tasks_file (Path): JSON file containing a list of Task-like objects

    Returns:
        tasks (list[Task]): All valid tasks found in the given file
    """

    with tasks_file.open('r', encoding=ENCODING) as file:
        # Again, skip validation for the sake of time
        tasks_json: list[dict[str, Any]] = json.load(file)
    tasks = [Task.from_json(task) for task in tasks_json]
    return [task for task in tasks if task is not None]
