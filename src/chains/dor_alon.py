from src.chains.engines.cerberus_web_client import CerberusWebClient


class DorAlon(CerberusWebClient):
    @property
    def username(self):
        return "doralon"

    _date_hour_format = "%Y-%m-%d %H:%M:%S"
