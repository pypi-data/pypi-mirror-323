#!/bin/bash
set -e
pip install --quiet --requirement requirements.txt
pylint "*.py" "tests/*.py"
coverage run -m pytest
coverage report -m
rm -f dist/*
python -m build
