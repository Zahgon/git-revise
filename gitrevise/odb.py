"""
Helper classes for reading cached objects from Git's Object Database.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
from collections import defaultdict
from contextlib import AbstractContextManager
from enum import Enum
from pathlib import Path
from subprocess import DEVNULL, PIPE, CalledProcessError, Popen, run
from tempfile import NamedTemporaryFile, TemporaryDirectory
from types import TracebackType
from typing import (
    IO,
    TYPE_CHECKING,
    Dict,
    Generic,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

if TYPE_CHECKING:
    from subprocess import _FILE

    from typing_extensions import Self


class MissingObject(Exception):
    """Exception raised when a commit cannot be found in the ODB"""

    def __init__(self, ref: str) -> None:
        Exception.__init__(self, f"Object {ref} does not exist")


class GPGSignError(Exception):
    """Exception raised when we fail to sign a commit"""

    def __init__(self, stderr: str) -> None:
        Exception.__init__(self, f"unable to sign object: {stderr}")


T = TypeVar("T")  # pylint: disable=invalid-name


class Oid(bytes):
    """Git object identifier"""

    __slots__ = ()

    def __new__(cls, b: bytes) -> Oid:
        if len(b) != 20:
            raise ValueError("Expected 160-bit SHA1 hash")
        return super().__new__(cls, b)

    @classmethod
    def fromhex(cls, instr: str) -> Oid:
        """Parse an ``Oid`` from a hexadecimal string"""
        pass

    @classmethod
    def null(cls) -> Oid:
        """An ``Oid`` consisting of entirely 0s"""
        pass

    def short(self) -> str:
        """A shortened version of the Oid's hexadecimal form"""
        pass

    @classmethod
    def for_object(cls, tag: str, body: bytes) -> Oid:
        """Hash an object with the given type tag and body to determine its Oid"""
        pass

    def __repr__(self) -> str:
        return self.hex()

    def __str__(self) -> str:
        return self.hex()


class Signature(bytes):
    """Git user signature"""

    __slots__ = ()

    sig_re = re.compile(
        rb"""
        (?P<signing_key>
            (?P<name>[^<>]+)<(?P<email>[^<>]+)>
        )
        [ ]
        (?P<timestamp>[0-9]+)
        (?:[ ](?P<offset>[\+\-][0-9]+))?
        """,
        re.X,
    )

    @property
    def name(self) -> bytes:
        """user name"""
        pass

    @property
    def email(self) -> bytes:
        """user email"""
        pass

    @property
    def signing_key(self) -> bytes:
        """user name <email>"""
        pass

    @property
    def timestamp(self) -> bytes:
        """unix timestamp"""
        pass

    @property
    def offset(self) -> bytes:
        """timezone offset from UTC"""
        pass


class Repository:
    """Main entry point for a git repository"""

    workdir: Path
    """working directory for this repository"""

    gitdir: Path
    """.git directory for this repository"""

    default_author: Signature
    """author used by default for new commits"""

    default_committer: Signature
    """committer used by default for new commits"""

    index: Index
    """current index state"""

    sign_commits: bool
    """sign commits with gpg"""

    gpg: bytes
    """path to GnuPG binary"""

    _objects: Dict[int, Dict[Oid, GitObj]]
    _catfile: Popen[bytes]
    _tempdir: Optional[TemporaryDirectory[str]]

    __slots__ = [
        "workdir",
        "gitdir",
        "default_author",
        "default_committer",
        "index",
        "sign_commits",
        "gpg",
        "_objects",
        "_catfile",
        "_tempdir",
    ]

    def __init__(self, cwd: Optional[Path] = None) -> None:
        self._tempdir = None

        self.workdir = Path(self.git("rev-parse", "--show-toplevel", cwd=cwd).decode())
        self.gitdir = self.workdir / Path(self.git("rev-parse", "--git-dir").decode())

        # XXX(nika): Does it make more sense to cache these or call every time?
        # Cache for length of time & invalidate?
        self.default_author = Signature(self.git("var", "GIT_AUTHOR_IDENT"))
        self.default_committer = Signature(self.git("var", "GIT_COMMITTER_IDENT"))

        self.index = Index(self)

        self.sign_commits = self.bool_config(
            "revise.gpgSign", default=self.bool_config("commit.gpgSign", default=False)
        )

        self.gpg = self.config("gpg.program", default=b"gpg")

        # Pylint 2.8 emits a false positive; fixed in 2.9.
        self._catfile = Popen(  # pylint: disable=consider-using-with
            ["git", "cat-file", "--batch"],
            bufsize=-1,
            stdin=PIPE,
            stdout=PIPE,
            cwd=self.workdir,
        )
        self._objects = defaultdict(dict)

        # Check that cat-file works OK
        try:
            self.get_obj(Oid.null())
            raise IOError("cat-file backend failure")
        except MissingObject:
            pass

    def git(
        self,
        *cmd: str,
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        stdin: Optional[bytes] = None,
        stdout: _FILE = PIPE,
        trim_newline: bool = True,
    ) -> bytes:
        pass

    def config(self, setting: str, default: T) -> Union[bytes, T]:
        pass

    def bool_config(self, config: str, default: T) -> Union[bool, T]:
        pass

    def int_config(self, config: str, default: T) -> Union[int, T]:
        pass

    def __enter__(self) -> Repository:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[Exception],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if self._tempdir:
            self._tempdir.__exit__(exc_type, exc_val, exc_tb)

        self._catfile.terminate()
        self._catfile.wait()

    def get_tempdir(self) -> Path:
        """Return a temporary directory to use for modifications to this repository"""
        pass

    def git_path(self, path: Union[str, Path]) -> Path:
        """Get the path to a file in the .git directory, respecting the environment"""
        pass

    def new_commit(
        self,
        tree: Tree,
        parents: Sequence[Commit],
        message: bytes,
        author: Optional[Signature] = None,
        committer: Optional[Signature] = None,
    ) -> Commit:
        """Directly create an in-memory commit object, without persisting it.
        If a commit object with these properties already exists, it will be
        returned instead."""
        pass

    def sign_buffer(self, buffer: bytes) -> bytes:
        """Return the text of the signed commit object."""
        pass

    def new_tree(self, entries: Mapping[bytes, Entry]) -> Tree:
        """Directly create an in-memory tree object, without persisting it.
        If a tree object with these entries already exists, it will be
        returned instead."""

        pass

    def get_obj(self, ref: Union[Oid, str]) -> GitObj:
        """Get the identified git object from this repository. If given an
        :class:`Oid`, the cache will be checked before asking git."""
        pass

    def get_commit(self, ref: Union[Oid, str]) -> Commit:
        """Like :py:meth:`get_obj`, but returns a :class:`Commit`"""
        pass

    def get_tree(self, ref: Union[Oid, str]) -> Tree:
        """Like :py:meth:`get_obj`, but returns a :class:`Tree`"""
        pass

    def get_blob(self, ref: Union[Oid, str]) -> Blob:
        """Like :py:meth:`get_obj`, but returns a :class:`Blob`"""
        pass

    def get_obj_ref(self, ref: str) -> Reference[GitObj]:
        """Get a :class:`Reference` to a :class:`GitObj`"""
        pass

    def get_commit_ref(self, ref: str) -> Reference[Commit]:
        """Get a :class:`Reference` to a :class:`Commit`"""
        pass

    def get_tree_ref(self, ref: str) -> Reference[Tree]:
        """Get a :class:`Reference` to a :class:`Tree`"""
        pass

    def get_blob_ref(self, ref: str) -> Reference[Blob]:
        """Get a :class:`Reference` to a :class:`Blob`"""
        pass


GitObjT = TypeVar("GitObjT", bound="GitObj")


class GitObj:
    """In-memory representation of a git object. Instances of this object
    should be one of :class:`Commit`, :class:`Tree` or :class:`Blob`"""

    repo: Repository
    """:class:`Repository` object is associated with"""

    body: bytes
    """Raw body of object in bytes"""

    oid: Oid
    """:class:`Oid` of this git object"""

    persisted: bool
    """If ``True``, the object has been persisted to disk"""

    __slots__ = ("repo", "body", "oid", "persisted")

    def __new__(cls, repo: Repository, body: bytes) -> "Self":
        oid = Oid.for_object(cls._git_type(), body)
        cache = repo._objects[oid[0]]  # pylint: disable=protected-access
        if oid in cache:
            cached = cache[oid]
            assert isinstance(cached, cls)
            return cached

        self = super().__new__(cls)
        self.repo = repo
        self.body = body
        self.oid = oid
        self.persisted = False
        cache[oid] = self
        self._parse_body()  # pylint: disable=protected-access
        return self

    @classmethod
    def _git_type(cls) -> str:
        pass

    def persist(self) -> Oid:
        """If this object has not been persisted to disk yet, persist it"""
        pass

    def _persist_deps(self) -> None:
        pass

    def _parse_body(self) -> None:
        pass

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GitObj):
            return self.oid == other.oid
        return False


class Commit(GitObj):
    """In memory representation of a git ``commit`` object"""

    tree_oid: Oid
    """:class:`Oid` of this commit's ``tree`` object"""

    parent_oids: Sequence[Oid]
    """List of :class:`Oid` for this commit's parents"""

    author: Signature
    """:class:`Signature` of this commit's author"""

    committer: Signature
    """:class:`Signature` of this commit's committer"""

    gpgsig: Optional[bytes]
    """GPG signature of this commit"""

    message: bytes
    """Body of this commit's message"""

    __slots__ = ("tree_oid", "parent_oids", "author", "committer", "gpgsig", "message")

    def _parse_body(self) -> None:
        # Split the header from the core commit message.
        pass

    def tree(self) -> Tree:
        """``tree`` object corresponding to this commit"""
        pass

    def parent_tree(self) -> Tree:
        """``tree`` object corresponding to the first parent of this commit,
        or the null tree if this is a root commit"""
        pass

    @property
    def is_root(self) -> bool:
        """Whether this commit has no parents"""
        pass

    def parents(self) -> Sequence[Commit]:
        """List of parent commits"""
        pass

    def parent(self) -> Commit:
        """Helper method to get the single parent of a commit. Raises
        :class:`ValueError` if the incorrect number of parents are
        present."""
        pass

    def summary(self) -> str:
        """The summary line of the commit message. Returns the summary
        as a single line, even if it spans multiple lines."""
        pass

    def rebase(self, parent: Optional[Commit]) -> Commit:
        """Create a new commit with the same changes, except with ``parent``
        as its parent. If ``parent`` is ``None``, this becomes a root commit."""
        pass

    def update(
        self,
        tree: Optional[Tree] = None,
        parents: Optional[Sequence[Commit]] = None,
        message: Optional[bytes] = None,
        author: Optional[Signature] = None,
        recommit: bool = False,
    ) -> Commit:
        """Create a new commit with specific properties updated or replaced"""
        # Compute parameters used to create the new object.
        pass

    def _persist_deps(self) -> None:
        pass

    def __repr__(self) -> str:
        return (
            f"<Commit {repr(self.oid)} "
            f"tree={repr(self.tree_oid)}, parents={repr(self.parent_oids)}, "
            f"author={repr(self.author)}, committer={repr(self.committer)}>"
        )


class Mode(Enum):
    """Mode for an entry in a ``tree``"""

    GITLINK = b"160000"
    """submodule entry"""

    SYMLINK = b"120000"
    """symlink entry"""

    DIR = b"40000"
    """directory entry"""

    REGULAR = b"100644"
    """regular entry"""

    EXEC = b"100755"
    """executable entry"""

    def is_file(self) -> bool:
        pass

    def comparable_to(self, other: Mode) -> bool:
        pass


class Entry:
    """In memory representation of a single ``tree`` entry"""

    repo: Repository
    """:class:`Repository` this entry originates from"""

    mode: Mode
    """:class:`Mode` of the entry"""

    oid: Oid
    """:class:`Oid` of this entry's object"""

    __slots__ = ("repo", "mode", "oid")

    def __init__(self, repo: Repository, mode: Mode, oid: Oid) -> None:
        self.repo = repo
        self.mode = mode
        self.oid = oid

    def blob(self) -> Blob:
        """Get the data for this entry as a :class:`Blob`"""
        pass

    def symlink(self) -> bytes:
        """Get the data for this entry as a symlink"""
        pass

    def tree(self) -> Tree:
        """Get the data for this entry as a :class:`Tree`"""
        pass

    def persist(self) -> None:
        """:py:meth:`GitObj.persist` the git object referenced by this entry"""
        pass

    def __repr__(self) -> str:
        return f"<Entry {self.mode}, {self.oid}>"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Entry):
            return self.mode == other.mode and self.oid == other.oid
        return False


class Tree(GitObj):
    """In memory representation of a git ``tree`` object"""

    entries: Dict[bytes, Entry]
    """mapping from entry names to entry objects in this tree"""

    __slots__ = ("entries",)

    def _parse_body(self) -> None:
        pass

    def _persist_deps(self) -> None:
        pass

    def to_index(self, path: Path, skip_worktree: bool = False) -> Index:
        """Read tree into a temporary index. If skip_workdir is ``True``, every
        entry in the index will have its "Skip Workdir" bit set."""

        pass

    def __repr__(self) -> str:
        return f"<Tree {self.oid} ({len(self.entries)} entries)>"


class Blob(GitObj):
    """In memory representation of a git ``blob`` object"""

    __slots__ = ()

    def __repr__(self) -> str:
        return f"<Blob {self.oid} ({len(self.body)} bytes)>"


class Index:
    """Handle on an index file"""

    repo: Repository
    """"""

    index_file: Path
    """Index file being referenced"""

    def __init__(self, repo: Repository, index_file: Optional[Path] = None) -> None:
        self.repo = repo

        if index_file is None:
            index_file = self.repo.git_path("index")
        self.index_file = index_file

        assert self.git("rev-parse", "--git-path", "index").decode() == str(index_file)

    def git(
        self,
        *cmd: str,
        cwd: Optional[Path] = None,
        env: Optional[Mapping[str, str]] = None,
        stdin: Optional[bytes] = None,
        stdout: _FILE = PIPE,
        trim_newline: bool = True,
    ) -> bytes:
        """Invoke git with the given index as active"""
        pass

    def tree(self) -> Tree:
        """Get a :class:`Tree` object for this index's state"""
        pass

    def commit(
        self, message: bytes = b"<git index>", parent: Optional[Commit] = None
    ) -> Commit:
        """Get a :class:`Commit` for this index's state. If ``parent`` is
        ``None``, use the current ``HEAD``"""

        pass


class Reference(Generic[GitObjT]):  # pylint: disable=unsubscriptable-object
    """A git reference"""

    shortname: str
    """Short unresolved reference name, e.g. 'HEAD' or 'master'"""

    name: str
    """Resolved reference name, e.g. 'refs/tags/1.0.0' or 'refs/heads/master'"""

    target: Optional[GitObjT]
    """Referenced git object"""

    repo: Repository
    """Repository reference is attached to"""

    _type: Type[GitObjT]

    # FIXME: On python 3.6, pylint doesn't know what to do with __slots__ here.
    # __slots__ = ("name", "target", "repo", "_type")

    def __init__(self, obj_type: Type[GitObjT], repo: Repository, name: str) -> None:
        self._type = obj_type

        self.name = name
        try:
            # Silently verify that a ref with the name exists and recover if it
            # doesn't.
            repo.git("show-ref", "--quiet", "--verify", self.name)
        except CalledProcessError:
            # `name` could be a branch name which can be resolved to a ref. Try
            # to do so with `rev-parse`, and verify that the new name exists.
            self.name = repo.git(
                "rev-parse", "--symbolic-full-name", self.name
            ).decode()
            repo.git("show-ref", "--verify", self.name)

        self.repo = repo
        self.refresh()

    def refresh(self) -> None:
        """Re-read the target of this reference from disk"""
        pass

    def update(self, new: GitObjT, reason: str) -> None:
        """Update this refreence to point to a new object.
        An entry with the reason ``reason`` will be added to the reflog."""
        pass
