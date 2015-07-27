import json
import urllib.parse
import urllib.request
import time
import hmac
import hashlib
import sys
import traceback
import random
import datatypes
import log
from colored import fore, style

USERNAME = "USERNAME"
API_KEY = "API_KEY"
API_SECRET = "API_SECRET"
ADDRESS = "ADDRESS"

URL_BALANCE = "https://bitnz.com/api/0/private/balance"
URL_ALL_ORDERS = "https://bitnz.com/api/0/orderbook"
URL_MY_ORDERS = "https://bitnz.com/api/0/private/orders/buy/open"
URL_CANCEL_ORDER = "https://bitnz.com/api/0/private/orders/buy/cancel"
URL_CREATE_ORDER = "https://bitnz.com/api/0/private/orders/buy/create"

random.seed()

def cancel_order(order):
    cancel_order_by_details(order.id, order.price, order.amount)

def cancel_order_by_details(order_id, price, amount):
    response = urllib.request.urlopen(URL_CANCEL_ORDER, get_parameters(order_id)).read().decode('utf-8')
    parse = json.loads(response)
    if not parse['result']:
        raise Exception('Error canceling order.')
    log.log_trading('- %.8f  %.8f' % (price, amount), 'red')


def place_order(price, amount):
    response = urllib.request.urlopen(URL_CREATE_ORDER, get_parameters(None, amount, price)).read().decode('utf-8')
    parse = json.loads(response)
    if not parse['result']:
        raise Exception('Error creating order.')
    log.log_trading('+ %.8f  %.8f' % (parse['price'], parse['amount']), 'blue')


def get_buy_orders():
    response = urllib.request.urlopen(URL_ALL_ORDERS).read().decode('utf-8')
    orders = json.loads(response)
    arr = []
    for item in orders['bids']:
        arr.append(datatypes.Order(None, item[0], item[1]))

    return arr


def get_my_orders():
    response = urllib.request.urlopen(URL_MY_ORDERS, get_parameters()).read().decode('utf-8')
    orders = json.loads(response)
    sorted_orders = sorted(orders, key=lambda order: order['price'], reverse=True)
    arr = []
    for item in sorted_orders:
        arr.append(datatypes.Order(item['id'], item['price'], item['amount']))

    return arr;


def get_balance():
    response = urllib.request.urlopen(URL_BALANCE, get_parameters()).read().decode('utf-8')
    balance = json.loads(response)
    return balance


def get_parameters(order_id=None, amount=None, price=None):
    nonce = "{0:.0f}".format(time.time())
    message = (nonce + USERNAME + API_KEY)
    signature = hmac.new(bytearray(API_SECRET, "utf-8"),
                         msg=message.encode("utf-8"),
                         digestmod=hashlib.sha256).hexdigest().upper()
    params = urllib.parse.urlencode({
        'key': API_KEY,
        'nonce': nonce,
        'signature': signature,
        'id': order_id,
        'amount': amount,
        'price': price
    })
    return params.encode('utf-8')


def get_other_orders(orders, value):
    total = 0
    other_orders = []
    for item in orders["bids"]:
        if item[0] > value:
            total = total + item[1]
            other_orders.append(item)
        else:
            break

    return total, other_orders


def replace_order(order, price, sell_order):
    if price + 2 >= sell_order:
        return

    price += random.randint(1, 1e4) * 1e-8
    response1 = urllib.request.urlopen(URL_CANCEL_ORDER, get_parameters(order["id"])).read()
    print("Canceling order: %.8f   %.8f   -   %s" % (order["price"], order["amount"], response1))

    balance = order["price"] * order["amount"]
    new_amount = (balance / price) - 1e-8

    response2 = urllib.request.urlopen(URL_CREATE_ORDER, get_parameters(None, new_amount, price)).read()
    print("Creating order : %s" % response2)


def find_next_smallest_order(top_order, all_orders):
    for item in all_orders["bids"]:
        if item[0] < top_order["price"]:
            return item[0]
    return top_order["price"]


def print_buy_orders(my_orders, all_orders):
    minimum = my_orders[len(my_orders) - 1]["price"]
    for item in all_orders["bids"]:
        if item[0] >= minimum:
            star = ""
            for mine in my_orders:
                if mine["price"] == item[0] and mine["amount"] == item[1]:
                    star = "*"
                    break
            print("                   %.8f   %.8f %s" % (item[0], item[1], star))
        else:
            break


def loop():
    while True:
        try:
            print("=[ " + time.strftime("%X") + " ]==============================")

            flag = False
            response1 = urllib.request.urlopen(URL_BALANCE, get_parameters()).read()
            balance = json.loads(response1)
            nzd_balance = balance["nzd_balance"]
            btc_balance = balance["btc_balance"]

            response2 = urllib.request.urlopen(URL_MY_ORDERS, get_parameters()).read()
            my_orders = json.loads(response2)
            my_orders = sorted(my_orders, key=lambda order: order['price'], reverse=True)
            top_order = my_orders[0]

            response3 = urllib.request.urlopen(URL_ALL_ORDERS).read()
            all_orders = json.loads(response3)
            total, other_orders = get_other_orders(all_orders, my_orders[0]["price"])
            sell_order = all_orders["asks"][0]

            if total >= top_order["amount"]:
                print("== Replacing top order == \a")
                flag = True
                replace_order(top_order, other_orders[0][0], sell_order[0])
            else:
                value = find_next_smallest_order(top_order, all_orders)
                if top_order["price"] - value > 0.1:
                    print("== Reducing value == \a")
                    flag = True
                    replace_order(top_order, value, sell_order[0])

            print("")
            print("Balance")
            print("    NZD: " + str(nzd_balance))
            print("    BTC: " + str(btc_balance))
            print("")
            print("Orders")
            print("    Buy:")
            print_buy_orders(my_orders, all_orders)
            print("")
            print("    Others (sell): %.8f   %.8f" % (sell_order[0], sell_order[1]))
            print("")

        except:
            print("UNEXPECTED ERROR:")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

        if not flag:
            time.sleep(30)

        time.sleep(30)
