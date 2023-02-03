import logging
import re

from bs4 import BeautifulSoup

from src.utils import xml_file_gen, create_bs_object
from src.supermarket_chain import SupermarketChain
from il_supermarket_scarper.main import FileTypesFilters

def log_stores_ids(city: str, load_xml: bool, chain: SupermarketChain):
    """
    This function prints the stores IDs of stores in a given city.
    The city must match its spelling in Shufersal's website (hence it should be in Hebrew).

    :param chain: A given supermarket chain
    :param load_xml: A boolean representing whether to load an existing xml or load an already saved one
    :param city: A string representing the city of the requested store.
    """
    xml_path: str = xml_file_gen(chain, -1, FileTypesFilters.STORE_FILE.name)
    bs_stores: BeautifulSoup = create_bs_object(chain, -1, FileTypesFilters.STORE_FILE, load_xml, xml_path)

    for store in bs_stores.find_all(lambda tag: tag.name.lower() == "store"):
        if store.find(re.compile(f"^city$", re.I), attrs={'text': city}) or store.find(re.compile(f"^storename$", re.I), attrs={'name': lambda x: x and city in x.lower()}):
        # if store.find(lambda tag: tag.name.lower() == "city", name=city) or city in store.find(lambda tag: city in tag.name.lower()):
        # if store.find("CITY").text == city or city in store.find("Store").text:
            logging.info((store.find("ADDRESS").text, store.find("STOREID").text, store.find("SUBCHAINNAME").text))
