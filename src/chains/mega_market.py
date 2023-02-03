import re
from datetime import datetime

import numpy as np
import requests
from bs4 import BeautifulSoup

from src.chains.engines.regex import Regex
from src.supermarket_chain import SupermarketChain

class MegaMarket(Regex):
    _date_hour_format = "%Y-%m-%d %H:%M:%S"


    @property
    def scraper(self):
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        return ScraperFactory.MEGA_MARKET