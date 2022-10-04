from chains.cerberus_web_client import CerberusWebClient


class Freshmarket(CerberusWebClient):
    _date_hour_format = "%Y-%m-%d %H:%M:%S"

    @property
    def username(self):
        return "freshmarket"
