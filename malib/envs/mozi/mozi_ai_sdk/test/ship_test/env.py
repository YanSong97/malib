#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from malib.envs.mozi.mozi_simu_sdk.mozi_server import MoziServer
from malib.envs.mozi.mozi_simu_sdk.scenario import CScenario
from malib.envs.mozi.mozi_ai_sdk.test.ship_test.ship_agent import CAgent
from malib.envs.mozi.mozi_utils.geo import*
import time
from malib.envs.mozi.mozi_simu_sdk.args import *


class Environment():
    '''
    环境
    '''
    def __init__(self, IP, AIPort, platform, scenario_name, simulate_compression, duration_interval, synchronous):
        self.server_ip = IP
        self.aiPort = AIPort
        self.platform = platform
        self.scenario_name = scenario_name
        self.websocker_conn = None
        self.mozi_server = None
        self.scenario = None
        self.connect_mode = 1
        self.num = 1
        self.simulate_compression = simulate_compression
        self.duration_interval = duration_interval
        self.synchronous = synchronous
        self.agent = CAgent()
    
    def step(self):
        '''
        步长
        主要用途：
        单步决策的方法
        根据环境态势数据改变战场环境
        '''
        self.mozi_server.update_situation(self.scenario)
        self.redside.static_update()
        self.blueside.static_update()
        return self.scenario

    def reset(self):
        '''
        重置函数
        主要用途：
        加载想定，
        '''
        self.create_scenario()
        self.mozi_server.set_simulate_compression(self.simulate_compression)
        self.mozi_server.init_situation(self.scenario)
        self.redside = self.scenario.get_side_by_name('红方')
        self.redside.static_construct()
        self.blueside = self.scenario.get_side_by_name('蓝方')
        self.blueside.static_construct()
        self.mozi_server.set_simulate_compression(4)
        self.mozi_server.run_simulate()

        #为了便于区分，定义了一个新的函数my_prepeo,以实例化的推演方对象作为参数输入，对推演前的任务进行设置
    
        #self.my_prepro(self.blueside)        
        
    def create_scenario(self):
        '''
        建立一个想定对象
        '''
        self.scenario = CScenario(self.mozi_server)

    def connect_mozi_server(self, time_out):
        """
        功能：连接墨子服务器
        参数：
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/28/20
        """
        self.mozi_server = MoziServer(self.server_ip, self.aiPort, self.platform, self.scenario_name,
                                       self.simulate_compression, self.synchronous)
        time.sleep(time_out)

    def start(self):
        '''
        开始函数
        主要用途：
        1.连接服务器端
        2.设置决策时间
        3.设置智能体决策想定是否暂停
        '''
        self.connect_mozi_server(20.0)
        self.mozi_server.set_run_mode(self.synchronous)
        self.mozi_server.set_decision_step_length(self.duration_interval)
