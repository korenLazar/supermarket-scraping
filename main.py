from typing import List, Dict
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import gzip
from enum import Enum
from argparse import ArgumentParser, ArgumentTypeError
import logging
import time

PRODUCTS_TO_IGNORE = ['סירים', 'מגבות', 'צלחות', 'כוסות', 'מאגים', 'מגבת', 'מפות']

STORE_ID_NOT_FOUND = -1


class ShufersalCategories(Enum):
    All, Prices, PricesFull, Promos, PromosFull, Stores = range(6)


def xml_file_gen(category_name: str, store_id: int) -> str:
    """
    This function generate an xml filename given a store id and a category_name
    If the given store_id is invalid, it is ignored in the returned string.

    :param store_id: A given store_id
    :param category_name: A given category name
    :return: An xml filename
    """
    store_id_str = f"-{str(store_id)}" if is_valid_store_id(store_id) else ""
    return f"{category_name}{store_id_str}.xml"


class Promotion:
    """
    A class of a promotion in Shufersal.
    It contains only part of the available information in Shufersal's data.
    """

    def __init__(self, content: str, end_date: datetime, update_date: datetime, code_items: List[str]):
        self.content: str = content
        self.end_date: datetime = end_date
        self.update_date: datetime = update_date
        self.code_items: List[str] = code_items

    def __str__(self):
        items = '\n'.join(str(item) for item in self.code_items)
        return f"*** {self.content} until {self.end_date.date()} ***\n{items}\n"


def get_download_url(store_id: int, cat_id: int) -> str:
    """
    This function scrapes Shufersal's website and returns a url that contains the data for a given store and category.
    For info about the categories, see ShufersalCategories.

    :param store_id: A given id of a store
    :param cat_id: A given id of a category
    :return: A downloadable link of the  data for a given store and category
    """
    url = f"http://prices.shufersal.co.il/FileObject/UpdateCategory?catID={cat_id}"
    if is_valid_store_id(store_id):
        url += f"&storeId={store_id}"
    req_res = requests.get(url)
    soup = BeautifulSoup(req_res.text, features='lxml')
    return soup.find('a', text="לחץ להורדה")['href']


def create_bs_object(xml_path, download_url: str) -> BeautifulSoup:
    """
    This function creates a BeautifulSoup object according to the given xml_path and download_url.
    In case the given download_url is an empty string, the function tries to read from the given xml_path,
    otherwise it downloads the gzip from the download link and extract it.

    :param xml_path: A given path to an xml file
    :param download_url: A string that may represent a link (described above)
    :return: A BeautifulSoup object with xml content (either from a file or a link).
    """
    if download_url:
        xml_content = gzip.decompress(requests.get(download_url).content)
        with open(xml_path, 'wb') as f_out:
            f_out.write(xml_content)
        return BeautifulSoup(xml_content, features='xml')
    else:
        with open(xml_path, 'rb') as f_in:
            return BeautifulSoup(f_in, features='xml')


def get_available_promos(store_id: int, load_xml: bool) -> List[Promotion]:
    """
    This function return the available promotions given a BeautifulSoup object.

    :param store_id: A given store id
    :param load_xml: A boolean representing whether to load an existing xml or load an already saved one
    :return: Promotions that are not included in PRODUCTS_TO_IGNORE and are currently available
    """
    start = time.time()
    items_dict = create_items_dict(store_id, load_xml)

    down_url = get_download_url(store_id, ShufersalCategories.PromosFull.value)
    bs_promos = create_bs_object(xml_file_gen(ShufersalCategories.PromosFull.name, store_id), down_url)

    promo_objs = list()
    for cur_promo in bs_promos.find_all("Promotion"):
        cur_promo = Promotion(
            content=cur_promo.find('PromotionDescription').text,
            end_date=datetime.strptime(cur_promo.find('PromotionEndDate').text, '%Y-%m-%d'),
            update_date=datetime.strptime(cur_promo.find('PromotionUpdateDate').text, '%Y-%m-%d %H:%M'),
            code_items=[items_dict.get(item.find('ItemCode').text) for item in cur_promo.find_all('Item')
                        if items_dict.get(item.find('ItemCode').text)],
        )
        if is_valid_promo(cur_promo):
            promo_objs.append(cur_promo)
    print(f"Finished getting available promos in {time.time() - start}")
    return promo_objs


def is_valid_promo(promo: Promotion):
    not_expired = promo.end_date > datetime.now()
    has_products = len(promo.code_items) > 0
    return not_expired and has_products and not any(product in promo.content for product in PRODUCTS_TO_IGNORE)


def create_items_dict(store_id: int, load_xml) -> Dict:
    """
    This function creates a dictionary where every key is an item code and its value is the item's name and price.

    :param load_xml: A boolean representing whether to load an existing prices xml file
    :param store_id: A given store id
    :return: A dictionary where the firs
    """
    down_url = "" if load_xml else get_download_url(store_id, ShufersalCategories.PricesFull.value)
    xml_path = xml_file_gen(ShufersalCategories.PricesFull.name, store_id)
    bs_prices = create_bs_object(xml_path, down_url)
    return {item.find('ItemCode').text: get_item_info(item) for item in bs_prices.find_all('Item')}


def get_item_info(item):
    return str((item.find('ItemName').text, item.find('ManufacturerName').text, item.find('ItemPrice').text))


def main_latest_promos(store_id: int, load_xml: bool):
    """
    This function logs the available promos in a Shufersal store with a given id sorted by their update date.

    :param store_id: A given store id
    :param load_xml: A boolean representing whether to load an existing prices xml file
    """

    promotions = get_available_promos(store_id, load_xml)
    promotions.sort(key=lambda promo: promo.update_date, reverse=True)
    logger.info('\n'.join(str(promotion) for promotion in promotions))


def get_store_id(city: str, load_xml: bool):
    """
    This function returns the id of a Shufersal store according to a given city.
    The city must match exactly to its spelling in Shufersal's website.

    :param load_xml: A boolean representing whether to load an existing xml or load an already saved one
    :param city: A string representing the city of the requested store.
    """
    down_url = "" if load_xml else get_download_url(-1, ShufersalCategories.Stores.value)
    bs = create_bs_object(xml_file_gen(ShufersalCategories.Stores.name, -1), down_url)

    for store in bs.find_all("STORE"):
        if store.find("CITY").text == city:
            logger.info((store.find("ADDRESS").text, store.find("STOREID").text, store.find("SUBCHAINNAME").text))


def get_products_prices(store_id: int, product_name: str, load_xml: bool):
    """
    This function logs the products in a given Shufersal store which contains a given product_name.

    :param store_id: A given Shufersal store id
    :param product_name: A given product name
    :param load_xml: A boolean representing whether to load an existing xml or load an already saved one
    """
    down_url = "" if load_xml else get_download_url(store_id, ShufersalCategories.PricesFull.value)
    bs = create_bs_object(xml_file_gen(ShufersalCategories.PricesFull.name, store_id), down_url)
    prods = [item for item in bs.find_all("Item") if product_name in item.find("ItemName").text]
    prods.sort(key=lambda x: float(x.find("UnitOfMeasurePrice").text))
    for prod in prods:
        logger.info(get_item_info(prod))


def is_valid_store_id(store_id: int):
    return isinstance(store_id, int) and store_id >= 0


def store_id_type(store_id: str):
    if not is_valid_store_id(int(store_id)):
        raise ArgumentTypeError(f"Given store_id: {store_id} is not a valid store_id.")
    return store_id


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--promos',
                        help="Param for getting the store's promotions",
                        metavar='store_id',
                        nargs='?',
                        type=store_id_type,
                        const=5,
                        )
    parser.add_argument('--price',
                        help='Params for calling get_products_prices',
                        metavar=('store_id', 'product_name'),
                        nargs=2,
                        )
    parser.add_argument('--find_store',
                        help='Params for calling get_store_id',
                        metavar='city',
                        nargs=1,
                        )
    parser.add_argument('--load_xml',
                        help='Whether to load an existing xml',
                        action='store_true',
                        )
    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if args.promos:
        arg_store_id = int(args.promos)
        handler = logging.FileHandler(filename=f'promos_{arg_store_id}.log', mode='w', encoding='utf-8')
        logger.addHandler(handler)
        try:
            main_latest_promos(store_id=arg_store_id, load_xml=args.load_xml)
        except FileNotFoundError:
            main_latest_promos(store_id=arg_store_id, load_xml=False)

    elif args.price:
        handler = logging.FileHandler(filename='products_prices.log', mode='w', encoding='utf-8')
        logger.addHandler(handler)
        try:
            get_products_prices(store_id=args.price[0], product_name=args.price[1], load_xml=args.load_xml)
        except FileNotFoundError:
            get_products_prices(store_id=args.price[0], product_name=args.price[1], load_xml=False)

    elif args.find_store:
        arg_city = args.find_store[0]
        handler = logging.FileHandler(filename=f'stores_{arg_city}.log', mode='w', encoding='utf-8')
        logger.addHandler(handler)
        try:
            get_store_id(city=arg_city, load_xml=args.load_xml)
        except FileNotFoundError:
            get_store_id(city=arg_city, load_xml=False)
