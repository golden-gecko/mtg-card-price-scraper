#!/bin/bash -ex

cd "$(dirname "$0")"
cd ../../api

PYTHONPATH=.:../common ~/.local/bin/flask db migrate
