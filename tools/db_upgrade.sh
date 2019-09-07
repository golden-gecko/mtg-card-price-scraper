#!/bin/bash -ex

cd "$(dirname "$0")/../api"

~/.local/bin/flask db migrate
~/.local/bin/flask db upgrade
