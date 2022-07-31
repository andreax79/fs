#!/usr/bin/env python

import io
from typing import Any

__all__ = ["GitFile"]


class GitFile(io.BytesIO):
    def __init__(self, blob):
        data = blob.repo.odb.stream(blob.binsha).read()
        super().__init__(data)

    def readable(self) -> bool:
        return True

    def writable(self) -> bool:
        return False

    def write(self, data: Any) -> int:
        raise io.UnsupportedOperation("write")

    def writelines(self, lines: Any) -> None:
        raise io.UnsupportedOperation("write")
