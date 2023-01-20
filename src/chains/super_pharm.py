from src.chains.engines.multipage import Multipage

class SuperPharm(Multipage):


    @property
    def scraper(self):
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        return ScraperFactory.SUPER_PHARM
