#!/bin/bash -ex

cd "$(dirname "$0")"

docker-compose up \
    --build \
    --detach \
    --remove-orphans \
    --scale elasticsearch=0 \
    --scale kibana=0 \
    --scale postgres=0 \
    --scale redis=0 \
    --scale selenium_hub=0 \
    --scale selenium_node_chrome=0 \
    --scale ui=0 \
    "$@"
