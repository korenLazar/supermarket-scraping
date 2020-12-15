from argparse import ArgumentParser
import logging
from promotion import main_latest_promos
from store import get_store_id, store_id_type
from utils import get_products_prices


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--promos',
                        help="generates a promos_{store_id}.log file with all the promotions in the requested store",
                        metavar='store_id',
                        nargs=1,
                        type=store_id_type,
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
    parser.add_argument('--load_xml',
                        help='boolean flag representing whether to load an existing xml',
                        action='store_true',
                        )
    args = parser.parse_args()

    if args.promos:
        arg_store_id = int(args.promos[0])

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename=f'promos_{arg_store_id}.log', mode='w', encoding='utf-8')
        logger.addHandler(handler)
        main_latest_promos(store_id=arg_store_id,
                           load_xml=args.load_xml,
                           logger=logger)

    elif args.price:
        get_products_prices(store_id=args.price[0], product_name=args.price[1], load_xml=args.load_xml)

    elif args.find_store_id:
        arg_city = args.find_store_id[0]
        get_store_id(city=arg_city, load_xml=args.load_xml)
