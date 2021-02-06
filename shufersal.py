from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from item import Item
from supermarket_chain import SupermarketChain


class ShuferSal(SupermarketChain):
    promotion_tag_name = 'Promotion'
    promotion_update_tag_name = 'PromotionUpdateDate'
    date_format = '%Y-%m-%d'
    date_hour_format = '%Y-%m-%d %H:%M'
    item_tag_name = 'Item'

    @property
    def update_date_format(self):
        return ShuferSal.date_hour_format

    @staticmethod
    def get_download_url(store_id: int, category: SupermarketChain.XMLFilesCategory, session: requests.Session) -> str:
        url = f"http://prices.shufersal.co.il/FileObject/UpdateCategory?catID={category.value}"
        if SupermarketChain.is_valid_store_id(int(store_id)):
            url += f"&storeId={store_id}"
        req_res: requests.Response = requests.get(url)
        soup = BeautifulSoup(req_res.text, features='lxml')
        down_url = soup.find('a', text="לחץ להורדה")['href']
        print(down_url)
        return down_url

    class XMLFilesCategory(SupermarketChain.XMLFilesCategory):
        All, Prices, PricesFull, Promos, PromosFull, Stores = range(6)

    def __repr__(self):
        return 'Shufersal'

    @staticmethod
    def get_items(promo: Tag, items_dict: Dict[str, Item]) -> List[Item]:
        items = list()
        for item in promo.find_all('Item'):
            item_code = item.find('ItemCode').text
            full_item_info = items_dict.get(item_code)
            if full_item_info:
                items.append(full_item_info)
        return items
