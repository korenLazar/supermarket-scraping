from src.chains.cerberus_web_client import CerberusWebClient


class TivTaam(CerberusWebClient):
    @property
    def username(self):
        return "TivTaam"
