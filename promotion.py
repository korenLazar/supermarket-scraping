from datetime import datetime
from typing import List
from utils import (
    ShufersalCategories,
    create_items_dict,
    xml_file_gen,
    create_bs_object,
)

PRODUCTS_TO_IGNORE = ['סירים', 'מגבות', 'צלחות', 'כוסות', 'מאגים', 'מגבת', 'מפות', 'פסטיגל']


class Promotion:
    """
    A class of a promotion in Shufersal.
    It contains only part of the available information in Shufersal's data.
    """

    def __init__(self, content: str, start_date: datetime, end_date: datetime, update_date: datetime,
                 code_items: List[str]):
        self.content: str = content
        self.start_date = start_date
        self.end_date: datetime = end_date
        self.update_date: datetime = update_date
        self.code_items: List[str] = code_items

    def __str__(self):
        title = self.content
        dates_range = f"Between {self.start_date.date()} and {self.end_date.date()}"
        update_line = f"Updated at {self.update_date.date()}"
        items = '\n'.join(str(item) for item in self.code_items)
        return '\n'.join([title, dates_range, update_line, items]) + '\n'


def get_available_promos(store_id: int, load_xml: bool) -> List[Promotion]:
    """
    This function return the available promotions given a BeautifulSoup object.

    :param store_id: A given store id
    :param load_xml: A boolean representing whether to load an existing xml or load an already saved one
    :return: Promotions that are not included in PRODUCTS_TO_IGNORE and are currently available
    """
    items_dict = create_items_dict(store_id, load_xml)
    xml_path = xml_file_gen(ShufersalCategories.PromosFull.name, store_id)
    bs_promos = create_bs_object(xml_path, ShufersalCategories.PromosFull.value, store_id, False)

    promo_objs = list()
    for cur_promo in bs_promos.find_all("Promotion"):
        cur_promo = Promotion(
            content=cur_promo.find('PromotionDescription').text,
            start_date=datetime.strptime(cur_promo.find('PromotionStartDate').text, '%Y-%m-%d'),
            end_date=datetime.strptime(cur_promo.find('PromotionEndDate').text, '%Y-%m-%d'),
            update_date=datetime.strptime(cur_promo.find('PromotionUpdateDate').text, '%Y-%m-%d %H:%M'),
            code_items=[items_dict.get(item.find('ItemCode').text) for item in cur_promo.find_all('Item')
                        if items_dict.get(item.find('ItemCode').text)],
        )
        if is_valid_promo(cur_promo):
            promo_objs.append(cur_promo)
    return promo_objs


def is_valid_promo(promo: Promotion):
    today_date = datetime.now()
    not_expired = promo.end_date.date() >= today_date.date()
    has_started = promo.start_date <= today_date
    has_products = len(promo.code_items) > 0
    in_promo_ignore_list = any(product in promo.content for product in PRODUCTS_TO_IGNORE)
    return not_expired and has_started and has_products and not in_promo_ignore_list


def main_latest_promos(store_id: int, load_xml: bool, logger):
    """
    This function logs the available promos in a  store with a given id sorted by their update date.

    :param store_id: A given store id
    :param load_xml: A boolean representing whether to load an existing prices xml file
    :param logger: A given logger
    """

    promotions = get_available_promos(store_id, load_xml)
    promotions.sort(key=lambda promo: max(promo.update_date, promo.start_date), reverse=True)
    logger.info('\n'.join(str(promotion) for promotion in promotions))
