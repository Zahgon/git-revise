"""
This module contains a basic implementation of an efficient, in-memory 3-way
git tree merge. This is used rather than traditional git mechanisms to avoid
needing to use the index file format, which can be slow to initialize for
large repositories.

The INDEX file for my local mozilla-central checkout, for reference, is 35MB.
While this isn't huge, it takes a perceptable amount of time to read the tree
files and generate. This algorithm, on the other hand, avoids looking at
unmodified trees and blobs when possible.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path
from subprocess import CalledProcessError
from typing import Iterator, Optional, Tuple, TypeVar

from .odb import Blob, Commit, Entry, Mode, Repository, Tree
from .utils import edit_file

T = TypeVar("T")  # pylint: disable=invalid-name


class MergeConflict(Exception):
    pass


def rebase(commit: Commit, new_parent: Optional[Commit]) -> Commit:
    pass


def conflict_prompt(
    path: Path,
    descr: str,
    labels: Tuple[str, str, str],
    current: T,
    current_descr: str,
    other: T,
    other_descr: str,
) -> T:
    pass


def merge_trees(
    path: Path, labels: Tuple[str, str, str], current: Tree, base: Tree, other: Tree
) -> Tree:
    # Merge every named entry which is mentioned in any tree.
    pass


def merge_entries(
    path: Path,
    labels: Tuple[str, str, str],
    current: Optional[Entry],
    base: Optional[Entry],
    other: Optional[Entry],
) -> Optional[Entry]:
    pass


def merge_blobs(
    path: Path,
    labels: Tuple[str, str, str],
    current: Blob,
    base: Optional[Blob],
    other: Blob,
) -> Blob:
    pass


def merge_files(
    repo: Repository,
    labels: Tuple[str, str, str],
    current: bytes,
    base: bytes,
    other: bytes,
    tmpdir: Path,
) -> Tuple[bool, bytes]:
    pass


def replay_recorded_resolution(
    repo: Repository, tmpdir: Path, preimage: bytes
) -> Tuple[bytes, Optional[str], Optional[Blob]]:
    pass


def record_resolution(
    repo: Repository,
    conflict_id: Optional[str],
    normalized_preimage: bytes,
    postimage: bytes,
) -> None:
    pass


class ConflictParseFailed(Exception):
    pass


def normalize_conflict(
    lines: Iterator[bytes],
    hasher: Optional[hashlib._Hash],
) -> bytes:
    pass


def normalize_conflicted_file(body: bytes) -> Tuple[bytes, str]:
    pass
