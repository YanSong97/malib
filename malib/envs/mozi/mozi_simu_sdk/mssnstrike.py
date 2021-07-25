#!/usr/bin/python
# -*- coding: utf-8 -*-
#####################################
# File name :mssnstrike.py
# Create date : 2020-3-18
# Modified date : 2020-3-18
# Author : xy
# Describe : not set
# Email : yang_31296@163.com

# from ..entitys.mission import CMission
from .mission import CMission


class CStrikeMission(CMission):
    """
    打击任务
    """

    def __init__(self, strGuid, mozi_server, situation):
        super().__init__(strGuid, mozi_server, situation)
        self.strName = None
        self.m_Category = None
        self.m_MissionClass = None
        self.m_StartTime = None
        self.m_EndTime = None
        self.m_MissionStatus = None
        self.m_AssignedUnits = None
        self.m_UnassignedUnits = None
        self.m_StrikeType = None
        self.m_MinimumContactStanceToTrigger = None
        self.m_FlightSize = None
        self.m_Bingo = None
        self.m_MinAircraftReq_Strikers = None
        self.iMinResponseRadius = None
        self.iMaxResponseRadius = None
        self.m_RadarBehaviour = None
        self.bUseRefuel = None
        self.m_UseRefuel = None
        self.bUseFlightSizeHardLimit = None
        self.bUseAutoPlanner = None
        self.bOneTimeOnly = None
        self.m_GroupSize = None
        self.bUseGroupSizeHardLimit = None
        self.bPrePlannedOnly = None
        self.m_Doctrine = None
        self.m_SpecificTargets = None
        self.m_strSideWayGUID = None
        self.m_strSideWeaponWayGUID = None
        self.m_EscortFlightSize = None
        self.m_MinAircraftReqEscorts = None
        self.m_MaxAircraftToFlyEscort = None
        self.iEscortResponseRadius = None
        self.m_EscortFlightSizeNo = None
        self.m_MinAircraftReqEscortsNo = None
        self.m_MaxAircraftToFlyEscortNo = None
        self.bUseFlightSizeHardLimitEscort = None
        self.m_EscortGroupSize = None
        self.bUseGroupSizeHardLimitEscort = None
        self.m_Doctrine_Escorts = None
        self.m_strContactWeaponWayGuid = None
        self.iEmptySlots = None

    def get_targets(self):
        """
        功能：返回任务打击目标
        参数：无
        返回：目标单元组成的词典
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/11/20
        """
        target_guids = self.m_SpecificTargets.split('@')
        targets = {k: v for k, v in self.situation.side_dic[self.m_Side].contacts.items() if k in target_guids}
        return targets

    def assign_targets(self, targets):
        """
        分配目标
        :param targets:
        :return:
        """
        trgts = "{'"
        for k in targets.keys():
            trgts = trgts + k + "','"
        trgts = trgts + '}'
        trgts = trgts.replace(",'}", '}')
        cmd = "ScenEdit_AssignUnitAsTarget({}, '{}')".format(trgts, self.strName)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def assign_units(self, units):
        """
        分配单元
        :param units:
        :return:
        """
        results = ''
        for k, v in units.items():
            cmd = "ScenEdit_AssignUnitToMission('{}', '{}')".format(v.strGuid, self.strName)
            self.mozi_server.throw_into_pool(cmd)
            ret = self.mozi_server.send_and_recv(cmd)
            results = results + ',' + ret
        return results

    def add_target(self, target_list):
        """
        设置打击目标
        :param target_list: 目标列表
        :return:'lua执行成功' 或 '脚本执行出错'
        修订：aie
        时间：4/10/20
        """
        strTargetList = "{"
        for i in target_list:
            strTargetList += "'" + i + "',"
        strTargetList = strTargetList[:len(strTargetList) - 1]
        strTargetList += "}"
        cmd = "print(ScenEdit_AssignUnitAsTarget(" + strTargetList + ",'" + self.strName + "'))"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def remove_target(self, target_list):
        """
        设置任务：删除打击任务目标
        :param target_list: 目标列表
        :return:'lua执行成功' 或 '脚本执行出错'
        修订：aie
        时间：4/10/20
        """
        strTargetList = "{"
        for i in target_list:
            strTargetList += "'" + i + "',"
        strTargetList = strTargetList[:len(strTargetList) - 1]
        strTargetList += "}"
        cmd = "print(ScenEdit_RemoveUnitAsTarget(" + strTargetList + ",'" + self.strName + "'))"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_preplan(self, bPreplan):
        """
        设置任务细节：是否仅考虑计划目标（在目标清单）
        :param bPreplan: bool, True:是仅考虑计划目标
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + self.m_Side + "', '" + self.strName + "', {strikePreplan = " + str(
            bPreplan).lower() + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_minimum_trigger(self, enum_strikeMinimumTrigger):
        """
        设置打击任务触发条件
        :param enum_strikeMinimumTrigger:StrikeMinimumTrigger
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + self.m_Side + "', '" + self.strName + "', {StrikeMinimumTrigger = " + str(
            enum_strikeMinimumTrigger.value) + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_strike_max(self, strikeMax):
        """
        设置任务细节：任务允许出动的最大飞行批次
        :param strikeMax:StrikeFlyTimeMax
        :return:修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + self.m_Side + "', '" + self.strName + "', {strikeMax = " + str(
            strikeMax) + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_flight_size(self, sideName, missionName, flightSize):
        """
        设置打击任务编队规模
        :param flightSize:FlightSize, 编队规模
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + sideName + "', '" + missionName + "', {strikeFlightSize = " + str(
            flightSize) + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_min_aircrafts_required(self, minAircraft):
        """
        设置打击任务所需最少飞机数
        :param minAircraft:StrikeMinAircraftReq
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + self.m_Side + "', '" + self.strName + "', {strikeMinAircraftReq = " + str(
            minAircraft) + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_radar_usage(self, radarUsage):
        """
        设置打击任务雷达运用规则
        :param radarUsage:StrikeRadarUasge
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + self.m_Side + "', '" + self.strName + "', { StrikeRadarUsage = " + str(
            radarUsage) + "} )"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_fuel_ammo(self, fuleAmmo):
        """
        设置打击任务燃油弹药规则
        :param fuleAmmo: StrikeFuleAmmo，0，1，2
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + self.m_Side + "', '" + self.strName + "', {StrikeFuleAmmo = " + str(
            fuleAmmo) + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

        # 设置任务细节：最小打击半径

    def set_min_strike_radius(self, minDist):
        """
        设置打击任务最小打击半径
        :param minDist:float, 公里
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + self.m_Side + "', '" + self.strName + "', {StrikeMinDist=" + str(
            minDist) + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_max_strike_radius(self, maxDist):
        """
        设置打击任务最大打击半径
        :param maxDist: float, 公里
        :return:修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + self.m_Side + "', '" + self.strName + "', {StrikeMaxDist=" + str(
            maxDist) + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_flight_size_check(self, side, strName, bUseFlightSize):
        """
        设置打击任务是否飞机数低于编组规模数要求就不能起飞
        :param bUseFlightSize: bool, 是否飞机数低于编组规模数要求就不能起飞
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + side + "', '" + strName + "', {strikeUseFlightSize = " + str(
            bUseFlightSize).lower() + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_auto_planner(self, bUseAutoPlanner):
        """
        设置打击任务是否多扇面攻击（任务AI自动生成）
        :param bUseAutoPlanner: bool, 是否多扇面攻击
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + self.m_Side + "', '" + self.strName + "', {StrikeUseAutoPlanner = " + str(
            bUseAutoPlanner).lower() + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_strike_one_time_only(self, bOneTimeOnly):
        """
        设置打击任务是否仅限一次
        :param bOneTimeOnly: bool, 是否仅一次
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('" + self.m_Side + "', '" + self.strName + "', {strikeOneTimeOnly = " + str(
            bOneTimeOnly) + "})"
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)
