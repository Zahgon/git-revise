from __future__ import annotations

import re
from enum import Enum
from typing import List, Optional

from .odb import Commit, MissingObject, Repository
from .utils import cut_commit, edit_commit_message, run_editor, run_sequence_editor


class StepKind(Enum):
    PICK = "pick"
    FIXUP = "fixup"
    SQUASH = "squash"
    REWORD = "reword"
    CUT = "cut"
    INDEX = "index"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    def parse(instr: str) -> StepKind:
        pass


class Step:
    kind: StepKind
    commit: Commit
    message: Optional[bytes]

    def __init__(self, kind: StepKind, commit: Commit) -> None:
        self.kind = kind
        self.commit = commit
        self.message = None

    @staticmethod
    def parse(repo: Repository, instr: str) -> Step:
        pass

    def __str__(self) -> str:
        return f"{self.kind} {self.commit.oid.short()}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Step):
            return False
        return (
            self.kind == other.kind
            and self.commit == other.commit
            and self.message == other.message
        )


def build_todos(commits: List[Commit], index: Optional[Commit]) -> List[Step]:
    pass


def validate_todos(old: List[Step], new: List[Step]) -> None:
    """Raise an exception if the new todo list is malformed compared to the
    original todo list"""
    pass


def add_autosquash_step(step: Step, picks: List[List[Step]]) -> None:
    pass


def autosquash_todos(todos: List[Step]) -> List[Step]:
    pass


def edit_todos_msgedit(repo: Repository, todos: List[Step]) -> List[Step]:
    pass


def edit_todos(
    repo: Repository, todos: List[Step], msgedit: bool = False
) -> List[Step]:
    pass


def apply_todos(
    current: Optional[Commit],
    todos: List[Step],
    reauthor: bool = False,
) -> Commit:
    pass
