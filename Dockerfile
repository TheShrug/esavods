# syntax=docker/dockerfile:1

########################################################################
# base — PHP 8.3 + the extensions this app needs. Shared by dev and the
# production build so the two never drift apart.
########################################################################
FROM php:8.3-fpm-alpine AS base

RUN apk add --no-cache \
        icu-libs \
        libpq \
        libzip \
        libpng \
        libjpeg-turbo \
        freetype \
    && apk add --no-cache --virtual .build-deps \
        $PHPIZE_DEPS \
        icu-dev \
        postgresql-dev \
        libzip-dev \
        libpng-dev \
        libjpeg-turbo-dev \
        freetype-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" \
        pdo_pgsql \
        intl \
        zip \
        bcmath \
        exif \
        pcntl \
        gd \
    && apk del .build-deps

WORKDIR /var/www

########################################################################
# dev — the verification toolchain. PHP + Composer + dev dependencies,
# source bind-mounted by docker-compose.yml so edits are live. Never
# copied into, and shares nothing with, the production stage below.
########################################################################
FROM base AS dev

RUN apk add --no-cache git unzip bash postgresql-client
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

CMD ["php-fpm"]

########################################################################
# vendor — build-only stage. Composer needs the full app (package:discover
# runs post-autoload-dump) but nothing here reaches the final image except
# the resulting vendor/.
########################################################################
FROM base AS vendor

RUN apk add --no-cache git unzip
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

COPY . .
RUN composer install --no-dev --optimize-autoloader --no-interaction --no-progress

########################################################################
# production — nginx + php-fpm serving the app. No Composer binary, no
# dev dependencies, no mounted source.
########################################################################
FROM base AS production

RUN apk add --no-cache nginx \
    # Image default is one worker per host CPU core, which on a shared,
    # memory-constrained box counts cores this container isn't budgeted for.
    && sed -i 's/^worker_processes auto;/worker_processes 2;/' /etc/nginx/nginx.conf

COPY --chown=www-data:www-data . .
COPY --from=vendor --chown=www-data:www-data /var/www/vendor ./vendor

COPY docker/nginx/default.conf /etc/nginx/http.d/default.conf
COPY docker/php-fpm/www.conf /usr/local/etc/php-fpm.d/www.conf
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh \
    && php artisan route:cache \
    && php artisan view:cache \
    && chown -R www-data:www-data storage bootstrap/cache

# storage/app, not "user uploads" — ImportCsvs reads storage/app/csv and it's
# the only durable write path in the app (see the #12 decisions comment).
VOLUME /var/www/storage/app

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
