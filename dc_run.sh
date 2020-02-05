#!/bin/bash -ex

cd "$(dirname "$0")"

docker-compose up \
    --build \
    --detach \
    --remove-orphans \
    --scale api=1 \
    --scale elasticsearch=1 \
    --scale grafana=0 \
    --scale kibana=1 \
    --scale mongo=1 \
    --scale mongo_express=1 \
    --scale postgres=1 \
    --scale rabbit=1 \
    --scale redis=1 \
    --scale scraper_gatherer=0 \
    --scale scraper_mtg=1 \
    --scale selenium_hub=0 \
    --scale selenium_node_chrome=0 \
    --scale static=1 \
    --scale ui=1 \
    --scale vault=0 \
    "$@"
