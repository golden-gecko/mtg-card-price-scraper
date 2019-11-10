#!/bin/bash -ex

cd "$(dirname "$0")"

PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
    --durations=0 \
    --junitxml=report.xml \
    --html=report.html \
    --self-contained-html \
    --showlocals \
    -p no:cacheprovider \
    -s \
    -vv \
    "$@"
