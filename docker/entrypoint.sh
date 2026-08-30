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
# migrate before serving so a schema failure kills the container first.
php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan migrate --force

# The CSVs in storage/app/csv are the record of what ran at each event, and
# importing them is what actually puts an event on the site. Merging a PR used
# to deploy the files and nothing else, so the site looked unchanged until
# someone remembered to run this by hand — a step with no prompt, no error and
# no visible symptom when skipped.
#
# Safe on every boot because #55 keys a run on its schedule slot rather than on
# its time, so re-importing updates in place instead of inserting duplicates.
# It re-reads every file, not just new ones; that is ~13s for the twelve events
# present today and grows with the backfill, which is why the image's
# HEALTHCHECK start-period allows for it.
#
# Deliberately NOT fatal, unlike migrate. A schema failure means the app cannot
# work and must not serve. A failed import only means the data is as stale as
# the last good one, and taking the whole site down over a data refresh is the
# worse outcome — so it warns and serves.
if ! php artisan runCsv:import; then
    echo "WARNING: runCsv:import failed; serving the data already in the database" >&2
fi

php-fpm -D
exec nginx -g "daemon off;"
