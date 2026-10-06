#!/usr/bin/env python

"""Preparation and verification script for the integration tests.
This script prepares the test repositories and sets up the test files for the integration tests or
performs verification after the action was executed.
"""

from .main import run_integration_test
from .scenarios import SCENARIOS

if __name__ == "__main__":
    run_integration_test(SCENARIOS)
