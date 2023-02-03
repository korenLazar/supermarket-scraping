import re
from datetime import datetime

import numpy as np
import requests
from bs4 import BeautifulSoup

from src.chains.engines.regex import Regex
from src.supermarket_chain import SupermarketChain

class YeinotBitan(Regex):
    _date_hour_format = "%Y-%m-%d %H:%M:%S"


    @property
    def scraper(self):
        from il_supermarket_scarper.scrappers_factory import ScraperFactory
        return ScraperFactory.YAYNO_BITAN

    def get_filter_function(
            links: list,
            store_id: int,
            category: SupermarketChain.XMLFilesCategory,
        ):
        promo_tags = re.compile(
                    rf"^{category.name.replace('s', '')}.*-{store_id:04d}-"
                )

        most_recent_tag_ind = np.argmax(
            [int(promo_tag["href"][-7:-3]) for promo_tag in promo_tags]
        )
        return ""#url + promo_tags[most_recent_tag_ind]["href"]
