#!/usr/bin/env python

from fs.opener.base import Opener
from fs.opener.registry import registry
from fs.opener.parse import ParseResult

__all__ = ["GitOpener"]


@registry.install
class GitOpener(Opener):
    protocols = ["git"]

    def open_fs(
        self,
        fs_url: str,
        parse_result: ParseResult,
        writeable: bool,
        create: bool,
        cwd: str,
    ):
        from fs.gitfs import GitFS

        git_fs = GitFS(parse_result.resource)
        return git_fs
