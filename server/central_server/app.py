import http
import json
import logging
import os.path
import requests

from flask import Flask, request, after_this_request
from logging.config import dictConfig
from flask import jsonify

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

TASK_QUEUE = []  # global task queue (stores file path)
MACHINES = []  # global machine list (stores Machine objs)
DIR = './collected_data'


class Machine:
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port
        self.running = False
        self.task = None


@app.route('/')
def home():  # put application's code here
    return 'Server is running !'


@app.route('/machineStatus', methods=['GET'])
def get_machine_status():
    data = json.dumps([ob.__dict__ for ob in MACHINES])
    return data


@app.route('/taskQueue', methods=['GET'])
def get_task_queue():
    data = json.dumps(TASK_QUEUE)
    return data


# @app.route('/getTask/<string:task>', methods=['GET'])
def get_task(task):
    task = os.path.join(DIR, task.replace("@", '/'))
    cids = []
    try:
        with open(task) as fin:
            for line in fin:
                cids.append(line.replace("\n", ""))
        # r_data = {'data': cids}
        # return r_data, 200
        if len(cids) > 0:
            return cids
        else:
            app.logger.info(f'Task {task} has empty file')
            return None
    except Exception as e:
        app.logger.info(e)
        app.logger.info(f'Failed loading task {task}')
        # return {}, 404
        return None


def distribute_task(task):
    """
    This function assign task to machines that is not running in MACHINES
    :param task: task to run
    :return: True for assign success false for fail
    """
    for m in MACHINES:
        m: Machine
        if m.running:
            continue
        # case of free machine
        url = f'http://{m.host}:{m.port}/startTask'
        logging.info(f'Sending Task {task}')
        task_data = get_task(task)
        if task_data is None:
            return False
        data = {
            'task_name': task,
            'task_data': task_data}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        res = requests.post(url, data=json.dumps(data), headers=headers)
        if res.status_code != 200:
            app.logger.error(f'Error on assigning task {task}')
            return False
        m.running = True
        m.task = task
        app.logger.info(f'Task {task} started in machine {m.name}@{m.host}:{m.port}')
        return True
    app.logger.warning(f'MACHINES ARE FULL')
    return False


@app.after_request
def pop_task_queue(response):
    TASK_QUEUE[:] = [task for task in TASK_QUEUE if not distribute_task(task)]
    return response


@app.route('/addTask', methods=['POST'])
def add_task():
    """
    signal for new gathered ipfs-data
    input json format =
    {
        folder : "date",
        file_name : "file_name"
    }
    :return:
    """
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json_data = request.json
        # parse task path
        date = json_data['date']
        folder_name = json_data['folder']
        file_name = json_data['file_name']
        task = f'{folder_name}@{file_name}'
        # append to task queue
        TASK_QUEUE.append(task)
        app.logger.info(f'Added Task {task} date = {date}')
        data = {"status": "Success"}
        return data, 200
    else:
        return {"status": "Error"}, 500


def update_machines(task):
    """
    free running machine for given task
    :param task: task name
    :return: True for success else false
    """
    for m in MACHINES:
        if m.task == task and m.running is True:
            m.running = False
            m.task = None
            app.logger.info(f'Updated machine {m.name} => Free')
            return True
    app.logger.info(f'Failed matching task {task} to machine')
    return False


@app.route('/taskDone', methods=['GET'])
def task_done():
    task = request.args.get('task_name', type=str)
    app.logger.info(f'Received task {task} done')
    if update_machines(task) is not True:
        return {}, 404
    return {}, 200


@app.before_first_request
def load_docker_containers():
    """
    load docker container from file
    config_json =
    {
        "name" : {
            "host" : ip,
            "port" : port,
        }
    }
    :return: None
    """
    with open('./server/central_server/config/machine-config.json', 'r') as fin:
        global MACHINES
        data = json.load(fin)
        for m_name, value in data.items():
            machine = Machine(m_name, value['host'], value['port'])
            MACHINES.append(machine)
            app.logger.info(f'Added Machine {machine.__dict__}')


if __name__ == '__main__':
    print(app.before_first_request_funcs)
    app.run()
