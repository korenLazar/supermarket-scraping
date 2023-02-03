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

