#!/usr/bin/python
# -*- coding: utf-8 -*-
#####################################
# File name :mssncargo.py
# Create date : 2020-3-18
# Modified date : 2020-3-18
# Author : xy
# Describe : not set
# All rights reserved:北京华戍防务技术有限公司
# Email : yang_31296@163.com
#from ..entitys.mission import CMission
from .mission import CMission


class CCargoMission(CMission):
    """
    投送任务
    """
    def __init__(self, strGuid, mozi_server, situation):  # changed by aie
        super().__init__(strGuid, mozi_server, situation)
        # 母舰平台
        self.m_Motherships = ''
        # 要卸载的货物
        self.m_MountsToUnload = ''
