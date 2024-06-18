FROM nginx:1.26.0-perl

COPY config/nginx.conf /etc/nginx/nginx.conf
