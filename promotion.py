import logging
import re
from datetime import datetime
from enum import Enum
from typing import Dict, List, Union
from bs4.element import Tag
import csv
import sys
import pandas as pd
import xlsxwriter
from tqdm import tqdm

from item import Item
from utils import (
    create_bs_object, create_items_dict,
    get_float_from_tag,
    log_message_and_time_if_debug, xml_file_gen,
)
from supermarket_chain import SupermarketChain

XML_FILES_PROMOTIONS_CATEGORIES = [SupermarketChain.XMLFilesCategory.PromosFull,
                                   SupermarketChain.XMLFilesCategory.Promos]

INVALID_OR_UNKNOWN_PROMOTION_FUNCTION = -1

PROMOTIONS_TABLE_HEADERS = [
    'תיאור מבצע',
    'הפריט המשתתף במבצע',
    'מחיר לפני מבצע',
    'מחיר אחרי מבצע',
    'אחוז הנחה',
    'סוג מבצע',
    'כמות מקס',
    'כפל הנחות',
    'המבצע החל',
    'זמן תחילת מבצע',
    'זמן סיום מבצע',
    'זמן עדכון אחרון',
    'יצרן',
    'ברקוד פריט',
    'סוג מבצע לפי תקנות שקיפות מחירים',
]


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

    def __init__(self, content: str, start_date: datetime, end_date: datetime, update_date: datetime, items: List[Item],
                 promo_func: callable, club_id: ClubID, promotion_id: int, max_qty: int,
                 allow_multiple_discounts: bool, reward_type: RewardType):
        self.content: str = content
        self.start_date: datetime = start_date
        self.end_date: datetime = end_date
        self.update_date: datetime = update_date
        self.promo_func: callable = promo_func
        self.items: List[Item] = items
        self.club_id: ClubID = club_id
        self.max_qty: int = max_qty
        self.allow_multiple_discounts: bool = allow_multiple_discounts
        self.reward_type: RewardType = reward_type
        self.promotion_id: int = promotion_id

    def repr_ltr(self):
        title = self.content
        dates_range = f"Between {self.start_date} and {self.end_date}"
        update_line = f"Updated at {self.update_date}"
        return '\n'.join([title, dates_range, update_line, str(self.items)]) + '\n'

    def __eq__(self, other):
        return self.promotion_id == other.promotion_id


def write_promotions_to_csv(promotions: List[Promotion], output_filename: str) -> None:
    """
    This function writes a promotions table to a given CSV or XLSX output file.

    :param promotions: A given list of promotions
    :param output_filename: A given file to write to
    """
    log_message_and_time_if_debug('Writing promotions to output file')
    rows = [get_promotion_row_for_csv(promo, item) for promo in promotions for item in promo.items]
    if output_filename.endswith('.csv'):
        encoding_file = "utf_8_sig" if sys.platform == "win32" else "utf_8"
        with open(output_filename, mode='w', newline='', encoding=encoding_file) as f_out:
            promos_writer = csv.writer(f_out)
            promos_writer.writerow(PROMOTIONS_TABLE_HEADERS)
            promos_writer.writerows(rows)

    elif output_filename.endswith('.xlsx'):
        df = pd.DataFrame(rows, columns=PROMOTIONS_TABLE_HEADERS)
        workbook = xlsxwriter.Workbook(output_filename)
        worksheet1 = workbook.add_worksheet()
        worksheet1.right_to_left()
        date_time_format = workbook.add_format({'num_format': 'm/d/yy h:mm;@'})
        number_format = workbook.add_format({'num_format': '0.00'})
        percentage_format = workbook.add_format({'num_format': '0.00%'})
        worksheet1.set_column('A:A', width=35)
        worksheet1.set_column('B:B', width=25)
        worksheet1.set_column('C:D', cell_format=number_format)
        worksheet1.set_column('E:E', cell_format=percentage_format)
        worksheet1.set_column('J:L', width=15, cell_format=date_time_format)
        worksheet1.add_table(
            first_row=0,
            first_col=0,
            last_row=len(df),
            last_col=len(df.columns) - 1,
            options={
                "columns": [{"header": i} for i in PROMOTIONS_TABLE_HEADERS],
                "data": df.values.tolist(),
                'style': 'Table Style Medium 11',
            }, )
        workbook.close()

    else:
        raise ValueError(f"The given output file has an invalid extension:\n{output_filename}")


def get_promotion_row_for_csv(promo: Promotion, item: Item):
    """
    This function returns a row in the promotions XLSX table.

    :param promo: A given Promotion object
    :param item: A given item object participating in the promotion
    """
    return [promo.content,
            item.name,
            item.price,
            promo.promo_func(item),
            (item.price - promo.promo_func(item)) / item.price,
            promo.club_id.name.replace('_', ' '),
            promo.max_qty,
            promo.allow_multiple_discounts,
            promo.start_date <= datetime.now(),
            promo.start_date,
            promo.end_date,
            promo.update_date,
            item.manufacturer,
            item.code,
            promo.reward_type.value]


def get_available_promos(chain: SupermarketChain, store_id: int, load_prices: bool, load_promos: bool) \
        -> List[Promotion]:
    """
    This function return the available promotions given a BeautifulSoup object.

    :param chain: The name of the requested supermarket chain
    :param store_id: A given store ID
    :param load_prices: A boolean representing whether to load an existing prices file or download it
    :param load_promos: A boolean representing whether to load an existing promotion file or download it
    :return: Promotions that are not included in PRODUCTS_TO_IGNORE and are currently available
    """
    log_message_and_time_if_debug('Importing prices XML file')
    items_dict: Dict[str, Item] = create_items_dict(chain, store_id, load_prices)
    log_message_and_time_if_debug('Importing promotions XML file')
    promo_tags = get_all_promos_tags(chain, store_id, load_promos)

    log_message_and_time_if_debug('Creating promotions objects')
    promo_objs = list()
    for promo in tqdm(promo_tags, desc='creating_promotions'):
        promotion_id = int(promo.find(re.compile('PromotionId', re.IGNORECASE)).text)
        if promo_objs and promo_objs[-1].promotion_id == promotion_id:
            promo_objs[-1].items.extend(chain.get_items(promo, items_dict))
            continue

        promo_inst = create_new_promo_instance(chain, items_dict, promo, promotion_id)
        if promo_inst:
            promo_objs.append(promo_inst)

    return promo_objs


def create_new_promo_instance(chain: SupermarketChain, items_dict: Dict[str, Item], promo: Tag, promotion_id: int) \
        -> Union[Promotion, None]:
    """
    This function generates a Promotion object from a promotion tag.

    :param chain: The supermarket chain publishing the promotion
    :param items_dict: A dictionary of items that might participate in the promotion
    :param promo: An xml Tag representing the promotion
    :param promotion_id: An integer representing the promotion ID
    :return: If the promotion expired - return None, else return the Promotion object
    """
    promo_end_time = datetime.strptime(promo.find('PromotionEndDate').text + ' ' +
                                       promo.find('PromotionEndHour').text,
                                       chain.date_hour_format)
    if promo_end_time < datetime.now():
        return None

    reward_type = RewardType(int(promo.find("RewardType").text))
    discounted_price = get_discounted_price(promo)
    promo_description = promo.find('PromotionDescription').text
    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    raw_discount_rate = promo.find('DiscountRate').text if promo.find('DiscountRate') else None
    discount_rate = get_discount_rate(raw_discount_rate, is_discount_in_percentage)
    min_qty = get_float_from_tag(promo, 'MinQty')
    max_qty = get_float_from_tag(promo, 'MaxQty')
    remark = promo.find("Remark")
    promo_func = find_promo_function(reward_type=reward_type, remark=remark.text if remark else '',
                                     promo_description=promo_description, min_qty=min_qty,
                                     discount_rate=discount_rate, discounted_price=discounted_price)
    promo_start_time = datetime.strptime(promo.find('PromotionStartDate').text + ' ' +
                                         promo.find('PromotionStartHour').text,
                                         chain.date_hour_format)
    promo_update_time = datetime.strptime(promo.find(chain.promotion_update_tag_name).text,
                                          chain.update_date_format)
    club_id = ClubID(int(promo.find(re.compile('ClubId', re.IGNORECASE)).text))
    multiple_discounts_allowed = bool(int(promo.find('AllowMultipleDiscounts').text))
    items = chain.get_items(promo, items_dict)

    return Promotion(content=promo_description, start_date=promo_start_time, end_date=promo_end_time,
                     update_date=promo_update_time, items=items, promo_func=promo_func,
                     club_id=club_id, promotion_id=promotion_id, max_qty=max_qty,
                     allow_multiple_discounts=multiple_discounts_allowed, reward_type=reward_type)


def get_discounted_price(promo):
    discounted_price = promo.find('DiscountedPrice')
    if discounted_price:
        return float(discounted_price.text)


def get_discount_rate(discount_rate: Union[float, None], discount_in_percentage: bool):
    if discount_rate:
        if discount_in_percentage:
            return int(discount_rate) * (10 ** -(len(str(discount_rate))))
        return float(discount_rate)


def find_promo_function(reward_type: RewardType, remark: str, promo_description: str, min_qty: float,
                        discount_rate: Union[float, None], discounted_price: Union[float, None]):
    if reward_type == RewardType.SECOND_INSTANCE_DIFFERENT_DISCOUNT:
        if not discounted_price:
            return lambda item: item.price * (1 - (discount_rate / min_qty))
        return lambda item: (item.price * (min_qty - 1) + discounted_price) / min_qty

    if reward_type == RewardType.DISCOUNT_IN_ITEM_IF_PURCHASING_OTHER_ITEMS:
        return lambda item: item.price

    if reward_type == RewardType.SECOND_OR_THIRD_INSTANCE_FOR_FREE:
        return lambda item: item.price * (1 - (1 / min_qty))

    if reward_type == RewardType.DISCOUNT_IN_PERCENTAGE:
        return lambda item: item.price * (1 - discount_rate / (2 if "השני ב" in promo_description else 1))

    if reward_type == RewardType.SECOND_INSTANCE_SAME_DISCOUNT:
        if "השני ב" in promo_description:
            return lambda item: (item.price + discounted_price) / 2
        return lambda item: discounted_price / min_qty

    if reward_type == RewardType.DISCOUNT_BY_THRESHOLD:
        return lambda item: item.price - discount_rate

    if 'מחיר המבצע הינו המחיר לק"ג' in remark:
        return lambda item: discounted_price

    if discounted_price and min_qty:
        return lambda item: discounted_price / min_qty

    return lambda item: INVALID_OR_UNKNOWN_PROMOTION_FUNCTION


def main_latest_promos(store_id: int, output_filename, chain: SupermarketChain, load_promos: bool,
                       load_xml: bool) -> None:
    """
    This function writes to a file the available promotions in a store with a given id sorted by their update date.

    :param chain: The name of the requested supermarket chain
    :param store_id: A given store id
    :param load_xml: A boolean representing whether to load an existing prices xml file
    :param load_promos: A boolean representing whether to load an existing promos xml file
    :param output_filename: A path to write the promotions table
    """
    promotions: List[Promotion] = get_available_promos(chain, store_id, load_xml, load_promos)
    promotions.sort(key=lambda promo: (max(promo.update_date.date(), promo.start_date.date()), promo.start_date -
                                       promo.end_date), reverse=True)
    write_promotions_to_csv(promotions, output_filename)


def log_promos_by_name(store_id: int, chain: SupermarketChain, promo_name: str, load_prices: bool, load_promos: bool):
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
            logging.info(promo.repr_ltr())


# TODO: change to returning list of Items
def get_all_null_items_in_promos(chain, store_id) -> List[str]:
    """
    This function finds all items appearing in the chain's promotions file but not in the chain's prices file.
    Outdated.
    """
    items_dict: Dict[str, Item] = create_items_dict(chain, store_id, load_xml=True)
    promo_tags = get_all_promos_tags(chain, store_id, load_xml=True)
    return [item for promo_tag in promo_tags for item in chain.get_null_items(promo_tag, items_dict)]


def get_all_promos_tags(chain: SupermarketChain, store_id: int, load_xml: bool) -> List[Tag]:
    """
    This function gets all the promotions tags for a given store in a given chain.
    It includes both the full and not full promotions files.

    :param chain: A given supermarket chain
    :param store_id: A given store ID
    :param load_xml: A boolean representing whether to try loading the promotions from an existing XML file
    :return: A list of promotions tags
    """
    bs_objects = list()
    for category in tqdm(XML_FILES_PROMOTIONS_CATEGORIES, desc='promotions_files'):
        xml_path = xml_file_gen(chain, store_id, category.name)
        bs_objects.append(create_bs_object(chain, store_id, category, load_xml, xml_path))

    return [promo for bs_obj in bs_objects for promo in bs_obj.find_all(chain.promotion_tag_name)]
