class Item:
    """
    A class representing a product in some supermarket.
    """

    def __init__(self, name: str, price: float, manufacturer: str, code: int):
        self.name: str = name
        self.price: float = price
        self.manufacturer: str = manufacturer
        self.code: int = code

    def __repr__(self):
        return str((self.name, self.price, self.manufacturer, self.code))
