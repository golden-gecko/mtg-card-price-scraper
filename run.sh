#!/bin/bash -ex

cd "$(dirname "$0")"

docker-compose up --build --detach --remove-orphans "$@"
