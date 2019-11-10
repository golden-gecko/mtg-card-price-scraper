#!/bin/bash -e

cd "$(dirname "$0")"

IMAGE=FROM python:3.7.4-slim-buster

COMMAND='
    for i in $(ls /data)
    do
        echo ${i}: $(ls /data/${i} | wc -l)
    done
'

docker run -it --volume cenykart_dev:/data ${IMAGE} bash -c "${COMMAND}"
