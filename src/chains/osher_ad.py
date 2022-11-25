from src.chains.cerberus_web_client import CerberusWebClient


class OsherAd(CerberusWebClient):
    @property
    def username(self):
        return "osherad"

    _date_hour_format = "%Y-%m-%d %H:%M:%S"
