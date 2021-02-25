import re
from datetime import datetime
from enum import Enum
from typing import Dict, List
import csv

from item import Item
from utils import (
    create_items_dict,
    xml_file_gen,
    create_bs_object,
)
from supermarket_chain import SupermarketChain

INVALID_OR_UNKNOWN_PROMOTION_FUNCTION = -1

PRODUCTS_TO_IGNORE = ['סירים', 'מגבות', 'מגבת', 'מפות', 'פסטיגל', 'ביגי']


# class ClubID(Enum):
#     Regular = 'מבצע רגיל'
#     Club = 'מועדון'
#     CreditCard = 'כרטיס אשראי'
#     Other = 'אחר'

class ClubID(Enum):
    מבצע_רגיל = 0
    מועדון = 1
    כרטיס_אשראי = 2
    אחר = 3


class RewardType(Enum):
    NO_PROMOTION = 0
    DISCOUNT_IN_AMOUNT = 1
    DISCOUNT_IN_PERCENTAGE = 2
    DISCOUNT_BY_THRESHOLD = 3
    DISCOUNT_IN_ITEM_IF_PURCHASING_OTHER_ITEMS = 6
    SECOND_OR_THIRD_INSTANCE_FOR_FREE = 7
    SECOND_INSTANCE_SAME_DISCOUNT = 8
    SECOND_INSTANCE_DIFFERENT_DISCOUNT = 9
    DISCOUNT_IN_MULTIPLE_INSTANCES = 10


class Promotion:
    """
    A class of a promotion in Shufersal.
    It contains only part of the available information in Shufersal's data.
    """

    def __init__(self, content: str, start_date: datetime, end_date: datetime, update_date: datetime, item: List[Item],
                 promo_func: callable, club_id: ClubID, promotion_id: float, max_qty: int,
                 allow_multiple_discounts: bool, reward_type: RewardType):
        self.content: str = content
        self.start_date: datetime = start_date
        self.end_date: datetime = end_date
        self.update_date: datetime = update_date
        self.promo_func: callable = promo_func
        self.items: List[Item] = item
        self.club_id: ClubID = club_id
        self.max_qty: int = max_qty
        self.allow_multiple_discounts = allow_multiple_discounts
        self.reward_type = reward_type
        self.promotion_id = promotion_id

    # def __repr__(self):
    #     title = self.content
    #     dates_range = f"Between {self.start_date} and {self.end_date}"
    #     update_line = f"Updated at {self.update_date}"
    #     items = '\n'.join(str(item) for item in self.item)
    #     return '\n'.join([title, dates_range, update_line, items]) + '\n'

    def repr_ltr(self):
        title = self.content
        dates_range = f"Between {self.start_date} and {self.end_date}"
        update_line = f"Updated at {self.update_date}"
        # items = '\n'.join(str(item) for item in self.item)
        return '\n'.join([title, dates_range, update_line, str(self.items)]) + '\n'

    def __eq__(self, other):
        return self.promotion_id == other.promotion_id


def write_promotions_to_csv(promotions: List[Promotion], output_filename: str) -> None:
    """
    This function writes a given list of promotions to a given output file in a CSV format.

    :param promotions: A given list of promotions
    :param output_filename: A given file to write to
    """
    with open(output_filename, mode='w', newline='') as f_out:
        promos_writer = csv.writer(f_out)
        promos_writer.writerow([
            'תיאור מבצע',
            'הפריט המשתתף במבצע',
            'מחיר לפני מבצע',
            'מחיר אחרי מבצע',
            'אחוז הנחה',
            'סוג מבצע',
            'כמות מקסימלית',
            'כפל הנחות',
            'זמן תחילת מבצע',
            'זמן סיום מבצע',
            'זמן עדכון אחרון',
            'יצרן',
            'ברקוד פריט',
            'סוג מבצע',
        ])

        for promo in promotions:
            promos_writer.writerows(
                [[promo.content,
                  item.name,
                  item.price,
                  f'{promo.promo_func(item):.3f}',
                  f'{(item.price - promo.promo_func(item)) / item.price:.3%}',
                  promo.club_id.name.replace('_', ' '),
                  promo.max_qty,
                  promo.allow_multiple_discounts,
                  promo.start_date,
                  promo.end_date,
                  promo.update_date,
                  item.manufacturer,
                  item.code,
                  promo.reward_type.value] for item in promo.items]
            )


def get_available_promos(chain: SupermarketChain, store_id: int, load_prices: bool, load_promos) -> List[Promotion]:
    """
    This function return the available promotions given a BeautifulSoup object.

    :param load_promos:
    :param chain: The name of the requested supermarket chain
    :param store_id: A given store id
    :param load_prices: A boolean representing whether to load an existing xml or load an already saved one
    :return: Promotions that are not included in PRODUCTS_TO_IGNORE and are currently available
    """
    items_dict: Dict[str, Item] = create_items_dict(chain, load_prices, store_id)
    xml_path: str = xml_file_gen(chain, store_id, chain.XMLFilesCategory.PromosFull.name)
    bs_promos = create_bs_object(xml_path, chain, store_id, load_promos, chain.XMLFilesCategory.PromosFull)

    promo_objs = list()
    for promo in bs_promos.find_all(chain.promotion_tag_name):
        promotion_id = promo.find(re.compile('PromotionId', re.IGNORECASE))
        if promo_objs and promo_objs[-1].promotion_id == promotion_id:
            promo_objs[-1].items.extend(chain.get_items(promo, items_dict))
            continue

        promo_inst = create_new_promo_instance(chain, items_dict, promo, promotion_id)
        if promo_inst:
            promo_objs.append(promo_inst)

    return promo_objs


def create_new_promo_instance(chain, items_dict, promo, promotion_id):
    reward_type = RewardType(int(promo.find("RewardType").text))
    discounted_price = get_discounted_price(promo)
    promo_description = promo.find('PromotionDescription').text
    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(promo, is_discount_in_percentage)
    min_qty = get_int_from_tag(promo, 'MinQty')
    max_qty = get_int_from_tag(promo, 'MaxQty')
    remark = promo.find("Remark")
    promo_func = determine_promo_function(
        reward_type=reward_type,
        remark=remark,
        promo_description=promo_description,
        discounted_price=discounted_price,
        discount_rate=discount_rate,
        min_qty=min_qty,
    )
    promo_start_time = datetime.strptime(promo.find('PromotionStartDate').text + ' ' +
                                         promo.find('PromotionStartHour').text,
                                         chain.date_hour_format)
    promo_end_time = datetime.strptime(promo.find('PromotionEndDate').text + ' ' +
                                       promo.find('PromotionEndHour').text,
                                       chain.date_hour_format)
    promo_update_time = datetime.strptime(promo.find(chain.promotion_update_tag_name).text,
                                          chain.update_date_format)
    club_id = ClubID(int(promo.find(re.compile('ClubId', re.IGNORECASE)).text))
    multiple_discounts_allowed = bool(int(promo.find('AllowMultipleDiscounts').text))
    items = chain.get_items(promo, items_dict)

    if is_valid_promo(start_time=promo_start_time, end_time=promo_end_time, description=promo_description):
        return Promotion(content=promo_description, start_date=promo_start_time, end_date=promo_end_time,
                         update_date=promo_update_time, item=items, promo_func=promo_func,
                         club_id=club_id, promotion_id=promotion_id, max_qty=max_qty,
                         allow_multiple_discounts=multiple_discounts_allowed, reward_type=reward_type)


def get_int_from_tag(tag, int_tag):
    content = tag.find(int_tag)
    return int(float(content.text)) if content else 0


def get_discounted_price(promo):
    discounted_price = promo.find('DiscountedPrice')
    if discounted_price:
        return float(discounted_price.text)


def get_discount_rate(promo, discount_in_percentage):
    discount_rate = promo.find("DiscountRate")
    if discount_rate:
        if discount_in_percentage:
            return int(discount_rate.text) * (10 ** -(len(str(discount_rate.text))))
        return float(discount_rate.text)


def determine_promo_function(reward_type, remark, promo_description, discounted_price, discount_rate, min_qty):
    if reward_type == RewardType.SECOND_INSTANCE_DIFFERENT_DISCOUNT:
        if not discounted_price:
            return lambda item: item.price * (1 - (discount_rate / min_qty))
        else:
            return lambda item: (item.price * (min_qty - 1) + discounted_price) / min_qty

    elif reward_type == RewardType.DISCOUNT_IN_ITEM_IF_PURCHASING_OTHER_ITEMS:
        return lambda item: item.price

    elif reward_type == RewardType.SECOND_OR_THIRD_INSTANCE_FOR_FREE:
        return lambda item: item.price * (1 - (1 / min_qty))

    elif reward_type == RewardType.DISCOUNT_IN_PERCENTAGE:
        return lambda item: item.price * (1 - discount_rate / (2 if "השני ב" in promo_description else 1))

    elif reward_type == RewardType.SECOND_INSTANCE_SAME_DISCOUNT:
        if "השני ב" in promo_description:
            return lambda item: (item.price + discounted_price) / 2
        else:
            return lambda item: discounted_price / min_qty

    elif reward_type == RewardType.DISCOUNT_BY_THRESHOLD:
        return lambda item: item.price - discount_rate

    elif remark and 'מחיר המבצע הינו המחיר לק"ג' in remark.text:
        return lambda item: discounted_price

    elif discounted_price and min_qty:
        return lambda item: discounted_price / min_qty

    return lambda item: INVALID_OR_UNKNOWN_PROMOTION_FUNCTION


def is_valid_promo(start_time: datetime, end_time: datetime, description):
    """
    This function returns whether a given Promotion object is currently valid.
    """
    today_date: datetime = datetime.now()
    not_expired: bool = end_time >= today_date
    has_started: bool = start_time <= today_date
    in_promo_ignore_list: bool = any(product in description for product in PRODUCTS_TO_IGNORE)
    return not_expired and has_started and not in_promo_ignore_list


def main_latest_promos(store_id: int, load_xml: bool, chain: SupermarketChain, load_promos: bool):
    """
    This function writes to a CSV file the available promotions in a store with a given id sorted by their update date.

    :param chain: The name of the requested supermarket chain
    :param store_id: A given store id
    :param load_xml: A boolean representing whether to load an existing prices xml file
    :param load_promos: A boolean representing whether to load an existing promos xml file
    """

    promotions: List[Promotion] = get_available_promos(chain, store_id, load_xml, load_promos)
    promotions.sort(key=lambda promo: (max(promo.update_date.date(), promo.start_date.date()), promo.start_date -
                                       promo.end_date), reverse=True)
    write_promotions_to_csv(promotions, f'results/{repr(type(chain))}_promos_{store_id}.csv')


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


def get_all_null_items_in_promos(chain, store_id):
    """
    This function finds all items appearing in the chain's promotions file but not in the chain's prices file.
    """
    items_dict: Dict[str, Item] = create_items_dict(chain, True, store_id)
    xml_path: str = xml_file_gen(chain, store_id, chain.XMLFilesCategory.PromosFull.name)
    bs_promos = create_bs_object(xml_path, chain, store_id, True, chain.XMLFilesCategory.PromosFull)

    null_items = list()
    for promo in bs_promos.find_all(chain.promotion_tag_name):
        null_items.extend(chain.get_null_items(promo, items_dict))

    return null_items
