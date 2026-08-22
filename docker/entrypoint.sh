#!/bin/sh
set -e

# `docker run esavods <cmd>` (e.g. an artisan one-off) runs <cmd> instead of
# serving, same as any normal ENTRYPOINT/CMD image.
if [ "$#" -gt 0 ]; then
    exec "$@"
fi

# Config cache is built here, not at image build time: it freezes whatever
# env() returns at cache time, and the real DB/session credentials only exist
# once Coolify injects them at container start.
php artisan config:cache
php artisan migrate --force

php-fpm -D
exec nginx -g 'daemon off;'
