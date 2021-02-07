from chains.binaproject_web_client import BinaProjectWebClient
from supermarket_chain import SupermarketChain


class ShukHayir(BinaProjectWebClient, SupermarketChain):
    @property
    def hostname_prefix(self): return "shuk-hayir"
