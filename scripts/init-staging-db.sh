#!/bin/bash
set -e

# Create the staging database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE movie_recommendation_staging'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'movie_recommendation_staging')\gexec
EOSQL

echo "Staging database initialized successfully!"
