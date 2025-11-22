#!/bin/bash -ex

cd "$(dirname "$0")"

docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "du -sh /data"
docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "du -sh /data/cards/details/oracle"
docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "du -sh /data/cards/details/printed"
docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "du -sh /data/cards/images"
docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "du -sh /data/cards/languages"
docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "du -sh /data/cards/printings"
docker run --volume cenykart_scraper:/data python:3.7.4-slim-buster bash -c "du -sh /data/pages"
