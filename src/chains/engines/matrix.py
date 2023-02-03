import re
from typing import Dict, List
from bs4.element import Tag

from src.item import Item
from src.supermarket_chain import SupermarketChain


class Matrix(SupermarketChain):
    _promotion_tag_name = "Sale"
    _promotion_update_tag_name = "PriceUpdateDate"
    _date_format = "%Y/%m/%d"
    _date_hour_format = "%Y/%m/%d %H:%M:%S"
    _update_date_format = "%Y/%m/%d %H:%M:%S"
    _item_tag_name = "Product"


    @staticmethod
    def get_items(promo: Tag, items_dict: Dict[str, Item]) -> List[Item]:
        promo_item = items_dict.get(promo.find("ItemCode").text)
        return [promo_item] if promo_item else []
