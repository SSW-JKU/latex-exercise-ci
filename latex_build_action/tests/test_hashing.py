# pylint: disable=missing-module-docstring

from typing import Tuple
import unittest

from pathlib import Path
from latex_build_action.hashing import (
    hash_directory,
    read_cached_dirhash,
    cache_dirhash,
    check_dirhash,
    check_and_update_hash,
)
from ._test_utils import FakeFileSystemTestCase, dont_call


class TestHashing(FakeFileSystemTestCase):
    # pylint: disable=missing-class-docstring
    def create_file_structure(self) -> None:
        # pylint: disable=missing-function-docstring
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
        # pylint: disable=missing-function-docstring
        h = hash_directory(Path("testdir"))
        self.assertEqual(h, hash_directory(Path("testdir")))
        self.assertNotEqual(h, hash_directory(Path("testdir", "testsubdir1")))

    def test_hash_skips_ignored_files(self) -> None:
        # pylint: disable=missing-function-docstring
        old_hash = hash_directory(Path("testdir"))
        ignored_hash = hash_directory(Path("testdir"), ignore=["*.notexextension"])
        file_to_remove = Path(
            "testdir", "testsubdir1", "testsubsubdir", "texfile5.notexextension"
        )

        file_to_remove.unlink()

        removed_file_hash = hash_directory(Path("testdir"))
        self.assertNotEqual(old_hash, ignored_hash)
        self.assertEqual(ignored_hash, removed_file_hash)

    def test_hash_detect_changes(self) -> None:
        # pylint: disable=missing-function-docstring
        old_hash = hash_directory(Path("testdir"))

        with open(Path("testdir", "texfile1.tex"), "w+", encoding="UTF-8") as f:
            f.write("some other content")

        self.assertNotEqual(old_hash, hash_directory(Path("testdir")))

    def test_read_cached_dirhash_exists(self) -> None:
        # pylint: disable=missing-function-docstring
        self.file(Path("testdir", ".checksum"), "somehash")
        self.assertEqual("somehash", read_cached_dirhash(Path("testdir")))

    def test_read_cached_dirhash_no_file(self) -> None:
        # pylint: disable=missing-function-docstring
        self.assertIsNone(read_cached_dirhash(Path("testdir")))

    def test_cache_dirhash(self) -> None:
        # pylint: disable=missing-function-docstring

        self.assertFalse(Path("testdir", ".checksum").exists())
        cache_dirhash(Path("testdir"), "my-custom-hash")
        self.assertTrue(Path("testdir", ".checksum").is_file())
        with open(Path("testdir", ".checksum"), "r", encoding="UTF-8") as f:
            self.assertEqual(f.read(), "my-custom-hash")

    def test_check_dirhash_existing_hash(self) -> None:
        # pylint: disable=missing-function-docstring
        existing_hash = hash_directory(Path("testdir"))
        self.file(Path("testdir", ".checksum"), existing_hash)

        same_hash, new_hash = check_dirhash(Path("testdir"))

        self.assertTrue(same_hash)
        self.assertEqual(existing_hash, new_hash)

    def test_check_dirhash_wrong_hash(self) -> None:
        # pylint: disable=missing-function-docstring
        existing_hash = hash_directory(Path("testdir"))
        self.file(Path("testdir", ".checksum"), "asdfasdfs")

        same_hash, new_hash = check_dirhash(Path("testdir"))

        self.assertFalse(same_hash)
        self.assertEqual(existing_hash, new_hash)

    def test_check_dirhash_no_hash_file(self) -> None:
        # pylint: disable=missing-function-docstring
        existing_hash = hash_directory(Path("testdir"))

        self.assertFalse(Path("testdir", ".checksum").exists())

        same_hash, new_hash = check_dirhash(Path("testdir"))

        self.assertFalse(same_hash)
        self.assertEqual(existing_hash, new_hash)

    def test_check_and_update_hash_hash_changed(self) -> None:
        # pylint: disable=missing-function-docstring
        old_hash = hash_directory(Path("testdir"))
        self.file(Path("testdir", ".checksum"), old_hash)
        self.file(Path("testdir", "lol"), "lol")

        proof = []

        def must_be_called() -> Tuple[bool, str]:
            proof.append("success")
            return True, "success"

        result = check_and_update_hash(Path("testdir"), must_be_called)

        with open(Path("testdir", ".checksum"), "r", encoding="UTF-8") as checksum:
            new_hash = hash_directory(Path("testdir"))
            self.assertNotEqual(old_hash, new_hash)
            self.assertEqual(checksum.read(), new_hash)

            self.assertEqual(result, "success")
            self.assertEqual(proof, ["success"])

    def test_check_and_update_hash_hash_changed_no_caching(self) -> None:
        # pylint: disable=missing-function-docstring
        old_hash = hash_directory(Path("testdir"))
        self.file(Path("testdir", ".checksum"), old_hash)

        self.file(Path("testdir", "lol"), "lol")

        proof = []

        def must_be_called() -> Tuple[bool, str]:
            proof.append("success")
            return False, "success"

        result = check_and_update_hash(Path("testdir"), must_be_called)

        with open(Path("testdir", ".checksum"), "r", encoding="UTF-8") as checksum:
            self.assertEqual(checksum.read(), old_hash)

            self.assertEqual(result, "success")
            self.assertEqual(proof, ["success"])

    def test_check_and_update_hash_no_change(self) -> None:
        # pylint: disable=missing-function-docstring
        self.file(Path("testdir", ".checksum"), hash_directory(Path("testdir")))

        result = check_and_update_hash(Path("testdir"), dont_call)

        self.assertIsNone(result)

    def test_check_and_update_hash_dont_overwrite(self) -> None:
        # pylint: disable=missing-function-docstring
        self.file(Path("testdir", ".checksum"), hash_directory(Path("testdir")))

        result = check_and_update_hash(Path("testdir"), dont_call)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
