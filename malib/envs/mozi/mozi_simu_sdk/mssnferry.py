#!/usr/bin/python
# -*- coding: utf-8 -*-
#####################################
# File name :mssnferry.py
# Create date : 2020-3-18
# Modified date : 2020-3-18
# Author : xy
# Describe : not set
# Email : yang_31296@163.com

#from ..entitys.activeunit import CActiveUnit
from .activeunit import CActiveUnit
#from ..entitys.mission import CMission
from .mission import CMission


class CFerryMission(CMission):
    '''
    转场任务
    '''

    def __init__(self, strGuid, mozi_server, situation):  # changed by aie
        super().__init__(strGuid, mozi_server, situation)
        # 转场任务行为
        self.m_FerryMissionBehavior = ''
        # 转场飞机数量
        self.m_FlightSize = ''
