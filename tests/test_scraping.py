import logging
import os

import pytest
from tqdm import tqdm
import pandas as pd

from chains.bareket import Bareket
from chains.co_op import CoOp
from chains.dor_alon import DorAlon
from chains.freshmarket import Freshmarket
from chains.hazi_hinam import HaziHinam
from chains.keshet import Keshet
from chains.maayan2000 import Maayan2000
from chains.mahsaneiHashook import MahsaneiHashook
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


def test_scraping():
    filename = 'temp.xlsx'
    for chain_name, chain in tqdm(chain_dict.items(), desc='chains'):
        if chain_name in [repr(Maayan2000), repr(ZolVebegadol), repr(ShukHayir)]:
            continue
        logging.info(f'Test scraping promotions from {chain_name}')
        if chain_name == repr(DorAlon):
            store_id = 501
        elif chain_name in [repr(Keshet), repr(TivTaam), repr(Bareket), repr(ZolVebegadol)]:
            store_id = 2
        elif chain_name == repr(CoOp):
            store_id = 202
        elif chain_name == repr(ShukHayir):
            store_id = 4
        elif chain_name == repr(StopMarket):
            store_id = 5
        else:
            store_id = 1

        try:
            main_latest_promos(
                store_id=store_id,
                output_filename=filename,
                chain=chain,
                load_promos=False,
                load_xml=False
            )
            df = pd.read_excel(filename)
        except Exception as e:
            logging.error(e)
            logging.info(f"Failed loading excel of {chain_name}")
            raise

        assert df.shape[0] > MIN_NUM_OF_PROMOS and df.shape[1] == PROMOTION_COLS_NUM, f"Failed scraping {chain_name}"
