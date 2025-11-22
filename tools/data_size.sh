#!/bin/bash -e

cd "$(dirname "$0")"

IMAGE=python:3.7.4-slim-buster

for directory in $(docker run -it --volume cenykart_dev:/data ${IMAGE} bash -c "ls /data")
do
    echo ${directory}: $(docker run -it --volume cenykart_dev:/data ${IMAGE} bash -c "du -sh /data/${directory}")
done
