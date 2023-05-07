from glob import glob
import shutil
from timeit import timeit
import yagmail
import datetime
import sqlite3
import subprocess
import re
import os


def create_mail_account(dict_account: dict):
    return yagmail.SMTP(dict_account["username"], dict_account["pwd"])

def calculate_size(sizes: list[int]):
    little = sizes[0]
    larger = sizes[1]
    counter = 1
    while larger > 1024**counter:
        counter+=1
    sizess = ["byes","KB","MB","GB","TB"]
    return [f"{larger/1024**3}{sizess[2]}",f"{(larger-little)/1024**counter}{sizess[counter-1]}",f"{little/1024**3}{sizess[2]}"]
def create_mail_to_send(
        old_count: int, new_count: int, time_finished: str, updated: int, dict_account: dict, updated_chains: dict, sizes: list[int]):
    mail = create_mail_account(dict_account)
    calc = calculate_size(sizes)
    content = f"""
    Today report:
    the old number of documents in the database was {old_count}. Now you've got {new_count-old_count} new items. At total, {new_count}, and {updated} have benn updated.
    the update has been finished at {time_finished}. The old size was {calc[-1]}, the new size is {calc[0]}. Today have been added {calc[1]}.
    """
    for chain in updated_chains:
        content += f"{chain}: {updated_chains[chain]}"
    mail.send(os.environ['SEND_TO_MAIL'].split(':'),
              f"Mongo Daily Report {datetime.date.today()}", content,
              ["/var/log/azureserver.out.log", "/var/log/azureserver.error.log"])

def sqlme(raw: str, res: str):
    subprocess.Popen("/Scripts/sqlite")
    
def zip_res_and_all(dict_account: dict):
    mail = create_mail_account(dict_account)
    timeing = [f"/home/saret/{datetime.datetime.now().strftime('%Y-%m-%d--%H,%M')}-all.7z",
               f"/home/saret/raw.{datetime.datetime.now().strftime('%Y-%m-%d--%H,%M')}.7z",
               f"/home/saret/{datetime.datetime.now().strftime('%Y-%m-%d--%H,%M')}.7z"]
    send_me_raw_files_rar(dict_account, timeing[1])
    send_me_results_rar(dict_account, timeing[2])
    d = glob("/home/saret/*.7z")
    sqlme(d[0],d[1])
    subprocess.Popen(
        ['sh', '-c',
         f"7zr a {timeing[0]} -mx=9 -m0=lzma /home/saret/*.7z"]).wait()
    mail.send(os.environ['SEND_TO_MAIL'].split(':'),
              f'raw files in rar, {datetime.date.today()}', attachments=timeing[0])
    move_res_and_raw()


def send_me_results_rar(dict_account: dict, timeing: str):
    subprocess.Popen(
        ['sh', '-c',
         f"7zr a {timeing} -mx=9 -m0=lzma /home/saret/Gits/ss/results/"]).wait()


def send_me_raw_files_rar(dict_account: dict, timeing: str):
    subprocess.Popen(
        ['sh', '-c',
         f"7zr a {timeing} -mx=9 -m0=lzma /home/saret/Gits/ss/raw_files/"]).wait()


def send_me_logs(dict_account: dict):
    mail = create_mail_account(dict_account)
    subprocess.Popen("/Scripts/MakeReport", shell=True).wait()
    mail.send(os.environ['SEND_TO_MAIL'].split(':'), f"data send {datetime.date.today()}", attachments=f"/home/saret/report{datetime.date.today()}.txt")
    os.remove(f"/home/saret/report{datetime.date.today()}.txt")

def move_res_and_raw():
    for file in glob("results/*")+glob('raw_files/*'):
        if not os.path.exists("/home/saret/old_ss_data"):
            os.mkdir("/home/saret/old_ss_data")
            os.mkdir("/home/saret/old_ss_data/raw_files")
            os.mkdir("/home/saret/old_ss_data/results")
        shutil.move(file, f"/home/saret/old_ss_data/{file}")
