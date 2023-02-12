import logging
import os
import re
import tempfile

import pandas as pd
import pytest
import requests
from il_supermarket_scarper.main import FileTypesFilters
from src.chains.bareket import Bareket
from src.chains.dor_alon import DorAlon
from src.chains.hazi_hinam import HaziHinam
from src.chains.keshet import Keshet
from src.chains.shuk_hayir import ShukHayir
from src.chains.stop_market import StopMarket
from src.chains.tiv_taam import TivTaam
from src.chains.yeinot_bitan import YeinotBitan
from src.chains.zol_vebegadol import ZolVebegadol
from src.main import CHAINS_DICT
from src.promotion import main_latest_promos, PROMOTIONS_TABLE_HEADERS
from src.supermarket_chain import SupermarketChain

pytest.main(args=["-s", os.path.abspath(__file__)])

MIN_NUM_OF_PROMOS = 3


@pytest.mark.parametrize("chain_name", CHAINS_DICT.keys())
def test_searching_for_download_urls(chain_name):
    """
    Test that get_download_url of each chain returns the correct download url for each category in every chain.
    """
    chain = CHAINS_DICT[chain_name]

    logging.info(f"Checking download urls in chain {chain_name}")
    store_id: int = valid_store_id_by_chain(chain_name)

    _test_download_url_helper(
        chain, store_id, FileTypesFilters.PROMO_FULL_FILE, r"promo[s]?full"
    )
    _test_download_url_helper(
        chain, store_id, FileTypesFilters.PROMO_FILE, r"promo[s]?"
    )
    _test_download_url_helper(
        chain, store_id, FileTypesFilters.PRICE_FULL_FILE, r"price[s]?full"
    )
    _test_download_url_helper(
        chain, store_id, FileTypesFilters.PRICE_FILE, r"price[s]?"
    )


def _test_download_url_helper(
    chain: SupermarketChain,
    store_id: int,
    category: FileTypesFilters,
    regex_pat: str,
):
    import uuid
    dump_folder = ".dump_"+str(uuid.uuid4())
    base_folder, download_urls = chain.get_download_url_or_path(store_id, category, dump_folder)
    if not download_urls:  # Not found non-full Promos/Prices file
        return
    download_url = os.path.join(base_folder,download_urls[0])
    logging.debug(download_url)
    assert re.search(
        regex_pat, download_url, re.IGNORECASE
    ), f"Invalid {category.name} url in {repr(type(chain))}"
    if category in [FileTypesFilters.PRICE_FILE, FileTypesFilters.PROMO_FILE]:
        assert not re.search(
            "full", download_url, re.IGNORECASE
        ), f"Downloaded the full {category.name} file mistakenly in {repr(type(chain))}"


@pytest.mark.parametrize("chain_name", CHAINS_DICT.keys())
def test_promotions_scraping(chain_name):
    """
    Test scraping of promotions is completed successfully and a valid xlsx file is generated as an output.
    """
    chain = CHAINS_DICT[chain_name]
    tf = tempfile.NamedTemporaryFile(suffix=".xlsx")

    logging.info(f"Test scraping promotions from {chain_name}")

    store_id: int = valid_store_id_by_chain(chain_name)
    try:
        main_latest_promos(
            store_id=store_id,
            output_filename=tf.name,
            chain=chain,
            load_promos=False,
            load_prices=False,
            include_non_full_files=True,
        )
        df = pd.read_excel(tf.name)
    except Exception as e:
        logging.error(e)
        logging.error(f"Failed loading excel of {chain_name}")
        raise

    assert df.shape[0] > MIN_NUM_OF_PROMOS and df.shape[1] == len(
        PROMOTIONS_TABLE_HEADERS
    ), f"Failed scraping {chain_name}"


def valid_store_id_by_chain(chain_name) -> int:
    """
    This function returns a valid store ID for a given chain.

    :param chain_name: The name of a chain as returned by repr(ChainClassName).
    :return: An integer representing a valid store ID in the given chain
    """
    if chain_name == repr(DorAlon):
        store_id = 501
    elif chain_name == repr(Bareket):
        return 6
    elif chain_name in [repr(TivTaam), repr(HaziHinam)]:
        store_id = 2
    elif chain_name in [repr(ShukHayir), repr(ZolVebegadol)]:
        store_id = 4
    elif chain_name in [repr(StopMarket), repr(Keshet)]:
        store_id = 5
    elif chain_name == repr(YeinotBitan):
        store_id = 3700
    else:
        store_id = 1
    return store_id
