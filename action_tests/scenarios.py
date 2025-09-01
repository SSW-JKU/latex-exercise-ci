"""
Defines various integration test scenarios and their verification steps.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class Scenario(ABC):
    REGISTRY = dict[str, "Scenario"]()

    def __init__(self, name: str, path: list[str]) -> None:
        self.name = name
        # auto-register scenario to simplify access and iteration
        Scenario.REGISTRY[name] = self
        self.path = Path(".") / "_files" / Path(*path)

    @abstractmethod
    def verify(self) -> None: ...


#### OLD BUILD SYSTEM ####


class OldBuildWorkingNoChecksum(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_no_checksum",
            ["old_build_system", "working_build_no_checksum"],
        )

    def verify(self) -> None:
        print(f"Verifying scenario: {self.name}")
        # TODO:


class OldBuildWorkingSameChecksum(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_same_checksum",
            ["old_build_system", "working_build_same_checksum"],
        )

    def verify(self) -> None:
        print(f"Verifying scenario: {self.name}")
        # TODO:


class OldBuildWorkingSameChecksumNoPDF(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_same_checksum_no_pdf",
            ["old_build_system", "working_same_checksum_no_pdf"],
        )

    def verify(self) -> None:
        print(f"Verifying scenario: {self.name}")
        # TODO:


class OldBuildWorkingWrongCheckSum(Scenario):
    def __init__(self) -> None:
        super().__init__(
            "old_build_working_wrong_checksum",
            ["old_build_system", "working_build_wrong_checksum"],
        )

    def verify(self) -> None:
        print(f"Verifying scenario: {self.name}")
        # TODO:


#### NEW BUILD SYSTEM ####
