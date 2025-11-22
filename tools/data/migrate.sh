#!/bin/bash -ex

cd "$(dirname "$0")"
cd ../..

IMAGE=cenykart_tools

docker build -f tools/Dockerfile -t ${IMAGE} .

docker run \
    --interactive \
    --volume cenykart_dev:/data \
    --tty \
    ${IMAGE} \
    bash -c "PYTHONPATH=/usr/local/app python3 /usr/local/app/data/migrate.py"
