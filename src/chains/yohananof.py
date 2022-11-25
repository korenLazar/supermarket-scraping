from src.chains.cerberus_web_client import CerberusWebClient


class Yohananof(CerberusWebClient):
    @property
    def username(self):
        return "yohananof"

    _date_hour_format = "%Y-%m-%d %H:%M:%S"
