from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from subprocess import CalledProcessError
from typing import List, Optional

from . import __version__
from .merge import MergeConflict
from .odb import Commit, Reference, Repository
from .todo import apply_todos, autosquash_todos, build_todos, edit_todos
from .utils import (
    EditorError,
    commit_range,
    cut_commit,
    edit_commit_message,
    local_commits,
    update_head,
)


def build_parser() -> ArgumentParser:
    pass


def interactive(
    args: Namespace, repo: Repository, staged: Optional[Commit], head: Reference[Commit]
) -> None:
    pass


def enable_autosquash(args: Namespace, repo: Repository) -> bool:
    pass


def noninteractive(
    args: Namespace, repo: Repository, staged: Optional[Commit], head: Reference[Commit]
) -> None:
    pass


def inner_main(args: Namespace, repo: Repository) -> None:
    # If '-a' or '-p' was specified, stage changes.
    # Note that stdout=None means "inherit current stdout".
    pass


def main(argv: Optional[List[str]] = None) -> None:
    pass
