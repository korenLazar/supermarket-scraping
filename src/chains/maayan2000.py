from src.chains.engines.binaproject_web_client import BinaProjectWebClient


class Maayan2000(BinaProjectWebClient):


    @property
    def scraper(self):
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        return ScraperFactory.MAAYAN_2000