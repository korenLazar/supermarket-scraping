from src.chains.engines.binaproject_web_client import BinaProjectWebClient
from il_supermarket_scarper.scrappers_factory import ScraperFactory


class ZolVebegadol(BinaProjectWebClient):
    @property
    def scraper(self):
        return ScraperFactory.ZOL_VEBEGADOL
