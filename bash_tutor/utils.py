"""Common utilities for this module."""

import glob
import hashlib
import subprocess
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Any, Optional, Sequence


REPO_DIR = Path(__file__).parent.parent

RESOURCES_DIR = REPO_DIR / "resources"
TASKS_JSON = RESOURCES_DIR / "tasks.json"

WORKSPACE_DIR = REPO_DIR / "workspace"


ENCODING = "utf-8"
HASH_ALG = "sha256"


class ExitCode(IntEnum):
    """Command-line exit code."""

    SUCCESS = 0
    BAD_CLI_ARG = 1


class Color(StrEnum):
    """Represents a color for console output."""

    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    CYAN = "\033[36m"
    BLUE = "\033[94m"
    MAGENTA = "\033[35m"
    RESET = "\033[0m"


@dataclass(frozen=True, slots=True, eq=True)
class FileSystem:
    """Represents a file system (either file or directory), including children (if applicable)."""

    full_path: Path
    dir_contents: Optional[dict[str, "FileSystem"]] = field(default=None, kw_only=True)
    file_hash: Optional[bytes] = field(default=None, kw_only=True)

    def __post_init__(self):
        if self.dir_contents is None and self.file_hash is None:
            raise ValueError("Must be dir or file")
        if self.dir_contents is not None and self.file_hash is not None:
            raise ValueError("Cannot be both dir and file")

    @classmethod
    def from_fs(cls, file_or_dir: Path) -> "FileSystem":
        """
        Reads a directory or hashes a file to generate a representation of a fs snapshot.

        Parameters:
            file_or_dir (Path): The file or directory to read/hash a snapshot

        Returns:
            fs (FileSystem): A representation of a snapshot of the file or directory
        """
        if file_or_dir.is_dir():
            dir_contents: dict[str, FileSystem] = {}
            for content in file_or_dir.iterdir():
                dir_contents[content.name] = cls.from_fs(file_or_dir / content.name)
            return cls(file_or_dir, dir_contents=dir_contents)
        if file_or_dir.is_file():
            with file_or_dir.open("rb") as file:
                hash = hashlib.file_digest(file, HASH_ALG).digest()
            return cls(file_or_dir, file_hash=hash)
        raise TypeError(f"{file_or_dir} is not a valid file or directory")

    def find_diff(self, other: Optional["FileSystem"]) -> Optional[str]:
        """
        Determines whether two filesystem snapshots differ, and in what way.

        Parameters:
            other (FileSystem | None): The filesystem to compare against this one

        Returns:
            diff (str | None): A string representing where the filesystems differ, if at all
        """
        if other is None:
            return f"Expected path {self.full_path}"
        if self.full_path != other.full_path:
            return f"Expected path {self.full_path}, but got {other.full_path}"
        if self.file_hash is not None:
            if other.file_hash is None:
                return f"Expected file {self.full_path}, but got dir"
            if self.file_hash != other.file_hash:
                return f"File {self.full_path} hash does not match"
            return None
        if self.dir_contents is not None:
            if other.dir_contents is None:
                return f"Expected dir {self.full_path}, but got file"
            if self.dir_contents.keys() != other.dir_contents.keys():
                return (
                    f"Expected dir {self.full_path} contents {self.dir_contents.keys()}, "
                    f"but got {other.dir_contents.keys()}"
                )
            for name, fs in self.dir_contents.items():
                diff = fs.find_diff(other.dir_contents.get(name))
                if diff is not None:
                    return diff
        return None


@dataclass(slots=True, kw_only=True)
class CommandResult:
    """Represents the result from the running of a subprocess."""

    command: Sequence[str | Path]
    new_cwd: Path
    stdout: str
    stderr: str
    success: bool


def print_color(text: Any, color: Color | str) -> None:
    """
    Prints the given field using the given color.

    Parameters:
        text (Any): The field to be printed (will be converted by F-strings)
        color (Color | str): The color to use, or the name of that color
    """
    print(color_text(text=text, color=color))


def color_text(text: Any, color: Color | str) -> str:
    """
    Returns a formatted string that is the given color.

    Parameters:
        text (Any): The field to be printed (will be converted by F-strings)
        color (Color | str): The color to use, or the name of that color

    Returns:
        color_text (str): The given field, formatted for console output with the given color
    """
    if not isinstance(color, Color):
        color = Color(color.upper())
    return f"{color}{text}{Color.RESET}"


def run_command(command: Sequence[str | Path], cwd: Optional[Path | str] = None) -> CommandResult:
    """
    Runs a given command and determines whether the CWD has changed.

    Parameters:
        command (Sequence[str | Path]): The command to invoke
        cwd (Path | str | None): The working directory from which to invoke the given command

    Returns:
        result (CommandResult): The result from running the given command
    """
    cwd_key = ":CWD:"
    result = subprocess.run(
        f'{' '.join(f'{segment}' for segment in command)}; echo {cwd_key}"$(pwd)"',
        shell=True,
        capture_output=True,
        cwd=cwd,
        check=False,
        text=True,
    )
    cwd_index = result.stdout.rfind(cwd_key)
    return CommandResult(
        command=command,
        new_cwd=Path(result.stdout[cwd_index + len(cwd_key) :].strip()),
        stdout=result.stdout[:cwd_index],
        stderr=result.stderr,
        success=(result.returncode == ExitCode.SUCCESS),
    )


def reset_workspace(workspace_dir: Path = WORKSPACE_DIR) -> bool:
    """
    Performs a `git restore` on the given workspace directory.

    Parameters:
        workspace_dir (Path): The directory on which to invoke `git restore`

    Returns:
        is_successful (bool): Whether restoration was successful
    """
    result = subprocess.run(
        ["git", "restore", "."], cwd=workspace_dir, check=False, capture_output=True
    )
    return result.returncode == ExitCode.SUCCESS
