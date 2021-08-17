import logging
import os
import pytest
import requests
from tqdm import tqdm
import pandas as pd
import re

from chains.bareket import Bareket
from chains.co_op import CoOp
from chains.dor_alon import DorAlon
from chains.keshet import Keshet
from chains.shuk_hayir import ShukHayir
from chains.stop_market import StopMarket
from chains.tiv_taam import TivTaam
from chains.zol_vebegadol import ZolVebegadol
from promotion import PROMOTION_COLS_NUM, main_latest_promos
from supermarket_chain import SupermarketChain
from chains import (
    bareket,
    mahsaneiHashook,
    dor_alon,
    freshmarket,
    hazi_hinam,
    keshet,
    stop_market,
    tiv_taam,
    shufersal,
    co_op,
    victory,
    yohananof,
    zol_vebegadol,
    rami_levi,
    osher_ad,
    maayan2000,
    shuk_hayir,
    king_store,
    shefa_birkat_hashem,
)

pytest.main(args=['-s', os.path.abspath(__file__)])

chain_dict = {repr(chain): chain() if callable(chain) else None for chain in SupermarketChain.__subclasses__()}

MIN_NUM_OF_PROMOS = 3


def test_searching_for_download_urls():
    """
    Test that get_download_url of each chain returns the correct download url for each category:
    """
    session = requests.Session()
    for chain_name, chain in tqdm(chain_dict.items(), desc='chains'):

        logging.info(f'Finding download url in chain {chain_name}')
        store_id: int = valid_store_id_by_chain(chain_name)

        _test_download_url_helper(chain, store_id, chain.XMLFilesCategory.PromosFull, r'promo[s]?full', session)
        _test_download_url_helper(chain, store_id, chain.XMLFilesCategory.Promos, r'promo[s]?', session)
        _test_download_url_helper(chain, store_id, chain.XMLFilesCategory.PricesFull, r'price[s]?full', session)
        _test_download_url_helper(chain, store_id, chain.XMLFilesCategory.Prices, r'price[s]?', session)


def _test_download_url_helper(chain: SupermarketChain, store_id: int, category: SupermarketChain.XMLFilesCategory,
                              regex_pat: str, session: requests.session):
    download_url: str = chain.get_download_url(store_id, category, session)
    logging.debug(download_url)
    if not download_url:  # Not found non-full Promos/Prices file
        return
    assert re.search(regex_pat, download_url, re.IGNORECASE), f'Invalid {category.name} url in {repr(type(chain))}'
    if category in [chain.XMLFilesCategory.Prices, chain.XMLFilesCategory.Promos]:
        assert not re.search('full', download_url, re.IGNORECASE), \
            f'Downloaded the full {category.name} file mistakenly in {repr(type(chain))}'


def test_promotions_scraping():
    """
    Test scraping of promotions is completed successfully and a valid xlsx file is generated as an output.
    """
    filename = 'temp.xlsx'
    for chain_name, chain in tqdm(chain_dict.items(), desc='chains'):
        logging.info(f'Test scraping promotions from {chain_name}')

        store_id: int = valid_store_id_by_chain(chain_name)
        try:
            main_latest_promos(
                store_id=store_id,
                output_filename=filename,
                chain=chain,
                load_promos=False,
                load_xml=False,
            )
            df = pd.read_excel(filename)
        except Exception as e:
            logging.error(e)
            logging.error(f"Failed loading excel of {chain_name}")
            raise

        assert df.shape[0] > MIN_NUM_OF_PROMOS and df.shape[1] == PROMOTION_COLS_NUM, f"Failed scraping {chain_name}"


def valid_store_id_by_chain(chain_name) -> int:
    """
    This function returns a valid store ID for a given chain.

    :param chain_name: The name of a chain as returned by repr(ChainClassName).
    :return: An integer representing a valid store ID in the given chain
    """
    if chain_name == repr(DorAlon):
        store_id = 501
    elif chain_name in [repr(TivTaam), repr(Bareket), repr(ZolVebegadol)]:
        store_id = 2
    elif chain_name == repr(CoOp):
        store_id = 202
    elif chain_name == repr(ShukHayir):
        store_id = 4
    elif chain_name in [repr(StopMarket), repr(Keshet)]:
        store_id = 5
    else:
        store_id = 1
    return store_id
