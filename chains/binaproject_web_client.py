import json
import requests

from supermarket_chain import SupermarketChain


class BinaProjectWebClient:
    _date_hour_format = '%Y-%m-%d %H:%M:%S'
    _update_date_format = '%Y-%m-%d %H:%M:%S'
    _path_prefix = ""
    _hostname_suffix = ".binaprojects.com"

    def get_download_url(self, store_id: int, category: SupermarketChain.XMLFilesCategory, session: requests.Session) \
            -> str:
        hostname = f"http://{self.hostname_prefix}{self.hostname_suffix}"
        url = '/'.join([hostname, self.path_prefix, "MainIO_Hok.aspx"])
        req_res: requests.Response = session.get(url)
        jsons_files = json.loads(req_res.text)
        suffix = next(cur_json["FileNm"] for cur_json in jsons_files if f'-{store_id:03d}-20' in cur_json["FileNm"]
                      and category.name.replace('s', '') in cur_json["FileNm"])
        down_url: str = '/'.join([hostname, self.path_prefix, "Download", suffix])
        return down_url

    @property
    def hostname_prefix(self):
        return repr(type(self))

    @property
    def path_prefix(self):
        return type(self)._path_prefix

    @property
    def hostname_suffix(self):
        return type(self)._hostname_suffix
