import time
import logging
import sqlite3
from paho.mqtt import publish

UPDATE_INTERVAL = 24 * 60 * 60

# Basic SQLite wrapper
class Database:
    def __init__(self, db_path='db.sqlite3'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def get_device_current_versions(self):
        versions = self.conn.execute('SELECT type,latest_version from djmq_DeviceType')
        return dict(versions)

    def get_device_installed_versions(self):
        versions = self.conn.execute('SELECT id,owner_id,type_id,version from djmq_Device')
        return versions


def run_checker(db, log):
    log.info('Started')
    while True:
        log.info('Checking device versions')
        current_versions = db.get_device_current_versions()
        devices = db.get_device_installed_versions()

        for device_id, user_id, type, version in devices:
            log.debug(f'Checking device {device_id}')
            if version != current_versions[type]:
                payload = type.encode('utf-8') + b'09' + current_versions[type].encode('utf-8')
                log.info(f"Device {device_id} version doesn't match current: {version}")
                publish.single(topic=f"{user_id}/{device_id}/system", payload=payload)
        time.sleep(UPDATE_INTERVAL)


if __name__ == '__main__':
    log = logging.Logger("Checker")
    log.setLevel(logging.DEBUG)
    h = logging.StreamHandler()
    fmt = logging.Formatter('[%(levelname)5s - %(name)7s]  %(message)s')
    h.setFormatter(fmt)
    log.addHandler(h)

    db = Database()
    run_checker(db, log)