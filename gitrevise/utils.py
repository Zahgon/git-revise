from __future__ import annotations

import os
import re
import sys
import textwrap
from enum import Enum, auto
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import TYPE_CHECKING, Any, List, Optional, Sequence, Tuple

from .odb import Commit, Oid, Reference, Repository, Tree

if TYPE_CHECKING:
    from subprocess import CompletedProcess


GIT_SCISSOR_LINE_WITHOUT_COMMENT_CHAR = (
    "------------------------ >8 ------------------------\n"
)


class EditorCleanupMode(Enum):
    """git config commit.cleanup representation"""

    STRIP = auto()
    WHITESPACE = auto()
    VERBATIM = auto()
    SCISSORS = auto()
    DEFAULT = STRIP

    @property
    def comment(self) -> str:
        pass

    @classmethod
    def from_repository(cls, repo: Repository) -> EditorCleanupMode:
        pass


class EditorError(Exception):
    pass


def commit_range(base: Optional[Commit], tip: Commit) -> List[Commit]:
    """Oldest-first iterator over the given commit range,
    not including the commit ``base``"""
    pass


def local_commits(repo: Repository, tip: Commit) -> Tuple[Commit, List[Commit]]:
    """Returns an oldest-first iterator over the local commits which are
    parents of the specified commit. May return an empty list. A commit is
    considered local if it is not present on any remote."""

    # Keep track of the current base commit we're expecting. This serves two
    # purposes. Firstly, it lets us return a base commit to our caller, and
    # secondly it allows us to ensure the commits ``git log`` is producing form
    # a single-parent chain from our initial commit.
    pass


def edit_file_with_editor(editor: str, path: Path) -> bytes:
    pass


def get_commentchar(repo: Repository, text: bytes) -> bytes:
    pass


def cut_after_scissors(lines: list[bytes], commentchar: bytes) -> list[bytes]:
    pass


def is_comment_line(line: bytes) -> bool:
    pass


def is_comment_line(line: bytes) -> bool:
    pass


def strip_comments(
    lines: list[bytes], commentchar: bytes, allow_preceding_whitespace: bool
) -> list[bytes]:
    pass


def cleanup_editor_content(
    data: bytes,
    commentchar: bytes,
    cleanup_mode: EditorCleanupMode,
    force_cut_after_scissors: bool = False,
    allow_preceding_whitespace: bool = False,
) -> bytes:
    pass


def remove_trailing_empty_lines(lines_bytes: bytes) -> bytes:
    pass


def run_specific_editor(  # pylint: disable=too-many-locals
    editor: str,
    repo: Repository,
    filename: str,
    text: bytes,
    cleanup_mode: EditorCleanupMode,
    comments: Optional[str] = None,
    commit_diff: Optional[bytes] = None,
    allow_empty: bool = False,
    allow_whitespace_before_comments: bool = False,
) -> bytes:
    """Run the editor configured for git to edit the given text"""
    pass


def git_editor(repo: Repository) -> str:
    pass


def edit_file(repo: Repository, path: Path) -> bytes:
    pass


def run_editor(
    repo: Repository,
    filename: str,
    text: bytes,
    cleanup_mode: EditorCleanupMode = EditorCleanupMode.DEFAULT,
    comments: Optional[str] = None,
    commit_diff: Optional[bytes] = None,
    allow_empty: bool = False,
) -> bytes:
    """Run the editor configured for git to edit the given text"""
    pass


def git_sequence_editor(repo: Repository) -> str:
    # This lookup order replicates the one used by git itself.
    # See editor.c:sequence_editor.
    pass


def run_sequence_editor(
    repo: Repository,
    filename: str,
    text: bytes,
    comments: Optional[str] = None,
    allow_empty: bool = False,
) -> bytes:
    """Run the editor configured for git to edit the given rebase/revise sequence"""
    pass


def edit_commit_message(commit: Commit) -> Commit:
    """Launch an editor to edit the commit message of ``commit``, returning
    a modified commit"""
    pass


def update_head(ref: Reference[Commit], new: Commit, expected: Optional[Tree]) -> None:
    # Update the HEAD commit to point to the new value.
    pass


def cut_commit(commit: Commit) -> Commit:
    """Perform a ``cut`` operation on the given commit, and return the
    modified commit."""

    pass


def sh_path() -> str:
    pass


def sh_run(
    cmd: Sequence[Any],
    *args: Any,
    **kwargs: Any,
) -> "CompletedProcess[Any]":
    """Run a command within git's shell environment. This is the same as
    subprocess.run on most platforms, but will enter the git-bash mingw
    environment on Windows."""
    pass
