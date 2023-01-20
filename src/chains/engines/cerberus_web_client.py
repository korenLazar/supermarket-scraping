from abc import abstractmethod
from src.supermarket_chain import SupermarketChain


class CerberusWebClient(SupermarketChain):

    @property
    @abstractmethod
    def scraper(self):
        pass


    def get_filter_function(
        links: list,
        store_id: int,
        category: SupermarketChain.XMLFilesCategory,
    ):
        for link in links:
            if category == SupermarketChain.XMLFilesCategory.Promos:
                filter_func = (
                    lambda l: "promo" in l
                    and "full" not in l
                    and f"-{store_id:03d}-20" in l
                )
            elif category == SupermarketChain.XMLFilesCategory.PromosFull:
                filter_func = (
                    lambda l: "promo" in l
                    and "full" in l
                    and f"-{store_id:03d}-20" in l
                )
            elif category == SupermarketChain.XMLFilesCategory.Prices:
                filter_func = (
                    lambda l: "price" in l
                    and "full" not in l
                    and f"-{store_id:03d}-20" in l
                )
            elif category == SupermarketChain.XMLFilesCategory.PricesFull:
                filter_func = (
                    lambda l: "price" in l
                    and "full" in l
                    and f"-{store_id:03d}-20" in l
                )
            elif category == SupermarketChain.XMLFilesCategory.Stores:
                filter_func = lambda l: "store" in l and "full" in l and f"-000-20" in l
            else:
                raise ValueError(f"Unknown category type: {category=}")

            if filter_func(link):
                if not best_link or int(link[-7:-3]) > int(best_link[-7:-3]):
                    best_link = link
        return best_link