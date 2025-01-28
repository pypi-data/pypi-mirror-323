# -*- coding: utf-8 -*-
# Quasarr
# Project by https://github.com/rix1337

import os
import time
from urllib import parse

from quasarr.providers.myjd_api import Myjdapi, TokenExpiredException, RequestTimeoutException, MYJDException, Jddevice
from quasarr.storage.config import Config
from quasarr.storage.sqlite_database import DataBase

values = {}
lock = None


def set_state(manager_dict, manager_lock):
    global values
    global lock
    values = manager_dict
    lock = manager_lock


def update(key, value):
    global values
    global lock
    lock.acquire()
    try:
        values[key] = value
    finally:
        lock.release()


def set_connection_info(internal_address, external_address, port):
    if internal_address.count(":") < 2:
        internal_address = f"{internal_address}:{port}"
    update("internal_address", internal_address)
    update("external_address", external_address)
    update("port", port)


def set_files(config_path):
    update("configfile", os.path.join(config_path, "Quasarr.ini"))
    update("dbfile", os.path.join(config_path, "Quasarr.db"))


def generate_api_key():
    api_key = os.urandom(32).hex()
    Config('API').save("key", api_key)
    print(f'API key replaced with: "{api_key}!"')
    return api_key


def extract_valid_hostname(url, shorthand):
    # Check if both characters from the shorthand appear in the url
    try:
        if '://' not in url:
            url = 'http://' + url
        result = parse.urlparse(url)
        domain = result.netloc

        # Check if both characters in the shorthand are in the domain
        if all(char in domain for char in shorthand):
            print(f'"{domain}" matches both characters from "{shorthand}". Continuing...')
            return domain
        else:
            print(f'Invalid domain "{domain}": Does not contain both characters from shorthand "{shorthand}"')
            return None
    except Exception as e:
        print(f"Error parsing URL {url}: {e}")
        return None


def connect_to_jd(jd, user, password, device_name):
    try:
        jd.connect(user, password)
        jd.update_devices()
        device = jd.get_device(device_name)
    except (TokenExpiredException, RequestTimeoutException, MYJDException) as e:
        print("Error connecting to JDownloader: " + str(e))
        return False
    if not device or not isinstance(device, (type, Jddevice)):
        return False
    else:
        device.downloadcontroller.get_current_state()  # request forces direct_connection info update
        connection_info = device.check_direct_connection()
        if connection_info["status"]:
            print(f'Direct connection to JDownloader established: "{connection_info['ip']}"')
        else:
            print("Could not establish direct connection to JDownloader.")
        update("device", device)
        return True


def set_device(user, password, device):
    jd = Myjdapi()
    jd.set_app_key('Quasarr')
    return connect_to_jd(jd, user, password, device)


def set_device_from_config():
    config = Config('JDownloader')
    user = str(config.get('user'))
    password = str(config.get('password'))
    device = str(config.get('device'))

    update("device", device)

    if user and password and device:
        jd = Myjdapi()
        jd.set_app_key('Quasarr')
        return connect_to_jd(jd, user, password, device)
    return False


def check_device(device):
    try:
        valid = isinstance(device,
                           (type, Jddevice)) and device.downloadcontroller.get_current_state()
    except (AttributeError, KeyError, TokenExpiredException, RequestTimeoutException, MYJDException):
        valid = False
    return valid


def connect_device():
    config = Config('JDownloader')
    user = str(config.get('user'))
    password = str(config.get('password'))
    device = str(config.get('device'))

    jd = Myjdapi()
    jd.set_app_key('Quasarr')

    if user and password and device:
        try:
            jd.connect(user, password)
            jd.update_devices()
            device = jd.get_device(device)
        except (TokenExpiredException, RequestTimeoutException, MYJDException):
            pass

    if check_device(device):
        update("device", device)
        return True
    else:
        return False


def get_device():
    attempts = 0

    while True:
        try:
            if check_device(values["device"]):
                break
        except (AttributeError, KeyError, TokenExpiredException, RequestTimeoutException, MYJDException):
            pass
        attempts += 1

        update("device", False)

        if attempts % 10 == 0:
            print(
                f"WARNING: {attempts} consecutive JDownloader connection errors. Please check your credentials!")
        time.sleep(3)

        if connect_device():
            break

    return values["device"]


def get_devices(user, password):
    jd = Myjdapi()
    jd.set_app_key('Quasarr')
    try:
        jd.connect(user, password)
        jd.update_devices()
        devices = jd.list_devices()
        return devices
    except (TokenExpiredException, RequestTimeoutException, MYJDException) as e:
        print("Error connecting to JDownloader: " + str(e))
        return []


def get_db(table):
    return DataBase(table)


def convert_to_mb(item):
    size = float(item['size'])
    unit = item['sizeunit'].upper()

    if unit == 'B':
        size_b = size
    elif unit == 'KB':
        size_b = size * 1024
    elif unit == 'MB':
        size_b = size * 1024 * 1024
    elif unit == 'GB':
        size_b = size * 1024 * 1024 * 1024
    elif unit == 'TB':
        size_b = size * 1024 * 1024 * 1024 * 1024
    else:
        raise ValueError(f"Unsupported size unit {item['name']} {item['size']} {item['sizeunit']}")

    size_mb = size_b / (1024 * 1024)
    return int(size_mb)


def debug():
    if os.getenv('DEBUG'):
        return True
    return False


def download_package(links, title, password, package_id):
    device = get_device()
    device.linkgrabber.add_links(params=[
        {
            "autostart": False,
            "links": str(links).replace(" ", ""),
            "packageName": title,
            "extractPassword": password,
            "priority": "DEFAULT",
            "downloadPassword": password,
            "destinationFolder": "Quasarr/<jd:packagename>",
            "comment": package_id,
            "overwritePackagizerRules": True
        }
    ])

    package_uuids = []
    link_ids = []

    for _ in range(30):
        try:
            collecting = device.linkgrabber.is_collecting()
            if not collecting:
                links = device.linkgrabber.query_links()
                for link in links:
                    if link["comment"] == package_id:
                        link_id = link["uuid"]
                        if link_id not in link_ids:
                            link_ids.append(link_id)
                        package_uuid = link["packageUUID"]
                        if package_uuid not in package_uuids:
                            package_uuids.append(package_uuid)

                if link_ids and package_uuids:
                    break

        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(1)

    if not link_ids and not package_uuids:
        print(f"No links or packages found within 30 seconds! Adding {title} package failed.")
        return False

    time.sleep(3)
    links = device.linkgrabber.query_links()
    for link in links:
        if link["comment"] == package_id:
            link_id = link["uuid"]
            if link_id not in link_ids:
                link_ids.append(link_id)
            package_uuid = link["packageUUID"]
            if package_uuid not in package_uuids:
                package_uuids.append(package_uuid)

    try:
        device.linkgrabber.move_to_downloadlist(link_ids, package_uuids)
    except Exception as e:
        print(f"Failed to start download for {title}: {e}")
        return False
    return True
