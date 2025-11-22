#!/bin/bash -ex

cd "$(dirname "$0")"/..

IMAGE=tools

docker build -f tools/Dockerfile -t ${IMAGE} .

docker run \
    --interactive \
    --volume cenykart_dev:/data \
    --volume ${PWD}/tools:/app \
    --tty \
    ${IMAGE} \
    bash -c "python3 /app/data_verify.py"
