#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from malib.envs.mozi.mozi_simu_sdk.mozi_server import MoziServer
import time
from malib.envs.mozi.mozi_ai_sdk.test.dppo.envs.common.utils import *
from malib.envs.mozi.mozi_ai_sdk.test.dppo.envs import etc


class Environment:
    """
    环境
    """

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

    def step(self):
        """
        步长
        主要用途：单步决策的方法,根据环境态势数据改变战场环境
        """
        self.situation = self.mozi_server.update_situation(self.scenario)
        self.redside.static_update()
        self.blueside.static_update()
        self.mozi_server.run_grpc_simulate()
        return self.scenario

    def reset(self):
        """
        重置函数
        主要用途：加载想定，
        """
        self.mozi_server.send_and_recv("IsMasterControl")
        self.create_scenario()
        # self.scenario = self.mozi_server.load_scenario()
        self.mozi_server.set_simulate_compression(self.simulate_compression)
        self.mozi_server.init_situation(self.scenario, etc.app_mode)
        self.redside = self.scenario.get_side_by_name('红方')
        self.redside.static_construct()
        self.blueside = self.scenario.get_side_by_name('蓝方')
        self.blueside.static_construct()
        self.mozi_server.run_simulate()

        return self.scenario

    def create_scenario(self):
        """
        建立一个想定对象
        """
        self.scenario = self.mozi_server.load_scenario()

    def connect_mozi_server(self, ip=None, port=None):
        """
        功能：连接墨子服务器
        参数：
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/28/20
        """
        if ip is None and port is None:
            self.mozi_server = MoziServer(etc.SERVER_IP, etc.SERVER_PORT, self.platform, self.scenario_name,
                                          self.simulate_compression, self.synchronous)
        elif ip is not None and port is not None:
            self.mozi_server = MoziServer(ip, str(port), self.platform, self.scenario_name,
                                          self.simulate_compression, self.synchronous)
        time.sleep(4.0)

    def start(self, ip=None, port=None):
        """
        开始函数
        主要用途：
            1.连接服务器端
            2.设置运行模式
            3.设置步长参数
        """
        if ip is None and port is None:
            self.connect_mozi_server()
        elif ip is not None and port is not None:
            self.connect_mozi_server(ip, port)
        else:
            raise ValueError('请正确配置墨子IP与端口！！！')

        self.mozi_server.set_run_mode(self.synchronous)
        self.mozi_server.set_decision_step_length(self.duration_interval)