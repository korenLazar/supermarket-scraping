from src.chains.engines.matrix import Matrix


class Bareket(Matrix):
 
    @property
    def scraper(self):
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        return ScraperFactory.BAREKET
