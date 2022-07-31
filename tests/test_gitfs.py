#!/usr/bin/env python

from pathlib import Path
import io
import pytest
import fs.gitfs.opener
import fs
from fs.errors import (
    ResourceNotFound,
    DirectoryExpected,
    FileExpected,
)

git_path = Path(__file__).parent.parent


def test_open_fs():
    git_fs = fs.open_fs(f"git://{git_path}")
    assert "gitfs" in str(git_fs)
    assert "GitFS" in repr(git_fs)
    assert git_fs.getmeta()["read_only"]
    assert not git_fs.getmeta("x")


def test_paths():
    git_fs = fs.open_fs(f"git://{git_path}")
    assert not git_fs.exists("/----")
    assert not git_fs.exists("/head/----")

    assert git_fs.exists("/")
    info = git_fs.getinfo("/")
    assert info.is_dir
    assert not info.is_writeable("namespace", "key")

    assert git_fs.exists("/head")
    info = git_fs.getinfo("/head")
    assert info.is_dir

    assert git_fs.exists("/head/fs")
    info = git_fs.getinfo("/head/fs")
    assert info.is_dir

    assert git_fs.exists("/head/fs/gitfs")
    info = git_fs.getinfo("/head/fs/gitfs")
    assert info.is_dir

    assert git_fs.exists("/branches")
    info = git_fs.getinfo("/branches")
    assert info.is_dir

    assert git_fs.exists("/remotes")
    info = git_fs.getinfo("/remotes")
    assert info.is_dir


def test_file():
    git_fs = fs.open_fs(f"git://{git_path}")
    assert not git_fs.isdir("head/LICENSE")
    assert "MIT License" in git_fs.readtext("head/LICENSE")
    info = git_fs.getinfo("head/LICENSE")
    assert not info.is_dir
    with pytest.raises(FileExpected):
        git_fs.readtext("head")
    with pytest.raises(ResourceNotFound):
        git_fs.readtext("---")
    with pytest.raises(ResourceNotFound):
        git_fs.readtext("/branches/---")
    with pytest.raises(ResourceNotFound):
        git_fs.readtext("/remotes/---")
    with pytest.raises(io.UnsupportedOperation):
        git_fs.writetext("head/LICENSE", "test")


def test_listdir():
    git_fs = fs.open_fs(f"git://{git_path}")
    assert "head" in git_fs.listdir("/")
    assert "fs" in git_fs.listdir("/head")
    assert "gitfs" in git_fs.listdir("/head/fs")
    with pytest.raises(DirectoryExpected):
        git_fs.listdir("/head/LICENSE")
    with pytest.raises(ResourceNotFound):
        git_fs.listdir("/head/---")
