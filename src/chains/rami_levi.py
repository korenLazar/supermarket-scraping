from src.chains.engines.cerberus_web_client import CerberusWebClient


class RamiLevi(CerberusWebClient):

    _date_hour_format = "%Y-%m-%d %H:%M:%S"

    @property
    def scraper(self):
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        return ScraperFactory.RAMI_LEVY