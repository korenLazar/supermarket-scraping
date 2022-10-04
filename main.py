import json
import logging
import os
import subprocess
import sys
from argparse import ArgumentParser
from datetime import datetime, date
from pathlib import Path

from chains.bareket import Bareket
from chains.co_op import CoOp
from chains.dor_alon import DorAlon
from chains.freshmarket import Freshmarket
from chains.hazi_hinam import HaziHinam
from chains.keshet import Keshet
from chains.king_store import KingStore
from chains.maayan2000 import Maayan2000
from chains.mahsaneiHashook import MahsaneiHashook
from chains.osher_ad import OsherAd
from chains.rami_levi import RamiLevi
from chains.shefa_birkat_hashem import ShefaBirkatHashem
from chains.shufersal import Shufersal
from chains.shuk_hayir import ShukHayir
from chains.stop_market import StopMarket
from chains.tiv_taam import TivTaam
from chains.victory import Victory
from chains.yeinot_bitan import YeinotBitan
from chains.yohananof import Yohananof
from chains.zol_vebegadol import ZolVebegadol
from promotion import main_latest_promos, log_promos_by_name, get_all_prices
from store_utils import log_stores_ids
from supermarket_chain import SupermarketChain
from utils import (
    RESULTS_DIRNAME,
    RAW_FILES_DIRNAME,
    VALID_PROMOTION_FILE_EXTENSIONS,
    log_products_prices,
    valid_promotion_output_file,
    is_valid_promotion_output_file,
)

CHAINS_LIST = [
    Bareket,
    MahsaneiHashook,
    DorAlon,
    Freshmarket,
    HaziHinam,
    Keshet,
    StopMarket,
    TivTaam,
    Shufersal,
    CoOp,
    Victory,
    Yohananof,
    ZolVebegadol,
    RamiLevi,
    OsherAd,
    Maayan2000,
    ShukHayir,
    KingStore,
    ShefaBirkatHashem,
    YeinotBitan,
]
Path(RESULTS_DIRNAME).mkdir(exist_ok=True)
Path(RAW_FILES_DIRNAME).mkdir(exist_ok=True)

CHAINS_DICT = {
    repr(chain): chain() if callable(chain) else None for chain in CHAINS_LIST
}

# TODO: change functions arguments to include all necessary parameters (e.g. chain) or split arguments
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--promos",
        help="generates a CSV file with all the promotions in the requested store",
        metavar="store_id",
        nargs=1,
        type=SupermarketChain.store_id_type,
    )
    parser.add_argument(
        "--find_promos_by_name",
        help="prints all promos containing the given promo_name in the given store",
        metavar=("store_id", "promo_name"),
        nargs=2,
    )
    parser.add_argument(
        "--price",
        help="prints all products that contain the given name in the requested store",
        metavar=("store_id", "product_name"),
        nargs=2,
    )
    parser.add_argument(
        "--prices-with-promos",
        help="logs all products with prices updated by promos",
        metavar="store_id",
        nargs=1,
        type=SupermarketChain.store_id_type,
    )
    parser.add_argument(
        "--find_store_id",
        help="prints all Shufersal stores in a given city. Input should be a city name in Hebrew",
        metavar="city",
        nargs=1,
    )
    parser.add_argument(
        "--load_prices",
        help="boolean flag representing whether to load an existing price XML file",
        action="store_true",
    )
    parser.add_argument(
        "--load_promos",
        help="boolean flag representing whether to load an existing promo XML file",
        action="store_true",
    )
    parser.add_argument(
        "--load_stores",
        help="boolean flag representing whether to load an existing stores XML file",
        action="store_true",
    )
    parser.add_argument(
        "--chain",
        required=True,
        help="The name of the requested chain",
        choices=CHAINS_DICT.keys(),
    )
    parser.add_argument(
        "--output_filename",
        help="The path to write the promotions/prices to",
        type=valid_promotion_output_file,
    )
    parser.add_argument(
        "--only_export_to_file",
        help="Boolean flag representing whether only export or also open the promotion output file",
        action="store_true",
    )
    parser.add_argument(
        "--debug",
        help="Boolean flag representing whether to run in debug mode",
        action="store_true",
    )
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

    chain: SupermarketChain = CHAINS_DICT[args.chain]

    if args.promos or args.prices_with_promos:
        arg_store_id = (
            int(args.promos[0]) if args.promos else int(args.prices_with_promos[0])
        )

        if args.output_filename:
            output_filename = args.output_filename
            if args.promos and not is_valid_promotion_output_file(output_filename):
                raise ValueError(
                    f"Output filename for promos must end with: {VALID_PROMOTION_FILE_EXTENSIONS}"
                )
            if args.prices_with_promos and not output_filename.endswith(".json"):
                raise ValueError(f"Output filename for promos must be a json file")
            directory = os.path.dirname(output_filename)
            Path(directory).mkdir(parents=True, exist_ok=True)
        else:
            Path(RESULTS_DIRNAME).mkdir(exist_ok=True)
            file_extension = ".xlsx" if args.promos else ".json"
            file_type = "promos" if args.promos else "prices"
            output_filename = f"{RESULTS_DIRNAME}/{repr(type(chain))}-{file_type}-{arg_store_id}-{date.today()}{file_extension}"

        if args.promos:
            main_latest_promos(
                store_id=arg_store_id,
                output_filename=output_filename,
                chain=chain,
                load_promos=args.load_promos,
                load_prices=args.load_prices,
            )
        else:
            items_dict = get_all_prices(
                store_id=arg_store_id,
                output_filename=output_filename,
                chain=chain,
                load_promos=args.load_promos,
                load_prices=args.load_prices,
            )
            items_dict_to_json = {
                item_code: {
                    k: v
                    for k, v in item.__dict__.items()
                    if not k.startswith("__") and not callable(k)
                }
                for item_code, item in items_dict.items()
            }

            with open(output_filename, "w") as fOut:
                json.dump(items_dict_to_json, fOut)

        if not args.only_export_to_file:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, Path(output_filename)])
            # os.startfile(Path(output_filename))
        logging.debug(f"Process finished at: {datetime.now()}")

    elif args.price:
        log_products_prices(
            chain,
            store_id=args.price[0],
            load_xml=args.load_prices,
            product_name=args.price[1],
        )

    elif args.find_store_id:
        arg_city = args.find_store_id[0]
        log_stores_ids(city=arg_city, load_xml=args.load_stores, chain=chain)

    elif args.find_promos_by_name:
        arg_store_id = int(args.find_promos_by_name[0])
        log_promos_by_name(
            store_id=arg_store_id,
            chain=chain,
            promo_name=args.find_promos_by_name[1],
            load_prices=args.load_prices,
            load_promos=args.load_promos,
        )
