from typing import Tuple
from time import sleep
import os
import sys
import datetime
import re
import json
import psycopg2
from psycopg2.extensions import connection, cursor
from psycopg2.extras import execute_batch
import pymongo
import requests
from pymongo.collection import Collection
from glob import glob
import certifi
import gridfs
import threading
from src.main import get_all_prices_with_promos, main_latest_promos, CHAINS_DICT
import psutil
from src.send_me_mail import create_mail_to_send, send_me_logs, zip_res_and_all
LIST_OF_DICTS = []
LIST_OF_BARCODES = []
GLOBAL_DICT = {}
BEGINING_COUNT_DOCUMENTS = 0
END_COUNT_DOCUMENTS = 0
ENDING_TIME = ""
RUNNER = []
ITEMS_BEEN_UPDATED = 0
UPDATED_CHAINS = {}
CHAIN_INDEX = {"OsherAd": 1, "HaziHinam": 2, "RamiLevi": 4,
               "Shufersal": 5, "Victory": 6, "YeinotBitan": 7, "Yohananof": 8}


def connect_to_pg() -> Tuple[connection, cursor]:
    conn = psycopg2.connect(dbname=os.environ['SUPER_PG_NAME'], user=os.environ['SUPER_PG_USER'], password=os.environ['SUPER_PG_PWD'],
                            host=os.environ['SUPER_PG_HOST'], port=os.environ['SUPER_PG_PORT'], sslmode=os.environ['SUPER_PG_SSL'])
    connection = conn.cursor()
    return conn, connection


def download_from_chain(chain: str, store_id: int, promos: bool = False):
    '''download_from_chain This function downloads data related to store prices or promotions from a chain.

    :param chain: a string that represents the chain from which the data is to be downloaded.
    :type chain: str
    :param store_id:  an integer that represents the ID of the store for which data is to be downloaded.
    :type store_id: int
    :param promos:  downloads the latest promotions and creates an Excel document for the promos, defaults to False
    :type promos: bool, optional
    '''
    print(f"{chain}, {store_id}")
    if not promos:
        d = get_all_prices_with_promos(
            chain=CHAINS_DICT[chain],
            store_id=store_id, load_prices=False, load_promos=False)
        items_dict_to_json = {
            item_code: {
                k: v
                for k, v in item.__dict__.items()
                if not k.startswith("__") and not callable(k)
            }
            for item_code, item in d.items()
        }
        with open(f"results/{chain}-prices-{store_id}-{datetime.date.today()}.json", "w") as file:
            json.dump(items_dict_to_json, file)
            send_data_to_db(items_dict_to_json, chain, store_id, f"{datetime.date.today()}")
    else:
        main_latest_promos(
            store_id, f"results/{chain}-{store_id}-{datetime.date.today()}.xlsx", CHAINS_DICT[chain],
            False, False, True)


def send_data_to_db(json_data: dict, _chainn: str = None, store_id: int = None, date: str = None) -> None:
    conn, connect = connect_to_pg()
    chhain = CHAIN_INDEX[_chainn]
    execute_batch(
        connect, "insert into product_names values(%(code)s,%(name)s," + f"{chhain}) on conflict do nothing",
        list(json_data.values()))
    conn.commit()
    execute_batch(
        connect,
        "insert into price(barcode,price,final_price,price_by_measure,manu,chain,_date,store_id) values(%(code)s,%(price)s,%(final_price)s,%(price_by_measure)s, %(manufacturer)s," +
        f"{chhain},'{date}',{store_id}) on conflict do nothing", list(json_data.values()))
    conn.commit()


def __create_chains_updating_dict(server: bool = True) -> dict:
    client = pymongo.MongoClient(
        os.environ['MONGODB']
    ) if server else pymongo.MongoClient(
        os.environ['MONGODB'], directConnection=True, tlsCAFile=certifi.where())
    col = client[os.environ['SUPER_PG_NAME']]['prices']
    return {key["chain"]: 0 for key in col.find({"chain": {"$exists": True}})}


def connect_mongo(server: bool = True, collection_name: str = "prices", check_beggining: bool = False) -> Collection:
    global BEGINING_COUNT_DOCUMENTS
    client = pymongo.MongoClient(
        os.environ['MONGODB']
    ) if server else pymongo.MongoClient(
        os.environ['MONGODB'], directConnection=True, tlsCAFile=certifi.where())
    col = client[os.environ['SUPER_PG_NAME']][collection_name]
    BEGINING_COUNT_DOCUMENTS = col.count_documents(
        {"chain": {"$exists": False}}) if check_beggining else BEGINING_COUNT_DOCUMENTS
    return col


def _get_date(text: str) -> str:
    return re.search(r'(?:(\d+-\d+){2})(?=\.json)', text).group()


def _get_chain(text: str) -> str:
    return re.search(r'[A-z]+(?=-promos|-prices)', text).group()


def _get_store(text: str) -> str:
    return re.search(r'(?<=(promos-|prices-))\d+(?=-)', text).group()


def read_json_export(json_file: str) -> dict:
    with open(json_file, "r", encoding="utf_8") as file:
        return json.load(file)


def read_chain(json_file: str) -> dict:
    return {"chain": re.search(r'[A-z]+(?=-promos|-prices)', json_file).group()}


def read_store_id(json_file: str) -> dict:
    return {"store_id": re.search(r'(?<=(promos-|prices-))\d+(?=-)', json_file).group()}


def read_date(json_file: str) -> dict:
    return {"date": re.search(r'(?:(\d+-\d+){2})(?=\.json)', json_file).group()}


def update_json(json_file: str) -> dict:
    global UPDATED_CHAINS
    json_update: dict = read_json_export(json_file)
    send_data_to_db(
        json_update, read_chain(json_file)["chain"],
        read_store_id(json_file)["store_id"],
        read_date(json_file)["date"])
    for key in json_update:
        json_update[key].update(read_chain(json_file))
        json_update[key].update(read_store_id(json_file))
        json_update[key].update(read_date(json_file))
    UPDATED_CHAINS[f'{read_chain(json_file)},{read_store_id(json_file)}'] = len(json_update[key])
    return json_update


def create_store_dict(jsons_path: str):
    return {_get_chain(jsonn): {_get_store(jsonn): {}} for jsonn in glob(f"{jsons_path}/*.json")}


def create_date_dict(jsons_path: str):
    return {_get_date(date): {} for date in glob(f"{jsons_path}/*.json")}


def create_empty_global_dict(list_of_barcodes: list, jsons_path) -> dict:
    return {barcode: create_date_dict(jsons_path) for barcode in list_of_barcodes}


def create_another_global_dict(list_of_barcodes: list, jsons_path: str) -> dict:
    return {barcode: create_store_dict(jsons_path) for barcode in list_of_barcodes}


def join_jsons(jsons_path: str) -> dict:
    global LIST_OF_DICTS, LIST_OF_BARCODES
    # dict_of_dates = {_get_date(date): [] for date in glob(f"{jsons_path}/*.json")}
    for jsond in glob(f"{jsons_path}/*.json"):
        with open(jsond, "r", encoding="utf_8") as F:
            if os.path.getsize(jsond) > 10 and F.read().startswith("{"):
                json_file = update_json(jsond)
                LIST_OF_BARCODES = list(set(list(json_file.keys())+LIST_OF_BARCODES))
                LIST_OF_DICTS.append(json_file)
    return create_global_dict(
        LIST_OF_BARCODES, LIST_OF_DICTS, create_empty_global_dict(LIST_OF_BARCODES, jsons_path),
        jsons_path)


def join_more_jsons(jsons_path: str) -> dict:
    global LIST_OF_DICTS, LIST_OF_BARCODES
    for jsond in glob(f"{jsons_path}/*.json"):
        if os.path.getsize(jsond) > 10:
            json_file = update_json(jsond)
            LIST_OF_BARCODES = list(set(list(json_file.keys())+LIST_OF_BARCODES))
            LIST_OF_DICTS.append(json_file)
    return create_global_dict(
        LIST_OF_BARCODES, LIST_OF_DICTS, create_another_global_dict(LIST_OF_BARCODES, jsons_path),
        jsons_path)


def get_barcode_in_date(dict_of_dates: dict, json_dict: dict, barcode: str, date: str):
    try:
        dict_of_dates[barcode][date][json_dict[barcode]['chain']][json_dict[barcode]['store_id']] = json_dict[barcode]
    except KeyError:
        dict_of_dates[barcode][date][json_dict[barcode]['chain']] = {}
        dict_of_dates[barcode][date][json_dict[barcode]['chain']][json_dict[barcode]['store_id']] = json_dict[barcode]


def create_global_dict(barcode_list: list, list_of_dicts: list[dict], dict_of_dates: dict, jsons_path: str) -> dict:
    global_dict = create_empty_global_dict(barcode_list, jsons_path)
    for d in list_of_dicts:
        for barcode in barcode_list:
            if d.get(barcode):
                temp_dict = {f"{d[barcode]['chain']},{d[barcode]['store_id']}": d[barcode]}
                get_barcode_in_date(dict_of_dates, d, barcode, d[barcode]["date"])
                global_dict.update(dict_of_dates)
    return global_dict


def generate_jsonl(jsons_path: str, local: bool = True):
    global END_COUNT_DOCUMENTS, BEG_TIME, ENDING_TIME, ITEMS_BEEN_UPDATED, UPDATED_CHAINS
    print(f"{datetime.datetime.now()}: connect to mongo")
    col: Collection = connect_mongo(local)
    print(f"{datetime.datetime.now()}: combine jsons")
    dict_many = join_jsons(jsons_path)
    ITEMS_BEEN_UPDATED = len(dict_many)
    print(f"{datetime.datetime.now()}: add to db")
    for item in dict_many:
        # save_own={"_id":item}
        # if col.find_one(save_own):
        col.update_one({"_id": item}, {"$set": dict_many[item]}, True)
        # else:
        #     save_own.update(dict_many[item])
        #     col.insert_one(save_own)
    END_COUNT_DOCUMENTS = col.count_documents({})
    ENDING_TIME = f"{datetime.datetime.now().strftime('%H:%M')}"
    print(f"{datetime.datetime.now()}: done")
    # ntfy.notify()
    requests.post(
        os.environ['NTFY'],
        data=f'done merging at {ENDING_TIME}, with {END_COUNT_DOCUMENTS}. {ITEMS_BEEN_UPDATED} items has been updated. Started at {BEG_TIME}',
        headers={
            "Title": f"{datetime.date.today()}",
            "Tags": "notify"
        })
    # subprocess.Popen(

    #     ["ntfy", "send", "http://db.saret.tk:8080/saret", f"{datetime.date.today()}",
    #      f'done merging at {ENDING_TIME}, with {END_COUNT_DOCUMENTS}. {ITEMS_BEEN_UPDATED} items has been updated. Started at {BEG_TIME}'])


def run_this_shit(chain: str, _id: str, promos: bool = False):
    download_from_chain(chain, _id, promos)


def main_run_first(run: bool = False):
    global RUNNER
    chain_stores = connect_mongo(check_beggining=True).find({"chain": {"$exists": True}}).sort("_id", pymongo.ASCENDING)
    for chains in chain_stores:
        p = False
        for _id in chains["storeId"]:
            try:
                run_this_shit(chains["chain"], _id, run)
            except Exception as e:
                print(e)
    while RUNNER:
        sleep(1)
        for ind, r in enumerate(RUNNER):
            if not psutil.pid_exists(r):
                RUNNER.pop(ind)


def main_run_secound():
    generate_jsonl("results", local)
    for file in glob("results/*.json"):
        os.rename(file, f"{file}.done")


def another_connetction_to_mongo():
    col: Collection = connect_mongo(collection_name="innerCommands")
    for file in os.listdir(os.path.abspath(os.path.curdir)):
        File = re.match(r"helper_.+\.py$", file)
        if File and os.path.isfile(os.path.abspath(file)):
            with open(os.path.abspath(file), "r", encoding='utf_8') as f:
                col.update_one({'file': file}, {"$set": {'value': f.read()}}, True)
            fileees = pymongo.MongoClient(
                os.environ['MONGODB']).get_database(os.environ['SUPER_PG_NAME'])
            varme = gridfs.GridFSBucket(fileees, "hhh")
            with varme.open_upload_stream(file) as g:
                with open(file, "rb") as read_binary_file:
                    g.write(read_binary_file)


if __name__ == "__main__":
    db_size = sum([os.path.getsize(file) for file in glob("/mnt/MongoDB", recursive=True)+glob("/mnt/MongoDB/mongodb/", recursive=True)]
                  ) if os.path.exists("/mnt/MongoDB") else sum([os.path.getsize(file) for file in glob("/var/lib/mongodb", recursive=True)])
    UPDATED_CHAINS = __create_chains_updating_dict()
    print(sys.argv)
    BEG_TIME = datetime.datetime.now().strftime('%H:%M')
    another_connetction_to_mongo()
    print(len(sys.argv))
    local = len(sys.argv) < 2
    print(f"len(sys.argv) <2?:\t{len(sys.argv) <2}")
    threads_before = threading.active_count()
    print(threads_before)
    if local:
        main_run_first()
        main_run_secound()
    else:
        main_run_secound()
        main_run_first()
    another_connetction_to_mongo()
    new_db_size = sum([os.path.getsize(file) for file in glob("/mnt/MongoDB", recursive=True)+glob("/mnt/MongoDB/mongodb/", recursive=True)]
                      ) if os.path.exists("/mnt/MongoDB") else sum([os.path.getsize(file) for file in glob("/var/lib/mongodb", recursive=True)])
    dict_account = connect_mongo(collection_name="innerCommands").find({"username": os.environ["MAIL"]})[0]
    create_mail_to_send(BEGINING_COUNT_DOCUMENTS, END_COUNT_DOCUMENTS, ENDING_TIME,
                        ITEMS_BEEN_UPDATED, dict_account, UPDATED_CHAINS, [db_size, new_db_size])
    zip_res_and_all(dict_account)
    for file in glob("/home/saret/*.7z", recursive=True):
        os.remove(file)
    send_me_logs(dict_account)
# TODO: documentize this shit!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
