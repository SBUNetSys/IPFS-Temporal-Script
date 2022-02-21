import json
import random


def main():
    with open('all_files.json', 'r') as fin:
        all_files = json.load(fin)
    all_cids = all_files.keys()
    # randomly pick 500 cids
    random_cids = random.sample(all_cids, 500)
    with open('random_sample_files_cid.txt', 'w') as fout:
        fout.write('\n'.join(random_cids))


if __name__ == '__main__':
    main()
