#!/bin/sh
set -e

until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USERNAME" -d "$DB_DATABASE" >/dev/null 2>&1; do
    echo "Waiting for Postgres at $DB_HOST:${DB_PORT:-5432}..."
    sleep 1
done

if [ -f composer.json ] && [ ! -d vendor ]; then
    composer install
fi

if [ "$#" -eq 0 ]; then
    php artisan migrate --force
    php-fpm -D
    exec nginx -g "daemon off;"
else
    exec "$@"
fi
