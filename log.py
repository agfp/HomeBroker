import time
import traceback
import sys
from gi.repository import GLib

list_store = None
lbl_total_nzd = None
lbl_available_nzd = None
lbl_available_btc = None
lbl_max_bid = None
lbl_last_update = None
lbl_trading = None
scroll_trading = None

info = []
error = []
trading = []



def add_to_treeview(order_id, price, amount):
    list_store.append([str(order_id), '%.8f' % price, '%.8f' % amount])


def log_trading(message, color=None):
    global trading
    #timestamp = time.strftime('%Y-%m-%d %H:%M:%S ')
    timestamp = time.strftime('%H:%M:%S ')
    if not color:
        color = 'black'

    # trading.insert(0, '<span color="%s">%s %s</span>\n' % (color, timestamp, message))
    if len(trading) > 1000:
        del trading[0]
    trading.append('<span color="%s">%s %s</span>\n' % (color, timestamp, message))

    def l():
        lbl_trading.set_markup(''.join(trading))
        adj = scroll_trading.get_vadjustment()
        adj.set_value(adj.get_upper())

    GLib.idle_add(l)


def log_info(message):
    #l = lambda: lbl_info.set_text(message)
    #GLib.idle_add(l)
    pass


def log_error(exc_type, exc_value, exc_traceback):
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
