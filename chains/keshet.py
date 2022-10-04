from chains.cerberus_web_client import CerberusWebClient


class Keshet(CerberusWebClient):
    @property
    def username(self):
        return "Keshet"

    _date_hour_format = "%Y-%m-%d %H:%M:%S"
