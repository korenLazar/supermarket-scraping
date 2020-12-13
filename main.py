from argparse import ArgumentParser
import logging
from promotion import main_latest_promos
from store import get_store_id, store_id_type
from utils import get_products_prices
# import json
# from bs4 import BeautifulSoup
# import requests

# def get_coupons():
#     coupons_json = requests.get('https://www.shufersal.co.il/online/he/my-account/coupons/my-coupons')
#     # with open('C:\\Users\\user\\Downloads\\my-coupons.json', "rb") as f:
#     #     coupons_json = json.load(f)
#     bs_coupons = [BeautifulSoup(coup['display'], 'xml') for coup in coupons_json['myCoupons']]
#     return [bs_coupon.find("img", src=lambda value: value and value.startswith(
#         "https://res.cloudinary.com/shufersal/image/upload/f_auto,"
#         "q_auto/v1551800918/prod/product_images/products_medium")).contents[1] for bs_coupon in bs_coupons]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--promos',
                        help="Param for getting the store's promotions",
                        metavar='store_id',
                        nargs='?',
                        type=store_id_type,
                        const=5,
                        )
    parser.add_argument('--price',
                        help='Params for calling get_products_prices',
                        metavar=('store_id', 'product_name'),
                        nargs=2,
                        )
    parser.add_argument('--find_store',
                        help='Params for calling get_store_id',
                        metavar='city',
                        nargs=1,
                        )
    parser.add_argument('--load_xml',
                        help='Whether to load an existing xml',
                        action='store_true',
                        )
    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if args.promos:
        arg_store_id = int(args.promos)
        handler = logging.FileHandler(filename=f'promos_{arg_store_id}.log', mode='w', encoding='utf-8')
        logger.addHandler(handler)
        try:
            main_latest_promos(store_id=arg_store_id,
                               load_xml=args.load_xml,
                               logger=logger)
        except FileNotFoundError:
            main_latest_promos(store_id=arg_store_id,
                               load_xml=False,
                               logger=logger)

    elif args.price:
        handler = logging.FileHandler(filename='products_prices.log', mode='w', encoding='utf-8')
        logger.addHandler(handler)
        try:
            get_products_prices(store_id=args.price[0],
                                product_name=args.price[1],
                                load_xml=args.load_xml,
                                logger=logger)
        except FileNotFoundError:
            get_products_prices(store_id=args.price[0],
                                product_name=args.price[1],
                                load_xml=False,
                                logger=logger)

    elif args.find_store:
        arg_city = args.find_store[0]
        handler = logging.FileHandler(filename=f'stores_{arg_city}.log',
                                      mode='w',
                                      encoding='utf-8')
        logger.addHandler(handler)
        try:
            get_store_id(city=arg_city,
                         load_xml=args.load_xml,
                         logger=logger)
        except FileNotFoundError:
            get_store_id(city=arg_city,
                         load_xml=False,
                         logger=logger)
