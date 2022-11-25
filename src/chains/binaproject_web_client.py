import json
import re

import requests

from src.supermarket_chain import SupermarketChain

FNAME_KEY = "FileNm"


class BinaProjectWebClient(SupermarketChain):
    _date_hour_format = '%Y-%m-%d %H:%M:%S'
    _update_date_format = '%Y-%m-%d %H:%M:%S'
    _path_prefix = ""
    _hostname_suffix = ".binaprojects.com"

    def get_download_url_or_path(self, store_id: int, category: SupermarketChain.XMLFilesCategory, session: requests.Session) \
            -> str:
        if not SupermarketChain.is_valid_store_id(store_id):
            raise ValueError(f"Invalid {store_id=} (store id must be a natural number)")
        hostname = f"http://{self.hostname_prefix}{self.hostname_suffix}"
        url = '/'.join([hostname, self.path_prefix, "MainIO_Hok.aspx"])
        req_res: requests.Response = session.get(url)
        jsons_files = json.loads(req_res.text)

        if category in [SupermarketChain.XMLFilesCategory.Promos, SupermarketChain.XMLFilesCategory.Prices]:
            filter_func = lambda fname: f'-{store_id:03d}-20' in fname and category.name.replace('s', '') in fname \
                                        and not re.search('full', fname, re.IGNORECASE)
            if not any(filter_func(cur_json[FNAME_KEY]) for cur_json in jsons_files):
                return ""  # Could not find non-full Promos/Prices file
        else:
            filter_func = lambda fname: f'-{store_id:03d}-20' in fname and category.name.replace('s', '') in fname and 'null' not in fname
        suffix = next(
            cur_json[FNAME_KEY] for cur_json in jsons_files if filter_func(cur_json[FNAME_KEY]))
        down_url: str = '/'.join([hostname, self.path_prefix, "Download", suffix])
        return down_url

    @property
    def hostname_prefix(self):
        return repr(type(self))

    @property
    def path_prefix(self):
        return type(self)._path_prefix

    @property
    def hostname_suffix(self):
        return type(self)._hostname_suffix
