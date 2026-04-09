"""Contains an engine used for running a task."""

import sys
from dataclasses import dataclass, field
from enum import StrEnum, auto
from pathlib import Path
from typing import Optional, Sequence

from .task import Task
from .utils import FileSystem, reset_workspace, run_command


@dataclass(slots=True)
class TaskEngine:
    """Engine for running a task."""

    class SpecialCommand(StrEnum):
        """Represents a special command that supercedes Bash commands for the tutor's sake."""

        HELP = auto()
        HINT = auto()
        SOLUTION = auto()
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
                return result
            attempts += 1
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
        success = False
        while not success:
            print(self.cwd)
            # Don't worry about vetting input
            command = input("$ ").split()
            if len(command) == 1 and command[0] in TaskEngine.SpecialCommand:
                exit_status = {
                    TaskEngine.SpecialCommand.HELP: self._cmd_help,
                    TaskEngine.SpecialCommand.HINT: self._cmd_hint,
                    TaskEngine.SpecialCommand.SOLUTION: self._cmd_solution,
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
                print(
                    f"Suspected path '{item}' goes outside workspace directory; rejecting command",
                    file=sys.stderr,
                )
                return False
        if any("$" in item for item in command):
            print(
                "Tutor disallows variables and subprocesses (via $); rejecting command",
                file=sys.stderr,
            )
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

    def _cmd_help(self) -> Optional[bool]:
        """
        In response to the 'help' command from the user.

        Returns:
            restart_status (bool | None):
                * `True` if this task is being aborted; i.e., no further attempts should be made
                * `False` if this task is being restarted; i.e., reset from the task beginning
                * `None` if this task should continue without restarting
        """
        print(
            "-- Bash Tutor Help --\n"
            "When prompted, enter a Bash command on the line following the $ (Bash prompt).\n"
            "You will be prevented from navigating away from the given workspace directory, "
            "or from using variables and subprocesses, for your safety.\n"
            "In addition to standard Bash commands, the following commands are available:\n"
            f"  {TaskEngine.SpecialCommand.HELP} - Displays this help message\n"
            f"  {TaskEngine.SpecialCommand.HINT} - Get the next hint for this task, "
            "and restart the current attempt\n"
            f"  {TaskEngine.SpecialCommand.SOLUTION} - Get a solution for this task\n"
            f"  {TaskEngine.SpecialCommand.RESTART} - Retry this task from the start\n"
            f"  {TaskEngine.SpecialCommand.EXIT} - Give up on this task"
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
        print("Aborting this task...")
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
            print(f"Hint {self.hint + 1} / {len(self.task.hints)}:\n{self.task.hints[self.hint]}")
            self.hint += 1
        else:
            return self._cmd_solution()
        return False

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
            f"Solution:\nEnter the following commands, in this order:\n"
            f"  {'\n  '.join(' '.join(command) for command in self.task.solution)}"
        )
        self.got_solution = True
        return False

    def _cmd_restart(self) -> Optional[bool]:
        """
        In response to the 'restart' command from the user.

        Returns:
            restart_status (bool | None):
                * `True` if this task is being aborted; i.e., no further attempts should be made
                * `False` if this task is being restarted; i.e., reset from the task beginning
                * `None` if this task should continue without restarting
        """
        print("Restarting this task...")
        return False
