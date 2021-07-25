#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from malib.envs.mozi.mozi_simu_sdk.mozi_server import MoziServer


#from mozi_simu_sdk.entitys import args
class Environment():
    '''
    环境
    '''
    def __init__(self, IP, port, platform, scenario_name, compression, synchronous):
        self.server_ip = IP
        self.server_port = port
        self.platform = platform
        self.scenario_name = scenario_name
        self.compression = compression
        self.synchronous = synchronous
        self.mozi_server = None
        self.scenario = None

    def start(self):
        '''
        开始函数
        主要用途：
        1.连接服务端
        2.设置交互模式
        3.设置决策时间步长
        '''
        self.connect_mozi_server()
        self.mozi_server.set_run_mode()
        self.mozi_server.set_decision_step_length(10)

    def connect_mozi_server(self):
        """
        功能：连接墨子服务器
        参数：
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/28/20
        """
        self.mozi_server = MoziServer(self.server_ip, self.server_port, self.platform, self.scenario_name,
                                       self.compression, self.synchronous)

    def reset(self):
        """
        重置函数
        主要用途：加载想定，获取初始态势，启动推演
        """
        """
        加载想定
        """
        self.mozi_server.suspend_simulate()
        self.scenario = self.mozi_server.load_scenario()
        """
        获取初始态势
        """
        self.mozi_server.init_situation(self.scenario)
        self.redside = self.scenario.get_side_by_name('红方')
        self.redside.static_construct()
        self.blueside = self.scenario.get_side_by_name('蓝方')
        self.blueside.static_construct()
        """
        开始推演
        """
        self.mozi_server.run_simulate()
        print(self.scenario.m_Time)

    def step(self):
        """
        功能：决策步函数,单步决策的方法,根据环境态势数据改变战场环境
        参数：无
        返回：想定概要
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/22/20
        """
        """
        获取更新态势
        """
        self.mozi_server.update_situation(self.scenario)
        self.redside.static_update()
        self.blueside.static_update()
        """
        test
        """
        rslt, sub_1 = self.redside.add_submarine('gjy#1', 10, 29.0, 123.0, 40.0)
        rslt, shp_1 = self.redside.add_ship('lsj#1', 24, 29.0, 123.5, 40.0)
        rslt, fac_1 = self.redside.add_facility('aq#1', 2325, 29.0, 120.0, 180)
        rslt, fac_2 = self.redside.add_facility('air_base_#1', 2416, 29.0, 115.0, 180)
        rslt, fac_3 = self.redside.add_facility('aq#2', 2325, 29.0, 123.0, 180)   #can't in water
        rslt, air_1 = self.redside.add_aircarft('gjy#1', 6, 130, 28.0, 123.0, 5000.0, 40.0)
        rslt, sat_1 = self.redside.add_satellite(3,20)
        self.scenario.situation.generate_guid()

        pnts=[None,None,None,None]
        delta_x=[0,1,1,0]
        delta_y=[0,0,1,1]
        for i in range(0,4):
            rslt,pnts[i]=self.redside.add_reference_point('RP-'+str(i),29.1+delta_x[i],129.1+delta_y[i])
        self.pnts=pnts
        self.redside.add_mission_patrol('patrol#1',0,pnts)
        self.redside.add_mission_strike('strike#1',1)
        self.redside.add_mission_support('support#1',pnts)
        self.redside.add_mission_cargo('cargo#1',pnts)
        self.redside.add_mission_ferry('ferry#1','air_base_#1')
        self.redside.add_mission_mining('mining#1',pnts)
        self.redside.add_mission_mine_clearing('mineclrng#1',pnts)
        return self.scenario
