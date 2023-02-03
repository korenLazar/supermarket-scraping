from src.chains.engines.binaproject_web_client import BinaProjectWebClient


class ShefaBirkatHashem(BinaProjectWebClient):



    @property
    def scraper(self):
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        return ScraperFactory.SHEFA_BARCART_ASHEM
