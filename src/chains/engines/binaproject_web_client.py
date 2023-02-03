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

    def get_filter_function(
        links: list,
        store_id: int,
        category: SupermarketChain.XMLFilesCategory,
    ):
        if category in [SupermarketChain.XMLFilesCategory.Promos, SupermarketChain.XMLFilesCategory.Prices]:
            filter_func = lambda fname: f'-{store_id:03d}-20' in fname and category.name.replace('s', '') in fname \
                                        and not re.search('full', fname, re.IGNORECASE)
            if not any(filter_func(cur_json[FNAME_KEY]) for cur_json in links):
                return ""  # Could not find non-full Promos/Prices file
        else:
            filter_func = lambda fname: f'-{store_id:03d}-20' in fname and category.name.replace('s', '') in fname and 'null' not in fname

        return list(filter(filter_func,links))

    @property
    def hostname_prefix(self):
        return repr(type(self))

    @property
    def path_prefix(self):
        return type(self)._path_prefix

    @property
    def hostname_suffix(self):
        return type(self)._hostname_suffix
