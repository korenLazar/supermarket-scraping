import re
from abc import abstractmethod
from enum import Enum
from argparse import ArgumentTypeError
from typing import Dict, List

import requests
from bs4.element import Tag

from item import Item


class Meta(type):
    def __repr__(cls):
        return cls.__name__


class SupermarketChain(object, metaclass=Meta):
    """
    A class representing a supermarket chain.
    """

    class XMLFilesCategory(Enum):
        """
        An enum class of different XML files produced by a supermarket chain
        """
        All, Prices, PricesFull, Promos, PromosFull, Stores = range(6)

    _promotion_tag_name = 'Promotion'
    _promotion_update_tag_name = 'PromotionUpdateDate'
    _date_format = '%Y-%m-%d'
    _date_hour_format = '%Y-%m-%d %H:%M'
    _update_date_format = '%Y-%m-%d %H:%M'
    _item_tag_name = 'Item'

    @property
    def promotion_tag_name(self):
        return type(self)._promotion_tag_name

    @property
    def promotion_update_tag_name(self):
        return type(self)._promotion_update_tag_name

    @property
    def date_format(self):
        return type(self)._date_format

    @property
    def date_hour_format(self):
        return type(self)._date_hour_format

    @property
    def update_date_format(self):
        return type(self)._update_date_format

    @property
    def item_tag_name(self):
        return type(self)._item_tag_name

    @staticmethod
    def is_valid_store_id(store_id: int) -> bool:
        """
        This method returns whether a given store ID is valid (French Natural number).

        :param store_id: A given store ID
        """
        return isinstance(store_id, int) and store_id >= 0

    @staticmethod
    def store_id_type(store_id: str) -> str:
        """
        This method used as a type verification for store_id.

        :param store_id: A given store ID
        :return: The given store_id if valid, else raise an ArgumentTypeError.
        """
        if not SupermarketChain.is_valid_store_id(int(store_id)):
            raise ArgumentTypeError(f"Given store_id: {store_id} is not a valid store_id.")
        return store_id

    @staticmethod
    @abstractmethod
    def get_download_url(store_id: int, category: XMLFilesCategory, session: requests.Session) -> str:
        """
        This method scrapes supermarket's website and returns a url containing the data for a given store and category.

        :param store_id: A given ID of a store
        :param category: A given category
        :return: A downloadable link of the  data for a given store and category
        :param session: A given session object
        """
        pass

    @staticmethod
    def get_items(promo: Tag, items_dict: Dict[str, Item]) -> List[Item]:
        """
        This method returns a list of the items that participate in a given promotion.

        :param promo: A given promotion
        :param items_dict: A given dictionary of products
        """
        items = list()
        for item in promo.find_all('Item'):
            item_code = item.find('ItemCode').text
            full_item_info = items_dict.get(item_code)
            if full_item_info:
                items.append(full_item_info)
        return items

    @staticmethod
    def get_null_items(promo: Tag, items_dict: Dict[str, Item]) -> List[str]:
        """
        This function returns all the items in a given promotion which do not appear in the given items_dict.
        """
        return [item.find('ItemCode').text for item in promo.find_all('Item')
                if not items_dict.get(item.find('ItemCode').text)]

    @staticmethod
    def get_item_info(item: Tag) -> Item:
        """
        This function returns a string containing important information about a given supermarket's product.
        """
        return Item(name=item.find(re.compile(r'ItemN[a]?m[e]?')).text, price=float(item.find('ItemPrice').text),
                    price_by_measure=float(item.find('UnitOfMeasurePrice').text), code=item.find('ItemCode').text,
                    manufacturer=item.find(re.compile(r'Manufacture[r]?Name')).text)
