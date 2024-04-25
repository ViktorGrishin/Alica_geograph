import datetime
import json
import os
import schedule


def check_file(file_name):
    if file_name.endswith('.json'):
        last_reading = time.ctime(os.stat(file_name).st_atime)
        if last_reading >= 30:
            os.remove(file_name)
    if os.path.exists(file_name) is False:
        return False


def job():
    files = os.listdir()
    for filename in files:
        check_file(filename)


schedule.every(10).minute.do(job)

while True:
    schedule.run_pending()
