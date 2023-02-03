import re
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
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

    def get_filter_function(
        links: list,
        store_id: int,
        category: SupermarketChain.XMLFilesCategory,
    ):
        if category in [
            SupermarketChain.XMLFilesCategory.Promos,
            SupermarketChain.XMLFilesCategory.Prices,
        ]:
            fname_filter_func = (
                lambda fname: fname
                and category.name.replace("s", "") in fname
                and f"-{store_id:03d}-20" in fname
                and not re.search("full", fname, re.IGNORECASE)
            )
        else:
            fname_filter_func = (
                lambda fname: fname
                and category.name.replace("s", "") in fname
                and f"-{store_id:03d}-20" in fname
            )

        return list(filter(fname_filter_func,links))



    @staticmethod
    def get_items(promo: Tag, items_dict: Dict[str, Item]) -> List[Item]:
        promo_item = items_dict.get(promo.find("ItemCode").text)
        return [promo_item] if promo_item else []
