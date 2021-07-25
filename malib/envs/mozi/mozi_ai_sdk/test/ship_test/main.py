#!/usr/bin/python
# -*- coding: utf-8 -*-
######################################
# File name : main_uav_anti_tank.py
# Create date : 2019-10-20 19:37
# Modified date : 2020-04-22 23:32
# Author : liuzy
# Describe : not set
# Email : lzygzh@126.com
######################################
import numpy as np
import gc
from malib.envs.mozi.mozi_ai_sdk.test.ship_test.env import Environment
from malib.envs.mozi.mozi_ai_sdk.test.ship_test import etc
from malib.envs.mozi.mozi_ai_sdk.test.ship_test.ship_agent import CAgent


def run(env):
    #start()函数不动
    env.start()
    while True:
        
        env.reset()
        i=0
        while True:
            scenario = env.step()
            scenario.mozi_server.run_simulate()
            print(i,env.blueside.iTotalScore)
            i+=1






def main():
    env = Environment(etc.SERVER_IP, etc.SERVER_PORT, etc.PLATFORM, etc.SCENARIO_NAME, etc.SIMULATE_COMPRESSION, etc.DURATION_INTERVAL,
                      etc.SYNCHRONOUS)
    run(env)



main()
