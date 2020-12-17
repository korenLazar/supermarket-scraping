from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from supermarket_chain import SupermarketChain


class ShuferSal(SupermarketChain):
    promotion_tag_name = 'Promotion'
    promotion_update_tag_name = 'PromotionUpdateDate'
    date_format = '%Y-%m-%d'
    date_hour_format = '%Y-%m-%d %H:%M'
    item_tag_name = 'Item'

    @staticmethod
    def get_download_url(store_id: int, category: SupermarketChain.XMLFilesCategory) -> str:
        url = f"http://prices.shufersal.co.il/FileObject/UpdateCategory?catID={category.value}"
        if SupermarketChain.is_valid_store_id(store_id):
            url += f"&storeId={store_id}"
        req_res: requests.Response = requests.get(url)
        soup = BeautifulSoup(req_res.text, features='lxml')
        return soup.find('a', text="לחץ להורדה")['href']

    class XMLFilesCategory(SupermarketChain.XMLFilesCategory):
        All, Prices, PricesFull, Promos, PromosFull, Stores = range(6)

    def __repr__(self):
        return 'Shufersal'

    @staticmethod
    def get_items(promo: Tag, items_dict: Dict[str, str]) -> List[str]:
        return [items_dict.get(item.find('ItemCode').text) for item in promo.find_all('Item')
                if items_dict.get(item.find('ItemCode').text)]
