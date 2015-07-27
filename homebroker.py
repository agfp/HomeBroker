import threading
import time
import log
import trader
import sys
import bitnz
from gi.repository import Gtk, GObject


class Handler:
    def on_window1_destroy(*args):
        global trader_thread, stop_trader
        stop_trader = True
        if trader_thread:
            trader_thread.join()
        Gtk.main_quit(*args)

    def on_btnStartTrader_clicked(self, button):
        global trader_thread, stop_trader
        stop_trader = False
        trader_thread = threading.Thread(target=loop)
        trader_thread.start()

    def on_btnStopTrader_clicked(self, button):
        global stop_trader, btn_starttrader, btn_stoptrader
        stop_trader = True

    def on_btnDeleteOrder_clicked(self, button):
        selected = treeview.get_selection().get_selected()
        order_id = list_store.get_value(selected[1], 0)
        if order_id:
            price = list_store.get_value(selected[1], 1)
            amount = list_store.get_value(selected[1], 2)
            bitnz.cancel_order_by_details(int(order_id), float(price), float(amount))
            list_store.remove(selected[1])


def trader_running(state):
    btn_starttrader.set_visible(not state)
    btn_stoptrader.set_visible(state)


def sleep():
    for i in range(20, 0, -1):
        if stop_trader:
            break
        lbl_next_update.set_text(str(i))
        time.sleep(1)


def loop():
    trader_running(True)
    while True:
        try:
            if stop_trader:
                break
            lbl_next_update.set_text('updating...')
            trader.main()
            sleep()

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            log.log_error(exc_type, exc_value, exc_traceback)
            lbl_next_update.set_text('error!')
            time.sleep(10)

    print('Trader Stopped')
    lbl_next_update.set_text('-')
    trader_running(False)


def add_column(p1, p2):
    column = Gtk.TreeViewColumn(p2, Gtk.CellRendererText(), text=p1)
    column.set_resizable(True)
    column.set_sort_column_id(p1)
    treeview.append_column(column)


if __name__ == '__main__':
    trader_thread = None
    GObject.threads_init()
    builder = Gtk.Builder()
    builder.add_from_file("homebroker2.glade")
    builder.connect_signals(Handler())

    treeview = builder.get_object('treeview1')
    add_column(0, 'Id')
    add_column(1, 'Price')
    add_column(2, 'Amount')
    list_store = Gtk.ListStore(str, str, str)
    treeview.set_model(list_store)

    btn_starttrader = builder.get_object('btnStartTrader')
    btn_stoptrader = builder.get_object('btnStopTrader')
    lbl_next_update = builder.get_object('lblNextUpdate')

    log.list_store = list_store
    log.lbl_total_nzd = builder.get_object('lblTotalNZD')
    log.lbl_available_nzd = builder.get_object('lblAvailableNZD')
    log.lbl_available_btc = builder.get_object('lblAvailableBTC')
    log.lbl_max_bid = builder.get_object('lblMaxBid')
    log.lbl_last_update = builder.get_object('lblLastUpdate')
    log.lbl_trading = builder.get_object('lblTrading')
    log.scroll_trading = builder.get_object('scrolledwindow1')

    window = builder.get_object("window1")
    window.show_all()
    trader_running(False)
    Gtk.main()
