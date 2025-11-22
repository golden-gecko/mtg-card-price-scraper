#!/bin/bash -ex

cd "$(dirname "$0")"
cd ..

IMAGE_NAME=cenykart-tests

docker build \
    -f tests/Dockerfile \
    -t ${IMAGE_NAME} \
    .

docker run \
    -e PYTHONDONTWRITEBYTECODE=1 \
    -i \
    -t \
    -v ${PWD}:/usr/local/app \
    ${IMAGE_NAME} \
    tests/run_tests_no_docker.sh "$@"
