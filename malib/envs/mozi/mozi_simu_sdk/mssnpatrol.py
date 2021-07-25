#!/usr/bin/python
# -*- coding: utf-8 -*-
#####################################
# File name :mssnpatrol.py
# Create date : 2020-3-18
# Modified date : 2020-3-18
# Author : xy
# Describe : not set
# Email : yang_31296@163.com

# from ..entitys.activeunit import CActiveUnit
from .activeunit import CActiveUnit
# from ..entitys.mission import CMission
from .mission import CMission
# from ..entitys import args
from . import args


class CPatrolMission(CMission):
    """
    巡逻任务
    """

    def __init__(self, strGuid, mozi_server, situation):
        super().__init__(strGuid, mozi_server, situation)

    def __get_zone_str(self, point_list):
        """
        功能：构造区域点集形成的字符串
        参数：point_list-参考点列表: {list: 例:[(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)]，其中纬度值在前，经度值在后，(40, 39.0)中,
                                        latitude = 40, longitude = 39.0
                                        或者[(40, 39.0, 'RP1'), (41, 39.0, 'RP2'), (41, 40.0, 'RP3'), (40, 40.0, 'RP4')]
                                        或者['RP1', 'RP2'，'RP3'，'RP4']，传入参考点名称要求提前创建好参考点
        返回：区域点集形成的字符串
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/10/20
        """
        zone_str = ''
        if type(point_list[0]) == str:
            zone_str = "Zone={'%s'}" % ("','".join(point_list))
        elif type(point_list[0]) == tuple:
            if type(point_list[0][-1]) == str:
                t = [k[-1] for k in point_list]
                zone_str = "Zone={'%s'}" % ("','".join(t))
            else:
                t = ['latitude=%s,longitude=%s' % (k[0], k[1]) for k in point_list]
                zone_str = "Zone={{%s}}" % ("},{".join(t))
        return zone_str

    def add_prosecution_zone(self, point_list):
        """
        增加巡逻任务的警戒区
        :param mission_name: str, 任务名
        :param point_list: list, list, 参考点列表,例:[(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)]，其中纬度值在前，经度值在后，(40, 39.0)中,latitude = 40, longitude = 39.0
                            或者[(40, 39.0, 'RP1'), (41, 39.0, 'RP2'), (41, 40.0, 'RP3'), (40, 40.0, 'RP4')]
                            或者['RP1', 'RP2'，'RP3'，'RP4']，传入参考点名称要求提前创建好参考点
        :return:
        """
        cmd = "ReturnObj(ScenEdit_SetMission('{}','{}',{}))".format(self.m_Side, self.strName,
                                                                    '{' + self.__get_zone_str(point_list).replace(
                                                                        'Zone', 'prosecutionZone') + '}')
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_mission(self, detailed):
        """
        设置任务属性
        side 方
        missionName :任务名称或者guid
        detailed 任务细节
        修订：aie
        时间：4/10/20
        """
        cmd = "ReturnObj(ScenEdit_SetMission('{}','{}',{}))".format(self.m_Side, self.strName, detailed)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_maintain_unit_number(self, unit_number):
        """
        巡逻任务阵位上每类平台保存作战单元数量
        :param unit_number: int, 阵位上每类平台保存单元数量
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = 'ScenEdit_SetMission("%s","%s",{PatrolMaintainUnitNumber=%d})' % (
            self.m_Side, self.strName, unit_number)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_one_third_rule(self,side_name, missionName, is_one_third):
        """
        设置任务是否遵循1/3原则
        :param is_one_third: bool, True:遵守，False:不遵守
        :return:
        修订：aie
        时间：4/10/20
        """
        return super().set_one_third_rule(side_name, missionName, is_one_third)

    def set_opa_check(self, sideName, missionName, ischeckOPA):
        """
        设置任务是否对巡逻区外的探测目标进行分析
        :param ischeckOPA: bool, True:分析，False:不分析
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + str(sideName) + "', '" + str(
            missionName) + "', { checkOPA = " + str(ischeckOPA).lower() + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_emcon_usage(self, isactiveEMCON):
        """
        设置任务是否仅在巡逻/警戒区内打开电磁辐射
        :param isactiveEMCON: bool, True:打开 False:不打开
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + str(self.m_Side) + "', '" + str(
            self.strGuid) + "', { activeEMCON = " + str(isactiveEMCON).lower() + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_wwr_check(self, sideName, missionName, ischeckWWR):
        """
        设置任务是否对武器射程内探测目标进行分析
        :param ischeckWWR: bool, True遵守 或 False不遵守
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + str(sideName) + "', '" + str(
            missionName) + "', { checkWWR = " + str(ischeckWWR).lower() + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_flight_size(self, sideName, missionName, enum_flight_size):
        """
        设置任务编队规模
        :param enum_flight_size:FlightSize, 编队规模
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + str(sideName) + "', '" + str(
            missionName) + "', { flightSize = " + str(enum_flight_size) + "})"
            # self.strGuid) + "', { flightSize = " + str(enum_flight_size.value) + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_flight_size_check(self, sideName, missionName, useFlightSize):
        """
        是否飞机数低于编队规模不允许起飞
        :param useFlightSize: bool, True:是
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = 'ScenEdit_SetMission("' + sideName + '","' + missionName + '", {''useFlightSize =' + str(
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

    def set_throttle_attack(self, enum_throttle_item):
        """
        功能：设置任务的攻击油门
        参数：enum_throttle_item: {Throttle.item: 油门列举类中的具体列举项。}
        返回：'不在设值范围内，请重新设置。' 或 'lua执行成功' 或 '脚本执行出错'
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/10/20
        """
        return super().set_throttle('attackThrottleAircraft', enum_throttle_item)

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

    def set_attack_altitude(self, altitude):
        """
        功能：设置任务的攻击高度
        参数：altitude-高度: {float: 单位：米，最多6位字符，例：99999.9， 888888}
        返回：'lua执行成功' 或 '脚本执行出错'
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/10/20
        """
        return super().set_altitude('attackAltitudeAircraft', altitude)

    def set_attack_distance(self, distance):
        """
        设置任务的攻击距离
        :param distance: float, 攻击距离，单位：公里
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + str(self.m_Side) + "','" + str(
            self.strGuid) + "', { attackDistanceAircraft = " + str(distance) + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_patrol_sonobuoys_cover(self, fSonobuoysCover, dropSonobuoysType):
        """
        函数功能：为反潜巡逻任务设置声呐浮标在巡逻区域内的覆盖密度和深浅类型。
        函数类型：推演函数
        :param fSonobuoysCover: 声呐与声呐之间的距离，按照投放声呐的探测圈范围
        :param dropSonobuoysType:声呐的深浅
        :return:
        """
        return self.mozi_server.send_and_recv(
            "Hs_SetPatrolSonobuoysCover('{}','{}','{}')".format(self.strGuid, fSonobuoysCover, dropSonobuoysType))