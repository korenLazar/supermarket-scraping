import re
from datetime import datetime

import numpy as np
import requests
from bs4 import BeautifulSoup

from src.supermarket_chain import SupermarketChain


class Mega(SupermarketChain):
    _date_hour_format = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def get_download_url_or_path(
        store_id: int,
        category: SupermarketChain.XMLFilesCategory,
        session: requests.Session,
    ) -> str:
        today_date_suffix = datetime.today().date().strftime("%Y%m%d")
        url = f"http://publishprice.mega.co.il/{today_date_suffix}/"
        req_res = requests.get(url)
        soup = BeautifulSoup(req_res.text, features="lxml")
        promo_tags = soup.findAll(
            "a",
            attrs={
                "href": re.compile(
                    rf"^{category.name.replace('s', '')}.*-{store_id:04d}-"
                )
            },
        )
        most_recent_tag_ind = np.argmax(
            [int(promo_tag["href"][-7:-3]) for promo_tag in promo_tags]
        )
        return url + promo_tags[most_recent_tag_ind]["href"]
