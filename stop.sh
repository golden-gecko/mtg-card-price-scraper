#!/bin/bash -ex

cd "$(dirname "$0")"

docker-compose stop "$@"
