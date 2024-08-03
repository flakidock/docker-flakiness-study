FROM php:5.6-apache
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        libxml2 \
        libxml2-dev && \
    docker-php-ext-install soap && rm -rf /var/lib/apt/lists/*;
COPY . /var/www/html