#!/bin/bash -e

cd "$(dirname "$0")"

IMAGE=python:3.8.1

COMMAND='
    for i in $(ls /data)
    do
        echo ${i}: $(du -sh /data/${i})
    done
'

docker run -it --volume cenykart_dev:/data ${IMAGE} bash -c "${COMMAND}"
