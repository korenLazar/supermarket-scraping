import json
import requests

from supermarket_chain import SupermarketChain


class RamiLevi(SupermarketChain):
    _date_hour_format = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def get_download_url(store_id: int, category: SupermarketChain.XMLFilesCategory, session: requests.Session) -> str:
        hostname: str = "https://publishedprices.co.il"

        # Post the payload to the site to log in
        session.post(hostname + "/login/user", data={'username': 'ramilevi'})

        # Scrape the data
        ajax_dir_payload: dict = {'iDisplayLength': 100000, 'sSearch': category.name.replace('s', '')}
        s: requests.Response = session.post(hostname + "/file/ajax_dir", data=ajax_dir_payload)
        s_json: dict = json.loads(s.text)
        suffix: str = next(d['name'] for d in s_json['aaData'] if f'-{store_id:03d}-20' in d['name'])

        download_url: str = hostname + "/file/d/" + suffix
        print(download_url)
        return download_url

    def __repr__(self):
        return 'RamiLevi'
