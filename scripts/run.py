import copy
import time
import json
from datetime import datetime

import pycurl
import multiprocessing
import lockfile
import subprocess
import requests
import io
import os

# query = ["rabbit", "google", "cat", "mouse", "dog", "game", "phone", "jojo", "apple", "app", "india"]
query = ["music", "movie", "game", "videogame", "minecraft", "cooking", "stream", "classic muisc", "live concert"]
base = "https://search.d.tube/avalon.contents/_search?&size=10000&q="
# https://search.d.tube/avalon.contents/_search?&size=100&q=tags:music

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}
waittime = 5 * 60
tmpvideofile = "/tmp/tmpvidfile"


class Video:
    def __init__(self, cid, dur, ts, category):
        self.cid = cid
        self.dur = dur
        # upload time
        self.ts = ts
        date_obj = datetime.fromtimestamp(ts)
        self.upload_date = str(date_obj.date())
        # query type which we got
        self.category = category
        self.local_data = {}
        self.public_data = {}

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def setwtime(t):
    lock = lockfile.LockFile("timekeeper.lock")
    with lock:
        with open("timekeeper.txt", "w") as f:
            f.write(str(t))


def getwtime():
    lock = lockfile.LockFile("timekeeper.lock")
    with lock:
        with open("timekeeper.txt", "r") as f:
            return float(f.read())


def cidsearch():
    """
    :param prev: previous cid list
    :return: stats for daily new video and its cid
    """
    queries = {"trending": "https://avalon.d.tube/trending",
               "new": "https://avalon.d.tube/new",
               "hot": "https://avalon.d.tube/hot"}
    stats = {"trending": {"total_video": 0, "youtube": 0, "skynet": 0, "ipfs": 0},
             "new": {"total_video": 0, "youtube": 0, "skynet": 0, "ipfs": 0},
             "hot": {"total_video": 0, "youtube": 0, "skynet": 0, "ipfs": 0}}
    ans = {"trending": [],
           "new": [],
           "hot": []}
    for i in queries:
        response = requests.get(queries[i], headers=headers)
        data = json.loads(response.content)
        # [{json:{files:{}}}]
        for vid in data:
            try:
                timestamp = int(vid["ts"]) / 1000
                json_obj = vid["json"]
                duration = int(json_obj["dur"])
                # get file count
                if "youtube" in json_obj["files"].keys():
                    stats[i]["youtube"] += 1
                    # success cast vid and add total count
                    stats[i]["total_video"] += 1
                elif "sia" in json_obj["files"].keys():
                    stats[i]["skynet"] += 1
                    # success cast vid and add total count
                    stats[i]["total_video"] += 1
                elif "ipfs" in json_obj["files"].keys():
                    try:
                        cid = json_obj["files"]["ipfs"]["vid"]["src"]
                        new_vid = Video(cid, duration, timestamp, i)
                        ans[i].append(new_vid)
                        stats[i]["ipfs"] += 1
                        # success cast vid and add total count
                        stats[i]["total_video"] += 1
                    except Exception as e:
                        print(f'Error IPFS {json_obj["files"]["ipfs"]}')
                        # print("hi")
                        # # fall back to old json format
                        # cid = json_obj["files"]["ipfs"]["videohash"]
                        # new_vid = Video(cid, duration, timestamp, i)
                        # ans[i].append(new_vid)
                else:
                    print(json_obj["files"].keys())
                    continue

            except Exception as e:
                continue
    return stats, ans


buf = io.BytesIO()


def writer(x):
    l = len(x)
    #    print ("writer called", l)
    global buf
    buf.write(x)
    if l > 0:
        setwtime(time.time())
    return None


def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)


def bw(vid: Video, gateway, return_dic):
    try:
        url = gateway + vid.cid
        #    url = "http://gateway.ipfs.io/ipfs/" + cid
        setwtime(time.time())
        print(url)
        # global buf
        # buf = io.BytesIO()

        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.VERBOSE, False)
        c.setopt(c.WRITEFUNCTION, writer)
        c.setopt(c.FOLLOWLOCATION, 1)
        c.perform()
        # with open(tmpvideofile, "wb") as out:
        #     out.write(buf.getvalue())

        m = {}
        m["total-time"] = c.getinfo(pycurl.TOTAL_TIME)
        m["namelookup-time"] = c.getinfo(pycurl.NAMELOOKUP_TIME)
        m["connect-time"] = c.getinfo(pycurl.CONNECT_TIME)
        m["pretransfer-time"] = c.getinfo(pycurl.PRETRANSFER_TIME)
        m["redirect-time"] = c.getinfo(pycurl.REDIRECT_TIME)
        m["starttransfer-time"] = c.getinfo(pycurl.STARTTRANSFER_TIME)
        m["length"] = c.getinfo(c.CONTENT_LENGTH_DOWNLOAD)

        # if os.path.getsize(tmpvideofile) != 0:
        #     length = get_length(tmpvideofile)
        # else:
        #     length = 0
        stall_rate = ((m["total-time"] - m["starttransfer-time"]) - vid.dur) / vid.dur
        if stall_rate < 0:
            stall_rate = 0

        data = {
            "overhead": m["starttransfer-time"],
            "download_time": (m["total-time"] - m["starttransfer-time"]),
            "file_size": m["length"],
            "video_length": vid.dur,
            "stall_rate": stall_rate,
            "bandwidth": m["length"] / (m["total-time"] - m["starttransfer-time"])
        }

        if "local" in gateway:
            return_dic['local'] = data
        else:
            return_dic['public'] = data

        print(vid.cid,
              "overhead:" + str(m["starttransfer-time"]),
              "download_time:" + str((m["total-time"] - m["starttransfer-time"])),
              "file_size:" + str(m["length"]),
              "video_length:" + str(vid.dur),
              "stall_rate:" + str(stall_rate),
              "bw(bits/s):" + str(m["length"] / (m["total-time"] - m["starttransfer-time"])))
    except Exception as e:
        print(e)
        return_dic['error'] = True
        return


def temp_progress(video, date):
    with open(f'{date}_temp.json', 'a') as fout:
        json.dump(video.__dict__, fout)


def run_video_test(vid):
    # start record data
    default_gw = "http://localhost:8080/ipfs/"
    dtube_gw = "https://player.d.tube/ipfs/"
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    x = multiprocessing.Process(target=bw, args=(vid, default_gw, return_dict))
    setwtime(2147483647)
    x.start()
    return_dict['error'] = False
    time_out = False
    while x.is_alive():
        time.sleep(1)
        if time.time() - getwtime() > waittime:
            x.terminate()
            print("local_gw", vid.cid, "timeout")
            time_out = True
            vid.local_data = None
            break
    x.join()
    x.terminate()
    if not time_out:
        # check if error
        if return_dict['error']:
            vid.local_data = None
        else:
            vid.local_data = return_dict['local']
    # public gateway
    time_out = False
    return_dict['error'] = False
    y = multiprocessing.Process(target=bw, args=(vid, dtube_gw, return_dict))
    setwtime(2147483647)
    y.start()
    while y.is_alive():
        time.sleep(1)
        if time.time() - getwtime() > waittime:
            x.terminate()
            print("public_gw", vid.cid, "timeout")
            vid.public_data = None
            time_out = True
            break
    y.join()
    y.terminate()
    if not time_out:
        if return_dict['error']:
            vid.public_data = None
        else:
            vid.public_data = return_dict['public']
    # print(vid.__dict__)
    # print(return_dict)


if __name__ == "__main__":
    # prev video
    # { cid, q_type, upload_date}
    # daily file
    # { cid, q_type, gw , data ... } // success
    # { cid, q_type, gw , null} // fail
    # daily summary of
    # youtube vid count
    # skynet vid count
    # ipfs vid count
    # gateway vs local success count

    # load all vid summary
    try:
        with open("all_vid_summary.json", "r") as f:
            all_vid_summary = json.load(f)
    except Exception as e:
        # {"cid":{"type":[], "upload_date":[],}}
        all_vid_summary = {}
    today = datetime.now().date()
    # get daily cid
    daily_summary, new_videos = cidsearch()
    # save daily summary
    with open(f'{today}-summary.json', 'w') as fout:
        json.dump(daily_summary, fout)
    # test_vid = {'trending': [new_videos['trending'][0]]}
    # new_videos = test_vid

    # remove duplicate cid and run daily vid
    daily_cids = []
    daily_reachable_videos = []  # array of reachable videos
    daily_reachable_videos_cid = []
    for tag in new_videos:
        for vid in new_videos[tag]:
            if vid.cid not in daily_cids:
                daily_cids.append(vid.cid)
                run_video_test(vid)
                temp_progress(vid, today)
                if vid.local_data is not None:
                    daily_reachable_videos.append(vid)
                    daily_reachable_videos_cid.append(vid.cid)

    # recreate all prev vid object
    daily_video_data = copy.deepcopy(daily_reachable_videos)
    for cid in all_vid_summary:
        # avoid duplicate run
        if cid not in daily_reachable_videos_cid:
            dur = all_vid_summary[cid]["dur"]
            ts = all_vid_summary[cid]["ts"]
            category = all_vid_summary[cid]["category"]
            vid = Video(cid, dur, ts, category)
            # run test
            run_video_test(vid)
            temp_progress(vid, today)
            # store daily information
            daily_video_data.append(vid)
            # store daily reachable info
            if vid.local_data is not None:
                daily_reachable_videos.append(vid)
                daily_reachable_videos_cid.append(vid.cid)
    # add all new reachable video into video database
    for vid in daily_reachable_videos:
        vid: Video
        # add new entry record
        if vid.cid not in all_vid_summary:
            all_vid_summary[vid.cid] = {
                "category": vid.category,
                "ts": vid.ts,
                "dur": vid.dur,
            }
    # save all_vid_summary
    with open('all_vid_summary.json', 'w') as fout:
        json.dump(all_vid_summary, fout)
    # save today's record
    with open(f'{today}.json', 'w') as fout:
        json.dump([ob.__dict__ for ob in daily_video_data], fout)
    # save cid to folder
    daily_cid = daily_reachable_videos_cid
    with open(f'{today}/{today}_cid.txt', 'w') as fout:
        for cid in daily_cid:
            fout.write(cid + '\n')
