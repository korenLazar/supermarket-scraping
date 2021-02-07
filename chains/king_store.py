from chains.binaproject_web_client import BinaProjectWebClient
from supermarket_chain import SupermarketChain


class KingStore(BinaProjectWebClient, SupermarketChain):
    _path_prefix = "Food_Law"
    _hostname_suffix = ".co.il"
