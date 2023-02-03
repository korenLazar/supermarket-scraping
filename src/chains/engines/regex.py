import re
from datetime import datetime

import numpy as np

from src.supermarket_chain import SupermarketChain


class Regex(SupermarketChain):
    _date_hour_format = "%Y-%m-%d %H:%M:%S"
