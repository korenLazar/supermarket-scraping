import json
import requests

from supermarket_chain import SupermarketChain


class ZolVebegadol(SupermarketChain):
    _date_hour_format = '%Y-%m-%d %H:%M:%S'
    _update_date_format = '%Y-%m-%d %H:%M:%S'
    item_tag_name = 'Item'

    @property
    def update_date_format(self):
        return ZolVebegadol.date_hour_format

    @staticmethod
    def get_download_url(store_id: int, category: SupermarketChain.XMLFilesCategory, session: requests.Session) -> str:
        prefix = "http://zolvebegadol.binaprojects.com"
        url = prefix + "/MainIO_Hok.aspx"
        req_res: requests.Response = session.get(url)
        jsons_files = json.loads(req_res.text)
        suffix = next(cur_json["FileNm"] for cur_json in jsons_files if f'-{store_id:03d}-20' in cur_json["FileNm"]
                      and category.name.replace('s', '') in cur_json["FileNm"])
        down_url: str = '/'.join([prefix, "Download", suffix])
        print(down_url)
        return down_url
