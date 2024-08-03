FROM flyimg/base-image:1.2.1

# Install other file processors
RUN apt update && \
    apt install -y \
    ghostscript \
    ffmpeg \
    --no-install-recommends && \
    pip3 install pillow && \
    rm -rf /var/lib/apt/lists/*

COPY .    /var/www/html

#add www-data + mdkdir var folder
RUN usermod -u 1000 www-data && \
    mkdir -p /var/www/html/var web/uploads/.tmb var/cache/ var/log/ && \
    chown -R www-data:www-data var/  web/uploads/ && \
    chmod 777 -R var/  web/uploads/

RUN composer install --no-dev --optimize-autoloader
