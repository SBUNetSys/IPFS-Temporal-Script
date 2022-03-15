#!/bin/bash
mkdir -p data
mkdir -p collected_data
source /home/ax/opt/anaconda3/etc/profile.d/conda.sh
conda activate py3
export FLASK_APP=./server/client_server/app.py
flask run -p 8888
