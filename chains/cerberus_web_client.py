import json
import re

import requests

from supermarket_chain import SupermarketChain


class CerberusWebClient:

    def get_download_url(self, store_id: int, category: SupermarketChain.XMLFilesCategory, session: requests.Session) \
            -> str:
        hostname: str = "https://publishedprices.co.il"

        # Post the payload to the site to log in
        session.post(hostname + "/login/user", data={'username': self.username})

        # Scrape the data
        ajax_dir_payload: dict = {'iDisplayLength': 100000, 'sSearch': category.name.replace('s', '')}
        s: requests.Response = session.post(hostname + "/file/ajax_dir", data=ajax_dir_payload)
        s_json: dict = json.loads(s.text)
        if category in [SupermarketChain.XMLFilesCategory.Promos, SupermarketChain.XMLFilesCategory.Prices]:
            filter_func = lambda d, id: f'-{id:03d}-20' in d['name'] and not re.search('full', d['name'], re.IGNORECASE)
            if not any(filter_func(d, store_id) for d in s_json['aaData']):
                return ""  # Could not find non-full Prices/Promos file
        else:
            filter_func = lambda d, id: f'-{id:03d}-20' in d['name']
        suffix: str = next(d['name'] for d in s_json['aaData'] if filter_func(d, store_id))

        download_url: str = hostname + "/file/d/" + suffix
        return download_url

    @property
    def username(self):
        return repr(type(self))
