import os
import shutil
import datetime


def main(dir_prefix):
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
    daily_file_path = os.path.join(dir_prefix, f'{current_day}_cids.txt')
    shutil.copy(global_db_path, daily_file_path)


if __name__ == '__main__':
    prefix = './collected_data'
    main(prefix)
