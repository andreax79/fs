#!/usr/bin/env python


def test_import_gitfs():
    import fs.gitfs
    import fs.gitfs.gitfs

    assert fs.gitfs
    assert fs.gitfs.gitfs


def test_import_gitfile():
    import fs.gitfs.gitfile

    assert fs.gitfs.gitfile


def test_import_objects():
    import fs.gitfs.objects

    assert fs.gitfs.objects


def test_import_openenr():
    import fs.gitfs.opener

    assert fs.gitfs.opener
