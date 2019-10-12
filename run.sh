#!/bin/bash -ex

cd "$(dirname "$0")"

docker-compose up \
    --build \
    --detach \
    --remove-orphans \
    --scale api=1 \
    --scale elasticsearch=0 \
    --scale kibana=0 \
    --scale mongo=1 \
    --scale mongo_express=1 \
    --scale postgres=0 \
    --scale rabbit=1 \
    --scale redis=0 \
    --scale scraper_gatherer=0 \
    --scale scraper_mtg=1 \
    --scale selenium_hub=0 \
    --scale selenium_node_chrome=0 \
    --scale ui=0 \
    --scale vault=0 \
    "$@"
