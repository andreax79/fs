#!/usr/bin/env python

import itertools
from git import Repo
from fs.base import FS
from fs.info import Info
from fs.errors import (
    ResourceNotFound,
    DirectoryExpected,
    FileExpected,
    ResourceReadOnly,
)
from typing import (
    Any,
    BinaryIO,
    Collection,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
)
from fs.gitfs.objects import GitObject, RootDir


__all__ = ["GitFS"]


class GitFS(FS):
    "Git Filesystem"

    _meta: Dict[str, Any] = {
        "case_insensitive": False,
        "invalid_path_chars": "\0",
        "max_path_length": None,
        "max_sys_path_length": None,
        "network": False,
        "read_only": True,
        "supports_rename": False,
        "thread_safe": True,
        "unicode_paths": True,
        "virtual": False,
    }

    def __init__(self, repo_path: str) -> None:
        super().__init__()
        self.repo_path = repo_path
        self.repo = Repo(repo_path)

    def __repr__(self) -> str:
        return f"GitFS({self.repo_path})"

    def __str__(self) -> str:
        return f"<gitfs '{self.repo_path}'>"

    def _get_obj_by_path(self, path: str) -> GitObject:
        path = path.strip("/")
        try:
            obj: GitObject = RootDir(self.repo)
            if path:
                for part in path.split("/"):
                    obj = obj.get(part)
            return obj
        except (IndexError, KeyError, NotImplementedError):
            raise ResourceNotFound(path)

    def exists(self, path: str) -> bool:
        """Check if a path maps to a resource.

        Arguments:
            path (str): Path to a resource.

        Returns:
            bool: `True` if a resource exists at the given path.
        """
        try:
            self._get_obj_by_path(path)
            return True
        except ResourceNotFound:
            return False

    def getinfo(self, path: str, namespaces: Optional[Collection[str]] = None) -> Info:
        """Get information about a resource on a filesystem.

        Arguments:
            path (str): A path to a resource on the filesystem.
            namespaces (list, optional): Info namespaces to query. The
                `"basic"` namespace is alway included in the returned
                info, whatever the value of `namespaces` may be.

        Returns:
            ~fs.info.Info: resource information object.

        Raises:
            fs.errors.ResourceNotFound: If ``path`` does not exist.
        """
        obj: GitObject = self._get_obj_by_path(path)
        return obj.getinfo(namespaces)

    def getmeta(self, namespace: str = "standard") -> Dict[str, Any]:
        """Get meta information regarding a filesystem.

        Arguments:
            namespace (str): The meta namespace (defaults
                to ``"standard"``).

        Returns:
            dict: the meta information.
        """
        result: Dict[str, Any] = {}
        if namespace == "standard":
            result = self._meta.copy()
        return result

    def listdir(self, path: str) -> List[str]:
        """Get a list of the resource names in a directory.

        This method will return a list of the resources in a directory.
        A *resource* is a file, directory, or one of the other types
        defined in `~fs.enums.ResourceType`.

        Arguments:
            path (str): A path to a directory on the filesystem

        Returns:
            list: list of names, relative to ``path``.

        Raises:
            fs.errors.DirectoryExpected: If ``path`` is not a directory.
            fs.errors.ResourceNotFound: If ``path`` does not exist.
        """
        obj: GitObject = self._get_obj_by_path(path)
        try:
            return [x.name for x in obj.scandir()]
        except NotImplementedError:
            raise DirectoryExpected(path)

    def scandir(
        self,
        path: str,
        namespaces: Optional[Collection[str]] = None,
        page: Optional[Tuple[int, int]] = None,
    ) -> Iterator[Info]:
        """Get an iterator of resource info.

        Arguments:
            path (str): A path to a directory on the filesystem.
            namespaces (list, optional): A list of namespaces to include
                in the resource information, e.g. ``['basic', 'access']``.
            page (tuple, optional): May be a tuple of ``(<start>, <end>)``
                indexes to return an iterator of a subset of the resource
                info, or `None` to iterate over the entire directory.
                Paging a directory scan may be necessary for very large
                directories.

        Returns:
            ~collections.abc.Iterator: an iterator of `Info` objects.

        Raises:
            fs.errors.DirectoryExpected: If ``path`` is not a directory.
            fs.errors.ResourceNotFound: If ``path`` does not exist.

        """
        obj: GitObject = self._get_obj_by_path(path)
        if not hasattr(obj, "scandir"):
            raise DirectoryExpected(path)
        result: Iterator[Info] = obj.scandir()
        if page is not None:
            start, end = page
            result = itertools.islice(result, start, end)
        return result

    def openbin(
        self, path: str, mode: str = "r", buffering: int = -1, **options: Any
    ) -> BinaryIO:
        """Open a binary file-like object.

        Arguments:
            path (str): A path on the filesystem.
            mode (str): Mode to open file (must be a valid non-text mode,
                defaults to *r*). Since this method only opens binary files,
                the ``b`` in the mode string is implied.
            buffering (int): Buffering policy (-1 to use default buffering,
                0 to disable buffering, or any positive integer to indicate
                a buffer size).
            **options: keyword arguments for any additional information
                required by the filesystem (if any).

        Returns:
            io.IOBase: a *file-like* object.

        Raises:
            fs.errors.FileExpected: If ``path`` exists and is not a file.
            fs.errors.FileExists: If the ``path`` exists, and
                *exclusive mode* is specified (``x`` in the mode).
            fs.errors.ResourceNotFound: If ``path`` does not exist and
                ``mode`` does not imply creating the file, or if any
                ancestor of ``path`` does not exist.
        """
        path = self.validatepath(path)
        obj: GitObject = self._get_obj_by_path(path)
        try:
            return obj.openbin()
        except NotImplementedError:
            raise FileExpected(path)

    def makedir(self, path, permissions=None, recreate=False):
        raise ResourceReadOnly(path)

    def remove(self, path):
        raise ResourceReadOnly(path)

    def removedir(self, path):
        raise ResourceReadOnly(path)

    def setinfo(self, path, info):
        raise ResourceReadOnly(path)
