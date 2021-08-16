import logging
from bs4 import BeautifulSoup

from utils import xml_file_gen, create_bs_object
from supermarket_chain import SupermarketChain


def log_stores_ids(city: str, load_xml: bool, chain: SupermarketChain):
    """
    This function prints the stores IDs of stores in a given city.
    The city must match its spelling in Shufersal's website (hence it should be in Hebrew).

    :param chain: A given supermarket chain
    :param load_xml: A boolean representing whether to load an existing xml or load an already saved one
    :param city: A string representing the city of the requested store.
    """
    xml_path: str = xml_file_gen(chain, -1, chain.XMLFilesCategory.Stores.name)
    bs_stores: BeautifulSoup = create_bs_object(chain, -1, chain.XMLFilesCategory.Stores, load_xml, xml_path)

    for store in bs_stores.find_all("STORE"):
        if store.find("CITY").text == city:
            logging.info((store.find("ADDRESS").text, store.find("STOREID").text, store.find("SUBCHAINNAME").text))
