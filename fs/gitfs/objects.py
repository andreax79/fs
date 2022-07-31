#!/usr/bin/env python

from git import Repo
from fs.path import split
from fs.info import Info
from fs.enums import ResourceType
from fs.permissions import Permissions
from typing import (
    Callable,
    Collection,
    Dict,
    Iterator,
    Optional,
)
from fs.gitfs.gitfile import GitFile

__all__ = [
    "GitInfo",
    "GitObject",
    "VDir",
    "Blob",
    "TreeDir",
    "RefsDir",
    "RemotesDir",
    "ObjectsDir",
    "RootDir",
]


class GitInfo(Info):
    "Container for resource informations"

    def __init__(self, git_obj: "GitObject", name: Optional[str] = None) -> None:
        self.git_obj = git_obj
        raw_info: Dict[str, Dict[str, object]] = {
            "basic": {
                "name": git_obj.name or name,
                "is_dir": git_obj.type != "blob",
            },
            "details": {
                "type": int(
                    ResourceType.directory
                    if git_obj.type != "blob"
                    else ResourceType.file
                ),
                "size": git_obj.size,
            },
            "access": {
                "permissions": Permissions(mode=git_obj.mode).dump(),
            },
        }
        return super().__init__(raw_info)

    def is_writeable(self, namespace: str, key: str) -> bool:
        "Check if a given key in a namespace is writable"
        return False


class GitObject:
    "Abstract Git object"
    name: str = ""
    type: str = ""
    size: int = 0
    mode: int = 0

    def getinfo(self, namespaces: Optional[Collection[str]] = None) -> Info:
        "Get information about this resource"
        raise NotImplementedError

    def get(self, name: str) -> "GitObject":
        raise NotImplementedError

    def scandir(self) -> Iterator[Info]:
        "Get an iterator of resource info"
        raise NotImplementedError

    def openbin(self) -> GitFile:
        raise NotImplementedError


class VDir(GitObject):
    "Git 'virtual' directory"

    def __init__(self, name):
        self.name = name
        self.type = "dir"
        self.size = 0
        self.mode = 16384

    def getinfo(self, namespaces: Optional[Collection[str]] = None) -> Info:
        "Get information about this resource"
        return GitInfo(self)


class Blob(GitObject):
    "Git blob"

    def __init__(self, blob):
        self.blob = blob

    def getinfo(self, namespaces: Optional[Collection[str]] = None) -> Info:
        "Get information about this resource"
        return GitInfo(self.blob)

    def openbin(self) -> GitFile:
        return GitFile(self.blob)


class TreeDir(GitObject):
    "Git tree"

    def __init__(self, name: str, commit, tree=None):
        self.name = name
        self.commit = commit
        if tree is None:
            self.tree = commit.tree
        else:
            self.tree = tree

    def getinfo(self, namespaces: Optional[Collection[str]] = None) -> Info:
        "Get information about this resource"
        return GitInfo(self.tree, name=self.name)

    def get(self, name: str) -> GitObject:
        git_obj = self.tree[name]
        if git_obj.type == "blob":
            return Blob(git_obj)
        else:
            return TreeDir(name=name, commit=self.commit, tree=git_obj)

    def scandir(self) -> Iterator[Info]:
        "Get an iterator of resource info"
        for tree in self.tree.trees:
            yield GitInfo(tree)
        for blob in self.tree.blobs:
            yield GitInfo(blob)


class RefsDir(VDir):
    "Git refs (tags, branch, remotes) directory"

    def __init__(self, name: str, refs):
        super().__init__(name)
        self.refs = refs

    def get(self, name: str) -> GitObject:
        commit = self.refs[name].commit
        return TreeDir(name=name, commit=commit)

    def scandir(self) -> Iterator[Info]:
        "Get an iterator of resource info"
        for ref in self.refs:
            _, name = split(ref.name)
            yield GitInfo(ref.commit.tree, name=name)


class RemotesDir(VDir):
    "Git remotes directory"

    def __init__(self, name: str, remotes):
        super().__init__(name)
        self.remotes = remotes

    def get(self, name: str) -> GitObject:
        return RefsDir(name, self.remotes[name].refs)

    def scandir(self) -> Iterator[Info]:
        "Get an iterator of resource info"
        for ref in self.remotes:
            yield RefsDir(ref.name, ref.refs).getinfo()


class ObjectsDir(VDir):
    "Git objects directory"

    def __init__(self, name: str, repo: Repo):
        super().__init__(name)
        self.repo = repo

    def get(self, name: str) -> GitObject:
        return RefsDir(name, self.remotes[name].refs)

    # def scandir(self) -> Iterator[Info]:
    #     "Get an iterator of resource info"
    #     for sha in self.repo.odb.sha_iter():
    #         info = self.repo.odb.info(sha)
    #         name = bin_to_hex(sha).decode('ascii')
    #         # yield RefsDir(ref.name, ref.refs).getinfo()


class RootDir(VDir):
    "Git root directory"

    children: Dict[str, Callable[[Repo], GitObject]] = {
        "head": lambda repo: TreeDir("head", repo.head.commit),
        "tags": lambda repo: RefsDir("tags", repo.tags),
        "branches": lambda repo: RefsDir("branches", repo.branches),
        "remotes": lambda repo: RemotesDir("remotes", repo.remotes),
        "objects": lambda repo: ObjectsDir("objects", repo),
    }

    def __init__(self, repo):
        super().__init__("/")
        self.repo = repo

    def get(self, name: str) -> GitObject:
        fn = self.children[name]
        return fn(self.repo)

    def scandir(self) -> Iterator[Info]:
        "Get an iterator of resource info"
        for name, fn in self.children.items():
            yield fn(self.repo).getinfo()
