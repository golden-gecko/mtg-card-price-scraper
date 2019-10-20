#!/bin/bash -ex

cd "$(dirname "$0")/../../backup"

function make_backup {
    database=$1
    collection=$2

    uri=mongodb://localhost:27017/${database}
    file_name=mongo/${database}_${collection}_$(date --utc +%Y_%m_%d_%H_%M_%S).json

    docker run \
        -i \
        -t \
        -v ${PWD}:/backup \
        -w /backup \
        --network host \
        mongo:4.2.0 \
        bash -c "mkdir -p mongo && mongoexport --uri=${uri} --collection=${collection} --out=${file_name}"
}

make_backup gatherer pages
make_backup scraper pages
make_backup scraper stats
