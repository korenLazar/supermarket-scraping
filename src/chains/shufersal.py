import requests
from bs4 import BeautifulSoup

from src.supermarket_chain import SupermarketChain


class Shufersal(SupermarketChain):

    @staticmethod
    def get_download_url_or_path(store_id: int, category: SupermarketChain.XMLFilesCategory, session: requests.Session) -> str:
        url = f"http://prices.shufersal.co.il/FileObject/UpdateCategory?catID={category.value}"
        if SupermarketChain.is_valid_store_id(int(store_id)):
            url += f"&storeId={store_id}"
        req_res: requests.Response = requests.get(url)
        soup: BeautifulSoup = BeautifulSoup(req_res.text, features='lxml')
        down_url: str = soup.find('a', text="לחץ להורדה")['href']
        return down_url
