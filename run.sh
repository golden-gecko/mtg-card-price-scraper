#!/bin/bash -ex

cd "$(dirname "$0")"

docker-compose up \
    --build \
    --detach \
    --remove-orphans \
    --scale api=1 \
    --scale dev=1 \
    --scale elasticsearch=0 \
    --scale kibana=0 \
    --scale mongo=1 \
    --scale mongo_express=1 \
    --scale postgres=0 \
    --scale rabbit=1 \
    --scale redis=0 \
    --scale scraper=0 \
    --scale selenium_hub=0 \
    --scale selenium_node_chrome=0 \
    --scale ui=0 \
    "$@"
