"""
Contains utility methods for hashing directories.
"""

import logging as log
from pathlib import Path
from typing import Callable, Iterable, Optional, TypeVar
from dirhash import dirhash, included_paths  # type: ignore

# Files that are by default ignored when calculating the directory hash
# (see dirhash documentation for supported patterns)
DEFAULT_IGNORE_PATTERNS = tuple([
    "*.aux",
    "*.fdb_latexmk",
    "*.fls",
    "*.log",
    "*.out",
    "*.synctex.gz",
    "*.build_log",
    ".checksum"
])

# the hash algorithm used as an input to the dirhash function
# (see the package documentation for details)
HASH_ALGORITHM = 'sha1'


def hash_directory(path: Path, ignore: Iterable[str] = DEFAULT_IGNORE_PATTERNS) -> str:
    """
    Hashes the given directory while using the provided list of patterns for
    exclusions.

    Args:
        path (Path) : The target directory path.
        ignore (list[str], default) : A list of patterns that should be ignored.

    Returns:
        A string containing a unique SHA1 hash over the directory contents
        (file structure and contents).
    """
    hash_str: str = dirhash(path, HASH_ALGORITHM, ignore=ignore)
    log.debug('Dirhash (%s) for path %s is %s (ignored patterns: %s)',
              HASH_ALGORITHM, str(path), hash_str, str(ignore))
    log.debug('Included files:\n%s', '\n'.join(
        included_paths(path, HASH_ALGORITHM, ignore=ignore)))
    return hash_str


def read_cached_dirhash(basepath: Path) -> Optional[str]:
    """
    Reads the cached hash from the .checksum file at the given basepath and
    returns it.

    Args:
        basepath (Path) : The directory that should contain the hash file.

    Returns:
        The cached hash or None if no hash file exists.
    """
    dirhash_file = basepath.joinpath('.checksum')
    if dirhash_file.is_file():
        with open(dirhash_file, 'r', encoding='UTF-8') as f:
            existing_hash = f.read().strip()
            log.debug('Stored .checksum (%s) for path %s is %s',
                      HASH_ALGORITHM, str(basepath), existing_hash)
            return existing_hash
    log.debug('No stored dirhash (%s) for path %s as no .checksum file was found',
              HASH_ALGORITHM, str(basepath))
    return None


def cache_dirhash(basepath: Path, h: str) -> None:
    """
    Caches the given hash in a .checksum file at the given basepath.

    Args:
        basepath (Path) : The directory that should contain the hash file.
        h (str) : The hash that should be stored.
    """
    dirhash_file = basepath.joinpath('.checksum')
    log.debug('Caching hash for path %s in file %s. Cached hash = %s',
              str(basepath), str(dirhash_file), str(h))
    with open(dirhash_file, 'w', encoding='UTF-8') as f:
        f.write(h)


def check_dirhash(basepath: Path,
                  ignore: Iterable[str] = DEFAULT_IGNORE_PATTERNS) -> tuple[bool, str]:
    """
    Compares the hash generated from the given directory with any already saved
    hash in the same directory.

    Args:
        basepath (Path) : The target directory.
        ignore (list[str], default) : The list of files that should be omitted
                                      from the hash calculation.

    Returns:
        (tuple[bool, str]) A tuple where the first value indicates the
        comparison result (True if the hash exists and matched, False otherwise)
        and the second value indicates the now valid directory hash.
    """
    new_hash = hash_directory(basepath, ignore)
    saved_hash = read_cached_dirhash(basepath)
    log.info('Checking cached hash for path %s. Cached hash = %s, new hash = %s',
              str(basepath), str(saved_hash), str(new_hash))
    return (saved_hash is not None and new_hash == saved_hash, new_hash)


R = TypeVar('R')


def check_and_update_hash(basepath: Path,
                          on_mismatch: Callable[[], tuple[bool, R]],
                          ignore: Iterable[str] = DEFAULT_IGNORE_PATTERNS
                          ) -> Optional[R]:
    """
    Checks whether the target directory has a matching cached hash
    (in a .checksum file). If the hashes differ, it executes the given callback
    and afterwards stores the new hash in the .checksum file.
    If the provided callback returns `False` as the first tuple value,
    the .checksum is not cached.
    If the hashes match, nothing is executed.

    Args:
        basepath (Path) : The directory that should contain the hash file.
        on_mismatch (Callable[[], R]) : The function that should be executed
                                        when the hashes differ.
        ignore (list[str], default) : The list of files that should be omitted
                                      from the hash calculation.

    Returns:
        (R) The result of the provided function or None if the hashes matched.
    """
    hashes_match, new_hash = check_dirhash(basepath, ignore)

    if hashes_match:
        log.debug('Hashes for path %s matched (ignored patterns: %s)',
                  str(basepath), str(ignore))
        return None

    log.debug('Hash mismatch for path %s matched (ignored patterns: %s)', str(
        basepath), str(ignore))
    cache, result = on_mismatch()
    if cache:
        log.info('Function after hash mismatch in path %s resulted in new hash %s', str(
            basepath), str(new_hash))
        cache_dirhash(basepath, new_hash)
    log.info('Result after hash mismach in path %s is %s',
              str(basepath), str(result))
    return result
