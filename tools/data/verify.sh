#!/bin/bash -ex

cd $(dirname ${0})
cd ../..

IMAGE=cenykart_tools

docker build -f tools/Dockerfile -t ${IMAGE} .

docker run \
    --interactive \
    --volume cenykart_dev:/data \
    --tty \
    ${IMAGE} \
    bash -c "python3 /usr/local/app/data/verify.py"
