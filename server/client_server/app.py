import json
import os.path
import subprocess
from logging.config import dictConfig

import requests
from flask import Flask, request

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

HOST_ULR = ""
HOST_IP = None
HOST_PORT = None


@app.route('/')
def hello_world():  # put application's code here
    return 'Docker Server is running'


def start_docker_container(task_name):
    """
    start docker container to collect data
    :param task_name: dir_name@file_name
    :return: True for success else false
    """
    script_path = './scripts/docker.sh'
    dir_data = task_name.split("@")  # 0 = dir_name, 1 = filename
    dir_name = dir_data[1].split("_")[0]
    file_name = dir_data[1].replace("\n", "")
    # start containter
    app.logger.info(f'Starting container {task_name}')
    cmds = ['bash', script_path, dir_name, file_name, task_name.replace("\n", ""), HOST_IP, HOST_PORT]
    app.logger.info(cmds)
    process = subprocess.Popen(cmds,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    for line in process.stdout.readlines():
        app.logger.info(f'{task_name}=>{line}')
    for line in process.stderr.readlines():
        app.logger.info(f'{task_name}=>{line}')
    # wait to finish
    # process.wait()
    if process.returncode is not None:
        app.logger.error(f'Container {task_name} error')
        return False
    return True


def store_task_to_file(task_name: str, task_data):
    """
    save task data to file
    :param task_name: dir_name@file_name
    :param task_data: array of cid
    :return: True for save sucess else flase
    """
    dir_prefix = './data'
    dir_data = task_name.split("@")  # 0 = dir_name, 1 = filename
    dir_name = dir_data[1].split("_")[0]
    file_name = dir_data[1].replace("\n", "")
    # make dir
    dir_path = os.path.join(dir_prefix, dir_name)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, file_name)
    app.logger.info(f'Saving task {task_name} to {file_path}')
    # save file
    try:
        with open(file_path, 'w') as fout:
            for cid in task_data:
                fout.write(cid + '\n')
        return True
    except Exception as e:
        app.logger.error(e)
        return False


@app.route('/startTask', methods=['POST'])
def start_task():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = request.json
        task_name = data['task_name']
        task_data = data['task_data']
        # parse task path
        app.logger.info(f'Received Task {task_name}\n{task_data}')
        # save to file
        if store_task_to_file(task_name, task_data) is False:
            return {}, 404
        # start task script
        if start_docker_container(task_name) is False:
            return {}, 404
        r_data = {"status": "Success"}
        return r_data, 200
    else:
        return {"status": "Error"}, 500


@app.before_first_request
def load_server_config():
    """
    load server info from config file
    config = {
        "host" : ip,
        "port" : port
    }
    :return:
    """
    with open('./server/client_server/config/server_config.json', 'r') as fin:
        data = json.load(fin)
        global HOST_ULR
        global HOST_IP
        global HOST_PORT
        HOST_ULR = f"http://{data['host']}:{data['port']}"
        HOST_IP = str(data['host'])
        HOST_PORT = str(data['port'])
        app.logger.info(f"Loaded {HOST_IP}:{HOST_PORT}")


if __name__ == '__main__':
    print(app.before_first_request_funcs)
    app.run()
