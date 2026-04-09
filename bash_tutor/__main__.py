"""Main entrypoint for the bash_tutor."""

import argparse
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .task import Task
from .task_engine import TaskEngine
from .utils import ENCODING, TASKS_JSON, WORKSPACE_DIR, Color, ExitCode, print_color


@dataclass(init=False)
class _ParsedArgs(argparse.Namespace):
    """A basic dataclass for static type checking purposes."""

    task: Optional[str]
    input_json: Path
    workspace_dir: Path
    task_attempts: Optional[int]
    select_random: bool


def main(args: list[str]) -> ExitCode:
    """
    Reads tasks from file, then runs various tasks as requested.

    Parameters:
        args (list[str]): Command-line arguments, *not* including the invoked file/module

    Returns:
        exit_code (ExitCode): 0 if successful (even if the user failed any task(s))
    """
    parsed_args = _parse_args(args)
    tasks = _load_tasks(parsed_args.input_json)
    if not tasks:
        print_color(
            f"Error: No tasks could be loaded from JSON file '{parsed_args.input_json}'", Color.RED
        )
        return ExitCode.BAD_CLI_ARG
    if parsed_args.task is not None:
        if parsed_args.task in tasks:
            _run_task(tasks[parsed_args.task], parsed_args.workspace_dir, parsed_args.task_attempts)
            return ExitCode.SUCCESS
        print_color(
            f"Couldn't find task '{parsed_args.task}' in tasks {tuple(tasks.keys())}", Color.RED
        )
        return ExitCode.BAD_CLI_ARG
    if parsed_args.select_random:
        is_success = True
        while is_success:
            task = random.choice(list(tasks.values()))
            is_success = _run_task(task, parsed_args.workspace_dir, parsed_args.task_attempts)
        print_color("Task aborted or failed; exiting since in 'random' mode", Color.CYAN)
        return ExitCode.SUCCESS
    successes = 0
    total_attempted = 0
    for task in tasks.values():
        total_attempted += 1
        if _run_task(task, parsed_args.workspace_dir, parsed_args.task_attempts):
            successes += 1
    print_color(f"{successes} / {total_attempted} tasks succeeded", Color.GREEN)
    return ExitCode.SUCCESS


def _parse_args(args: list[str]) -> _ParsedArgs:
    """
    Parses command-line arguments for this module.

    Parameters:
        args (list[str]): Command-line arguments, *not* including this file/module name

    Returns:
        parsed_args (_ParsedArgs): A namespace containing any relevant values
    """
    parser = argparse.ArgumentParser(
        "bash_tutor",
        description="A proof-of-concept constraint-based Bash tutor.",
        epilog="Created for USU CS-5620, AI in Education (Dr. Seth Poulsen), by Toby Reid.",
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
    if not parsed_args.input_json.is_file():
        parser.error(f"Given input JSON file '{parsed_args.input_json}' is not a file")
    if not parsed_args.workspace_dir.is_dir():
        parser.error(f"Given workspace dir '{parsed_args.workspace_dir}' is not a directory")
    return parsed_args


def _load_tasks(tasks_file: Path) -> Optional[dict[str, Task]]:
    """
    Loads tasks from a given JSON file.

    Parameters:
        tasks_file (Path): JSON file containing a list of Task-like objects

    Returns:
        tasks (dict[str, Task]): All valid tasks found in the given file
    """

    with tasks_file.open("r", encoding=ENCODING) as file:
        # Again, skip validation for the sake of time
        tasks_json: dict[str, dict[str, Any]] = json.load(file)
    try:
        tasks = {name: Task.from_json(name, task) for name, task in tasks_json.items()}
    except (AttributeError, TypeError) as e:
        print_color(
            f"Error: Invalid JSON provided ({e})\nPlease ensure your Tasks JSON is valid", Color.RED
        )
        return None
    return {name: task for name, task in tasks.items() if task is not None}


def _run_task(task: Task, workspace_dir: Path, max_attempts: Optional[int] = None) -> bool:
    """
    Runs the given task and provides feedback on whether the user was successful.

    Parameters:
        task (Task): The task to run
        workspace_dir (Path): The workspace directory to use when running the task
        max_attempts (int | None): Maximum number of failures to allow, if setting a limit

    Returns:
        is_successful (bool): Whether the user successfully completed the given task
    """

    task_engine = TaskEngine(task, workspace_dir)
    is_success = task_engine.run(max_attempts=max_attempts)
    if is_success:
        print_color("Task completed successfully!", Color.GREEN)
    else:
        print_color("Task failed or completed with solution provided.", Color.MAGENTA)
    return is_success


sys.exit(main(sys.argv[1:]))
