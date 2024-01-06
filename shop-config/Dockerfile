FROM prestashop/prestashop:1.7.8

COPY ./ssl.conf /etc/apache2/sites-available/ssl.conf

RUN apt-get update && \
    apt-get install -y libmemcached-dev zlib1g-dev && \
    pecl install memcached && \
    docker-php-ext-enable memcached

RUN update-ca-certificates && a2enmod ssl && a2ensite ssl && a2enmod rewrite