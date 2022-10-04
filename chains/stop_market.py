from chains.cerberus_web_client import CerberusWebClient


class StopMarket(CerberusWebClient):
    _date_hour_format = "%Y-%m-%d %H:%M:%S"

    @property
    def username(self):
        return "Stop_Market"
