from cerberus_web_client import CerberusWebClient
from supermarket_chain import SupermarketChain


class TivTaam(CerberusWebClient, SupermarketChain):
    _class_name = 'TivTaam'

    @property
    def username(self):
        return self._class_name
