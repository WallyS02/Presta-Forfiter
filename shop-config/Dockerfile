FROM prestashop/prestashop:1.7.8

COPY ./ssl.conf /etc/apache2/sites-available/ssl.conf

RUN update-ca-certificates && a2enmod ssl && a2ensite ssl && a2enmod rewrite