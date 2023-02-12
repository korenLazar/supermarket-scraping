from src.chains.engines.matrix import Matrix
from il_supermarket_scarper.scrappers_factory import ScraperFactory


class SuperYuda(Matrix):
    @property
    def scraper(self):
        return ScraperFactory.SUPER_YUDA
