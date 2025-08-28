#!/bin/env bash

# Executes the action
cd $GITHUB_ACTION_PATH && python -m latex_build_action --config "$WORKING_DIRECTORY/$CONFIG_FILE" --workdir "$WORKING_DIRECTORY"
