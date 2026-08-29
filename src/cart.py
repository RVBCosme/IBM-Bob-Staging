"""Shop cart pricing. Items are (unit_price, quantity) pairs."""


def subtotal(items):
    return round(sum(price * qty for price, qty in items), 2)
