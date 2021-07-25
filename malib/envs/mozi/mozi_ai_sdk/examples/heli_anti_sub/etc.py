#!/usr/bin/python
# -*- coding: utf-8 -*-
#####################################
# File name : etc_uav_anti_tank.py
# Create date : 2020-01-07 03:28
# Modified date : 2020-04-30 10:21
# Author : DARREN
# Describe : not set
# Email : lzygzh@126.com
#####################################


import torch
import os

app_abspath = os.path.dirname(__file__)
#USE_CUDA = torch.cuda.is_available()
USE_CUDA = False
device = torch.device("cuda" if USE_CUDA else "cpu")

#######################
SERVER_IP = "127.0.0.1"
SERVER_PORT = "6060"
SERVER_PLAT = "linux"                 # windows linux
SCENARIO_NAME = "heli_anti_sub.scen"    # 直升机反潜想定
SIMULATE_COMPRESSION = 4                #推演档位
SYNCHRONOUS = True  # True同步, False异步
DURATION_INTERVAL = 90

target_radius = 50000.0
target_name = "PL-636.3“阿尔罗萨级”柴电潜艇"

task_end_point = {"latitude": 43.4874, "longitude": 34.1755}

control_noise = True
#######################

#######################
MAX_EPISODES = 5000
MAX_BUFFER = 1000000
MAX_STEPS = 30
#######################

#######################
TMP_PATH = "%s/%s/tmp" % (app_abspath, SCENARIO_NAME)
OUTPUT_PATH = "%s/%s/output" % (app_abspath, SCENARIO_NAME)

MODELS_PATH = "%s/Models/" % OUTPUT_PATH
#######################

TRANS_DATA = True
