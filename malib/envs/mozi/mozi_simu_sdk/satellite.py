# -*- coding:utf-8 -*-
##########################################################################################################
# File name : satellite.py
# Create date : 2020-1-8
# Modified date : 2020-1-8
# All rights reserved:北京华戍防务技术有限公司
# Author:xy
##########################################################################################################
#from mozi_simu_sdk.activeunit import CActiveUnit
from .activeunit import CActiveUnit


class CSatellite(CActiveUnit):
    """
    卫星类
    """

    def __init__(self, strGuid, mozi_server, situation):
        super().__init__(strGuid, mozi_server, situation)
        # 卫星类别
        self.m_SatelliteCategory = None
        # 卫星航迹线 航迹是根据卫星算法得出的
        self.m_TracksPoints = None
        self.ClassName = 'CSatellite'

    def set_radar_shutdown(self, trunoff):
        """
        类别：编辑使用函数
        设置雷达开关机
        trunoff 开关机 true 开机  false 关机
        """
        return super().set_radar_shutdown(trunoff)

    def set_sonar_shutdown(self, trunoff):
        """
        类别：编辑使用函数
        设置声纳开关机
        trunoff 开关机 true 开机  false 关机
        """
        return super().set_sonar_shutdown(trunoff)

    def set_oecm_shutdown(self, trunoff):
        """
        类别：编辑使用函数
        设置干扰开关机
        trunoff 开关机 true 开机  false 关机
        """
        return super().set_oecm_shutdown(trunoff)
