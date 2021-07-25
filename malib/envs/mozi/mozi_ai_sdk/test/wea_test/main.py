#!/usr/bin/python
# -*- coding: utf-8 -*-
######################################
# File name : main_uav_anti_tank.py
# Create date : 2019-10-20 19:37
# Modified date : 2020-01-09 19:22
# Author : liuzy
# Describe : not set
# Email : lzygzh@126.com
######################################

import numpy as np
import gc
from malib.envs.mozi.mozi_ai_sdk.test.wea_test.env import Environment
from malib.envs.mozi.mozi_ai_sdk.test.wea_test import etc
from malib.envs.mozi.mozi_ai_sdk.test.wea_test.wea_agent import CAgent

def run(env):
    env.start()
    while True:
        agent = CAgent()
        env.reset()
        while True:
            scenario = env.step()
            agent.test(scenario)
            if etc.SYNCHRONOUS == True:
                env.mozi_server.run_simulate()






def main():
    env = Environment(etc.SERVER_IP, etc.SERVER_PORT, etc.PLATFORM, etc.SCENARIO_NAME, etc.simulate_compression, etc.SYNCHRONOUS)
    run(env)



main()
