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
    # with open("/home/saret/fuckthispass","r",encoding='utf_8') as file:
    #     acc = file.read().split("\n")
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
    # db = sqlite3.connect("/mnt/MongoDB/helper_save_data.db")
    # datetime_me = re.findall(r'(?:[\d\-\,]+)', raw)[0]
    
    subprocess.Popen("/Scripts/sqlite")
        # ['/usr/bin/sqlite3', '/mnt/MongoDB/helper_save_data.db', f"""'insert into xml(xml, datetime) values (readfile("{raw}"),{datetime_me})'"""], shell=True)
        # f"""/usr/bin/sqlite3 /mnt/MongoDB/helper_save_data.db 'insert into xml(xml, datetime) values (readfile("{raw}"),{datetime_me})'""")
    # db.execute(f"insert into xml(xml, datetime) values({raw},{datetime_me})")
    # datetime_me = re.findall(r'(?:[\d\-\,]+)', res)[0]
    # subprocess.Popen(
        # f"""/usr/bin/sqlite3 /mnt/MongoDB/helper_save_data.db 'insert into xml(xml, datetime) values (readfile("{{{res}}}"),{datetime_me})'""")
    # db.execute(f"insert into xml(xml, datetime) values({res},{datetime_me})")
    # db.commit()
    
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
    # mail = create_mail_account(dict_account)
    subprocess.Popen(
        ['sh', '-c',
         f"7zr a {timeing} -mx=9 -m0=lzma /home/saret/Gits/ss/results/"]).wait()
    # mail.send(['saretbenny@gmail.com','bennyc@savion.huji.ac.il'],'results in rar',attachments=f"/home/saret/{datetime.datetime.now().strftime('%Y-%m-%d--%H.%M')}.7z")


def send_me_raw_files_rar(dict_account: dict, timeing: str):
    subprocess.Popen(
        ['sh', '-c',
         f"7zr a {timeing} -mx=9 -m0=lzma /home/saret/Gits/ss/raw_files/"]).wait()


def send_me_logs(dict_account: dict):
    mail = create_mail_account(dict_account)
    subprocess.Popen("/Scripts/MakeReport", shell=True).wait()
    mail.send(os.environ['SEND_TO_MAIL'].split(':'), f"data send {datetime.date.today()}", attachments=f"/home/saret/report{datetime.date.today()}.txt")
    os.remove(f"/home/saret/report{datetime.date.today()}.txt")
    #subprocess.Popen(["sudo", "rm", "/var/mail/saret"], shell=True).wait()

def move_res_and_raw():
    for file in glob("results/*")+glob('raw_files/*'):
        if not os.path.exists("/home/saret/old_ss_data"):
            os.mkdir("/home/saret/old_ss_data")
            os.mkdir("/home/saret/old_ss_data/raw_files")
            os.mkdir("/home/saret/old_ss_data/results")
        shutil.move(file, f"/home/saret/old_ss_data/{file}")
