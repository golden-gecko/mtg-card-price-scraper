#!/bin/bash -ex

cd "$(dirname "$0")"

docker-compose up \
    --build \
    --detach \
    --remove-orphans \
    --scale grafana=0 \
    --scale scraper_gatherer=0 \
    --scale selenium_hub=0 \
    --scale selenium_node_chrome=0 \
    --scale vault=0 \
    "$@"
