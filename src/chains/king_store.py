from src.chains.engines.binaproject_web_client import BinaProjectWebClient


class KingStore(BinaProjectWebClient):
    _path_prefix = "Food_Law"
    _hostname_suffix = ".co.il"
