import bitnz
import mercadobitcoin
import time
import log

EXCHANGE_RATE = 2.19
TOP_ORDER_PRICE = 1


def delete_overpriced_bids(max_value, orders):
    for i in range(len(orders) - 1, -1, -1):
        if orders[i].price > max_value:
            log.log_trading('Deleting overpriced order')
            bitnz.cancel_order(orders[i])
            del orders[i]


def find_next_order(price, orders):
    for order in orders:
        if order.price < price:
            return order
    return None


def place_first_order(max_price, my_order, orders):
    # TODO: receive balance as parameter and check:
    # TODO: 1) is it possible to place before cancel?
    # TODO: 2) do i have balance for creating order?
    if my_order.price == orders[0].price and my_order.amount == orders[0].amount:  # My order is top order
        next_order = find_next_order(my_order.price, orders)
        update, price = False, 0

        if my_order.price - next_order.price > 0.2:  # If price is can be reduced
            log.log_trading('Reducing top order price')
            update = True
            price = next_order.price + 0.1
        elif my_order.amount < TOP_ORDER_PRICE:  # If my top order is less than TOP_ORDER_PRICE BTC
            log.log_trading('Increasing top order amount')
            update = True
            price = my_order.price

        if update:
            bitnz.place_order(price, TOP_ORDER_PRICE)
            bitnz.cancel_order(my_order)
            my_order.price = price
            my_order.amount = TOP_ORDER_PRICE

    elif not my_order.price == max_price:  # If my order is not top order and is not max_price
        log.log_trading('Replacing top order')
        price = orders[0].price + 1e-8
        if price > max_price:
            price = max_price
        bitnz.place_order(price, TOP_ORDER_PRICE)
        bitnz.cancel_order(my_order)
        my_order.price = price
        my_order.amount = TOP_ORDER_PRICE


def place_orders(my_orders, orders, max_price):
    place_first_order(max_price, my_orders[0], orders)


def print_stats(balance, max_price):
    log.lbl_total_nzd.set_text('%.2f' % balance['nzd_balance'])
    log.lbl_available_nzd.set_text('%.2f' % balance['nzd_available'])
    log.lbl_available_btc.set_text('%.6f' % balance['btc_available'])
    log.lbl_max_bid.set_text(str(max_price))
    log.lbl_last_update.set_text(time.strftime('%X'))


def print_orders(my_orders, orders):
    log.list_store.clear()
    minimum = my_orders[-1].price
    for item in orders:
        if item.price >= minimum:
            amount = item.amount
            for mine in my_orders:
                if mine.price == item.price:
                    log.add_to_treeview(mine.id, mine.price, mine.amount)
                    amount = item.amount - mine.amount
                    break
            if amount > 0:
                log.add_to_treeview('', item.price, amount)
        else:
            break


def main():
    max_price = int(mercadobitcoin.average_bid() / EXCHANGE_RATE)
    my_orders = bitnz.get_my_orders()

    delete_overpriced_bids(max_price, my_orders)
    balance = bitnz.get_balance()
    print_stats(balance, max_price)
    buy_orders = bitnz.get_buy_orders()
    print_orders(my_orders, buy_orders)

    place_orders(my_orders, buy_orders, max_price)


if __name__ == '__main__':
    while True:
        main()
        time.sleep(30)
