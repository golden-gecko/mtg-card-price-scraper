#!/bin/bash -ex

cd "$(dirname "$0")"

docker-compose logs --follow --tail 10 "$@"
