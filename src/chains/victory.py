from src.chains.engines.matrix import MahsaneiHashook


class Victory(MahsaneiHashook):


    @property
    def scraper(self):
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        return ScraperFactory.VICTORY