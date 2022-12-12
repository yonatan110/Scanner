import logging
import threading
import os

from dataclasses import dataclass
from datetime import datetime
from pymongo import MongoClient


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


cluster = MongoClient("""Mongo Cluster""")
db = cluster["IP_activity"]
collection = db["IP_activity"]


IP_ACTIVITY_LIST = []
ONLINE_LIST = []
OFFLINE_LIST = []


@dataclass
class IPActivity:
    ip_address: str
    first_seen: str = None
    last_seen: str = None


def set_mongo_collection(ip):
    IP_address = {"ip": ip, "first_seen": None, "last_seen": None}
    collection.insert_one(IP_address)


def current_time():
    now_time = datetime.utcnow()
    return now_time


def create_ip_list(ip_list):
    ip_start = '192.168.0.'
    for i in range(254):
        ip = (ip_start + str(i+1))
        address = IPActivity(ip_address=ip)
        ip_list.append(address)


def scan_all_ip():
    for ip_activity in IP_ACTIVITY_LIST:
        response = os.system(f"ping -n 1 -w 1 {ip_activity.ip_address}")
        if response == 0:
            set_online(ip_activity)
            set_first_seen(ip_activity)
            set_last_seen(ip_activity)
        else:
            set_offline(ip_activity)


def set_online(ip):
    ONLINE_LIST.append(ip)


def set_offline(ip):
    OFFLINE_LIST.append(ip)


def set_first_seen(ip):
    first_seen = collection.find_one({"ip": ip.ip_address})["first_seen"]
    if not first_seen:
        collection.update_one({"ip": ip.ip_address}, {"$set": {"first_seen": current_time().replace(microsecond=0)}},)
    ip.first_seen = first_seen


def set_last_seen(ip):
    ip.last_seen = current_time()
    collection.update_one({"ip": ip.ip_address}, {"$set": {"last_seen": current_time().replace(microsecond=0)}})


def is_still_online():
    while True:
        for ip in ONLINE_LIST:
            response = os.system(f"ping -n 1 -w 2 {ip.ip_address}")
            if response == 0:
                set_last_seen(ip)
            else:
                ONLINE_LIST.remove(ip)
                set_offline(ip)


def is_still_offline():
    while True:
        for ip in OFFLINE_LIST:
            response = os.system(f"ping -n 1 -w 2 {ip.ip_address}")
            if response == 0:
                OFFLINE_LIST.remove(ip)
                set_online(ip)


def status():
    is_online = threading.Thread(target=is_still_online)
    is_online.start()

    is_offline = threading.Thread(target=is_still_offline)
    is_offline.start()


def check_if_all_ip_existed():
    for ip in IP_ACTIVITY_LIST:
        try:
            collection.find_one({"ip": ip.ip_address})['ip']
        except:
            set_mongo_collection(ip.ip_address)


def set_lists():
    create_ip_list(ip_list=IP_ACTIVITY_LIST)
    check_if_all_ip_existed()
    scan_all_ip()


def main():
    set_lists()
    status()


if __name__ == '__main__':
    main()
