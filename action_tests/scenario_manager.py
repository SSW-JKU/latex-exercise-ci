"""Collects and manages test scenarios."""

from collections.abc import Iterable
from typing import Optional

from .scenario import Scenario


class ScenarioManager:
    """Manages created `Scenarios` and simplifies access and iteration over them."""

    def __init__(self, *scenarios: Scenario) -> None:
        """Initialize the scenario manager.

        Args:
            *scenarios (Scenario) : The scenarios to manage.

        """
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

    def get_scenario(self, name: str) -> Optional["Scenario"]:
        """Retrieve the scenario registered under the given `name`.

        Args:
            name (str) : The name that identifies the target scenario

        Returns:
            (Scenario | None) The scenario or `None` if no such scenario is
            registered

        """
        return self._scenarios.get(name, None)

    def scenarios(self) -> Iterable["Scenario"]:
        """Return all registered scenarios.

        Returns:
            (Iterable[tuple[str, Scenario]]) an iterable of name-scenario tuples

        """
        return self._scenarios.values()
