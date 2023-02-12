from src.chains.engines.multipage import Multipage
from il_supermarket_scarper.scrappers_factory import ScraperFactory


class Shufersal(Multipage):
    @property
    def scraper(self):
        return ScraperFactory.SHUFERSAL
