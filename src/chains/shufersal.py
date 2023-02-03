import requests
from bs4 import BeautifulSoup

from src.chains.engines.multipage import Multipage


class Shufersal(Multipage):

    @property
    def scraper(self):
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        return ScraperFactory.SHUFERSAL