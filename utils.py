import gzip
import io
import logging
import os.path
import zipfile
from argparse import ArgumentTypeError
from datetime import date
from datetime import datetime
from os import path
from typing import AnyStr, Dict

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from item import Item
from supermarket_chain import SupermarketChain

RESULTS_DIRNAME = "results"
RAW_FILES_DIRNAME = "raw_files"
VALID_PROMOTION_FILE_EXTENSIONS = [".csv", ".xlsx"]


def xml_file_gen(chain: SupermarketChain, store_id: int, category_name: str) -> str:
    """
    This function generate an XML filename given a store id and a category_name
    If the given store_id is invalid, it is ignored in the returned string.

    :param chain: A given supermarket chain
    :param store_id: A given store_id
    :param category_name: A given category name
    :return: An xml filename
    """
    store_id_str: str = (
        f"-{str(store_id)}" if SupermarketChain.is_valid_store_id(store_id) else ""
    )
    return path.join(
        RAW_FILES_DIRNAME,
        f"{repr(type(chain))}-{category_name}{store_id_str}-{date.today()}.xml",
    )


def create_bs_object(
    chain: SupermarketChain,
    store_id: int,
    category: SupermarketChain.XMLFilesCategory,
    load_xml: bool,
    xml_path: str,
) -> BeautifulSoup:
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
        return get_bs_object_from_xml(xml_path)
    return get_bs_object_from_link(chain, store_id, category, xml_path)


def get_bs_object_from_link(
    chain: SupermarketChain,
    store_id: int,
    category: SupermarketChain.XMLFilesCategory,
    xml_path: str,
) -> BeautifulSoup:
    """
    This function creates a BeautifulSoup (BS) object by generating a download link the given chain's API.

    :param chain: A given supermarket chain
    :param xml_path: A given path to an XML file to load/save the BS object from/to.
    :param store_id: A given id of a store
    :param category: A given category
    :return: A BeautifulSoup object with xml content.
    """
    session = requests.Session()
    download_url_or_path: str = chain.get_download_url_or_path(store_id, category, session)
    if not download_url_or_path:
        return BeautifulSoup()
    if os.path.isfile(download_url_or_path):
        with gzip.open(download_url_or_path) as fIn:
            xml_content = fIn.read()
        os.remove(download_url_or_path)  # Delete gz file
    else:
        response_content = session.get(download_url_or_path).content
        try:
            xml_content: AnyStr = gzip.decompress(response_content)
        except gzip.BadGzipFile:
            with zipfile.ZipFile(io.BytesIO(response_content)) as the_zip:
                zip_info = the_zip.infolist()[0]
                with the_zip.open(zip_info) as the_file:
                    xml_content = the_file.read()
    with open(xml_path, "wb") as f_out:
        f_out.write(xml_content)
    return BeautifulSoup(xml_content, features="xml")


def get_bs_object_from_xml(xml_path: str) -> BeautifulSoup:
    """
    This function creates a BeautifulSoup (BS) object from a given XML file.

    :param xml_path: A given path to an xml file to load/save the BS object from/to.
    :return: A BeautifulSoup object with xml content.
    """
    with open(xml_path, "rb") as f_in:
        return BeautifulSoup(f_in, features="xml")


def create_items_dict(
    chain: SupermarketChain, store_id: int, load_xml
) -> Dict[str, Item]:
    """
    This function creates a dictionary where every key is an item code and its value is its corresponding Item instance.
    We take both full and not full prices files, and assume that the no full is more updated (in case of overwriting).

    :param chain: A given supermarket chain
    :param load_xml: A boolean representing whether to load an existing prices xml file
    :param store_id: A given store id
    """
    items_dict = dict()
    for category in tqdm(
        [chain.XMLFilesCategory.PricesFull, chain.XMLFilesCategory.Prices],
        desc="prices_files",
    ):
        xml_path: str = xml_file_gen(chain, store_id, category.name)
        bs_prices: BeautifulSoup = create_bs_object(
            chain, store_id, category, load_xml, xml_path
        )
        items_tags = bs_prices.find_all(chain.item_tag_name)
        items_dict.update(
            {
                item_tag.find("ItemCode").text: Item.from_tag(item_tag)
                for item_tag in items_tags
            }
        )

    return items_dict


def log_products_prices(
    chain: SupermarketChain, store_id: int, load_xml: bool, product_name: str
) -> None:
    """
    This function prints the products in a given store which contains a given product_name.

    :param chain: A given supermarket chain
    :param store_id: A given store id
    :param product_name: A given product name
    :param load_xml: A boolean representing whether to load an existing xml or load an already saved one
    """
    items_dict: Dict[str, Item] = create_items_dict(chain, store_id, load_xml)
    products_by_name = [
        item for item in items_dict.values() if product_name in item.name
    ]
    products_by_name_sorted_by_price = sorted(
        products_by_name, key=lambda item: item.price_by_measure
    )

    for prod in products_by_name_sorted_by_price:
        logging.info(prod)


def get_float_from_tag(tag, int_tag) -> int:
    content = tag.find(int_tag)
    return float(content.text) if content else 0


def is_valid_promotion_output_file(output_file: str) -> bool:
    return any(
        output_file.endswith(extension) for extension in VALID_PROMOTION_FILE_EXTENSIONS
    )


def valid_promotion_output_file(output_file: str) -> str:
    if not is_valid_promotion_output_file(output_file):
        raise ArgumentTypeError(
            f"Given output file has an invalid extension is invalid: {output_file}"
        )
    return output_file


def log_message_and_time_if_debug(msg: str) -> None:
    logging.info(msg)
    logging.debug(datetime.now())
