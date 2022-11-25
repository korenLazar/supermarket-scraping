import re
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from src.item import Item
from src.supermarket_chain import SupermarketChain


class MahsaneiHashook(SupermarketChain):
    _promotion_tag_name = "Sale"
    _promotion_update_tag_name = "PriceUpdateDate"
    _date_format = "%Y/%m/%d"
    _date_hour_format = "%Y/%m/%d %H:%M:%S"
    _update_date_format = "%Y/%m/%d %H:%M:%S"
    _item_tag_name = "Product"

    @staticmethod
    def get_download_url_or_path(
        store_id: int,
        category: SupermarketChain.XMLFilesCategory,
        session: requests.Session,
    ) -> str:
        prefix = "http://matrixcatalog.co.il/"
        url = prefix + "NBCompetitionRegulations.aspx"
        req_res: requests.Response = requests.get(url)
        soup = BeautifulSoup(req_res.text, features="lxml")
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
            if soup.find("a", href=fname_filter_func) is None:
                return ""  # Could not find non-full Promos/Prices file
        else:
            fname_filter_func = (
                lambda fname: fname
                and category.name.replace("s", "") in fname
                and f"-{store_id:03d}-20" in fname
            )
        suffix: str = soup.find("a", href=fname_filter_func).attrs["href"]
        down_url: str = prefix + suffix
        return down_url

    @staticmethod
    def get_items(promo: Tag, items_dict: Dict[str, Item]) -> List[Item]:
        promo_item = items_dict.get(promo.find("ItemCode").text)
        return [promo_item] if promo_item else []
