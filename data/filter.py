import json


def main():
    with open('all_files.json', 'r') as fin:
        all_files = json.load(fin)

    with open('random_sample_files_cid.txt', 'r') as fin:
        selected_file_size = []
        for line in fin.readlines():
            line = line.replace("\n", "")
            size = float(all_files[line]['size'] / (1024 * 1024))
            if size > 200:
                print(line)
            selected_file_size.append(size)     # MB?
    selected_file_size.sort(reverse=True)
    print(selected_file_size)


if __name__ == '__main__':
    main()
