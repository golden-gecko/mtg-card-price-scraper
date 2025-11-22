#!/bin/bash -ex

cd "$(dirname "$0")/../api"

PGPASSWORD=postgres psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS dev"
PGPASSWORD=postgres psql -h localhost -U postgres -c "CREATE DATABASE dev"

PGPASSWORD=postgres psql -h localhost -U postgres -c "DROP USER IF EXISTS dev"
PGPASSWORD=postgres psql -h localhost -U postgres -c "CREATE USER dev WITH PASSWORD 'dev'"

~/.local/bin/flask db init
