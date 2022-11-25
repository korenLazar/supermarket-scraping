from src.chains.cerberus_web_client import CerberusWebClient


class RamiLevi(CerberusWebClient):
    @property
    def username(self):
        return "RamiLevi"

    _date_hour_format = "%Y-%m-%d %H:%M:%S"
