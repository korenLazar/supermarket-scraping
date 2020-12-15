import gzip
from enum import Enum
from typing import Dict
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from os import path

XMLS_DIRNAME = "xmls"
Path(XMLS_DIRNAME).mkdir(exist_ok=True)


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
    return path.join(XMLS_DIRNAME, f"{category_name}{store_id_str}.xml")


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


def create_bs_object(xml_path: str, cat_id: int, store_id: int, load_xml: bool) -> BeautifulSoup:
    """
    This function creates a BeautifulSoup (BS) object according to the given parameters.
    In case the given load_xml is True and the XML file exists, the function creates the BS object from the given
    xml_path, otherwise it uses Shufersal's APIs to download the xml with the relevant content and saves it for
    future use.

    :param xml_path: A given path to an xml file to load/save the BS object from/to.
    :param cat_id: A given id of a category from ShufersalCategories
    :param store_id: A given id of a store
    :param load_xml: A flag representing whether to try loading an existing XML file
    :return: A BeautifulSoup object with xml content.
    """
    if load_xml and path.isfile(xml_path):
        return create_bs_object_from_xml(xml_path)
    return create_bs_object_from_link(xml_path, store_id, cat_id)


def create_bs_object_from_link(xml_path: str, store_id: int, cat_id: int) -> BeautifulSoup:
    """
    This function creates a BeautifulSoup (BS) object by generating a download link from Shufersal's API.

    :param xml_path: A given path to an xml file to load/save the BS object from/to.
    :param store_id: A given id of a store
    :param cat_id: A given id of a category from ShufersalCategories
    :return: A BeautifulSoup object with xml content.
    """
    download_url = get_download_url(store_id, cat_id)
    xml_content = gzip.decompress(requests.get(download_url).content)
    with open(xml_path, 'wb') as f_out:
        f_out.write(xml_content)
    return BeautifulSoup(xml_content, features='xml')


def create_bs_object_from_xml(xml_path: str) -> BeautifulSoup:
    """
    This function creates a BeautifulSoup (BS) object from a given xml file.

    :param xml_path: A given path to an xml file to load/save the BS object from/to.
    :return: A BeautifulSoup object with xml content.
    """
    with open(xml_path, 'rb') as f_in:
        return BeautifulSoup(f_in, features='xml')


def create_items_dict(store_id: int, load_xml) -> Dict:
    """
    This function creates a dictionary where every key is an item code and its value is the item's name and price.

    :param load_xml: A boolean representing whether to load an existing prices xml file
    :param store_id: A given store id
    :return: A dictionary where the firs
    """
    xml_path = xml_file_gen(ShufersalCategories.PricesFull.name, store_id)
    bs_prices = create_bs_object(xml_path, ShufersalCategories.PricesFull.value, store_id, load_xml)
    return {item.find('ItemCode').text: get_item_info(item) for item in bs_prices.find_all('Item')}


def get_item_info(item):
    return str((item.find('ItemName').text, item.find('ManufacturerName').text, item.find('ItemPrice').text))


def get_products_prices(store_id: int, product_name: str, load_xml: bool):
    """
    This function prints the products in a given Shufersal store which contains a given product_name.

    :param store_id: A given Shufersal store id
    :param product_name: A given product name
    :param load_xml: A boolean representing whether to load an existing xml or load an already saved one
    """
    xml_path = xml_file_gen(ShufersalCategories.PricesFull.name, store_id)
    bs_prices = create_bs_object(xml_path, ShufersalCategories.PricesFull.value, store_id, load_xml)
    prods = [item for item in bs_prices.find_all("Item") if product_name in item.find("ItemName").text]
    prods.sort(key=lambda x: float(x.find("UnitOfMeasurePrice").text))
    for prod in prods:
        print((prod.find('ItemName').text[::-1], prod.find('ManufacturerName').text[::-1],
               prod.find('ItemPrice').text))


def is_valid_store_id(store_id: int):
    return isinstance(store_id, int) and store_id >= 0
