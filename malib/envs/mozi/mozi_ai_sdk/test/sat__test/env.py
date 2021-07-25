#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from malib.envs.mozi.mozi_simu_sdk.mozi_server import MoziServer
from malib.envs.mozi.mozi_simu_sdk.scenario import CScenario
import malib.envs.mozi.mozi_utils.pylog as pylog
import time
import json
from websocket import create_connection
class Environment():
    '''
    环境
    '''
    def __init__(self, IP, AIPort, scenario_name, simulate_compression):
        self.server_ip = IP
        self.aiPort = AIPort
        self.scenario_name = scenario_name
        self.websocker_conn = None
        self.mozi_server = None
        self.scenario = None
        self.connect_mode = 1
        self.num = 1
        self.simulate_compression = simulate_compression
    
    def step(self):
        '''
        步长
        主要用途：
        单步决策的方法
        根据环境态势数据改变战场环境
        '''
        time.sleep(1)
        self.mozi_server.suspend_simulate()
        #self.mozi_server.suspend_simulate()
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
        self.mozi_server.suspend_simulate()
        self.mozi_server.load_scenario("linux")
        self.create_scenario()
        self.mozi_server.init_situation(self.scenario)
        self.redside = self.scenario.get_side_by_name('红方')
        self.redside.static_construct()
        self.blueside = self.scenario.get_side_by_name('蓝方')
        self.blueside.static_construct()
        self.mozi_server.run_simulate()
        self.mozi_server.set_simulate_compression(3)

    def create_scenario(self):
        '''
        建立一个想定对象
        '''
        self.scenario = CScenario(self.mozi_server)

    def connect_mozi_server(self, websocket_Ip, websocket_port):
        """
        连接墨子服务器
        param ：
        websocket_server 要连接的服务器的ip
        websocket_port 要连接的服务器的端口
        :return:
        """
        pylog.info("connect_mozi_server")
        if self.connect_mode == 1:
            self.mozi_server = MoziServer(self.server_ip ,self.aiPort,self.scenario_name)
            return True
        # server_address = r"ws://%s:%d/websocket" % ('60.205.207.206', 9998)
        server_address = r"ws://%s:%d/websocket" % (websocket_Ip, websocket_port)
        pylog.info(server_address)
        for i in range(10):
            try:
                self.websocket_connect = create_connection(server_address)
                break
            except:
                pylog.info("can not connect to %s." % server_address)
                time.sleep(2)
                self.websocket_connect = None
        #
        if self.websocket_connect is None:
            pylog.warning("Interrupted, can not connect to %s." % server_address)
            return False
        #
        self.websocket_connect.send("{\"RequestType\":\"StartServer\"}")
        result = self.websocket_connect.recv()
        print("connect server result:%s" % result)
        jsons = json.loads(result)
        self.ai_server = jsons['IP']
        self.ai_port = jsons['AIPort']
        self.mozi_task = MoziServer(self.server_ip ,self.aiPort,self.scenario_name)
        return True

    def start(self):
        '''
        开始函数
        主要用途：
        1.连接服务器端
        2.设置决策时间
        3.设置智能体决策想定是否暂停
        '''
        self.connect_mozi_server(self.server_ip,self.aiPort)
        self.mozi_server.set_run_mode()
        self.mozi_server.set_decision_step_length(10)
