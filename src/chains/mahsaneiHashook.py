from src.chains.engines.matrix import Matrix
from il_supermarket_scarper.scrappers_factory import ScraperFactory

class MahsaneiHashook(Matrix):
    @property
    def scraper(self):
        return ScraperFactory.MAHSANI_ASHUK
