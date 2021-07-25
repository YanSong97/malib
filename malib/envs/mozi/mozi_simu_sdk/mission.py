# -*- coding:utf-8 -*-
##########################################################################################################
# File name : mission.py
# Create date : 2020-1-8
# Modified date : 2020-1-8
# All rights reserved:北京华戍防务技术有限公司
# Author:xy
##########################################################################################################
#from mozi_simu_sdk.commonfunction import get_lua_table2json, get_lua_mission_parser
from malib.envs.mozi.mozi_simu_sdk.commonfunction import get_lua_table2json, get_lua_mission_parser
#from MoZiAI_SDK.core.entitys import args
from malib.envs.mozi.mozi_simu_sdk import args
import re


class CMission:
    """任务"""

    def __init__(self, strGuid, mozi_server, situation):
        # GUID
        self.strGuid = strGuid
        # 仿真服务类MoziServer实例
        self.mozi_server = mozi_server
        # 态势
        self.situation = situation
        # 类名
        self.ClassName = ""
        # 名称
        self.strName = ''
        # 推演方
        self.m_Side = ''
        # 推演方名称
        self.side_name = ""
        # 任务类别
        self.m_Category = 0
        # 任务类型
        self.m_MissionClass = 0
        # 任务状态
        self.m_MissionStatus = 0
        # 飞机设置-编队规模
        self.m_FlightSize = 0
        # 空中加油任务设置-任务执行设置 -加油机遵循受油机的飞行计划是否选中
        self.bTankerFollowsReceivers = False
        # 任务描述
        self.strDescription = ""
        # 空中加油任务设置-任务规划设置 加油机没到位的情况下启动任务
        self.bLaunchMissionWithoutTankersInPlace = False
        # 水面舰艇/潜艇设置-水面舰艇/潜艇树低于编队规模要求,不能出击(根据基地编组)
        self.bUseGroupSizeHardLimit = False
        # 已分配单元的集合
        self.m_AssignedUnits = ""
        # 空中加油任务设置-任务执行设置 - 每架加油机允许加油队列最大长度
        self.strMaxReceiversInQueuePerTanker_Airborne = ""
        # 水面舰艇/潜艇设置-编队规模
        self.m_GroupSize = 0
        # 空中加油-  点击配置  显示如下两个选项： 返回选中的值1.使用优良充足的最近加油机加油2.使用已分配特定任务的加油机加油
        self.m_TankerUsage = 0
        # 条令
        self.m_Doctrine = ""
        # 空中加油任务设置-任务规划设置 阵位上加油机最小数量
        self.strTankerMinNumber_Station = ""
        # 未分配单元的集合
        self.m_UnassignedUnits = ""
        # 单元航线
        self.m_strSideWayGUID = ""
        # 空中加油任务设置-任务执行设置 -受油机寻找加油机的时机条件
        self.strFuelQtyToStartLookingForTanker_Airborne = ""
        # 空中加油选项是否与上级保持一致
        self.bUseRefuel = False
        # 飞机数低于编队规模要求,不能起飞
        self.bUseFlightSizeHardLimit = False
        # 飞机设置-空中加油
        self.m_UseRefuel = 0
        # 行动预案
        self.bUseActionPlan = False
        # 空中加油任务设置-任务规划设置 留空的加油机最小数量
        self.strTankerMinNumber_Airborne = ""
        # 空中加油任务设置-任务规划设置1.需要加油机的最小数量
        self.strTankerMinNumber_Total = ""
        self.m_TransitThrottle_Aircraft = ''  # 飞机航速与高度-出航油门
        self.m_StationThrottle_Aircraft = ''  # 飞机航速与高度-阵位油门
        self.strTransitAltitude_Aircraft = ''  # 飞机航速与高度-出航高度
        self.strStationAltitude_Aircraft = ''  # 飞机航速与高度-阵位高度
        self.m_TransitThrottle_Submarine = ''  # 潜艇航速与潜深-出航油门
        self.m_StationThrottle_Submarine = ''  # 潜艇航速与潜深-阵位油门
        self.strTransitDepth_Submarine = ''  # 潜艇航速与潜深-出航潜深
        self.strStationDepth_Submarine = ''  # 潜艇航速与潜深-阵位潜深
        self.m_TransitThrottle_Ship = ''  # 水面舰艇航速-出航油门
        self.m_StationThrottle_Ship = ''  # 水面舰艇航速-阵位油门

    def get_assigned_units(self):
        """
        获取已分配任务的单元
        :return:
        """
        guid_list = self.m_AssignedUnits.split('@')
        units = {}
        for guid in guid_list:
            units[guid] = self.situation.get_obj_by_guid(guid)
        return units

    def get_unassigned_units(self):
        """
        获取未分配任务的单元
        :return:
        """
        guid_list = self.m_UnassignedUnits.split('@')
        units = {}
        for guid in guid_list:
            units[guid] = self.situation.get_obj_by_guid(guid)
        return units

    def get_doctrine(self):
        """
        获取条令
        by aie
        """
        if self.m_Doctrine in self.situation.doctrine_dic:
            doctrine = self.situation.doctrine_dic[self.m_Doctrine]
            doctrine.category = 'Mission'  # 需求来源：20200331-2/2:Xy
            return doctrine
        return None

    def get_weapon_dbids(self):
        """
        功能：获取编组内所有武器的dbid
        参数：无
        返回：编组内所有武器的dbid组成的列表
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/7/20
        """
        side = self.situation.side_dic[self.m_Side]
        unit_guids = self.m_AssignedUnits.split('@')
        # 考虑了编组作为执行单位时的情况。
        groups = self.situation.side_dic[self.m_Side].groups
        assigned_groups = {k: v for k, v in groups.items() if k in unit_guids}
        lst = []
        if len(assigned_groups) > 0:
            gg = [k.get_weapon_dbids() for k in assigned_groups.values()]
            for n in gg:
                lst.extend(n)
        assigned_units_guids = [k for k in unit_guids if k not in groups.keys()]
        weapon_record = []
        lst02 = []
        if len(assigned_units_guids) > 0:
            weapon_record.extend(
                list({v.m_UnitWeapons: k for k, v in side.submarines.items() if k in assigned_units_guids}))
            weapon_record.extend(
                list({v.m_UnitWeapons: k for k, v in side.ships.items() if k in assigned_units_guids}))
            weapon_record.extend(
                list({v.m_UnitWeapons: k for k, v in side.facilities.items() if k in assigned_units_guids}))
            weapon_record.extend(
                list({v.m_UnitWeapons: k for k, v in side.aircrafts.items() if k in assigned_units_guids}))
            weapon_record.extend(
                list({v.m_UnitWeapons: k for k, v in side.satellites.items() if k in assigned_units_guids}))
            lst01 = re.findall(r"\$[0-9]*", '@'.join(weapon_record))
            lst02 = [k.replace('$', '') for k in lst01]
        lst.extend(lst02)
        return lst

    def get_weapon_infos(self):
        """
        功能：获取编组内所有武器的名称及dbid
        参数：无
        返回：编组内所有武器的名称及dbid组成的列表
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/7/20
        """
        side = self.situation.side_dic[self.m_Side]
        unit_guids = self.m_AssignedUnits.split('@')
        # 考虑了编组作为执行单位时的情况。
        groups = self.situation.side_dic[self.m_Side].groups
        assigned_groups = {k: v for k, v in groups.items() if k in unit_guids}
        lst = []
        if len(assigned_groups) > 0:
            gg = [k.get_weapon_infos() for k in assigned_groups.values()]
            for n in gg:
                lst.extend(n)
        assigned_units_guids = [k for k in unit_guids if k not in groups.keys()]
        weapon_record = []
        lst04 = []
        if len(assigned_units_guids) > 0:
            weapon_record.extend(
                list({v.m_UnitWeapons: k for k, v in side.submarines.items() if k in assigned_units_guids}))
            weapon_record.extend(
                list({v.m_UnitWeapons: k for k, v in side.ships.items() if k in assigned_units_guids}))
            weapon_record.extend(
                list({v.m_UnitWeapons: k for k, v in side.facilities.items() if k in assigned_units_guids}))
            weapon_record.extend(
                list({v.m_UnitWeapons: k for k, v in side.aircrafts.items() if k in assigned_units_guids}))
            weapon_record.extend(
                list({v.m_UnitWeapons: k for k, v in side.satellites.items() if k in assigned_units_guids}))
            lst01 = '@'.join(weapon_record)
            lst02 = lst01.split('@')
            lst03 = [k.split('$') for k in lst02]
            lst04 = [x for x in lst03 if x != ['']]
        lst.extend(lst04)
        return lst

    def get_side(self):
        """
        获取方
        by aie
        """
        return self.situation.side_dic[self.m_Side]

    def is_active(self, is_active=''):
        """
        是否启用任务
        :param is_active: bool, 是否启用
        :return:
        """
        str_set = str(is_active).lower()
        lua = "print(ScenEdit_SetMission('%s','%s',{isactive='%s'}))" % (self.side_name, self.strName, str_set)
        return self.mozi_server.send_and_recv(lua)

    def set_start_time(self, start_time):
        """
        设置、删除任务开始时间
        :param start_time: 开始时间
        :return:
        """
        cmd_str = "ScenEdit_SetMission('" + self.side_name + "','" + self.strName + "',{starttime='" + start_time + "'})"
        return self.mozi_server.send_and_recv(cmd_str)

    def set_end_time(self, endTime):
        """
        设置任务：删除任务结束时间
        :param endTime:
        :return:
        """
        cmd_str = "ScenEdit_SetMission('" + self.side_name + "','" + self.strName + "',{endtime='" + endTime + "'})"
        return self.mozi_server.send_and_recv(cmd_str)

    def set_one_third_rule(self,side_name, missionName, is_one_third):
        """
        设置任务是否遵循1/3原则
        :param is_one_third: bool, True:遵守，False:不遵守
        :return:
        修订：aie
        时间：4/10/20
        """
        cmd = 'ScenEdit_SetMission("%s","%s", {oneThirdRule=%s})' % \
              (side_name, missionName, str(is_one_third).lower())
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def switch_radar(self, switch_on):
        """
        设置任务雷达是否打开
        :param switch_on: bool, 雷达打开或者静默，True:打开
        :return:
        """
        if switch_on:
            set_str = 'Radar=Active'
        else:
            set_str = 'Radar=Passive'
        return self.situation.side_dic[self.m_Side].set_ecom_status("Mission", self.strName, set_str)  #amended by aie

    def assign_unit(self, unitID, is_escort=False):
        """
        设置任务：将实体分配到任务中来
        :param unitID: str, 实体
        :param is_escort: bool,  是否护航任务
        :return: 
        """
        cmd_str = "ScenEdit_AssignUnitToMission('" + unitID + "', '" + self.strName + "', " + str(
            is_escort).lower() + ")"
        return self.mozi_server.send_and_recv(cmd_str)

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

    def get_information(self):
        """
        返回任务详细信息, 巡逻，打击或支援任务共用 :return:dict, 例子:{"isactive":true,"SISH":false,"endtime":"2019/8/8 91609",
        "subtype":"AAW Patrol","starttime":"2019/8/26 91609"}
        """
        return get_lua_table2json() + (get_lua_mission_parser() % (self.side_name, self.strName))

    def is_area_valid(self):
        """
        验证区域角点连线是否存在交叉现象
        返回值：验证结果状态标识（'Yes'：正常，'No'：异常）
        """
        lua_scrpt = "print(Hs_IsValidArea('%s'))" % self.strName
        return self.mozi_server.send_and_recv(lua_scrpt)

    def unassign_unit(self, activeunit_name_guid):
        """
        单元从任务中移除
        activeunit_name_guid 字符串。单元名称或 GUID
        ScenEdit_UnAssignUnitFromMission ('飞机#2','空巡')
        """
        lua_scrpt = "print(ScenEdit_UnAssignUnitFromMission('%s','%s'))" % (activeunit_name_guid, self.strName)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def export_mission(self):
        """
        作者：赵俊义
        日期：2020-3-10
        函数功能：将相应的任务导出到 Defaults 文件夹中
        函数类型：推演函数
        :return:
        """
        return self.mozi_server.send_and_recv("ScenEdit_ExportMission('{}','{}')".format(self.m_Side, self.strGuid))

    def set_throttle(self, throttle_type, enum_throttle_item):
        """
        功能：设置任务油门类型及值
        参数：throttle_type-油门类型: {str: 'transitThrottleAircraft'-出航油门,
                                  'stationThrottleAircraft'-阵位油门,
                                  'attackThrottleAircraft'-攻击油门}
             enum_throttle_item-油门列举类中的具体列举项: {Throttle.item}
        返回：'不在设值范围内，请重新设置。' 或 'lua执行成功' 或 '脚本执行出错'
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/10/20
        """
        throttle_dict = args.enum_to_dict(args.Throttle)
        if enum_throttle_item.value not in throttle_dict:
            return '不在设值范围内，请重新设置。'
        cmd = "ScenEdit_SetMission('%s','%s', {%s = '%s'}) "%(self.m_Side, self.strGuid, throttle_type,
                                                                                  enum_throttle_item.value)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def set_altitude(self, altitude_type, altitude):
        """
        功能：设置任务高度类型及值
        参数：altitude_type-高度类型: {str: 'transitAltitudeAircraft'-出航高度,
                                         'stationAltitudeAircraft'-阵位高度,
                                         'attackAltitudeAircraft'-攻击高度}
             altitude-高度值: {float: 单位：米，最多6位字符，例：99999.9， 888888}
        返回：'lua执行成功' 或 '脚本执行出错'
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/10/20
        """
        cmd = "ScenEdit_SetMission('%s','%s', {%s=%s})"%(self.m_Side, self.strGuid, altitude_type, altitude)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)