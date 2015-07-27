import threading
import time
import log
import trader
import sys
from gi.repository import Gtk, GObject


class Handler:
    def on_window1_destroy(*args):
        Gtk.main_quit(*args)

    def delete_order(self, button):
        a=selection.get_selection().get_selected()
        order_id = list.get_value(a[1],0)
        print(order_id)

def add_column(p1, p2):
    column = Gtk.TreeViewColumn(p2, Gtk.CellRendererText(), text=p1)
    column.set_resizable(True)
    column.set_sort_column_id(p1)
    treeview.append_column(column)


builder = Gtk.Builder()
builder.add_from_file('homebroker2.glade')
builder.connect_signals(Handler())
window = builder.get_object('window1')

selection = builder.get_object('treeview-selection1')

treeview = builder.get_object('treeview1')

add_column(1, 'Id')
add_column(2, 'Price')
add_column(3, 'Amount')




list = Gtk.ListStore(int, str, str)
treeview.set_model(list)
list.append([1, 'xoxota', 'boceta'])
list.append([2, 'bosta', 'cu'])

window.show_all()
Gtk.main()
