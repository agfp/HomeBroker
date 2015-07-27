class Order:
    def __init__(self, order_id, price, amount):
        self.id = order_id
        self.amount = amount
        self.price = price

    def __repr__(self):
        return 'id: {0} | price: {1} | amount: {2}'.format(self.id, self.price, self.amount)
