"""
Defines various integration test scenarios and their verification steps.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from .test_repository import TestRepository

# auto-register scenario to simplify access and iteration
_scenarios = dict[str, "Scenario"]()


def _add_scenario(s: "Scenario") -> None:
    assert s.name not in _scenarios, f"Scenario '{s.name}' already registered."
    _scenarios[s.name] = s


def get_scenario(name: str) -> "Scenario | None":
    return _scenarios.get(name, None)


def scenarios() -> Iterable[tuple[str, "Scenario"]]:
    return _scenarios.items()


class Scenario(ABC):
    def __init__(self, name: str, path: list[str]) -> None:
        self.name = name
        self.path = Path(".") / "action_tests" / "_files" / Path(*path)

    @abstractmethod
    def verify(self, repo: TestRepository) -> None: ...


#### OLD BUILD SYSTEM ####


class OldBuildWorkingNoChecksum(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_no_checksum",
            ["old_build_system", "working_build_no_checksum"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        # TODO:


class OldBuildWorkingSameChecksum(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_same_checksum",
            ["old_build_system", "working_build_same_checksum"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        # TODO:


class OldBuildWorkingSameChecksumNoPDF(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_same_checksum_no_pdf",
            ["old_build_system", "working_build_same_checksum_no_pdf"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        # TODO:


class OldBuildWorkingWrongCheckSum(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_wrong_checksum",
            ["old_build_system", "working_build_wrong_checksum"],
        )

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        # TODO:


#### NEW BUILD SYSTEM ####


_add_scenario(OldBuildWorkingNoChecksum())
_add_scenario(OldBuildWorkingSameChecksum())
_add_scenario(OldBuildWorkingSameChecksumNoPDF())
_add_scenario(OldBuildWorkingWrongCheckSum())
