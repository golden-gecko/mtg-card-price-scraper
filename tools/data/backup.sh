#!/bin/bash -ex

cd "$(dirname "$0")"

function make_backup {
    volume=$1
    path=$2
    name=$3

    file_name=/backup/data/${name}_$(date --utc +%Y_%m_%d_%H_%M_%S).tar.gz

    docker run \
        -i \
        -t \
        -v /backup:/backup \
        -v ${volume}:/data \
        -w / \
        python:3.7.4-slim-buster \
        bash -c "mkdir -p data && tar -zcvf ${file_name} ${path}"
}

make_backup cenykart_scraper_gatherer data/cards gatherer_cards
make_backup cenykart_scraper_gatherer data/pages gatherer_pages

make_backup cenykart_dev data/cardmarket scraper_cardmarket
make_backup cenykart_dev data/cardstore scraper_cardstore
make_backup cenykart_dev data/channelfireball scraper_channelfireball
make_backup cenykart_dev data/centrum_mtg scraper_centrum_mtg
make_backup cenykart_dev data/e_legion scraper_e_legion
make_backup cenykart_dev data/flamberg scraper_flamberg
make_backup cenykart_dev data/futurex scraper_futurex
make_backup cenykart_dev data/gamesmasters scraper_gamesmasters
make_backup cenykart_dev data/morigal scraper_morigal
make_backup cenykart_dev data/mtgstore scraper_mtgstore
make_backup cenykart_dev data/planeswalker scraper_planeswalker
make_backup cenykart_dev data/strefamtg scraper_strefamtg
