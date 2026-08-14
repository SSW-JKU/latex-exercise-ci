#!/usr/bin/env python

from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from latex_build_action.hashing import (
    cache_dirhash,
    check_and_update_hash,
    check_dirhash,
    hash_directory,
    read_cached_dirhash,
)

from ._test_utils import file


def _should_not_be_called[R](_: R | None = None) -> tuple[bool, R]:
    """Asserts that this callback is never actually invoked."""
    msg = "should not be called"
    raise AssertionError(msg)


@pytest.fixture
def setup_filesystem(fs: FakeFilesystem) -> None:
    testdir = Path("testdir")
    fs.create_dir(testdir)
    subdir1 = testdir.joinpath("testsubdir1")
    subdir2 = testdir.joinpath("testsubdir2")
    subsubdir = subdir1.joinpath("testsubsubdir")

    subsubdir.mkdir(parents=True)
    subdir2.mkdir(parents=True)

    file(testdir.joinpath("texfile1.tex"), "foo")
    file(subdir1.joinpath("texfile2.tex"), "bar")
    file(subdir1.joinpath("texfile3.tex"), "baz")
    file(subdir2.joinpath("texfile4.tex"), "___")
    file(subsubdir.joinpath("texfile5.notexextension"), "asdfasdf")


@pytest.mark.usefixtures("setup_filesystem")
def test_hash_deterministic() -> None:
    h = hash_directory(Path("testdir"))
    assert h == hash_directory(Path("testdir"))
    assert h != hash_directory(Path("testdir", "testsubdir1"))


@pytest.mark.usefixtures("setup_filesystem")
def test_hash_skips_ignored_files() -> None:
    old_hash = hash_directory(Path("testdir"))
    ignored_hash = hash_directory(Path("testdir"), ignore=["*.notexextension"])
    file_to_remove = Path("testdir", "testsubdir1", "testsubsubdir", "texfile5.notexextension")

    file_to_remove.unlink()

    removed_file_hash = hash_directory(Path("testdir"))
    assert old_hash != ignored_hash
    assert ignored_hash == removed_file_hash


@pytest.mark.usefixtures("setup_filesystem")
def test_hash_detect_changes() -> None:
    old_hash = hash_directory(Path("testdir"))

    with Path("testdir", "texfile1.tex").open("w+", encoding="UTF-8") as f:
        f.write("some other content")

    assert old_hash != hash_directory(Path("testdir"))


@pytest.mark.usefixtures("setup_filesystem")
def test_read_cached_dirhash_exists() -> None:
    file(Path("testdir", ".checksum"), "somehash")
    assert read_cached_dirhash(Path("testdir")) == "somehash"


@pytest.mark.usefixtures("setup_filesystem")
def test_read_cached_dirhash_no_file() -> None:
    assert read_cached_dirhash(Path("testdir")) is None


@pytest.mark.usefixtures("setup_filesystem")
def test_cache_dirhash() -> None:
    assert not Path("testdir", ".checksum").exists()
    cache_dirhash(Path("testdir"), "my-custom-hash")
    assert Path("testdir", ".checksum").is_file()
    with Path("testdir", ".checksum").open(encoding="UTF-8") as f:
        assert f.read() == "my-custom-hash"


@pytest.mark.usefixtures("setup_filesystem")
def test_check_dirhash_existing_hash() -> None:
    existing_hash = hash_directory(Path("testdir"))
    file(Path("testdir", ".checksum"), existing_hash)

    same_hash, new_hash = check_dirhash(Path("testdir"))

    assert same_hash
    assert existing_hash == new_hash


@pytest.mark.usefixtures("setup_filesystem")
def test_check_dirhash_wrong_hash() -> None:
    existing_hash = hash_directory(Path("testdir"))
    file(Path("testdir", ".checksum"), "asdfasdfs")

    same_hash, new_hash = check_dirhash(Path("testdir"))

    assert not same_hash
    assert existing_hash == new_hash


@pytest.mark.usefixtures("setup_filesystem")
def test_check_dirhash_no_hash_file() -> None:
    existing_hash = hash_directory(Path("testdir"))

    assert not Path("testdir", ".checksum").exists()

    same_hash, new_hash = check_dirhash(Path("testdir"))

    assert not same_hash
    assert existing_hash == new_hash


@pytest.mark.usefixtures("setup_filesystem")
def test_check_and_update_hash_hash_changed() -> None:
    old_hash = hash_directory(Path("testdir"))
    file(Path("testdir", ".checksum"), old_hash)
    file(Path("testdir", "lol"), "lol")

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


@pytest.mark.usefixtures("setup_filesystem")
def test_check_and_update_hash_hash_changed_no_caching() -> None:
    old_hash = hash_directory(Path("testdir"))
    file(Path("testdir", ".checksum"), old_hash)

    file(Path("testdir", "lol"), "lol")

    proof: list[str] = []

    def must_be_called() -> tuple[bool, str]:
        proof.append("success")
        return False, "success"

    result = check_and_update_hash(Path("testdir"), must_be_called)

    with Path("testdir", ".checksum").open(encoding="UTF-8") as checksum:
        assert checksum.read() == old_hash

        assert result == "success"
        assert proof == ["success"]


@pytest.mark.usefixtures("setup_filesystem")
def test_check_and_update_hash_no_change() -> None:
    file(Path("testdir", ".checksum"), hash_directory(Path("testdir")))

    result = check_and_update_hash(Path("testdir"), _should_not_be_called)

    assert result is None


@pytest.mark.usefixtures("setup_filesystem")
def test_check_and_update_hash_dont_overwrite() -> None:
    file(Path("testdir", ".checksum"), hash_directory(Path("testdir")))

    result = check_and_update_hash(Path("testdir"), _should_not_be_called)

    assert result is None
