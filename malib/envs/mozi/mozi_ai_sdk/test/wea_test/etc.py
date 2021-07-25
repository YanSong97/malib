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

APP_ABSPATH = os.path.dirname(__file__)
USE_CUDA = False
DEVICE = torch.device("cuda" if USE_CUDA else "cpu")

#######################
SERVER_IP = "127.0.0.1"
SERVER_PORT = "6260"
PLATFORM = 'linux'
SCENARIO_NAME = "wea_test"  # 距离近，有任务
simulate_compression = 3
SYNCHRONOUS = True
DURATION_INTERVAL = 30
TARGET_RADIUS = 3700.0
CONTROL_NOISE = True
#######################
MAX_EPISODES = 5000
MAX_BUFFER = 1000000
MAX_STEPS = 30
#######################

#######################
TMP_PATH = "%s/%s/tmp" % (APP_ABSPATH, SCENARIO_NAME)
OUTPUT_PATH = "%s/%s/output" % (APP_ABSPATH, SCENARIO_NAME)

CMD_LUA = "%s/cmd_lua" % TMP_PATH
PATH_CSV = "%s/path_csv" % OUTPUT_PATH
MODELS_PATH = "%s/Models/" % OUTPUT_PATH
EPOCH_FILE = "%s/epochs.txt" % (OUTPUT_PATH)
#######################

TRANS_DATA = True
