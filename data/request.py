import json

import requests


def get_page_data(page_number):
    headers = {
        'accept': 'application/json',
    }
    url = f'https://api.ipfs-search.com/v1/search?q=last-seen%3A%3Enow-1M&type=file&page={page_number}'
    r = requests.get(url, headers=headers)
    return r.json()


def extract_data(page_data):
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


def main():
    initial_data = get_page_data(page_number=0)
    total_page_number = initial_data['page_count']
    all_files = {}
    all_files.update(extract_data(initial_data))
    # due to ipfs-search api limit, only allowed 100 paging
    total_page_number = 100
    # start page number 2
    page_number = 2
    while page_number <= total_page_number:
        page_data = get_page_data(page_number)
        page_number += 1
        all_files.update(extract_data(page_data))
    with open('all_files.json', 'w') as fout:
        json.dump(all_files, fout)


if __name__ == '__main__':
    main()
