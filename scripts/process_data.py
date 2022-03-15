import argparse
import json
import os
import shutil
import datetime

import requests


def main(dir_prefix, host, port):
    now = datetime.datetime.now()
    # check if collecting period ends or not
    with open(os.path.join(dir_prefix, 'collect_period.txt'), 'r') as fin:
        target_day = fin.readline().replace("\n", "")
    current_day = now.strftime("%Y-%m-%d")
    if current_day > target_day:
        exit(0)
    # load all today's data to global pool
    # 2022-03-08_all_cid
    file_name = f'{current_day}_all_cid.txt'
    file_path = os.path.join(dir_prefix, current_day, file_name)
    new_cids = []
    with open(file_path, 'r') as fin:
        for line in fin.readlines():
            new_cids.append(line.replace("\n", ""))
    # CAP to 1000
    if len(new_cids) > 1000:
        new_cids = new_cids[:1000]
    # load global dataset
    global_db_path = os.path.join(dir_prefix, 'all_data.txt')
    global_db = []
    try:
        with open(global_db_path, 'r') as fin:
            for line in fin.readlines():
                global_db.append(line.replace("\n", ""))
    except FileNotFoundError as e:
        print("No global DB found, first time running?")
    # update global db
    with open(global_db_path, 'a') as fout:
        for cid in new_cids:
            fout.write(cid + '\n')
    # store as today's run
    daily_file_path = os.path.join(dir_prefix, current_day, f'{current_day}_run_cids.txt')
    shutil.copy(global_db_path, daily_file_path)

    # send to server
    # case of free machine
    url = f'http://{host}:{port}/addTask'
    data = {
        'folder_name': current_day,
        'file_name': f'{current_day}_run_cids.txt'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    res = requests.post(url, data=json.dumps(data), headers=headers)
    if res.status_code != 200:
        print("Error on sending request")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', type=str, help='central server ip', required=True)
    parser.add_argument('-p', '--port', type=str, help='central host port', required=True)
    args = parser.parse_args()

    prefix = './collected_data'
    main(prefix, args.server, args.port)
