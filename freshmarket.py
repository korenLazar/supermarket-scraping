from cerberus_web_client import CerberusWebClient
from supermarket_chain import SupermarketChain


class Freshmarket(CerberusWebClient, SupermarketChain):
    _date_hour_format = '%Y-%m-%d %H:%M:%S'
    _class_name = 'Freshmarket'

    @property
    def username(self):
        return self._class_name
