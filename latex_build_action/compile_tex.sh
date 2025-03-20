#!/bin/sh

# This is a helper script that is called by the Python CI actions.
# This prevents bash/latexmk escaping issues when passing the pdflatex options.

TEXFILE_PATH="${1}"
OUTPUT_NAME="${2}"
PDFLATEX_ARGS="${3}"

latexmk \
    -gg \
    -pdf \
    -pdflatex="pdflatex %O -interaction=nonstopmode -halt-on-error -synctex=0 ${PDFLATEX_ARGS}" \
    -jobname="${OUTPUT_NAME}" \
    -cd "${TEXFILE_PATH}"
