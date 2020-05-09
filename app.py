#!/usr/bin/env python3
import requests

import sys
import re
import time
import json
from datetime import datetime, timedelta
from dateutil import parser

# Shopify store configuration
ACCESS_TOKEN = 'xXXXXXXXXXXXXXXXXXx'
SHOP_NAME = 'xXXXXXXx'

# number of seconds to wait between fetching pages
SLEEP_DURATION = 2

# debug mode
VERBOSE = False

def get_query(date=None, cursor=None):
    created_at = ""
    if date:
        created_at = '''query: "created_at:%s",''' % date

    after = ""
    if cursor:
        after = ''', after: "%s"''' % cursor

    return '''\
query {
  orders(%s first: 8 %s) {
    pageInfo {
      hasNextPage
      hasPreviousPage
    }
    edges {
      cursor
      node {
        id
        email
        name
        discountCode
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        createdAt
        updatedAt
        discountCode
        billingAddress {
          country
          province
          city
          zip
        }
        fulfillments {
          fulfillmentLineItems(first: 15) {
            edges {
              node {
                lineItem {
                  id
                  sku
                  name
                  quantity
                  originalTotalSet {
                    shopMoney {
                      amount
                      currencyCode
                    }
                  }
                  discountAllocations {
                    allocatedAmountSet {
                      shopMoney {
                        amount
                        currencyCode
                      }
                    }
                  }
                }
              }
            }
          }
        }
        cancelledAt
        cancelReason
        refunds {
          refundLineItems(first: 10) {
            edges {
              node {
                lineItem {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
  }
}\
''' % (created_at, after)


def get_reports(date=None, cursor=None):
    query = get_query(date, cursor)
    headers = {'Content-Type': 'application/json', 'X-Shopify-Access-Token': ACCESS_TOKEN}
    req = requests.Request('POST', 'https://%s.myshopify.com/admin/api/2020-07/graphql.json' % SHOP_NAME,
                           json={"query": query}, headers=headers)
    prepared = req.prepare()
    if VERBOSE:
        pretty_print_POST(prepared)
    s = requests.Session()
    r = s.send(prepared)

    if r.status_code != 200:
        if r.status_code == 204:
            print("No data to get.")
            print(r.status_code)
            return
        else:
            print("Error to get json data:")
            print(r.status_code)
            print(r.text)
            print("Exiting now.")
            sys.exit(1)

    j = r.json()
    if j['data'] and \
            j['data']['orders'] and \
            j['data']['orders']['pageInfo'] and \
            j['data']['orders']['pageInfo']['hasNextPage']:
        last_pos = len(j['data']['orders']['edges'])
        cursor = j['data']['orders']['edges'][last_pos - 1]['cursor']
        print("Found next page cursor cursor=%s" % cursor)
    else:
        cursor = None

    handle_data(j)

    if cursor:
        print("Waiting %s seconds before fetching next page via cursor %s" % (SLEEP_DURATION, cursor))
        time.sleep(SLEEP_DURATION)
        get_reports(date=date, cursor=cursor)


def handle_data(json_data):
    j = json_data

    if VERBOSE:
        print(json.dumps(json_data, indent=2, sort_keys=True))

    if j['data']['orders']['edges'] and len(j['data']['orders']['edges']) > 0:
        print("Handling %s orders..." % len(j['data']['orders']['edges']))

        for order_node in j['data']['orders']['edges']:
            order = order_node['node']
            print("Order: %s -> %s" % (order['createdAt'], order['email']))

            fulfillments = order['fulfillments']
            for fulfillment in fulfillments:
                for line_item_node in fulfillment['fulfillmentLineItems']['edges']:
                    line_item = line_item_node['node']
                    print("sku: %s -> quantity: %s" % (line_item['lineItem']['sku'], line_item['lineItem']['quantity']))
    return


def pretty_print_POST(req):
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide a valid date to run for: YYYY-MM-DD")
        sys.exit(1)
    else:
        # validate that it's a date
        try:
            d = datetime.strptime(sys.argv[1], '%Y-%m-%d')
            get_reports(date=sys.argv[1])
        except ValueError:
            print("Please provide a valid date to run for: YYYY-MM-DD")
            sys.exit(1)

