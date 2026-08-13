#!/usr/bin/env python

import unittest
from pathlib import Path

from latex_build_action.hashing import (
    cache_dirhash,
    check_and_update_hash,
    check_dirhash,
    hash_directory,
    read_cached_dirhash,
)

from ._test_utils import FakeFileSystemTestCase


def _should_not_be_called[R](_: R | None = None) -> tuple[bool, R]:
    """Asserts that this callback is never actually invoked."""
    msg = "should not be called"
    raise AssertionError(msg)


class TestHashing(FakeFileSystemTestCase):
    def create_file_structure(self) -> None:
        testdir = Path("testdir")
        subdir1 = testdir.joinpath("testsubdir1")
        subdir2 = testdir.joinpath("testsubdir2")
        subsubdir = subdir1.joinpath("testsubsubdir")

        subsubdir.mkdir(parents=True)
        subdir2.mkdir(parents=True)

        self.file(testdir.joinpath("texfile1.tex"), "foo")
        self.file(subdir1.joinpath("texfile2.tex"), "bar")
        self.file(subdir1.joinpath("texfile3.tex"), "baz")
        self.file(subdir2.joinpath("texfile4.tex"), "___")
        self.file(subsubdir.joinpath("texfile5.notexextension"), "asdfasdf")

    def test_hash_deterministic(self) -> None:
        h = hash_directory(Path("testdir"))
        assert h == hash_directory(Path("testdir"))
        assert h != hash_directory(Path("testdir", "testsubdir1"))

    def test_hash_skips_ignored_files(self) -> None:
        old_hash = hash_directory(Path("testdir"))
        ignored_hash = hash_directory(Path("testdir"), ignore=["*.notexextension"])
        file_to_remove = Path("testdir", "testsubdir1", "testsubsubdir", "texfile5.notexextension")

        file_to_remove.unlink()

        removed_file_hash = hash_directory(Path("testdir"))
        assert old_hash != ignored_hash
        assert ignored_hash == removed_file_hash

    def test_hash_detect_changes(self) -> None:
        old_hash = hash_directory(Path("testdir"))

        with Path("testdir", "texfile1.tex").open("w+", encoding="UTF-8") as f:
            f.write("some other content")

        assert old_hash != hash_directory(Path("testdir"))

    def test_read_cached_dirhash_exists(self) -> None:
        self.file(Path("testdir", ".checksum"), "somehash")
        assert read_cached_dirhash(Path("testdir")) == "somehash"

    def test_read_cached_dirhash_no_file(self) -> None:
        assert read_cached_dirhash(Path("testdir")) is None

    def test_cache_dirhash(self) -> None:
        assert not Path("testdir", ".checksum").exists()
        cache_dirhash(Path("testdir"), "my-custom-hash")
        assert Path("testdir", ".checksum").is_file()
        with Path("testdir", ".checksum").open(encoding="UTF-8") as f:
            assert f.read() == "my-custom-hash"

    def test_check_dirhash_existing_hash(self) -> None:
        existing_hash = hash_directory(Path("testdir"))
        self.file(Path("testdir", ".checksum"), existing_hash)

        same_hash, new_hash = check_dirhash(Path("testdir"))

        assert same_hash
        assert existing_hash == new_hash

    def test_check_dirhash_wrong_hash(self) -> None:
        existing_hash = hash_directory(Path("testdir"))
        self.file(Path("testdir", ".checksum"), "asdfasdfs")

        same_hash, new_hash = check_dirhash(Path("testdir"))

        assert not same_hash
        assert existing_hash == new_hash

    def test_check_dirhash_no_hash_file(self) -> None:
        existing_hash = hash_directory(Path("testdir"))

        assert not Path("testdir", ".checksum").exists()

        same_hash, new_hash = check_dirhash(Path("testdir"))

        assert not same_hash
        assert existing_hash == new_hash

    def test_check_and_update_hash_hash_changed(self) -> None:
        old_hash = hash_directory(Path("testdir"))
        self.file(Path("testdir", ".checksum"), old_hash)
        self.file(Path("testdir", "lol"), "lol")

        proof: list[str] = []

        def must_be_called() -> tuple[bool, str]:
            proof.append("success")
            return True, "success"

        result = check_and_update_hash(Path("testdir"), must_be_called)

        with Path("testdir", ".checksum").open(encoding="UTF-8") as checksum:
            new_hash = hash_directory(Path("testdir"))
            assert old_hash != new_hash
            assert checksum.read() == new_hash

            assert result == "success"
            assert proof == ["success"]

    def test_check_and_update_hash_hash_changed_no_caching(self) -> None:
        old_hash = hash_directory(Path("testdir"))
        self.file(Path("testdir", ".checksum"), old_hash)

        self.file(Path("testdir", "lol"), "lol")

        proof: list[str] = []

        def must_be_called() -> tuple[bool, str]:
            proof.append("success")
            return False, "success"

        result = check_and_update_hash(Path("testdir"), must_be_called)

        with Path("testdir", ".checksum").open(encoding="UTF-8") as checksum:
            assert checksum.read() == old_hash

            assert result == "success"
            assert proof == ["success"]

    def test_check_and_update_hash_no_change(self) -> None:
        self.file(Path("testdir", ".checksum"), hash_directory(Path("testdir")))

        result = check_and_update_hash(Path("testdir"), _should_not_be_called)

        assert result is None

    def test_check_and_update_hash_dont_overwrite(self) -> None:
        self.file(Path("testdir", ".checksum"), hash_directory(Path("testdir")))

        result = check_and_update_hash(Path("testdir"), _should_not_be_called)

        assert result is None


if __name__ == "__main__":
    unittest.main()
