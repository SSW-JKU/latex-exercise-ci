"""Collects and manages test scenarios."""

import inspect
import logging
import sys
from collections.abc import Generator, Iterable
from importlib.util import module_from_spec, spec_from_file_location
from os import PathLike
from pathlib import Path
from types import ModuleType

from .scenario import Scenario, is_scenario

log = logging.getLogger(__name__)


class ScenarioManager:
    """Manages created `Scenarios` and simplifies access and iteration over them."""

    def __init__(self, remote_path: PathLike[str], local_path: PathLike[str], *scenarios: Scenario) -> None:
        """Initialize the scenario manager.

        Args:
            remote_path (PathLike[str]) : The path to the remote repository.
            local_path (PathLike[str]) : The path to the local repository.
            *scenarios (Scenario) : The scenarios to manage.

        """
        self.local_path = Path(local_path)
        self.remote_path = Path(remote_path)
        self._scenarios = dict[str, "Scenario"]()
        for s in scenarios:
            self._add_scenario(s)

    def _add_scenario(self, s: Scenario) -> None:
        """Register the given scenario in the `scenarios` dictionary.

        Args:
            s (Scenario) : The test scenario to register.

        """
        if s.name not in self._scenarios:
            self._scenarios[s.name] = s
        else:
            msg = f"Scenario '{s.name}' already registered."
            raise ValueError(msg)

    def get_scenario(self, name: str) -> "Scenario":
        """Retrieve the scenario registered under the given `name`.

        Args:
            name (str) : The name that identifies the target scenario

        Returns:
            (Scenario) The scenario

        Raises:
            ValueError : If the given scenario is not registered

        """
        s = self._scenarios.get(name, None)
        if s is None:
            msg = f"Scenario '{name}' not found."
            raise ValueError(msg)
        return s

    def scenarios(self) -> Iterable["Scenario"]:
        """Return all registered scenarios.

        Returns:
            (Iterable[Scenario]) an iterable of scenarios

        """
        return self._scenarios.values()

    def prepare(self, scenario: str) -> None:
        """Prepare the given scenario.

        Args:
            scenario (str) : The name of the scenario to prepare

        Raises:
            ValueError : If the given scenario is not registered

        """
        self.get_scenario(scenario).prepare(self.remote_path, self.local_path)

    def verify(self, scenario: str, outcome: str) -> None:
        """Verify the given scenario and outcome.

        Args:
            scenario (str) : The name of the scenario to verify
            outcome (str) : The outcome of the action execution

        Raises:
            ValueError : If the given scenario is not registered

        """
        self.get_scenario(scenario).test(self.remote_path, self.local_path, outcome)

    @staticmethod
    def collect_scenarios(
        directory: PathLike[str], remote_path: PathLike[str], local_path: PathLike[str]
    ) -> "ScenarioManager":
        """Collect all `Scenario` definitions in the given directory.

        Args:
            directory (PathLike[str]) : the base path
            remote_path (PathLike[str]) : the path to the remote repository
            local_path (PathLike[str]) : the path to the local repository

        Returns:
            (ScenarioManager) a ScenarioManager encompassing all collected scenarios

        """
        scenarios = list[Scenario]()
        for file_path in Path(directory).glob("**/*.py"):
            if file_path.name.startswith("__"):
                continue

            module: ModuleType | None = None
            try:
                module = _load_module(file_path)
                scenarios.extend(_instantiate_scenarios(module))
            except Exception:
                log.exception("Failed to import module %s from %s. Skipping.", file_path.name, file_path)

        return ScenarioManager(remote_path, local_path, *scenarios)


def _load_module(module_path: Path) -> ModuleType:
    """Perform a dynamic import of the target module."""
    module_name = module_path.stem

    spec = spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        msg = f"Cannot create spec for {module_path}"
        raise ImportError(msg)

    module = module_from_spec(spec)
    sys.modules[module_name] = module  # register before exec (circular imports)
    spec.loader.exec_module(module)
    return module


def _instantiate_scenarios(module: ModuleType) -> Generator[Scenario]:
    """Instantiate all scenarios of the given module."""
    # reflection: inspect module for scenario definitions
    for name, obj in inspect.getmembers(module):
        # filter out non-scenario classes and already looked at classes (e.g. imported from other modules)
        if is_scenario(obj) and obj.__module__ == module.__name__:
            try:
                scenario = obj()  # instantiate the scenario
                yield scenario
            except Exception:
                log.exception("Failed to instantiate scenario %s from module %s. Skipping.", name, module.__name__)
