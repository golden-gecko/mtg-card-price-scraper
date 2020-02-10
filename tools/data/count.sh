#!/bin/bash -e

cd "$(dirname "$0")"

IMAGE=python:3.8.1

COMMAND='
    for i in $(ls /data)
    do
        echo ${i}: $(ls /data/${i} | wc -l)
    done
'

docker run -it --volume cenykart_scraper_mtg:/data ${IMAGE} bash -c "${COMMAND}"
