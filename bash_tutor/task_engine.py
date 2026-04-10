"""Contains an engine used for running a task."""

import sys
from dataclasses import dataclass, field
from enum import StrEnum, auto
from pathlib import Path
from typing import Optional, Sequence

from .task import Task
from .utils import Color, FileSystem, color_text, print_color, reset_workspace, run_command


_BANNED_SYMBOLS = ("$", "!", ";", "&")


@dataclass(slots=True)
class TaskEngine:
    """Engine for running a task."""

    class SpecialCommand(StrEnum):
        """Represents a special command that supercedes Bash commands for the tutor's sake."""

        TASK = auto()
        HELP = auto()
        HINT = auto()
        SOLUTION = auto()
        RESET = auto()
        RESTART = auto()
        EXIT = auto()

    task: Task
    start_dir: Path
    desired_result: Task.Result = field(init=False)
    attempt_commands: list[list[str]] = field(init=False)
    cwd: Path = field(init=False)
    hint: int = field(default=0, init=False)
    got_solution: bool = field(default=False, init=False)

    def __post_init__(self):
        self.desired_result = self.task.evaluate(self.start_dir)

    def run(self, max_attempts: Optional[int] = None) -> bool:
        """
        Attempts this task, potentially multiple times.

        Parameters:
            max_attempts (int | None):
                The maximum number of times the user may attempt this task, if limited

        Returns:
            is_successful (bool): Whether the user completed the task without getting the solution
        """
        attempts = 0
        while max_attempts is None or attempts < max_attempts:
            result = self._run()
            if result is not None:
                reset_workspace(self.start_dir)
                return result
            attempts += 1
        reset_workspace(self.start_dir)
        return False

    def _run(self) -> Optional[bool]:
        """
        Conducts a single attempt of this task.

        Returns:
            task_completed (bool | None):
                * `True` if the task was completed successfully
                * `False` if the task was aborted or completed after being given the solution
                * `None` if the task was not completed successfully
        """
        self.cwd = self.start_dir
        reset_workspace(self.start_dir)
        self.attempt_commands = []
        self._cmd_task()
        if self.task.command_limit is not None and self.task.command_limit <= 0:
            print_color(
                f"Task requested invalid limit {self.task.command_limit}; aborting", Color.RED
            )
            return False
        while (
            self.task.command_limit is None or len(self.attempt_commands) < self.task.command_limit
        ):
            print(
                color_text("student", Color.BLUE),
                color_text(
                    f"/{self.start_dir.name / self.cwd.relative_to(self.start_dir)}", Color.GREEN
                ),
                sep=":",
            )
            # Don't worry about vetting input
            command = input("$ ").split()
            if len(command) == 1 and command[0] in TaskEngine.SpecialCommand:
                exit_status = {
                    TaskEngine.SpecialCommand.TASK: self._cmd_task,
                    TaskEngine.SpecialCommand.HELP: self._cmd_help,
                    TaskEngine.SpecialCommand.HINT: self._cmd_hint,
                    TaskEngine.SpecialCommand.SOLUTION: self._cmd_solution,
                    TaskEngine.SpecialCommand.RESET: self._cmd_restart,
                    TaskEngine.SpecialCommand.RESTART: self._cmd_restart,
                    TaskEngine.SpecialCommand.EXIT: self._cmd_exit,
                }[TaskEngine.SpecialCommand(command[0])]()
                if exit_status is not None:
                    return False if exit_status else None
                continue
            if not self._is_safe(command):
                continue
            if self._run_command(command):
                return not self.got_solution
        print_color(
            f"Failed to complete task within command limit of {self.task.command_limit}",
            Color.YELLOW,
        )
        return None

    def _is_safe(self, command: Sequence[str]) -> bool:
        """
        Checks paths to ensure they stay within the workspace, and checks for any usage of potential
        Bash-style variables and subcommands.

        Parameters:
            command (Sequence[str]): The user-provided command to check

        Returns:
            is_safe (bool): Whether the command is (probably) safe to execute
        """
        for item in command[1:]:  # first may be an absolute path to an executable, so ignore it
            if item.startswith("/"):
                path = Path(item).resolve()
            else:
                path = (self.cwd / item).resolve()
            if not path.is_relative_to(self.start_dir):
                print_color(
                    f"Suspected path '{item}' goes outside workspace directory; rejecting command",
                    Color.MAGENTA,
                )
                return False
        if any(any(banned_sym in item for banned_sym in _BANNED_SYMBOLS) for item in command):
            print_color(f"Tutor disallows keys {_BANNED_SYMBOLS}; rejecting command", Color.MAGENTA)
            return False
        return True

    def _run_command(self, command: Sequence[str]) -> bool:
        """
        Invokes the given command from this object's current working directory.

        Paramters:
            command (Sequence[str]): The user-provided command to execute

        Returns:
            is_complete (bool): Whether all checked results match the desired results
        """
        result = run_command(command, self.cwd)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)  # send to stdout
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

    def _cmd_task(self) -> Optional[bool]:
        """
        In response to the 'task' command from the user, or as an initial task information.

        Returns:
            restart_status (bool | None):
                * `True` if this task is being aborted; i.e., no further attempts should be made
                * `False` if this task is being restarted; i.e., reset from the task beginning
                * `None` if this task should continue without restarting
        """
        print_color(f"-- Task: {self.task.name} --\n{self.task.prompt}", Color.CYAN)
        return None

    def _cmd_help(self) -> Optional[bool]:
        """
        In response to the 'help' command from the user.

        Returns:
            restart_status (bool | None):
                * `True` if this task is being aborted; i.e., no further attempts should be made
                * `False` if this task is being restarted; i.e., reset from the task beginning
                * `None` if this task should continue without restarting
        """
        print_color(
            "-- Bash Tutor Help --\n"
            "When prompted, enter a Bash command on the line following the $ (Bash prompt).\n"
            "You will be prevented from navigating away from the given workspace directory, "
            "or from using variables and subprocesses, for your safety.\n"
            "In addition to standard Bash commands, the following commands are available:\n"
            f"  {TaskEngine.SpecialCommand.TASK} - Get task details\n"
            f"  {TaskEngine.SpecialCommand.HELP} - Displays this help message\n"
            f"  {TaskEngine.SpecialCommand.HINT} - Get the next hint for this task\n"
            f"  {TaskEngine.SpecialCommand.SOLUTION} - Get a solution for this task\n"
            f"  {TaskEngine.SpecialCommand.RESET} - Retry this task from the start\n"
            f"  {TaskEngine.SpecialCommand.EXIT} - Give up on this task",
            Color.CYAN,
        )
        return None

    def _cmd_exit(self) -> Optional[bool]:
        """
        In response to the 'exit' command from the user.

        Returns:
            restart_status (bool | None):
                * `True` if this task is being aborted; i.e., no further attempts should be made
                * `False` if this task is being restarted; i.e., reset from the task beginning
                * `None` if this task should continue without restarting
        """
        print_color("Aborting this task...", Color.CYAN)
        return True

    def _cmd_hint(self) -> Optional[bool]:
        """
        In response to the 'hint' command from the user.

        Returns:
            restart_status (bool | None):
                * `True` if this task is being aborted; i.e., no further attempts should be made
                * `False` if this task is being restarted; i.e., reset from the task beginning
                * `None` if this task should continue without restarting
        """
        if self.hint < len(self.task.hints):
            print_color(
                f"Hint {self.hint + 1} / {len(self.task.hints)}:\n{self.task.hints[self.hint]}",
                Color.CYAN,
            )
            self.hint += 1
        else:
            return self._cmd_solution()
        return None

    def _cmd_solution(self) -> Optional[bool]:
        """
        In response to the 'solution' command from the user.

        Returns:
            restart_status (bool | None):
                * `True` if this task is being aborted; i.e., no further attempts should be made
                * `False` if this task is being restarted; i.e., reset from the task beginning
                * `None` if this task should continue without restarting
        """
        print(
            color_text("Solution:\nEnter the following commands, in this order:\n", Color.CYAN)
            + f"  {'\n  '.join(' '.join(command) for command in self.task.solution)}"
        )
        self.got_solution = True
        return self._cmd_restart()

    def _cmd_restart(self) -> Optional[bool]:
        """
        In response to the 'restart' command from the user.

        Returns:
            restart_status (bool | None):
                * `True` if this task is being aborted; i.e., no further attempts should be made
                * `False` if this task is being restarted; i.e., reset from the task beginning
                * `None` if this task should continue without restarting
        """
        print_color("Restarting this task...", Color.CYAN)
        return False
