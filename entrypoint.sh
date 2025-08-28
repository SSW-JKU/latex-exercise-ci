#!/bin/env bash

# Executes the action
cd $GITHUB_ACTION_PATH && python -m latex_build_action --config "$GITHUB_WORKSPACE/$CONFIG_FILE" --workdir "$GITHUB_WORKSPACE"
