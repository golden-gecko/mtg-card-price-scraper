#!/bin/bash -ex

cd "$(dirname "$0")"
cd ../../api

# PGPASSWORD=postgres psql -h 192.168.0.162 -U postgres -c "DROP USER IF EXISTS cenykart"
# PGPASSWORD=postgres psql -h 192.168.0.162 -U postgres -c "CREATE USER cenykart WITH PASSWORD 'ca978112ca1bbdcafac2'"

# PGPASSWORD=postgres psql -h 192.168.0.162 -U postgres -c "DROP DATABASE IF EXISTS cenykart"
# PGPASSWORD=postgres psql -h 192.168.0.162 -U postgres -c "CREATE DATABASE cenykart"

PYTHONPATH=.:../common ~/.local/bin/flask db init
