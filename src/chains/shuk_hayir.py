from src.chains.binaproject_web_client import BinaProjectWebClient


class ShukHayir(BinaProjectWebClient):
    @property
    def hostname_prefix(self):
        return "shuk-hayir"
