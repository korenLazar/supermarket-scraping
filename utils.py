import gzip
import io
import zipfile
from typing import AnyStr, Dict, List
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from os import path
from supermarket_chain import SupermarketChain
import re

LOGS_DIRNAME = "logs"
XMLS_DIRNAME = "xmls"


def xml_file_gen(chain: SupermarketChain, store_id: int, category_name: str) -> str:
    """
    This function generate an XML filename given a store id and a category_name
    If the given store_id is invalid, it is ignored in the returned string.

    :param chain: A given supermarket chain
    :param store_id: A given store_id
    :param category_name: A given category name
    :return: An xml filename
    """
    store_id_str: str = f"-{str(store_id)}" if SupermarketChain.is_valid_store_id(store_id) else ""
    return path.join(XMLS_DIRNAME, f"{chain}-{category_name}{store_id_str}.xml")


def create_bs_object(xml_path: str, chain: SupermarketChain, store_id: int, load_xml: bool,
                     category: SupermarketChain.XMLFilesCategory) -> BeautifulSoup:
    """
    This function creates a BeautifulSoup (BS) object according to the given parameters.
    In case the given load_xml is True and the XML file exists, the function creates the BS object from the given
    xml_path, otherwise it uses Shufersal's APIs to download the xml with the relevant content and saves it for
    future use.

    :param chain: A given supermarket chain
    :param xml_path: A given path to an xml file to load/save the BS object from/to.
    :param category: A given category
    :param store_id: A given id of a store
    :param load_xml: A flag representing whether to try loading an existing XML file
    :return: A BeautifulSoup object with xml content.
    """
    if load_xml and path.isfile(xml_path):
        return create_bs_object_from_xml(xml_path)
    return create_bs_object_from_link(xml_path, chain, category, store_id)


def create_bs_object_from_link(xml_path: str, chain: SupermarketChain, category: SupermarketChain.XMLFilesCategory,
                               store_id: int) -> BeautifulSoup:
    """
    This function creates a BeautifulSoup (BS) object by generating a download link from Shufersal's API.

    :param chain: A given supermarket chain
    :param xml_path: A given path to an XML file to load/save the BS object from/to.
    :param store_id: A given id of a store
    :param category: A given category
    :return: A BeautifulSoup object with xml content.
    """
    download_url: str = chain.get_download_url(store_id, category)
    response_content = requests.get(download_url).content
    try:
        xml_content: AnyStr = gzip.decompress(response_content)
    except gzip.BadGzipFile:
        with zipfile.ZipFile(io.BytesIO(response_content)) as the_zip:
            zip_info = the_zip.infolist()[0]
            with the_zip.open(zip_info) as the_file:
                xml_content = the_file.read()
    with open(xml_path, 'wb') as f_out:
        f_out.write(xml_content)
    return BeautifulSoup(xml_content, features='xml')


def create_bs_object_from_xml(xml_path: str) -> BeautifulSoup:
    """
    This function creates a BeautifulSoup (BS) object from a given XML file.

    :param xml_path: A given path to an xml file to load/save the BS object from/to.
    :return: A BeautifulSoup object with xml content.
    """
    with open(xml_path, 'rb') as f_in:
        return BeautifulSoup(f_in, features='xml')


def create_items_dict(chain: SupermarketChain, load_xml, store_id: int) -> Dict[str, str]:
    """
    This function creates a dictionary where every key is an item code and its value is the item's name and price.

    :param chain: A given supermarket chain
    :param load_xml: A boolean representing whether to load an existing prices xml file
    :param store_id: A given store id
    :return: A dictionary where the firs
    """
    xml_path: str = xml_file_gen(chain, store_id, chain.XMLFilesCategory.PricesFull.name)
    bs_prices: BeautifulSoup = create_bs_object(xml_path, chain, store_id, load_xml, chain.XMLFilesCategory.PricesFull)
    return {item.find('ItemCode').text: get_item_info(item) for item in bs_prices.find_all(chain.item_tag_name)}


def get_item_info(item: Tag) -> List[str]:
    """
    This function returns a string containing important information about a given supermarket's product.
    """
    return [item.find(re.compile(r'ItemN[a]?m[e]?')).text, item.find(re.compile(r'Manufacture[r]?Name')).text,
            item.find('ItemPrice').text, item.find('ItemCode').text]


def get_products_prices(chain: SupermarketChain, store_id: int, load_xml: bool, product_name: str) -> None:
    """
    This function prints the products in a given store which contains a given product_name.

    :param chain: A given supermarket chain
    :param store_id: A given store id
    :param product_name: A given product name
    :param load_xml: A boolean representing whether to load an existing xml or load an already saved one
    """
    xml_path: str = xml_file_gen(chain, store_id, chain.XMLFilesCategory.PricesFull.name)
    bs_prices: BeautifulSoup = create_bs_object(xml_path, chain, store_id, load_xml, chain.XMLFilesCategory.PricesFull)
    prods = [item for item in bs_prices.find_all("Item") if product_name in item.find("ItemName").text]
    prods.sort(key=lambda x: float(x.find("UnitOfMeasurePrice").text))
    for prod in prods:
        print((prod.find('ItemName').text[::-1], prod.find('ManufacturerName').text[::-1],
               prod.find('ItemPrice').text))
