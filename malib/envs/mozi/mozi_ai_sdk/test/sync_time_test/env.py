#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from malib.envs.mozi.mozi_simu_sdk.mozi_server import MoziServer
from malib.envs.mozi.mozi_simu_sdk.scenario import CScenario


class Environment():
    '''
    环境
    '''
    def __init__(self, IP, AIPort, platform, scenario_name, simulate_compression, synchronous):
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
        self.synchronous = synchronous
        self.i = 0
        self.time =0.0
    
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
        print( (float(self.scenario.m_Time) - self.time))
        if (int(self.scenario.m_Time) - int(self.time)) != 10:
            print("------------------------------------------"+str(self.i))
            self.i += 1
        self.time = float(self.scenario.m_Time)
        self.mozi_server.run_simulate()
    
    def reset(self):
        '''
        重置函数
        主要用途：
        加载想定，
        '''
        # self.mozi_server.suspend_simulate()
        self.mozi_server.load_scenario()
        self.create_scenario()
        self.mozi_server.init_situation(self.scenario)
        self.redside = self.scenario.get_side_by_name('红方')
        self.redside.static_construct()
        self.blueside = self.scenario.get_side_by_name('蓝方')
        self.blueside.static_construct()
        self.mozi_server.run_simulate()
        self.mozi_server.set_simulate_compression(3)
        self.time = float(self.scenario.m_Time)

    def create_scenario(self):
        '''
        建立一个想定对象
        '''
        self.scenario = CScenario(self.mozi_server)

    def connect_mozi_server(self):
        """
        功能：连接墨子服务器
        参数：
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/28/20
        """
        self.mozi_server = MoziServer(self.server_ip, self.aiPort, self.platform,self.scenario_name,
                                       self.simulate_compression, self.synchronous)

    def start(self):
        '''
        开始函数
        主要用途：
        1.连接服务器端
        2.设置决策时间
        3.设置智能体决策想定是否暂停
        '''
        self.connect_mozi_server()
        self.mozi_server.set_run_mode()
        self.mozi_server.set_decision_step_length(10)
