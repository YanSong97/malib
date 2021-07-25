#!/usr/bin/python
# -*- coding: utf-8 -*-
#####################################
# File name : etc_uav_anti_tank.py
# Create date : 2020-01-07 03:28
# Modified date : 2020-01-09 19:31
# Author : DARREN
# Describe : not set
# Email : lzygzh@126.com
#####################################

import torch
import os

app_abspath = os.path.dirname(__file__)
USE_CUDA = False
device = torch.device("cuda" if USE_CUDA else "cpu")

#######################
SERVER_IP = "127.0.0.1"
SERVER_PORT = "6260"
SCENARIO_NAME = "1212.scen"  # 距离近，有任务
simulate_compression = 3
DURATION_INTERVAL = 30
target_radius = 3700.0
control_noise = True
#######################
MAX_EPISODES = 5000
MAX_BUFFER = 1000000
MAX_STEPS = 30
#######################

#######################
TMP_PATH = "%s/%s/tmp" % (app_abspath, SCENARIO_NAME)
OUTPUT_PATH = "%s/%s/output" % (app_abspath, SCENARIO_NAME)

CMD_LUA = "%s/cmd_lua" % TMP_PATH
PATH_CSV = "%s/path_csv" % OUTPUT_PATH
MODELS_PATH = "%s/Models/" % OUTPUT_PATH
EPOCH_FILE = "%s/epochs.txt" % (OUTPUT_PATH)
#######################

TRANS_DATA = True
