import json
from typing import Dict, List
import requests
from bs4.element import Tag

from item import Item
from supermarket_chain import SupermarketChain


class ZolVebegadol(SupermarketChain):
    def __repr__(self):
        return 'Zol-Vebegadol'

    class XMLFilesCategory(SupermarketChain.XMLFilesCategory):
        All, Promos, PromosFull, Prices, PricesFull, Stores = range(6)

    promotion_tag_name = 'Promotion'
    promotion_update_tag_name = 'PromotionUpdateDate'
    date_format = '%Y-%m-%d'
    date_hour_format = '%Y-%m-%d %H:%M:%S'
    item_tag_name = 'Item'

    @staticmethod
    def get_download_url(store_id: int, category: SupermarketChain.XMLFilesCategory) -> str:
        prefix = "http://zolvebegadol.binaprojects.com"
        url = prefix + "/MainIO_Hok.aspx"
        req_res: requests.Response = requests.get(url)
        jsons_files = json.loads(req_res.text)
        suffix = next(cur_json["FileNm"] for cur_json in jsons_files if f'-{store_id:03d}-20' in cur_json["FileNm"]
                      and category.name.replace('s', '') in cur_json["FileNm"])
        down_url = '/'.join([prefix, "Download", suffix])
        print(down_url)
        return down_url

    @staticmethod
    def get_items(promo: Tag, items_dict: Dict[str, Item]) -> List[Item]:
        items = list()
        for item in promo.find_all('Item'):
            item_code = item.find('ItemCode').text
            full_item_info = items_dict.get(item_code)
            if full_item_info:
                items.append(full_item_info)
        return items
