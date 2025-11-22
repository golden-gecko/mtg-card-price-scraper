#!/bin/bash -e

cd $(dirname ${0})
cd ../..

IMAGE=python:3.7.4-slim-buster

for directory in $(docker run -it --volume cenykart_dev:/data ${IMAGE} bash -c "ls /data")
do
    echo ${directory}: $(docker run -it --volume cenykart_dev:/data ${IMAGE} bash -c "ls /data/${directory} | wc -l")
done
