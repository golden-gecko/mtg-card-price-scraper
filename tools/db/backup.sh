#!/bin/bash -ex

cd "$(dirname "$0")"

function make_backup_mongo {
    database=$1
    collection=$2

    uri=mongodb://localhost:27017/${database}
    file_name=mongo/${database}_${collection}_$(date --utc +%Y_%m_%d_%H_%M_%S).gz

    docker run \
        -i \
        -t \
        -v /backup:/backup \
        -w /backup \
        --network host \
        mongo:4.2.0 \
        bash -c "mkdir -p mongo && mongoexport --uri=${uri} --collection=${collection} | gzip > ${file_name}"
}

make_backup_mongo gatherer cards
make_backup_mongo gatherer pages

make_backup_mongo scraper pages
make_backup_mongo scraper stats
