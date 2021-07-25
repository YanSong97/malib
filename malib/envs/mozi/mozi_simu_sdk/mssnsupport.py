#!/usr/bin/python
# -*- coding: utf-8 -*-
#####################################
# File name :mssnsupport.py
# Create date : 2020-3-18
# Modified date : 2020-3-18
# Author : xy
# Describe : not set
# Email : yang_31296@163.com

#from ..entitys.activeunit import CActiveUnit
from .activeunit import CActiveUnit
#from ..entitys.mission import CMission
from .mission import CMission
#from ..entitys import args
from . import args

class CSupportMission(CMission):
    '''
    支援任务
    '''

    def __init__(self, strGuid, mozi_server, situation):
        super().__init__(strGuid,mozi_server,situation)

    def set_maintain_unit_number(self, support_maintain_count):
        """
        阵位上每类平台保持几个
        :param support_maintain_count: int, 保持阵位的数量
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = 'ScenEdit_SetMission("' + self.side_name + '","' + self.strName + '",{SupportMaintainUN=' + str(
                support_maintain_count) + '})'
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_one_time_only(self, isoneTimeOnly):
        """
        仅一次
        :param isoneTimeOnly: bool, 是否仅一次
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = 'ScenEdit_SetMission("' + self.side_name + '","' + self.strName + '", {oneTimeOnly=' + str(
                isoneTimeOnly).lower() + '})'
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_emcon_usage(self, is_active_EMCON):
        """
        仅在阵位上打开电磁辐射
        :param is_active_EMCON: bool, True:打开, False:不打开
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = 'ScenEdit_SetMission("' + self.side_name + '","' + self.strName + '", {activeEMCON =' + str(
                is_active_EMCON).lower() + '})'
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_loop_type(self, is_loop_type):
        """
        导航类型
        :param is_loop_type: bool, True-仅一次；False-连续循环
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = 'ScenEdit_SetMission("' + self.side_name + '","' + self.strName + '", {loopType =' + str(
                is_loop_type).lower() + '})'
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_flight_size(self, enum_flightSize):
        """
        编队规模
        :param enum_flightSize: FlightSize, 编队规模
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = 'ScenEdit_SetMission("' + self.side_name + '","' + self.strName + '",{flightSize=' + str(
                enum_flightSize.value) + '})'
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_flight_size_check(self, sideName, MissionName, useFlightSize):
        """
        是否飞机数低于编队规模不允许起飞
        :param useFlightSize: bool, True:是
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = 'ScenEdit_SetMission("' + sideName + '","' + MissionName + '", {useFlightSize =' + str(
                useFlightSize).lower() + '})'
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_throttle_transit(self, enum_throttle_item):
        """
        功能：设置任务的出航油门
        参数：enum_throttle_item: {Throttle.item: 油门列举类中的具体列举项。}
        返回：'不在设值范围内，请重新设置。' 或 'lua执行成功' 或 '脚本执行出错'
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/10/20
        """
        return super().set_throttle('transitThrottleAircraft', enum_throttle_item)

    def set_throttle_station(self, enum_throttle_item):
        """
        功能：设置任务的阵位油门
        参数：enum_throttle_item: {Throttle.item: 油门列举类中的具体列举项。}
        返回：'不在设值范围内，请重新设置。' 或 'lua执行成功' 或 '脚本执行出错'
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/10/20
        """
        return super().set_throttle('stationThrottleAircraft', enum_throttle_item)

    def set_transit_altitude(self, altitude):
        """
        功能：设置任务的出航高度
        参数：altitude-高度: {float: 单位：米，最多6位字符，例：99999.9， 888888}
        返回：'lua执行成功' 或 '脚本执行出错'
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/10/20
        """
        return super().set_altitude('transitAltitudeAircraft', altitude)

    def set_station_altitude(self, altitude):
        """
        功能：设置任务的阵位高度
        参数：altitude-高度: {float: 单位：米，最多6位字符，例：99999.9， 888888}
        返回：'lua执行成功' 或 '脚本执行出错'
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/10/20
        """
        return super().set_altitude('stationAltitudeAircraft', altitude)



