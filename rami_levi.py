import json
from typing import Dict, List
import requests
from bs4.element import Tag

from item import Item
from supermarket_chain import SupermarketChain


class RamiLevi(SupermarketChain):
    @property
    def promotion_tag_name(self):
        return 'Promotion'

    @property
    def promotion_update_tag_name(self):
        return 'PromotionUpdateDate'

    @property
    def date_format(self):
        return '%Y-%m-%d'

    @property
    def date_hour_format(self):
        return '%Y-%m-%d %H:%M:%S'

    @property
    def update_date_format(self):
        return '%Y-%m-%d %H:%M'

    @property
    def item_tag_name(self):
        return 'Item'

    @staticmethod
    def get_download_url(store_id: int, category: SupermarketChain.XMLFilesCategory, session: requests.Session) -> str:
        hostname = "https://publishedprices.co.il"

        # Post the payload to the site to log in
        session.post(hostname + "/login/user", data={'username': 'ramilevi'})

        # Scrape the data
        ajax_dir_payload = {'iDisplayLength': 100000, 'sSearch': category.name.replace('s', '')}
        s = session.post(hostname + "/file/ajax_dir", data=ajax_dir_payload)
        s_json = json.loads(s.text)
        suffix = next(d['name'] for d in s_json['aaData'] if f'-{store_id:03d}-20' in d['name'])

        download_url = hostname + "/file/d/" + suffix
        print(download_url)
        return download_url

    @staticmethod
    def get_items(promo: Tag, items_dict: Dict[str, Item]) -> List[Item]:
        items = list()
        for item in promo.find_all('Item'):
            item_code = item.find('ItemCode').text
            full_item_info = items_dict.get(item_code)
            if full_item_info:
                items.append(full_item_info)
        return items

    class XMLFilesCategory(SupermarketChain.XMLFilesCategory):
        All, Promos, PromosFull, Prices, PricesFull, Stores = range(6)

    def __repr__(self):
        return 'RamiLevi'
