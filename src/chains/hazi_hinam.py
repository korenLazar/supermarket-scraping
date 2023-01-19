from src.chains.engines.cerberus_web_client import CerberusWebClient


class HaziHinam(CerberusWebClient):
    @property
    def username(self):
        return "HaziHinam"

    _date_hour_format = "%Y-%m-%d %H:%M:%S"
