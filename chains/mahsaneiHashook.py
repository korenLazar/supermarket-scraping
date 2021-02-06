from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from item import Item
from supermarket_chain import SupermarketChain


class MahsaneiHashook(SupermarketChain):
    _promotion_tag_name = 'Sale'
    _promotion_update_tag_name = 'PriceUpdateDate'
    _date_format = '%Y/%m/%d'
    _date_hour_format = '%Y/%m/%d %H:%M:%S'
    _update_date_format = '%Y/%m/%d %H:%M:%S'
    _item_tag_name = 'Product'

    @staticmethod
    def get_download_url(store_id: int, category: SupermarketChain.XMLFilesCategory, session: requests.Session) -> str:
        prefix = "http://matrixcatalog.co.il/"
        url = prefix + "NBCompetitionRegulations.aspx"
        req_res: requests.Response = requests.get(url)
        soup = BeautifulSoup(req_res.text, features='lxml')
        suffix: str = soup.find('a', href=lambda value: value and category.name.replace('s', '') in value
                                                        and f'-{store_id:03d}-20' in value).attrs['href']
        down_url: str = prefix + suffix
        print(down_url)
        return down_url

    @staticmethod
    def get_items(promo: Tag, items_dict: Dict[str, Item]) -> List[Item]:
        promo_item = items_dict.get(promo.find('ItemCode').text)
        return [promo_item] if promo_item else []
