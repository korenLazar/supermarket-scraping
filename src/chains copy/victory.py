from src.chains.engines.matrix import Matrix
from il_supermarket_scarper.scrappers_factory import ScraperFactory


class Victory(Matrix):
    pass

    @property
    def scraper(self):
        return ScraperFactory.VICTORY
