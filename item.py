class Item:
    """
    A class representing a product in some supermarket.
    """

    def __init__(self, name: str, price: float, price_by_measure: float, code: str, manufacturer: str):
        self.name: str = name
        self.price: float = price
        self.price_by_measure = price_by_measure
        self.manufacturer: str = manufacturer
        self.code: str = code

    def __repr__(self):
        return f"\nשם: {self.name}\nמחיר: {self.price}\nיצרן: {self.manufacturer}\nקוד: {self.code}\n"
