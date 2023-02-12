from src.chains.engines.matrix import Matrix
from il_supermarket_scarper.scrappers_factory import ScraperFactory


class NativHased(Matrix):
    @property
    def scraper(self):
        return ScraperFactory.NETIV_HASED
