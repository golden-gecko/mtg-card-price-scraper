#!/bin/bash -ex

cd "$(dirname "$0")"

docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "du -sh /data"

docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "ls /data/pages | wc -l"

docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "ls /data/cards/details/oracle | wc -l"
docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "ls /data/cards/details/printed | wc -l"
docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "ls /data/cards/images | wc -l"
docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "ls /data/cards/printings | wc -l"
