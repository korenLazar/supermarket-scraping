from argparse import ArgumentParser
import logging
from pathlib import Path

from promotion import main_latest_promos, get_promos_by_name
from store_utils import get_store_id
from utils import RESULTS_DIRNAME, RAW_FILES_DIRNAME, get_products_prices
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
)

# TODO: fix problem of left-to-right printing

Path(RESULTS_DIRNAME).mkdir(exist_ok=True)
Path(RAW_FILES_DIRNAME).mkdir(exist_ok=True)

chain_dict = {repr(chain): chain() for chain in SupermarketChain.__subclasses__()}

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--promos',
                        help="generates a promos_{store_id}.log file with all the promotions in the requested store",
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
                        help='prints all Shufersal stores within a city. Input should be a name of a city in Hebrew',
                        metavar='city',
                        nargs=1,
                        )
    # parser.add_argument('--all_deals',
    #                     action='store_true',
    #                     )
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
    args = parser.parse_args()

    chain: SupermarketChain = chain_dict[args.chain]
    if args.promos:
        arg_store_id = int(args.promos[0])

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename=f'{RESULTS_DIRNAME}/{args.chain}_promos_{arg_store_id}.log', mode='w',
                                      encoding='utf-8')
        logger.addHandler(handler)
        main_latest_promos(store_id=arg_store_id, load_xml=args.load_prices, logger=logger, chain=chain,
                           load_promos=args.load_promos)

    elif args.price:
        get_products_prices(chain, store_id=args.price[0], load_xml=args.load_prices, product_name=args.price[1])

    elif args.find_store_id:
        arg_city = args.find_store_id[0]
        get_store_id(city=arg_city, load_xml=args.load_stores, chain=chain)

    elif args.find_promos_by_name:
        arg_store_id = int(args.find_promos_by_name[0])
        get_promos_by_name(store_id=arg_store_id, chain=chain, promo_name=args.find_promos_by_name[1],
                           load_prices=args.load_prices, load_promos=args.load_promos)
