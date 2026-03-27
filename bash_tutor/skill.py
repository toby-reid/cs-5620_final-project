"""TODO"""

from dataclasses import dataclass, field
from enum import StrEnum, auto


class Skill(StrEnum):
    """TODO"""

    LS = auto()
    CD = auto()
    CAT = auto()
    ECHO = auto()
    REDIRECTION = auto()
    RM = auto()
    MKDIR = auto()


@dataclass(slots=True)
class Progress:
    """TODO"""

    skill: Skill
    overall_knowledge: int = field(init=False, default=0)
    basic_usage: int = field(init=False, default=0)



class Tracker:
    """TODO"""

    # static member

