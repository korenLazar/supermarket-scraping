from src.chains.engines.binaproject_web_client import BinaProjectWebClient


class ZolVebegadol(BinaProjectWebClient):

    @property
    def scraper(self):
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        return ScraperFactory.ZOL_VEBEGADOL
