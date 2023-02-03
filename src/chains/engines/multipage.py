import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from src.supermarket_chain import SupermarketChain


class Multipage(SupermarketChain):

    def get_filter_function(
            links: list,
            store_id: int,
            category: SupermarketChain.XMLFilesCategory,
        ):
            if category in [
                SupermarketChain.XMLFilesCategory.Promos,
                SupermarketChain.XMLFilesCategory.Prices,
            ]:
                fname_filter_func = (
                    lambda fname: fname
                    and category.name.replace("s", "") in fname
                    and f"-{store_id:03d}-20" in fname
                    and not re.search("full", fname, re.IGNORECASE)
                )
            else:
                fname_filter_func = (
                    lambda fname: fname
                    and category.name.replace("s", "") in fname
                    and f"-{store_id:03d}-20" in fname
                )

            return list(filter(fname_filter_func,links))
            
    @staticmethod
    def get_download_url_or_path(store_id: int, category: SupermarketChain.XMLFilesCategory, session: requests.Session) -> str:
        base_url = "http://prices.super-pharm.co.il/"
        today_date = datetime.today().date()
        category = category.name.replace('s', '')  # TODO: support also StoresFull case
        url = base_url + f"?type={category}&date={today_date}"
        if SupermarketChain.is_valid_store_id(int(store_id)):
            url += f"&store={store_id}"
        req_res: requests.Response = session.get(url)
        session.cookies.save()
        soup: BeautifulSoup = BeautifulSoup(req_res.text, features='lxml')
        down_url = base_url + soup.find('a', text="הורדה")['href']
        req_res_2 = session.get(down_url)
        spath = json.loads(req_res_2.content)
        session.cookies.save()
        return base_url + spath['href']
