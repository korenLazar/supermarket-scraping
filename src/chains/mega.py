from src.chains.engines.regex import Regex
from il_supermarket_scarper.scrappers_factory import ScraperFactory


class Mega(Regex):
    _date_hour_format = "%Y-%m-%d %H:%M:%S"

    @property
    def scraper(self):
        return ScraperFactory.MEGA
