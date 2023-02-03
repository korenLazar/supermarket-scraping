from src.chains.engines.cerberus_web_client import CerberusWebClient
from il_supermarket_scarper.scrappers_factory import ScraperFactory

class Freshmarket(CerberusWebClient):
    _date_hour_format = "%Y-%m-%d %H:%M:%S"

    @property
    def scraper(self):
        return ScraperFactory.FRESH_MARKET_AND_SUPER_DOSH
