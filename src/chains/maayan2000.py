from src.chains.engines.binaproject_web_client import BinaProjectWebClient
from il_supermarket_scarper.scrappers_factory import ScraperFactory

class Maayan2000(BinaProjectWebClient):
    @property
    def scraper(self):
        return ScraperFactory.MAAYAN_2000
