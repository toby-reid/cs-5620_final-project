"""TODO"""

import argparse
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .task import Task
from .task_engine import TaskEngine
from .utils import ENCODING, TASKS_JSON, WORKSPACE_DIR, ExitCode


@dataclass(init=False)
class _ParsedArgs(argparse.Namespace):
    """A basic dataclass for static type checking purposes."""

    smoke_check: bool
    task: Optional[str]
    input_json: Path
    workspace_dir: Path
    task_attempts: Optional[int]
    select_random: bool


def main(args: list[str]) -> ExitCode:
    """TODO"""
    parsed_args = _parse_args(args)
    tasks = _load_tasks(parsed_args.input_json)
    if not tasks:
        print(f"Error: No tasks in JSON file '{parsed_args.input_json}'", file=sys.stderr)
        return ExitCode.BAD_CLI_ARG
    if parsed_args.task is not None:
        if parsed_args.task in tasks:
            _run_task(tasks[parsed_args.task], parsed_args.workspace_dir, parsed_args.task_attempts)
            return ExitCode.SUCCESS
        print(f"Couldn't find task '{parsed_args.task}' in tasks {tuple(tasks.keys())}", file=sys.stderr)
        return ExitCode.BAD_CLI_ARG
    if parsed_args.select_random:
        is_success = True
        while is_success:
            task = random.choice(list(tasks.values()))
            is_success = _run_task(task, parsed_args.workspace_dir, parsed_args.task_attempts)
        print("Task aborted or failed; exiting since in 'random' mode")
        return ExitCode.SUCCESS
    successes = 0
    total_attempted = 0
    for task in tasks.values():
        total_attempted += 1
        if _run_task(task, parsed_args.workspace_dir, parsed_args.task_attempts):
            successes += 1
    print(f"{successes} / {total_attempted} tasks succeeded")
    return ExitCode.SUCCESS


def _parse_args(args: list[str]) -> _ParsedArgs:
    """TODO"""
    parser = argparse.ArgumentParser(
        "bash_tutor",
        description="A proof-of-concept constraint-based Bash tutor.",
        epilog="Created for USU CS-5620, AI in Education (Dr. Seth Poulsen), by Toby Reid.",
    )
    parser.add_argument(
        "-c",
        "--smoke-check",
        action="store_true",
        help="Ensures imports and other such functionality are working",
    )
    parser.add_argument("-t", "--task", help="Specify a particular task to perform")
    parser.add_argument(
        "-i",
        "--input-json",
        help=f"Specify the input tasks JSON file to read (default '{TASKS_JSON}')",
        default=TASKS_JSON,
        type=Path,
    )
    parser.add_argument(
        "-w",
        "--workspace-dir",
        help=f"Specify the workspace dir to use. Must have Git functionality (default '{WORKSPACE_DIR}')",
        default=WORKSPACE_DIR,
        type=Path,
    )
    parser.add_argument(
        "-a",
        "--task-attempts",
        help="Specify a maximum number of attempts on a task before aborting",
        type=int,
    )
    parser.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="Set to select tasks at random (instead of iterating through all tasks)",
        dest="select_random",
    )
    parsed_args = parser.parse_args(args, namespace=_ParsedArgs())
    if parsed_args.smoke_check:
        parser.exit(ExitCode.SUCCESS, "Exiting after smoke check")
    if not parsed_args.input_json.is_file():
        parser.error(f"Given input JSON file '{parsed_args.input_json}' is not a file")
    if not parsed_args.workspace_dir.is_dir():
        parser.error(f"Given workspace dir '{parsed_args.workspace_dir}' is not a directory")
    return parsed_args


def _load_tasks(tasks_file: Path) -> dict[str, Task]:
    """
    Loads tasks from a given JSON file.

    Parameters:
        tasks_file (Path): JSON file containing a list of Task-like objects

    Returns:
        tasks (dict[Any, Task]): All valid tasks found in the given file
    """

    with tasks_file.open("r", encoding=ENCODING) as file:
        # Again, skip validation for the sake of time
        tasks_json: dict[str, dict[str, Any]] = json.load(file)
    tasks = {name: Task.from_json(name, task) for name, task in tasks_json.items()}
    return {name: task for name, task in tasks.items() if task is not None}


def _run_task(task: Task, workspace_dir: Path, max_attempts: Optional[int] = None) -> bool:
    """TODO"""

    task_engine = TaskEngine(task, workspace_dir)
    is_success = task_engine.run(max_attempts=max_attempts)
    print("Task completed successfully!" if is_success else "Task failed.")
    return is_success
