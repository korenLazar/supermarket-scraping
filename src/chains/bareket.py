from src.chains.engines.matrix import Matrix
from il_supermarket_scarper.scrappers_factory import ScraperFactory

class Bareket(Matrix):
    @property
    def scraper(self):
        return ScraperFactory.BAREKET
