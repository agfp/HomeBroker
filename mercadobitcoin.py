import json
import urllib
import urllib.parse
import urllib.request
import time
import hmac
import hashlib

MERCADO_TAPI_CHAVE = "TAPI_CHAVE"
MERCADO_TAPI_CODIGO = "TAPI_CODIGO"
PIN = "0000"

URL_ORDER_BOOK = "https://www.mercadobitcoin.net/api/orderbook/"


def average_bid():
    response = urllib.request.urlopen('https://www.mercadobitcoin.net/api/orderbook/').read().decode('utf-8')
    parse = json.loads(response)
    avg = 0
    for i in range(0, 3):
        avg += parse['bids'][i][0]

    return avg / 3


def get_data(metodo):
    tonce = str(int(time.time()))
    h = hmac.new(MERCADO_TAPI_CODIGO.encode('utf-8'), digestmod=hashlib.sha512)
    h.update((metodo + ':' + PIN + ':' + str(tonce)).encode('utf-8'))
    sign = h.hexdigest()
    params = urllib.parse.urlencode({
        'method': metodo,
        'tonce': tonce,
        'pair': 'btc_brl',
        'status': 'active'
    })
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Key": MERCADO_TAPI_CHAVE,
        "Sign": sign
    }

    request = urllib.request.Request('https://www.mercadobitcoin.net/tapi/', params.encode('utf-8'), headers)
    response = urllib.request.urlopen(request).read().decode('utf-8')
    print(response)
    parse = json.loads(response)
    return parse


def get_my_smallest_order(orders):
    min_value = float("inf")
    for key, value in orders["return"].iteritems():
        v = float(value["price"])
        if v < min_value:
            min_value = v

    return min_value


def get_btc_balance(orders):
    total = 0
    for key, value in orders["return"].iteritems():
        total = total + float(value["volume"])
        for key2, value2 in value["operations"].iteritems():
            total = total - float(value2["volume"])

    return total


def get_smaller_orders(orders, value):
    smaller_orders = []
    total = 0
    for item in orders["asks"]:
        if item[0] < value:
            total = total + item[1]
            smaller_orders.append(item)
        else:
            break

    return total, smaller_orders


def main():
    while True:
        print("=[ " + time.strftime("%X") + " ]==============================")

        response1 = get_data("getInfo")
        brl_balance = response1["return"]["funds"]["brl"]

        response2 = get_data("OrderList")
        print(response2)
        exit()

        first_order = get_my_smallest_order(response2)

        if first_order == float("inf"):
            print("Balance BRL: " + str(brl_balance))
            time.sleep(60)
            continue

        btc_balance = get_btc_balance(response2)

        response3 = urllib.request.urlopen(URL_ORDER_BOOK).read()
        all_orders = json.loads(response3)

        total, smaller_orders = get_smaller_orders(all_orders, first_order)
        buy_order_price = all_orders["bids"][0][0]

        print("")
        print("Balance")
        print("    BRL: " + str(brl_balance))
        print("    BTC: " + str(btc_balance))
        print("")
        print("Orders:")
        print("    Mine (sell)  : " + str(first_order))
        print("    Others (buy) : " + str(buy_order_price))
        print("    Others (sell): ")
        for item in smaller_orders:
            print("        %.4f  %.8f" % (item[0], item[1]))
        if len(smaller_orders) > 1:
            print("")
            print("           Total: %.8f" % total)
        print("")

        time.sleep(60)
