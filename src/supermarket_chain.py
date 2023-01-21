from abc import abstractmethod
from argparse import ArgumentTypeError
from typing import Dict, List

import requests
from aenum import Enum
from bs4.element import Tag

from src.item import Item


class Meta(type):
    def __repr__(cls):
        return cls.__name__


class SupermarketChain(object, metaclass=Meta):
    """
    A class representing a supermarket chain.
    """
    @property
    def scraper():
        pass

    class XMLFilesCategory(Enum):
        """
        An enum class of different XML files produced by a supermarket chain
        """

        All, Prices, PricesFull, Promos, PromosFull, Stores = range(6)

    _promotion_tag_name = "Promotion"
    _promotion_update_tag_name = "PromotionUpdateDate"
    _date_format = "%Y-%m-%d"
    _date_hour_format = "%Y-%m-%d %H:%M"
    _update_date_format = "%Y-%m-%d %H:%M"
    _item_tag_name = "Item"

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
            raise ArgumentTypeError(
                f"Given store_id: {store_id} is not a valid store_id."
            )
        return store_id

    @abstractmethod
    def get_download_url_or_path(
        self,
        store_id: int, category: XMLFilesCategory
    ) -> str:
        return self.scraper.value().scarpe(store_id,category)

    @staticmethod
    def get_items(promo: Tag, items_dict: Dict[str, Item]) -> List[Item]:
        """
        This method returns a list of the items that participate in a given promotion.

        :param promo: A given promotion
        :param items_dict: A given dictionary of products
        """
        items = list()
        for item in promo.find_all("Item"):
            item_code = item.find("ItemCode").text
            full_item_info = items_dict.get(item_code)
            if full_item_info:
                items.append(full_item_info)
        return items

    @staticmethod
    def get_null_items(promo: Tag, items_dict: Dict[str, Item]) -> List[str]:
        """
        This function returns all the items in a given promotion which do not appear in the given items_dict.
        """
        return [
            item.find("ItemCode").text
            for item in promo.find_all("Item")
            if not items_dict.get(item.find("ItemCode").text)
        ]
