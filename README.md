# Shopify GraphQL Python 3 Starter

Fetches orders from a Shopify store (via private app access token) using the GraphQL API.

Supports pagination by following cursors.

# Building
To build, run:

    ./build.sh

This builds the `shopify/python-api:latest` Docker image.

# Running
To run:

    ./run.sh YYYY-MM-DD

Will run and fetch orders for the given date.

