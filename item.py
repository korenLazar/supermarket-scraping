import json
import re
from typing import List, Optional

from bs4.element import Tag


class Item:
    """
    A class representing a product in some supermarket.
    """

    def __init__(
        self,
        name: str,
        price: float,
        price_by_measure: float,
        code: str,
        manufacturer: str,
        promotions: Optional[List] = None,
    ):
        self.name: str = name
        self.price: float = price
        self.final_price: float = price
        self.price_by_measure = price_by_measure
        self.manufacturer: str = manufacturer
        self.code: str = code
        self.promotions = (
            promotions if promotions else []
        )  # Promotions the item is participating in

    @classmethod
    def from_tag(cls, item: Tag):
        """
        This method creates an Item instance from an xml tag.
        """
        return cls(
            name=item.find(re.compile(r"ItemN[a]?m[e]?")).text,
            price=float(item.find("ItemPrice").text),
            price_by_measure=float(item.find("UnitOfMeasurePrice").text),
            code=item.find("ItemCode").text,
            manufacturer=item.find(re.compile(r"Manufacture[r]?Name")).text,
        )

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __repr__(self):
        return f"\nשם: {self.name}\nמחיר: {self.price}\nיצרן: {self.manufacturer}\nקוד: {self.code}\n"
