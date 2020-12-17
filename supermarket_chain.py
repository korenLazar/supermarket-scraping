from abc import abstractmethod
from enum import Enum
from argparse import ArgumentTypeError
from typing import Dict, List
from bs4.element import Tag


class SupermarketChain:
    """
    A class representing a supermarket chain.
    """
    class XMLFilesCategory(Enum):
        """
        An enum class of different XML files produced by a supermarket chain
        """
        pass

    @property
    @abstractmethod
    def promotion_tag_name(self): pass

    @property
    @abstractmethod
    def promotion_update_tag_name(self): pass

    @property
    @abstractmethod
    def date_format(self): pass

    @property
    @abstractmethod
    def date_hour_format(self): pass

    @property
    @abstractmethod
    def item_tag_name(self): pass

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
    def get_download_url(store_id: int, category: XMLFilesCategory) -> str:
        """
        This method scrapes supermarket's website and returns a url containing the data for a given store and category.

        :param store_id: A given id of a store
        :param category: A given category
        :return: A downloadable link of the  data for a given store and category
        """
        pass

    @staticmethod
    @abstractmethod
    def get_items(promo: Tag, items_dict: Dict[str, str]) -> List[str]:
        """
        This method returns a list of the items that participate in a given promo

        :param promo: A given promo
        :param items_dict: A given dictionary of products
        """
        pass
