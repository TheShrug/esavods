#!/bin/sh
set -e

# Guarded on DB_HOST, matching speedrunwr's entrypoint. Unguarded, this loops
# forever for any invocation that deliberately has no database - `make database
# download` runs in this container to reach rclone and never touches Postgres,
# and an unset DB_HOST made it hang instead of failing. Converged rather than
# worked around, per homelab Conventions/Container Shape.
if [ -n "$DB_HOST" ]; then
    until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USERNAME" -d "$DB_DATABASE" >/dev/null 2>&1; do
        echo "Waiting for Postgres at $DB_HOST:${DB_PORT:-5432}..."
        sleep 1
    done
fi

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
