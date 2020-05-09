FROM alpine:3.11
RUN apk add --update --no-cache --virtual .build-deps \
    python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    pip3 install --upgrade ShopifyAPI oauth2client python-dateutil mysql-connector-python-rf requests

