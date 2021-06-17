import os
import sys
import time
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
import logging

from promotion import main_latest_promos, log_promos_by_name
from store_utils import log_stores_ids
from utils import RESULTS_DIRNAME, RAW_FILES_DIRNAME, VALID_PROMOTION_FILE_EXTENSIONS, log_products_prices, \
    valid_promotion_output_file
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

# TODO: fix problem of left-to-right printing

Path(RESULTS_DIRNAME).mkdir(exist_ok=True)
Path(RAW_FILES_DIRNAME).mkdir(exist_ok=True)

chain_dict = {repr(chain): chain() if callable(chain) else None for chain in SupermarketChain.__subclasses__()}

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--promos',
                        help="generates a CSV file with all the promotions in the requested store",
                        metavar='store_id',
                        nargs=1,
                        type=SupermarketChain.store_id_type,
                        )
    parser.add_argument('--find_promos_by_name',
                        help="prints all promos containing the given promo_name in the given store",
                        metavar=('store_id', 'promo_name'),
                        nargs=2,
                        # type=store_id_type,  # TODO: add type-checking of first parameter
                        )
    parser.add_argument('--price',
                        help='prints all products that contain the given name in the requested store',
                        metavar=('store_id', 'product_name'),
                        nargs=2,
                        )
    parser.add_argument('--find_store_id',
                        help='prints all Shufersal stores in a given city. Input should be a city name in Hebrew',
                        metavar='city',
                        nargs=1,
                        )
    parser.add_argument('--load_prices',
                        help='boolean flag representing whether to load an existing price XML file',
                        action='store_true',
                        )
    parser.add_argument('--load_promos',
                        help='boolean flag representing whether to load an existing promo XML file',
                        action='store_true',
                        )
    parser.add_argument('--load_stores',
                        help='boolean flag representing whether to load an existing stores XML file',
                        action='store_true',
                        )
    parser.add_argument('--chain',
                        required=True,
                        help='The name of the requested chain',
                        choices=chain_dict.keys(),
                        )
    parser.add_argument('--file_extension',
                        help='The extension of the promotions output file',
                        choices=VALID_PROMOTION_FILE_EXTENSIONS,
                        default='.xlsx',
                        )
    parser.add_argument('--output_filename',
                        help='The path to write the promotions table to',
                        type=valid_promotion_output_file,
                        )
    parser.add_argument('--only_export_to_file',
                        help='Boolean flag representing whether only export or also open the promotion output file',
                        action='store_true',
                        )
    parser.add_argument('--debug',
                        help='Boolean flag representing whether to run in debug mode',
                        action='store_true',
                        )
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    chain: SupermarketChain = chain_dict[args.chain]

    if args.promos:
        arg_store_id = int(args.promos[0])

        if args.output_filename:
            output_filename = args.output_filename
            directory = os.path.dirname(output_filename)
            Path(directory).mkdir(parents=True, exist_ok=True)
        else:
            Path(RESULTS_DIRNAME).mkdir(exist_ok=True)
            output_filename = f'{RESULTS_DIRNAME}/{repr(type(chain))}_promos_{arg_store_id}{args.file_extension}'

        main_latest_promos(store_id=arg_store_id, output_filename=output_filename, chain=chain,
                           load_promos=args.load_promos, load_xml=args.load_prices)
        if not args.only_export_to_file:
            os.startfile(Path(output_filename))
        logging.debug(f'Process finished at: {datetime.now()}')

    elif args.price:
        log_products_prices(chain, store_id=args.price[0], load_xml=args.load_prices, product_name=args.price[1])

    elif args.find_store_id:
        arg_city = args.find_store_id[0]
        log_stores_ids(city=arg_city, load_xml=args.load_stores, chain=chain)

    elif args.find_promos_by_name:
        arg_store_id = int(args.find_promos_by_name[0])
        log_promos_by_name(store_id=arg_store_id, chain=chain, promo_name=args.find_promos_by_name[1],
                           load_prices=args.load_prices, load_promos=args.load_promos)
