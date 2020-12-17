from datetime import datetime
from typing import Dict, List
from bs4 import BeautifulSoup

from utils import (
    create_items_dict,
    xml_file_gen,
    create_bs_object,
)
from supermarket_chain import SupermarketChain

PRODUCTS_TO_IGNORE = ['סירים', 'מגבות', 'צלחות', 'כוסות', 'מאגים', 'מגבת', 'מפות', 'פסטיגל']


class Promotion:
    """
    A class of a promotion in Shufersal.
    It contains only part of the available information in Shufersal's data.
    """

    def __init__(self, content: str, start_date: datetime, end_date: datetime, update_date: datetime, items: List[str]):
        self.content: str = content
        self.start_date = start_date
        self.end_date: datetime = end_date
        self.update_date: datetime = update_date
        self.items: List[str] = items

    def __repr__(self):
        title = self.content
        dates_range = f"Between {self.start_date} and {self.end_date}"
        update_line = f"Updated at {self.update_date}"
        items = '\n'.join(str(item) for item in self.items)
        return '\n'.join([title, dates_range, update_line, items]) + '\n'

    def repr_ltr(self):
        title = self.content[::-1]
        dates_range = f"Between {self.start_date} and {self.end_date}"
        update_line = f"Updated at {self.update_date}"
        items = '\n'.join(str(item)[::-1] for item in self.items)
        return '\n'.join([title, dates_range, update_line, items]) + '\n'


def get_available_promos(chain: SupermarketChain, store_id: int, load_prices: bool, load_promos) -> List[Promotion]:
    """
    This function return the available promotions given a BeautifulSoup object.

    :param load_promos:
    :param chain: The name of the requested supermarket chain
    :param store_id: A given store id
    :param load_prices: A boolean representing whether to load an existing xml or load an already saved one
    :return: Promotions that are not included in PRODUCTS_TO_IGNORE and are currently available
    """
    items_dict: Dict[str, str] = create_items_dict(chain, load_prices, store_id)
    xml_path: str = xml_file_gen(chain, store_id, chain.XMLFilesCategory.PromosFull.name)
    bs_promos = create_bs_object(xml_path, chain, store_id, load_promos, chain.XMLFilesCategory.PromosFull)

    promo_objs = list()
    for promo in bs_promos.find_all(chain.promotion_tag_name):
        promo = Promotion(
            content=promo.find('PromotionDescription').text,
            start_date=datetime.strptime(
                promo.find('PromotionStartDate').text + ' ' + promo.find('PromotionStartHour').text,
                chain.date_hour_format),
            end_date=datetime.strptime(promo.find(
                'PromotionEndDate').text + ' ' + promo.find('PromotionEndHour').text, chain.date_hour_format),
            update_date=datetime.strptime(promo.find(chain.promotion_update_tag_name).text, chain.date_hour_format),
            items=chain.get_items(promo, items_dict),
        )
        if is_valid_promo(promo):
            promo_objs.append(promo)
    return promo_objs


def is_valid_promo(promo: Promotion):
    """
    This function checks if a given promo object is valid.

    :param promo: A given promotion
    :return: True iff the given Promotion is valid.
    """
    today_date: datetime = datetime.now()
    not_expired: bool = promo.end_date >= today_date
    has_started: bool = promo.start_date <= today_date
    has_products: bool = len(promo.items) > 0
    in_promo_ignore_list: bool = any(product in promo.content for product in PRODUCTS_TO_IGNORE)
    return not_expired and has_started and has_products and not in_promo_ignore_list


def main_latest_promos(store_id: int, load_xml: bool, logger, chain: SupermarketChain):
    """
    This function logs the available promos in a  store with a given id sorted by their update date.

    :param chain: The name of the requested supermarket chain
    :param store_id: A given store id
    :param load_xml: A boolean representing whether to load an existing prices xml file
    :param logger: A given logger
    """

    promotions: List[Promotion] = get_available_promos(chain, store_id, load_xml, False)
    promotions.sort(key=lambda promo: max(promo.update_date, promo.start_date), reverse=True)
    logger.info('\n'.join(str(promotion) for promotion in promotions))


def get_promos_by_name(store_id: int, chain: SupermarketChain, promo_name: str, load_prices: bool, load_promos: bool):
    """
    This function prints all promotions in a given chain and store_id containing a given promo_name.

    :param store_id: A given store ID
    :param chain: A given supermarket chain
    :param promo_name: A given name of a promo (or part of it)
    :param load_prices: A boolean representing whether to load an saved prices XML file or scrape a new one
    :param load_promos: A boolean representing whether to load an saved XML file or scrape a new one
    """
    promotions: List[Promotion] = get_available_promos(chain, store_id, load_prices, load_promos)
    for promo in promotions:
        if promo_name in promo.content:
            print(promo.repr_ltr())
