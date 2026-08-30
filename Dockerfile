# syntax=docker/dockerfile:1

########################################################################
# base — PHP 8.3 + nginx + the extensions this app needs. Shared by dev
# and the production build so the two never drift apart. Both stages
# serve HTTP, so nginx and postgresql-client (for the entrypoints'
# pg_isready wait) live here, not in either leaf stage.
########################################################################
FROM php:8.3-fpm-alpine AS base

# postgresql16-client is PINNED to the server's major version, not the floating
# `postgresql-client`. pg_restore reconstructs the dump's SQL preamble using the
# CLIENT's version, so an 18.x client emits `SET transaction_timeout`, which the
# 16.x server rejects - every restore then reports an error it can do nothing
# about, and pg_restore exits non-zero over it. Matches speedrunwr, which
# already pinned this.
RUN apk add --no-cache \
        nginx \
        postgresql16-client \
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
    && apk del .build-deps \
    # Image default is one worker per host CPU core, which on a shared,
    # memory-constrained box counts cores this container isn't budgeted for.
    && sed -i 's/^worker_processes auto;/worker_processes 2;/' /etc/nginx/nginx.conf

COPY docker/php/opcache.ini /usr/local/etc/php/conf.d/zz-opcache.ini
COPY docker/nginx/default.conf /etc/nginx/http.d/default.conf

WORKDIR /var/www/html

########################################################################
# dev — the verification toolchain. PHP + Composer + dev dependencies,
# source bind-mounted by docker-compose.yml so edits are live, serving
# over the same nginx+php-fpm shape as production so the pages the
# database tickets need checked by hand are actually browsable. Never
# copied into, and shares nothing with, the production stage below.
########################################################################
FROM base AS dev

RUN apk add --no-cache git unzip bash curl

# rclone for `make database download`, pinned and taken from upstream rather
# than the distro package. The version racknerd's backup installer pins, for the
# same reason: 1.60 fails its first attempt against R2 with 501 NotImplemented
# and only succeeds on retry.
ARG RCLONE_VERSION=v1.75.0
RUN curl -fsSL -o /tmp/rclone.zip \
      "https://downloads.rclone.org/${RCLONE_VERSION}/rclone-${RCLONE_VERSION}-linux-amd64.zip" \
 && unzip -oq /tmp/rclone.zip -d /tmp \
 && install -m 755 "/tmp/rclone-${RCLONE_VERSION}-linux-amd64/rclone" /usr/local/bin/rclone \
 && rm -rf /tmp/rclone.zip "/tmp/rclone-${RCLONE_VERSION}-linux-amd64"

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

COPY docker/entrypoint-dev.sh /usr/local/bin/entrypoint-dev.sh
RUN chmod +x /usr/local/bin/entrypoint-dev.sh

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/entrypoint-dev.sh"]

########################################################################
# vendor — build-only stage. --no-scripts because package:discover can't
# run meaningfully here (no runtime env, and it would run against every
# COPY layer if not disabled); the production stage bakes the discovery
# manifest itself once vendor/ is actually in place.
########################################################################
FROM base AS vendor

RUN apk add --no-cache git unzip
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

COPY . .
RUN composer install --no-dev --optimize-autoloader --no-interaction --no-progress --no-scripts

########################################################################
# production — nginx + php-fpm serving the app. No Composer binary, no
# dev dependencies, no mounted source.
########################################################################
FROM base AS production

COPY --chown=www-data:www-data . .
COPY --from=vendor --chown=www-data:www-data /var/www/html/vendor ./vendor

COPY docker/php-fpm/www.conf /usr/local/etc/php-fpm.d/www.conf
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh \
    && php artisan package:discover --ansi \
    && chown -R www-data:www-data storage bootstrap/cache

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s \
    CMD wget -qO- http://127.0.0.1/up || exit 1

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
