from src.chains.engines.cerberus_web_client import CerberusWebClient
from il_supermarket_scarper.scrappers_factory import ScraperFactory


class TivTaam(CerberusWebClient):
    @property
    def scraper(self):
        return ScraperFactory.TIV_TAAM
