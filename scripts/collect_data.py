import argparse
import datetime
import json
import os.path
import pathlib

import requests
from dateutil.parser import parse


def get_page_data(page_number):
    """
    abstract json data from query
    :param page_number: page number for api to call
    :return: data of the page in json
    """
    headers = {
        'accept': 'application/json',
    }
    url = f'https://api.ipfs-search.com/v1/search?q=last-seen%3A%3Enow-1M&type=file&page={page_number}'
    r = requests.get(url, headers=headers)
    return r.json()


def extract_data(page_data):
    """
    extract file data from page json
    :param page_data: page data in json
    :return: extracted data in dic
    """
    extracted_data = {}
    # loop through all cid in this page
    for file in page_data['hits']:
        cid = file['hash']
        first_seen = file['first-seen']
        score = file['score']
        file_type = file['mimetype']
        file_size = file['size']
        file_data = {'first-seen': first_seen, 'score': score, 'size': file_size, 'mimetype': file_type}
        extracted_data[cid] = file_data

    return extracted_data


def main(dir_prefix, collect_duration,):
    if collect_duration != 0:
        # TODO  auto find refresh period
        exit(0)
    else:
        now = datetime.datetime.now()
        # check if collecting period ends or not
        with open(os.path.join(dir_prefix, 'collect_period.txt'), 'r') as fin:
            target_day = fin.readline().replace("\n", "")
        current_day = now.strftime("%Y-%m-%d")
        if current_day > target_day:
            exit(0)

        # check previous refresh time
        prev_fresh_path = os.path.join(dir_prefix, 'prev_refresh.txt')
        with open(prev_fresh_path, 'r') as fin:
            prev_refresh = int(fin.readline().replace("\n", ""))
        next_refresh = prev_refresh + 9
        if next_refresh >= 24:
            next_refresh = next_refresh - 24

        # if time is not on refresh period we exit
        if now.hour != next_refresh:
            exit(0)

        # collecting data
        initial_data = get_page_data(page_number=0)
        total_page_number = initial_data['page_count']
        all_files = {}
        all_files.update(extract_data(initial_data))
        # due to ipfs-search api limit, only allowed 100 paging
        total_page_number = 100
        # start page number 1
        page_number = 1
        while page_number <= total_page_number:
            page_data = get_page_data(page_number)
            page_number += 1
            all_files.update(extract_data(page_data))
        # save data
        folder_name = now.strftime("%Y-%m-%d")
        file_name = f'{now.strftime("%Y-%m-%d-%H")}.json'
        folder_path = os.path.join(dir_prefix, folder_name)
        # create dir if not exist
        os.makedirs(folder_path, exist_ok=True)
        # save record
        file_path = os.path.join(dir_prefix, folder_name, file_name)
        with open(file_path, 'w') as fout:
            json.dump(all_files, fout)
        # update previous refresh
        prev_fresh_path = os.path.join(dir_prefix, 'prev_refresh.txt')
        with open(prev_fresh_path, 'w') as fout:
            fout.write(str(now.hour))
        # load daily global fresh file
        global_path = os.path.join(dir_prefix, folder_name, f'{folder_name}_all_cid.txt')
        all_daily_fresh_file = pathlib.Path(global_path)
        all_daily_cids = []
        if all_daily_fresh_file.is_file():
            # case we have global files
            with open(all_daily_fresh_file, 'r') as fin:
                for line in fin:
                    all_daily_cids.append(line.replace("\n", ""))
        # filter and store fresh file
        fresh_file_cids = []
        for key, value in all_files.items():
            first_seen_date = parse(value['first-seen'])
            first_seen_str = first_seen_date.strftime("%Y-%m-%d")
            if first_seen_str == folder_name and key not in all_daily_cids:
                # case of true fresh file
                fresh_file_cids.append(key)
        file_name = f'{now.strftime("%Y-%m-%d-%H")}_cid.txt'
        path = os.path.join(dir_prefix, folder_name, file_name)
        # store file
        with open(path, 'w') as fout:
            for cid in fresh_file_cids:
                fout.write(cid + '\n')
        # update all daily fresh file cid
        with open(all_daily_fresh_file, 'a') as fout:
            for cid in fresh_file_cids:
                fout.write(cid + '\n')


if __name__ == '__main__':
    # start parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--new', type=int, help="if specified new collecting, value represents collecting period "
                                                      "(days)")
    args = parser.parse_args()
    if args.new:
        duration = args.new
        if duration < 1:
            print("Error, duration cannot be less than 1 days")
            exit(1)
    else:
        duration = 0
    prefix = './collected_data'
    main(prefix, duration)
