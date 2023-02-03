from src.chains.engines.cerberus_web_client import CerberusWebClient


class TivTaam(CerberusWebClient):
    

    @property
    def scraper(self):
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        return ScraperFactory.TIV_TAAM