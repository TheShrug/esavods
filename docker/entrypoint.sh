#!/bin/sh
set -e

# `docker run esavods <cmd>` (e.g. an artisan one-off) runs <cmd> instead of
# serving, same as any normal ENTRYPOINT/CMD image.
if [ "$#" -gt 0 ]; then
    exec "$@"
fi

# The shared Postgres (homelab#29) can be slower to accept connections than
# this container is to start; a fixed sleep would race it occasionally.
until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USERNAME" -d "$DB_DATABASE" >/dev/null 2>&1; do
    echo "Waiting for Postgres at $DB_HOST:${DB_PORT:-5432}..."
    sleep 1
done

# config:cache first so everything after it reads one consistent config;
# migrate last so a schema failure kills the container before it serves.
php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan migrate --force

php-fpm -D
exec nginx -g "daemon off;"
