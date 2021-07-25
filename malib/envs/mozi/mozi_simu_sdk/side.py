#!/usr/bin/env python3
# -*- coding:utf-8 -*-
##########################################################################################################
# File name : side.py
# Create date : 2020-1-8
# Modified date : 2020-05-08 16:22
# All rights reserved:北京华戍防务技术有限公司
# Author:xy
##########################################################################################################
from abc import ABCMeta, abstractmethod
import re
import logging
from malib.envs.mozi.mozi_simu_sdk.mission import CMission
from malib.envs.mozi.mozi_simu_sdk.activeunit import CActiveUnit
from malib.envs.mozi.mozi_simu_sdk.submarine import CSubmarine
# from ..entitys.ship import CShip
from malib.envs.mozi.mozi_simu_sdk.ship import CShip
# from ..entitys.facility import CFacility
from malib.envs.mozi.mozi_simu_sdk.facility import CFacility
# from ..entitys.aircraft import CAircraft
from malib.envs.mozi.mozi_simu_sdk.aircraft import CAircraft
# from ..entitys.satellite import CSatellite
from malib.envs.mozi.mozi_simu_sdk.satellite import CSatellite
# from ..entitys.facility import CFacility
from malib.envs.mozi.mozi_simu_sdk.facility import CFacility
# from ..entitys.referencepoint import CReferencePoint
from malib.envs.mozi.mozi_simu_sdk.referencepoint import CReferencePoint
# from ..entitys.args import is_in_domain
from malib.envs.mozi.mozi_simu_sdk.args import is_in_domain
# from ..entitys.args import ArgsMission
from malib.envs.mozi.mozi_simu_sdk.args import ArgsMission


########################################################################
class CSide:
    """方"""

    def __init__(self, strGuid, mozi_server, situation):
        # GUID
        self.strGuid = strGuid
        # 仿真服务类MoziServer实例
        self.mozi_server = mozi_server
        # 态势
        self.situation = situation
        self.__zone_index_increment = 1  # 创建封锁区或禁航区的自增命名序号
        self.__reference_point_index_increment = 1  # 创建参考点的自增命名序号
        self.missions = {}  # key:key:mission name, value: Mission instance 
        # 实体
        self.aircrafts = {}  # key:unit guid, value: Unit instance
        self.facilities = {}  # key:unit guid, value: Unit instance
        self.ships = {}
        self.submarines = {}
        self.weapons = {}
        self.satellites = {}
        # 目标
        self.contacts = {}  # key:contact guid, value, contact instance
        # 编组
        self.groups = {}
        # 点
        self.acrionPoints = {}
        # 参考点
        self.referencePoints = {}
        # 条令
        self.doctrine = None
        # 天气
        self.weather = None
        # 消息
        self.logged_messages = self.get_logged_messages()
        self.current_point = 0  # 当前得分
        self.point_record = []  # 得分记录
        self.simulate_time = ""  # 当前推演时间
        self.last_step_missing = {}  # 当前决策步损失的单元（我方），丢掉或击毁的单元（敌方）
        self.last_step_new = {}  # 当前决策步新增的单元（我方），新增的情报单元（敌方）
        self.all_units = {}
        self.activeunit = {}
        self.strName = ""  # 名称
        self.m_PosturesDictionary = []  # 获取针对其它推演方的立场
        self.m_Doctrine = ''  # 作战条令
        self.m_ProficiencyLevel = []
        self.m_AwarenessLevel = ''
        self.m_PosturesDictionary = ''
        self.iTotalScore = 0.0
        self.m_Expenditures = ''  # 战损
        self.m_Losses = ''  # 战耗
        self.iScoringDisaster = 0.0  # 完败阀值
        self.iScoringTriumph = 0.0  # 完胜阀值
        self.bCATC = False  # 自动跟踪非作战单元
        self.bCollectiveResponsibility = False  # 集体反应
        self.bAIOnly = False  # 只由计算机扮演
        self.strBriefing = ''  # 简要
        self.strCloseResult = ''  # 战斗结束后的结果
        self.fCamerAltitude = 0.0  # 中心点相机高度
        self.fCenterLatitude = 0.0  # 地图中心点纬度
        self.fCenterLongitude = 0.0  # 地图中心点经度
        self.strSideColorKey = ''  # 推演方颜色Key
        self.strFriendlyColorKey = ''  # 友方颜色Key
        self.strNeutralColorKey = ''  # 中立方颜色Key
        self.strUnfriendlyColorKey = ''  # 非友方颜色Key
        self.strHostileColorKey = ''  # 敌方颜色Key
        self.iSideStopCount = 0  # 推演方剩余停止次数
        self.m_ScoringLogs = ''
        self.m_ContactList = ''  # 所有的目标
        self.m_WarDamageOtherTotal = ''  # 战损的其它统计，包含但不限于(统计损失单元带来的经济和人员损失)
        self.pointname2location = {}  # 存放已命名的参考点的名称     #aie 20200408

    def static_construct(self):
        """
        将推演方准静态化
        by aie
        """
        self.doctrine = self.get_doctrine()
        self.groups = self.get_groups()
        self.submarines = self.get_submarines()
        self.ships = self.get_ships()
        self.facilities = self.get_facilities()
        self.aircrafts = self.get_aircrafts()
        self.satellites = self.get_satellites()
        self.weapons = self.get_weapons()
        self.unguidedwpns = self.get_unguided_weapons()
        self.sideways = self.get_sideways()  # TODO  经验证，数据中未传递sideway
        self.contacts = self.get_contacts()
        self.loggedmssgs = self.get_logged_messages()
        self.patrolmssns = self.get_patrol_missions()
        self.strikemssns = self.get_strike_missions()
        self.supportmssns = self.get_support_missions()
        self.cargomssns = self.get_cargo_missions()
        self.ferrymssns = self.get_ferry_missions()
        self.miningmssns = self.get_mining_missions()
        self.mineclrngmssns = self.get_mine_clearing_missions()
        self.referencepnts = self.get_reference_points()
        self.nonavzones = self.get_no_nav_zones()
        self.excluzones = self.get_exclusion_zones()

        self.missions.update(self.patrolmssns)
        self.missions.update(self.strikemssns)
        self.missions.update(self.supportmssns)
        self.missions.update(self.cargomssns)
        self.missions.update(self.ferrymssns)
        self.missions.update(self.miningmssns)
        self.missions.update(self.mineclrngmssns)

    def static_update(self):
        """
        功能：静态更新推演方类下的关联类实例
        参数：无
        返回：无
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/9/20
        """
        self.static_add()
        self.static_delete()

    def static_delete(self):
        """
        将推演方删除的准静态化对象进行更新
        by aie
        """
        popped = []
        for k, v in self.situation.all_guid_delete_info.items():
            if v["side"] == self.strGuid:
                popped.append(k)
                if v["strType"] == 1005 and k in self.groups.keys():
                    self.groups.pop(k)
                    continue
                if v["strType"] == 2001 and k in self.submarines.keys():
                    self.submarines.pop(k)
                    continue
                if v["strType"] == 2002 and k in self.ships.keys():
                    self.ships.pop(k)
                    continue
                if v["strType"] == 2003 and k in self.facilities.keys():
                    self.facilities.pop(k)
                    continue
                if v["strType"] == 2004 and k in self.aircrafts.keys():
                    self.aircrafts.pop(k)
                    continue
                if v["strType"] == 2005 and k in self.satellites.keys():
                    self.satellites.pop(k)
                    continue
                if v["strType"] == 3005 and k in self.weapons.keys():
                    self.weapons.pop(k)
                    continue
                if v["strType"] == 3006 and k in self.unguidedwpns.keys():
                    self.unguidedwpns.pop(k)
                    continue
                if v["strType"] == 3008 and k in self.sideways.keys():
                    self.sideways.pop(k)
                    continue
                if v["strType"] == 4001 and k in self.contacts.keys():
                    self.contacts.pop(k)
                    continue
                if v["strType"] == 5001 and k in self.loggedmssgs.keys():
                    self.loggedmssgs.pop(k)
                    continue
                if v["strType"] == 10001 and k in self.missions.keys():
                    self.missions.pop(k)
                    continue
                if v["strType"] == 10001 and k in self.patrolmssns.keys():
                    self.patrolmssns.pop(k)
                    continue
                if v["strType"] == 10002 and k in self.strikemssns.keys():
                    self.strikemssns.pop(k)
                    continue
                if v["strType"] == 10003 and k in self.supportmssns.keys():
                    self.supportmssns.pop(k)
                    continue
                if v["strType"] == 10004 and k in self.cargomssns.keys():
                    self.cargomssns.pop(k)
                    continue
                if v["strType"] == 10005 and k in self.ferrymssns.keys():
                    self.ferrymssns.pop(k)
                    continue
                if v["strType"] == 10006 and k in self.miningmssns.keys():
                    self.miningmssns.pop(k)
                    continue
                if v["strType"] == 10007 and k in self.mineclrngmssns.keys():
                    self.mineclrngmssns.pop(k)
                    continue
                if v["strType"] == 11001 and k in self.referencepnts.keys():
                    self.referencepnts.pop(k)
                    continue
                if v["strType"] == 11002 and k in self.nonavzones.keys():
                    self.nonavzones.pop(k)
                    continue
                if v["strType"] == 11003 and k in self.excluzones.keys():
                    self.excluzones.pop(k)
        for k in popped:
            self.situation.all_guid_delete_info.pop(k)

    def static_add(self):
        """
        将推演方增加的准静态化对象进行更新
        by aie
        """
        for k, v in self.situation.all_guid_add_info.items():
            if v["side"] == self.strGuid:
                if v["strType"] == 1005:
                    self.groups.update({k: self.situation.group_dic[k]})
                    continue
                if v["strType"] == 2001:
                    self.submarines.update({k: self.situation.submarine_dic[k]})
                    continue
                if v["strType"] == 2002:
                    self.ships.update({k: self.situation.ship_dic[k]})
                    continue
                if v["strType"] == 2003:
                    self.facilities.update({k: self.situation.facility_dic[k]})
                    continue
                if v["strType"] == 2004:
                    self.aircrafts.update({k: self.situation.aircraft_dic[k]})
                    continue
                if v["strType"] == 2005:
                    self.satellites.update({k: self.situation.satellite_dic[k]})
                    continue
                if v["strType"] == 3005:
                    self.weapons.update({k: self.situation.weapon_dic[k]})
                    continue
                if v["strType"] == 3006:
                    self.unguidedwpns.update({k: self.situation.unguidedwpn_dic[k]})
                    continue
                if v["strType"] == 3008:
                    self.sideways.update({k: self.situation.sideway_dic[k]})
                    continue
                if v["strType"] == 4001:
                    self.contacts.update({k: self.situation.contact_dic[k]})
                    continue
                if v["strType"] == 5001:
                    self.loggedmssgs.update({k: self.situation.logged_messages[k]})
                    continue
                if v["strType"] == 10001:
                    self.patrolmssns.update({k: self.situation.mssnpatrol_dic[k]})
                    self.missions.update({k: self.situation.mssnpatrol_dic[k]})
                    continue
                if v["strType"] == 10002:
                    self.strikemssns.update({k: self.situation.mssnstrike_dic[k]})
                    self.missions.update({k: self.situation.mssnstrike_dic[k]})
                    continue
                if v["strType"] == 10003:
                    self.supportmssns.update({k: self.situation.mssnsupport_dic[k]})
                    self.missions.update({k: self.situation.mssnsupport_dic[k]})
                    continue
                if v["strType"] == 10004:
                    self.cargomssns.update({k: self.situation.mssncargo_dic[k]})
                    self.missions.update({k: self.situation.mssncargo_dic[k]})
                    continue
                if v["strType"] == 10005:
                    self.ferrymssns.update({k: self.situation.mssnferry_dic[k]})
                    self.missions.update({k: self.situation.mssnferry_dic[k]})
                    continue
                if v["strType"] == 10006:
                    self.miningmssns.update({k: self.situation.mssnmining_dic[k]})
                    self.missions.update({k: self.situation.mssnmining_dic[k]})
                    continue
                if v["strType"] == 10007:
                    self.mineclrngmssns.update({k: self.situation.mssnmnclrng_dic[k]})
                    self.missions.update({k: self.situation.mssnmnclrng_dic[k]})
                    continue
                if v["strType"] == 11001:
                    self.referencepnts.update({k: self.situation.referencept_dic[k]})
                    continue
                if v["strType"] == 11002:
                    self.nonavzones.update({k: self.situation.zonenonav_dic[k]})
                    continue
                if v["strType"] == 11003:
                    self.excluzones.update({k: self.situation.zonexclsn_dic[k]})

    def get_doctrine(self):
        """
        获取推演方条令
        by aie
        """
        if self.m_Doctrine in self.situation.doctrine_dic:
            doctrine = self.situation.doctrine_dic[self.m_Doctrine]
            doctrine.category = 'Side'  # 需求来源：20200331-2/2:Xy
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
        weapon_record = list({v.m_UnitWeapons: k for k, v in self.submarines.items()})
        weapon_record.extend(list({v.m_UnitWeapons: k for k, v in self.ships.items()}))
        weapon_record.extend(list({v.m_UnitWeapons: k for k, v in self.facilities.items()}))
        weapon_record.extend(list({v.m_UnitWeapons: k for k, v in self.aircrafts.items()}))
        weapon_record.extend(list({v.m_UnitWeapons: k for k, v in self.satellites.items()}))
        lst = re.findall(r"\$[0-9]*", '@'.join(weapon_record))
        lst1 = [k.replace('$', '') for k in lst]
        return lst1

    def get_weapon_infos(self):
        """
        功能：获取编组内所有武器的名称及dbid
        参数：无
        返回：编组内所有武器的名称及dbid组成的列表
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/7/20
        """
        weapon_record = list({v.m_UnitWeapons: k for k, v in self.submarines.items()})
        weapon_record.extend(list({v.m_UnitWeapons: k for k, v in self.ships.items()}))
        weapon_record.extend(list({v.m_UnitWeapons: k for k, v in self.facilities.items()}))
        weapon_record.extend(list({v.m_UnitWeapons: k for k, v in self.aircrafts.items()}))
        weapon_record.extend(list({v.m_UnitWeapons: k for k, v in self.satellites.items()}))
        lst = '@'.join(weapon_record)
        lst1 = lst.split('@')
        lst2 = [k.split('$') for k in lst1]
        return [x for x in lst2 if x != ['']]

    def get_groups(self):
        """
        获取本方编组
        :return:
        """
        group_dic = {}
        for k, v in self.situation.group_dic.items():
            if v.m_Side == self.strGuid:
                group_dic[k] = v
        return group_dic

    def get_submarines(self):
        """
        获取本方潜艇
        :return:
        """
        submarine_dic = {}
        for k, v in self.situation.submarine_dic.items():
            if v.m_Side == self.strGuid:
                submarine_dic[k] = v
        return submarine_dic

    def get_ships(self):
        """
        获取本方船
        :return:
        """
        ship_dic = {}
        for k, v in self.situation.ship_dic.items():
            if v.m_Side == self.strGuid:
                ship_dic[k] = v
        return ship_dic

    def get_facilities(self):
        """
        获取本方地面单位
        return:
        """
        facility_dic = {}
        for k, v in self.situation.facility_dic.items():
            if v.m_Side == self.strGuid:
                facility_dic[k] = v
        return facility_dic

    def get_aircrafts(self):
        """
        获取本方飞机
        :return:
        """
        air_dic = {}
        for k, v in self.situation.aircraft_dic.items():
            if v.m_Side == self.strGuid:
                air_dic[k] = v
        return air_dic

    def get_satellites(self):
        """
        获取本方卫星
        :return:
        """
        satellite_dic = {}
        for k, v in self.situation.satellite_dic.items():
            if v.m_Side == self.strGuid:
                satellite_dic[k] = v
        return satellite_dic

    def get_weapons(self):
        """
        获取本方武器
        :return:
        """
        weapon_dic = {}
        for k, v in self.situation.weapon_dic.items():
            if v.m_Side == self.strGuid:
                weapon_dic[k] = v
        return weapon_dic

    def get_unguided_weapons(self):
        """
        获取本方非指导武器
        :return:
        """
        unguidedwpn_dic = {}
        for k, v in self.situation.unguidedwpn_dic.items():
            if v.m_Side == self.strGuid:
                unguidedwpn_dic[k] = v
        return unguidedwpn_dic

    def get_sideways(self):
        """
        获取预定义航路
        by aie
        """
        return {k: v for k, v in self.situation.sideway_dic.items() if v.m_Side == self.strGuid}

    def get_contacts(self):
        """
        获取本方目标
        :return:
        """
        contact_dic = {}
        for k, v in self.situation.contact_dic.items():
            if v.m_OriginalDetectorSide == self.strGuid:  # changed by aie
                contact_dic[k] = v
        return contact_dic

    def get_logged_messages(self):
        """
        获取本方日志消息
        :return:
        """
        logged_messages = {}
        for k, v in self.situation.logged_messages.items():
            if v.m_Side == self.strGuid:
                logged_messages[k] = v
        return logged_messages

    def get_patrol_missions(self):
        """
        获取巡逻任务
        by aie
        """
        return {k: v for k, v in self.situation.mssnpatrol_dic.items() if v.m_Side == self.strGuid}

    def get_strike_missions(self):
        """
        获取打击任务
        by aie
        """
        return {k: v for k, v in self.situation.mssnstrike_dic.items() if v.m_Side == self.strGuid}

    def get_support_missions(self):
        """
        获取支援任务
        by aie
        """
        return {k: v for k, v in self.situation.mssnsupport_dic.items() if v.m_Side == self.strGuid}

    def get_cargo_missions(self):
        """
        获取运输任务
        by aie
        """
        return {k: v for k, v in self.situation.mssncargo_dic.items() if v.m_Side == self.strGuid}

    def get_ferry_missions(self):
        """
        获取转场任务
        by aie
        """
        return {k: v for k, v in self.situation.mssnferry_dic.items() if v.m_Side == self.strGuid}

    def get_mining_missions(self):
        """
        获取布雷任务
        by aie
        """
        return {k: v for k, v in self.situation.mssnmining_dic.items() if v.m_Side == self.strGuid}

    def get_missions_by_name(self, name):
        """
        功能：根据任务名称获取任务
        编写：aie
        时间：20200331
        :param name:
        :return:
        """
        # 需求来源：20200331－1:Xy
        # return {k: v for k, v in self.missions.items() if v.strName == name}
        # 临时需改，by 赵俊义
        for k, v in self.missions.items():
            if v.strName == name:
                return v

    def get_mine_clearing_missions(self):
        """
        获取扫雷任务
        by aie
        """
        return {k: v for k, v in self.situation.mssnmnclrng_dic.items() if v.m_Side == self.strGuid}

    def get_reference_points(self):
        """
        获取参考点
        :return:
        """
        referencept_dic = {}
        for k, v in self.situation.referencept_dic.items():
            if v.m_Side == self.strGuid:
                referencept_dic[k] = v
        return referencept_dic

    def get_no_nav_zones(self):
        """
        获取禁航区
        :return:
        """
        zonenonav_dic = {}
        for k, v in self.situation.zonenonav_dic.items():
            if v.m_Side == self.strGuid:
                zonenonav_dic[k] = v
        return zonenonav_dic

    def set_reference_point(self, guid, lat, lon):
        """
        ÉÖ²ο¼µãλÖ
        :param : tuple, Ðµľ­γ¶È»Ö (lat, lon)
        :return:
        """
        set_str = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
            self.strName, guid, lat, lon)
        return self.mozi_server.send_and_recv(set_str)

    def get_exclusion_zones(self):
        """
        获取本方日志消息
        :return:
        """
        zonexclsn_dic = {}
        for k, v in self.situation.zonexclsn_dic.items():
            if v.m_Side == self.strGuid:
                zonexclsn_dic[k] = v
        return zonexclsn_dic

    def get_score(self):
        """
        功能：获取本方分数
        参数：无
        返回：本方总分
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/21/20
        """
        return self.iTotalScore

    def get_unit_by_guid(self, guid):
        """
        获取实体
        :param guid: str, 实体guid/
        :return: Unit, 作战单元
        """
        if guid in self.aircrafts:
            return self.aircrafts[guid]
        if guid in self.facilities:
            return self.facilities[guid]
        if guid in self.weapons:
            return self.weapons[guid]
        if guid in self.ships:
            return self.ships[guid]
        if guid in self.satellites:
            return self.satellites[guid]
        if guid in self.submarines:
            return self.submarines[guid]
        return None

    def get_contact_by_guid(self, contact_guid):
        """
        获取情报对象
        :param contact_guid:  情报对象guid, 非实际单元guid
        :return:
        """
        if contact_guid in self.contacts:
            return self.contacts[contact_guid]
        else:
            return None

    def get_identified_targets_by_name(self, name):
        """
        功能：从推演方用名称确认目标
        编写：aie
        时间：20200330
        :param name:
        :return:
        """
        # 需求来源：20200330-1.3/3:lzy
        return {k: v for k, v in self.contacts.items() if v.strName == name}

    def get_elevation(self, coord_point):
        """
        获取某点（纬经度）
        :param coord_point: tuple, (float, float) (lat, lon)
        :return: int, 地形高程数据
        """
        lua_cmd = "ReturnObj(World_GetElevation ({latitude='%lf',longitude='%lf'}))" % (coord_point[0], coord_point[1])
        return int(self.mozi_server.send_and_recv(lua_cmd))

    def add_unit(self, unit_type, name, dbid, latitude, longitude, heading):
        """
        功能：添加单元
        参数：dbid的格式为 '12'，而不是 ‘hsfw-datafacility-000000000012’
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/26/20
        """
        guid = self.situation.generate_guid()
        cmd = ("HS_LUA_AddUnit({side = '%s', guid = '%s', type = '%s', name = '%s', dbid = %s, latitude = %s, "
               "longitude = %s, heading = %s})"
               % (self.strName, guid, unit_type, name, dbid, latitude, longitude, heading))
        rslt = self.mozi_server.send_and_recv(cmd)
        type_selected = {'SUB': CSubmarine, 'ship': CShip, 'facility': CFacility, 'air': CAircraft}
        obj = None
        if rslt == 'lua执行成功':
            self.mozi_server.throw_into_pool(cmd)
            self.situation.throw_into_pseudo_situ_all_guid(guid)
            obj = type_selected[unit_type](guid, self.mozi_server, self.situation)
            obj.strName = name
            obj.iDBID = dbid
            obj.dLatitude = latitude
            obj.dLongitude = longitude
            obj.fCurrentHeading = heading
        return rslt, obj

    def add_submarine(self, name, dbid, latitude, longitude, heading):
        """
        功能：添加潜艇
        参数：dbid的格式为 '12'，而不是 ‘hsfw-datafacility-000000000012’
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/21/20
        """
        guid = self.situation.generate_guid()
        cmd = ("HS_LUA_AddUnit({type = 'SUB', name = '%s', guid = '%s', heading = %s, dbid = %s, "
               "side = '%s', latitude=%s, longitude=%s})"
               % (name, guid, heading, dbid, self.strName, latitude, longitude))
        rslt = self.mozi_server.send_and_recv(cmd)
        obj = None
        if rslt == 'lua执行成功':
            self.mozi_server.throw_into_pool(cmd)
            self.situation.throw_into_pseudo_situ_all_guid(guid)
            obj = CSubmarine(guid, self.mozi_server, self.situation)
            obj.strName = name
            obj.iDBID = dbid
            obj.dLatitude = latitude
            obj.dLongitude = longitude
            obj.fCurrentHeading = heading
        return rslt, obj

    def add_ship(self, name, dbid, latitude, longitude, heading):
        """
        功能：添加舰艇
        参数：dbid的格式为 '12'，而不是 ‘hsfw-datafacility-000000000012’
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/21/20
        """
        guid = self.situation.generate_guid()
        cmd = ("HS_LUA_AddUnit({type = 'ship', name = '%s', guid = '%s', heading = %s, dbid = %s, "
               "side = '%s', latitude=%s, longitude=%s})"
               % (name, guid, heading, dbid, self.strName, latitude, longitude))
        rslt = self.mozi_server.send_and_recv(cmd)
        obj = None
        if rslt == 'lua执行成功':
            self.mozi_server.throw_into_pool(cmd)
            self.situation.throw_into_pseudo_situ_all_guid(guid)
            obj = CShip(guid, self.mozi_server, self.situation)
            obj.strName = name
            obj.iDBID = dbid
            obj.dLatitude = latitude
            obj.dLongitude = longitude
            obj.fCurrentHeading = heading
        return rslt, obj

    def add_facility(self, name, dbid, latitude, longitude, heading):
        """
        功能：添加地面设施
        参数：dbid的格式为 '12'，而不是 ‘hsfw-datafacility-000000000012’
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/21/20
        """
        guid = self.situation.generate_guid()
        cmd = ("HS_LUA_AddUnit({type = 'facility', name = '%s', guid = '%s', heading = %s, dbid = %s, "
               "side = '%s', latitude=%s, longitude=%s})"
               % (name, guid, heading, dbid, self.strName, latitude, longitude))
        rslt = self.mozi_server.send_and_recv(cmd)
        obj = None
        if rslt == 'lua执行成功':
            self.mozi_server.throw_into_pool(cmd)
            self.situation.throw_into_pseudo_situ_all_guid(guid)
            obj = CFacility(guid, self.mozi_server, self.situation)
            obj.strName = name
            obj.iDBID = dbid
            obj.dLatitude = latitude
            obj.dLongitude = longitude
            obj.fCurrentHeading = heading
        return rslt, obj

    def add_aircarft(self, name, dbid, loadoutid, latitude, longitude, altitude, heading):
        """
        功能：添加飞机
        参数：dbid的格式为 '12'，而不是 ‘hsfw-datafacility-000000000012’
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/14/20
        """
        guid = self.situation.generate_guid()
        cmd = ("HS_LUA_AddUnit({type = 'air', name = '%s', guid = '%s', loadoutid = %s, heading = %s, dbid = %s, "
               "side = '%s', latitude=%s, longitude=%s, altitude=%s})"
               % (name, guid, loadoutid, heading, dbid, self.strName, latitude, longitude, altitude))
        rslt = self.mozi_server.send_and_recv(cmd)
        obj = None
        if rslt == 'lua执行成功':
            self.mozi_server.throw_into_pool(cmd)
            self.situation.throw_into_pseudo_situ_all_guid(guid)
            obj = CAircraft(guid, self.mozi_server, self.situation)
            obj.strName = name
            obj.iDBID = dbid
            obj.loadout = loadoutid
            obj.dLatitude = latitude
            obj.dLongitude = longitude
            obj.fCurrentAltitude_ASL = altitude
            obj.fCurrentHeading = heading
        return rslt, obj

    def add_satellite(self, satellite_id, orbital):
        """
        作者：赵俊义
        日期：2020-3-9
        函数类别：编辑所用的函数
        功能说明: 向推定推演方添加卫星
        @param satellite_id: 卫星的数据库id，数值型
        @param orbital:  卫星的轨道， 数值型
        @return:
        """
        cmd = "Hs_AddSatellite('{}',{},{})".format(self.strName, satellite_id, orbital)
        rslt = self.mozi_server.send_and_recv(cmd)
        obj = None
        if rslt == 'lua执行成功':
            self.mozi_server.throw_into_pool(cmd)
            obj = CSatellite('generate-obj-for-cmd-operation', self.mozi_server, self.situation)
            obj.iDBID = satellite_id
            obj.m_TracksPoints = orbital
        return rslt, obj

    def import_inst_file(self, filename):
        """
        导入 inst 文件
        side string 导入 inst 文件的阵营
        filename string inst 文件名
        """
        return self.mozi_server.send_and_recv("ScenEdit_ImportInst('{}','{}')".format(self.strName, filename))

    def import_mission(self, mission_name):
        """
        作者：赵俊义
        日期：2020-3-10
        函数功能：从 Defaults 文件夹中查找对应的任务，导入到想定中
        函数类型：推演函数
        :return:
        """
        return self.mozi_server.send_and_recv("ScenEdit_ImportMission('{}','{}')".format(self.strGuid, mission_name))

    def add_mission(self, name, type, detail):
        """
        编辑函数，添加任务
        :param name:
        :param type: 任务类型
        :param detail:
        :return:
        """

        cmd = "ScenEdit_AddMission('{}','{}','{}',{})".format(self.strGuid, name, type, detail)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def add_mission_patrol(self, name, patrol_type_num, zone_points):
        """
        功能：添加巡逻任务
        参数：name:{str:任务名称}
             patrol_type_num:{int:巡逻类型的编号}
             zone_points:{list:参考点对象组成的列表}
        返回："patrol_type_num不在域中" 或 执行是否成功
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/24/20,4/25/20
        """
        if not is_in_domain(patrol_type_num, ArgsMission.patrol_type):
            return "patrol_type_num不在域中"
        patrol_type = ArgsMission.patrol_type[patrol_type_num].replace(' ', '').split(':')[0]
        detail = ["{type='"]
        detail.append(patrol_type)
        detail.append("', Zone={'%s'}}")
        points = []
        for v in zone_points:
            points.append(v)
        zone = "','".join(points)
        detail = "".join(detail)
        detail = detail % (zone)
        return self.add_mission(name, 'Patrol', detail)

    def add_mission_strike(self, name, strike_type_num):
        """
        功能：添加打击任务
        参数：name:{str:任务名称}
             strike_type_num:{int:打击类型的编号}
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/24/20,4/25/20
        """
        if not is_in_domain(strike_type_num, ArgsMission.strike_type):
            return "strike_type_num不在域中"
        strike_type = ArgsMission.strike_type[strike_type_num].replace(' ', '').split(':')[0]
        detail = ["{type='"]
        detail.append(strike_type)
        detail.append("'}")
        detail = ''.join(detail)
        return self.add_mission(name, 'Strike', detail)

    def add_mission_support(self, name, zone_points):
        """
        功能：添加支援任务
        参数：name:{str:任务名称}
             zone_points:{list:参考点对象组成的列表}
        返回：执行是否成功
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/25/20
        """
        detail = "{Zone={'%s'}}"
        points = []
        for v in zone_points:
            points.append(v)
        zone = "','".join(points)
        detail = detail % (zone)
        return self.add_mission(name, 'Support', detail)

    def add_mission_ferry(self, name, destination):
        """
        功能：添加转场任务
        参数：name:{str:任务名称}
             zone_points:{list:参考点对象组成的列表}
        返回：执行是否成功
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/25/20
        """
        detail = "{destination='%s'}"
        detail = detail % (destination)
        return self.add_mission(name, 'Ferry', detail)

    def add_mission_mining(self, name, zone_points):
        """
        功能：添加布雷任务
        参数：name:{str:任务名称}
             zone_points:{list:参考点对象组成的列表}
        返回：执行是否成功
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/25/20
        """
        detail = "{Zone={'%s'}}"
        points = []
        for v in zone_points:
            points.append(v.strName)
        zone = "','".join(points)
        detail = detail % (zone)
        return self.add_mission(name, 'Mining', detail)

    def add_mission_mine_clearing(self, name, zone_points):
        """
        功能：添加扫雷任务
        参数：name:{str:任务名称}
             zone_points:{list:参考点对象组成的列表}
        返回：执行是否成功
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/25/20
        """
        detail = "{Zone={'%s'}}"
        points = []
        for v in zone_points:
            points.append(v.strName)
        zone = "','".join(points)
        detail = detail % (zone)
        return self.add_mission(name, 'MineClearing', detail)

    def add_mission_cargo(self, name, zone_points):
        """
        功能：添加投送任务
        参数：name:{str:任务名称}
             zone_points:{list:参考点对象组成的列表}
        返回：执行是否成功
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/25/20
        """
        detail = "{Zone={'%s'}}"
        points = []
        for v in zone_points:
            points.append(v.strName)
        zone = "','".join(points)
        detail = detail % (zone)
        return self.add_mission(name, 'Cargo', detail)

    def delete_mission(self, mission_name):
        """
        删除任务
        :param mission_name: str, 任务名称
        :return:
        """
        lua = 'ScenEdit_DeleteMission("%s", "%s")' % (self.strName, mission_name)
        self.mozi_server.send_and_recv(lua)
        del self.missions[mission_name]

    def add_group(self, unitGuidList):
        """
        类别：编辑所用函数
        函数功能：将同类型单元单元合并创建编队，暂不支持不同类型单元。
        参数说明：
        1）{unitGuidstoadd}：同类型单元 GUID 组成的表对象。
        2）返回参数：编队信息组成的表对象。
        用法：
        scenEdit_AddGroup({'613f00e1-4fd9-4715-a672-7ec5c22486cb','431337a9-987e-46b6-8cb8-2f92b9b80335','0bc3        1a3c-096a-4b8e-a
        23d-46f7ba3b06b3'})
        """
        return self.mozi_server.send_and_recv("Hs_ScenEdit_AddGroup({})".format(unitGuidList))

    def air_group_out(self, air_guid_list):
        """
        编组出动
        :param air_guid_list:  list, 飞机的guid，  例子：['71136bf2-58ba-4013-92f5-2effc99d2wds','71136bf2-58ba-4013-92f5
                                                        -2effc99d2fa0']
        :return:
        """
        table = str(air_guid_list).replace('[', '{').replace(']', '}')
        lua_scrpt = "Hs_LUA_AirOpsGroupOut('{}',{})".format(self.strName, table)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def set_event(self, eventName, model):
        """
        #创建和设置事件 eventname为事件名称
        #eventTableMode为{mode='add',IsActive = false, IsRepeatable=true, Probability =100,IsShown = false}
        # mode 是类型 添加删除修改之类的 isactive 是否激活  IsRepeatable 是否重复 Probability概率 IsShown是否显示
        返回乱执行是否成功 （string）
        """
        return self.mozi_server.send_and_recv("ScenEdit_SetEvent ('%s',{mode='%s'})" % (eventName, model))

    def set_event_trigger(self, triggerTableMode):
        """
        创建和设置触发器
        triggerTableMode 为 {Description='航母被摧毁',mode='add',type= "unitdestroyed",TargetFilter={TARGETSIDE="中国",
        TARGETTYPE="Ship"}}
        Description 触发器名称 mode 操作类型同上 type触发器类型 类似有单元被摧毁 单元被毁伤之类的
        TargetFilter={TARGETSIDE="中国",TARGETTYPE="Ship"} 是单元被毁伤和单元被摧毁的 TARGETSIDE为单元所在方
        TARGETTYPE 为类型还有子类型参数
        返回乱执行是否成功 （string）
        """
        return self.mozi_server.send_and_recv("ScenEdit_SetTrigger ({})".format(triggerTableMode))

    def set_event_trigger_options(self, eventName, mode, triggername, replacedby=None):
        """
        为事件添加触发器
        eventName 事件名称
        triggername 触发器名称
        mode 操作类型
        返回乱执行是否成功 （string）
        """
        if replacedby is None:
            lua_scrpt = "ScenEdit_SetEventTrigger('%s', {mode = '%s',name = '%s'})" % (eventName, mode, triggername)
        else:

            lua_scrpt = "ScenEdit_SetEventTrigger('%s', {mode = '%s',name = '%s' ,replacedby = '%s'})" % (
                eventName, mode, self.strName, replacedby)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def set_event_condition(self, descrp, mode, Type, observersideID, targetsideID, posture, NOT):
        """
        以多种模式设置多种条件
        :param descrp:设置条件的描述
        :param mode:模式
        :param Type:不同的类型
        :param observersideID:将 TargetSide 视作……的推演方
        :param targetsideID:目标的id
        :param posture:方的相互关系
        :param NOT:否定描述符，将条件从真变为假
        :return:
        """
        lua_scrpt = "ScenEdit_SetCondition ({'{}','{}','{}','{}','{}','{}',{}})".format(descrp, mode, Type,
                                                                                        observersideID, targetsideID,
                                                                                        posture, NOT)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def set_event_action_options(self, eventName, mode, name):
        """
        为事件添加动作
        eventName 事件名称
        actionName 动作器名称
        mode 操作类型
        返回乱执行是否成功 （string）
        """
        lua_scrpt = "ScenEdit_SetEventAction('%s', {mode = '%s',name = '%s'})" % (eventName, mode, name)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def set_event_action(self, actionTableMode):
        """
        创建动作和设置动作
        actionTableMode 为{Description='想定结束',mode='add',type='endscenario'}
        Description 动作名称 mode 操作类型 类似有添加删除 type为类型 有想定结束单元移动等
        返回乱执行是否成功 （string）
        """
        return self.mozi_server.send_and_recv(" ScenEdit_SetAction({})".format(actionTableMode))

    def set_del_event_condition(self, eventname, mode, name):
        """
        作者：赵俊义
        日期：2020-3-12
        函数功能：删除事件的条件
        函数类别：编辑函数
        :param eventname:事件类型
        :param mode:操作类型
        :param name:事件名称
        :return:
        """
        return self.mozi_server.send_and_recv(
            "ScenEdit_SetEventCondition('{}',{mode='{}',name='{}'})".format(eventname, mode, name))

    def set_edit_event_condition(self, eventname, mode, name, replaceby):
        """
        作者：赵俊义
        日期：2020-3-12
        函数功能：编辑事件的条件
        函数类别：编辑函数
        :param eventname:事件类型
        :param mode:操作类型
        :param name:事件名称
        :param replaceby:替换为某个事件
        :return:
        """
        return self.mozi_server.send_and_recv("ScenEdit_SetEventCondition('{}',{mode='{}',name='{}', replacedby='{}'})"
                                              .format(eventname, mode, name, replaceby))

    def add_unit_to_facility(self, unit_type, name, dbid, loadoutid, baseUnitGuid):
        """
        往机场，码头添加单元
        """
        self.mozi_server.send_and_recv(
            "ReturnObj(ScenEdit_AddUnit({ type = '%s', unitname = '%s',side='%s', dbid = %s, loadoutid = %s, "
            "base = '%s'}))" % (unit_type, name, self.strName, dbid, loadoutid, baseUnitGuid))

    def delete_allUnit(self):
        """
        删除本方所有单元
        """
        return self.mozi_server.send_and_recv("Hs_DeleteAllUnits({})".format(self.strName))

    def set_ecom_status(self, objectType, objectName, emcon):
        """
        设置选定对象的 EMCON
        objectType 对象类型 'Side' / 'Mission' / 'Group' / 'Unit'
        objectName 对象名称 'Side Name or ID' / 'Mission Name or ID' / 'Group Name or ID' / 'Unit Name or ID'
        emcon 传感器类型和传感器状态 'Radar/Sonar/OECM=Active/Passive;' / 'Inherit'
        例 ：
        ScenEdit_SetEMCON(['Side' / 'Mission' / 'Group' / 'Unit'], ['Side Name or ID' / 'Mission Name or ID' /
        'Group Name or ID' / 'Unit Name or ID'], ['Radar/Sonar/OECM=Active/Passive;' / 'Inherit'])
        """
        return self.mozi_server.send_and_recv("ScenEdit_SetEMCON('{}','{}','{}')".format(objectType, objectName, emcon))

    def add_reference_point(self, sideName, name, lat, lon):
        """
        功能：
        参数：
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/24/20
        """
        cmd = "ScenEdit_AddReferencePoint({side='%s', name='%s', lat=%s, lon=%s})" % (sideName, name, lat, lon)
        rslt = self.mozi_server.send_and_recv(cmd)
        pnt = None
        if rslt == 'lua执行成功':
            self.mozi_server.throw_into_pool(cmd)
            pnt = CReferencePoint('generate-obj-for-cmd-operation', self.mozi_server, self.situation)
            pnt.strName = name
            pnt.dLatitude = lat
            pnt.dLongitude = lon
        return pnt

    def add_zone(self, zoneTableMode):
        """
        创建和设置区域
        :param zoneGuid: 区域id
        :param zoneTableMode: 类型,禁航区,封锁区
        :return:
        """
        guid = self.situation.generate_guid()
        self.situation.throw_into_pseudo_situ_all_guid(guid)
        return self.mozi_server.send_and_recv(
            "Hs_ScenEdit_SetZone('{}', '{}',{})".format(self.strGuid, guid, zoneTableMode))

    def set_zone(self, zoneGuid, zoneTableMode):
        """
        创建和设置区域
        :param zoneGuid: 区域id
        :param zoneTableMode: 类型,禁航区,封锁区
        :return:
        """
        guid = self.situation.generate_guid()
        return self.mozi_server.send_and_recv(
            "Hs_ScenEdit_SetZone('{}', '{}',{})".format(self.strGuid, guid, zoneTableMode))

    def deploy_mine(self, mineType, mineCount, area):
        """
        给某一方添加雷
        mineType 类型
        mineCount 数量
        area table类型 布雷区域
        """
        return self.mozi_server.send_and_recv(
            "Hs_DeployMine('{}','{}',{},{})".format(self.strName, mineType, mineCount, area))

    def add_no_navi_zone(self, description, area):
        """
        添加禁航区
        description 禁航区名称
        area 区域 area={"RP-112","RP-113","RP-114","RP-115"}
        """
        return self.mozi_server.send_and_recv(
            "Hs_AddZone('%s', {Description = '%s', Area = %s})" % (self.strName, description, area))

    def clone_etac(self, table):
        """
        作者：赵俊义
        日期：2020-3-7
        功能说明：克隆指定事件
        函数类别：推演所用的函数
        函数功能：克隆指定事件（触发器、条件、动作）
        table  {CLONETRIGGER = '", triggerGuid, "'} { CLONEEVENT = '", eventGuid, "' }
        { CLONECONDITION = '", conditionGuid, "' }     { CLONEACTION = '", actionGuid, "' }
        """
        return self.mozi_server.send_and_recv("Hs_CloneETAC({})".format(table))

    def reset_doctrine(self, GUID, LeftMiddleRight, EnsembleWeaponEMCON):
        """
        Hs_ResetDoctrine 重置条令
        GUID 为要设置的推演方、任务、单元、编组 GUID
        LeftMiddleRight Left：重置作战条令，Middle 重置关联的作战单元，Right 重置关联的使命任务
        EnsembleWeaponEMCON Ensemble：总体，EMCON 电磁管控设置，Weapon 武器使用规则
        """
        return self.mozi_server.send_and_recv(
            "Hs_ResetDoctrine('{}','{}','{}')".format(GUID, LeftMiddleRight, EnsembleWeaponEMCON))

    def set_new_name(self, new_name):
        """
        推演方重命名
        sideNewIdOrName 新名称
        """
        return self.mozi_server.send_and_recv("setNewSideNaem('{}','{}')".format(self.strName, new_name))

    def set_mark_contact(self, contact, relation):
        """
        设置目标对抗关系
        ContactType：字符串。目标立场类型（'F'：友方，'N'：中立，'U'：非友方，'H'：敌方）。
        """
        lua = "Hs_SetMarkContact('%s', '%s', '%s')" % (self.strName, contact, relation)
        self.mozi_server.send_and_recv(lua)

    def assign_target_to_mission(self, contact_guid, unit_guid):
        """
        将目标分配给一项打击任务
        """
        lua = "ScenEdit_AssignUnitAsTarget({'%s'}, '%s')" % (contact_guid, unit_guid)
        self.mozi_server.send_and_recv(lua)

    def set_score(self, score, reason_for_change=''):
        """
        类别：编辑所用函数
        函数功能：设置指定推演方的总分及总分变化原因。
        参数说明：
        1）sidename_or_id：字符串。推演方名称或 GUID；
        2）score：数值型。总分；
        3）reason_for_change：字符串。总分变化原因。
        """
        lua = "ScenEdit_SetScore('%s',%s,'%s')" % (self.strGuid, score, reason_for_change)
        self.mozi_server.send_and_recv(lua)

    def side_scoring(self, scoringDisaster, scoringTriumph):
        """
        作者：赵俊义
        日期：2020-3-10
        函数类别：编辑所用的函数
        功能说明: 为指定推演方设置完败、完胜分数线。
        :param scoringDisaster:完败值
        :param scoringTriumph:完胜值
        :return:
        """
        return self.mozi_server.send_and_recv(
            "Hs_SideScoring('{}','{}','{}')".format(self.strGuid, scoringDisaster, scoringTriumph))

    def drop_contact(self, contact_guid):
        """
        类别：编辑用函数
        放弃目标
        不再将所选目标列为探测对象。
        contact_guid 字符串。目标 GUID
        Hs_ContactDropTarget('红方','a5561d29-b136-448b-af5d-0bafaf218b3d')
        """
        lua_scrpt = "Hs_ContactDropTarget('%s','%s')" % (self.strGuid, contact_guid)
        self.mozi_server.send_and_recv(lua_scrpt)

    def wcsfa_contact_types_all_unit(self, HoldTightFreeInheri):
        """
        函数功能：控制所有单元对所有目标类型的攻击状态。
        参数说明：
        1）HoldTightFreeInheri
        ted：控制状态标识符（'Hold'：禁止，'Tight'：限制，'Free'：自由，'Inherited'：按上级条令执行）
        """
        lua = "Hs_WCSFAContactTypesAllUnit('%s','%s')" % (self.strGuid, HoldTightFreeInheri)
        self.mozi_server.send_and_recv(lua)

    def lpcw_attack_all_unit(self, yesNoOrInherited):
        """
        函数功能：所有单元攻击时是否忽略计划航线。
        参数说明：
        1）'YesNoOrInherited'：控制状态标识符（'Yes'：忽略，'No'：不忽略，'Inherited'：按上级条令执行）
        """
        lua = "Hs_LPCWAttackAllUnit('{}','{}')".format(self.strGuid, yesNoOrInherited)
        return self.mozi_server.send_and_recv(lua)

    def get_side_info(self, side):
        """
        作者：赵俊义
        日期：2020-3-7
        功能说明：获取推演方信息
        函数类别：推演所用的函数
        """
        return self.mozi_server.send_and_recv("VP_GetSide('{}')".format(side))

    def set_side_options(self, awareness, proficiency, isAIOnly, isCollRespons):
        """
        作者：赵俊义
        日期：2020-3-7
        函数类别：推演所用的函数
        功能说明：设置推演方的名称、GUID、认知能力、训练水平、AI 操控、集
        体反应、自动跟踪非作战单元等组成的属性集合
        """
        return self.mozi_server.send_and_recv(
            "ScenEdit_SetSideOptions({},{},{},{},{})".format(self.strName, awareness, proficiency, isAIOnly,
                                                             isCollRespons))

    def get_side_attribute(self):
        """
        作者：赵俊义
        日期：2020-3-9
        函数类别：推演所用的函数
        功能说明：获取推演方的名称、GUID、认知能力、训练水平、计算机操控、
                 集体反应、自动跟踪非作战单元等组成的属性集合。
        """
        return self.mozi_server.send_and_recv("ScenEdit_GetSideOptions('{}')".format(self.strName))

    def get_ishuman_attribute(self):
        """
        作者：赵俊义
        日期：2020-3-9
        函数类别：推演所用的函数
        功能说明：获取推演方操控属性，以便判断该推演方是人操控还是计算机操控
        """
        return self.mozi_server.send_and_recv("ScenEdit_GetSideIsHuman('{}')".format(self.strName))

    def get_unit_attribute(self, unit):
        """
        LUA_ScenEdit_GetUnit
        unit 选择单元。基于阵营和名字、或 GUID，推荐使用后者。
        name string 选择的单元名
        side string 单元所属的阵营名
        guid string 单元的 guid
        """
        result = self.mozi_server.send_and_recv(" ReturnObj(scenEdit_GetUnit({}))".format(unit))
        activeUnit = CActiveUnit(self.strGuid, self.mozi_server, self.situation)
        if result[:4] == "unit":
            # 处理接收的数据
            result_split = result[6:-1].replace('\'', '')
            result_join = ""
            result_join = result_join.join([one for one in result_split.split('\n')])
            lst = result_join.split(',')
            for keyValue in lst:
                keyValue_list = keyValue.split('=')
                if len(keyValue_list) == 2:
                    attr = keyValue_list[0].strip()
                    value = keyValue_list[1].strip()
                    if attr == "name":
                        activeUnit.name = value
                    elif attr == "side":
                        activeUnit.side = value
                    elif attr == "type":
                        activeUnit.type = value
                    elif attr == "subtype":
                        activeUnit.subtype = value
                    elif attr == "guid":
                        activeUnit.guid = value
                    elif attr == "proficiency":
                        activeUnit.proficiency = value
                    elif attr == "latitude":
                        activeUnit.latitude = float(value)
                    elif attr == "longitude":
                        activeUnit.longitude = float(value)
                    elif attr == "altitude":
                        activeUnit.altitude = float(value)
                    elif attr == "heading":
                        activeUnit.heading = float(value)
                    elif attr == "speed":
                        activeUnit.speed = float(value)
                    elif attr == "throttle":
                        activeUnit.throttle = value
                    elif attr == "autodetectable":
                        activeUnit.autodetectable = bool(value)
                    elif attr == "mounts":
                        activeUnit.mounts = int(value)
                    elif attr == "magazines":
                        activeUnit.magazines = int(value)
                    elif attr == "unitstate":
                        activeUnit.unitstate = value
                    elif attr == "fuelstate":
                        activeUnit.fuelstate = value
                    elif attr == "weaponstate":
                        activeUnit.weaponstate = value
            code = "200"
        else:
            code = "500"
        return code, activeUnit

    def copy_unit(self, unit_name, lon, lat):
        """
        作者：赵俊义
        日期：2020-3-9
        函数类别：编辑所用的函数
        功能说明：将想定中当前推演方中的已有单元复制到指定经纬度处
        @param unit_name: 被复制的单元名称
        @param lon: 经度
        @param lat: 纬度
        @return:
        """
        return self.mozi_server.send_and_recv("Hs_CopyUnit('{}',{},{})".format(unit_name, lon, lat))

    def delete_unit(self, unit_name):
        """
        作者：赵俊义
        日期：2020-3-9
        函数类别：编辑所用的函数
        功能说明：删除当前推演方中指定单元
        @param unit_name: 单元名
        @return:
        """
        return self.mozi_server.send_and_recv("ScenEdit_DeleteUnit('{}')".format(unit_name))

    def kill_unit(self, unit_name):
        """
        作者：赵俊义
        日期：2020-3-9
        函数类别：编辑所用的函数
        功能说明：一旦推演执行到此函数，就摧毁指定推演方的指定单元，并输出该摧毁事件的消息，并影响到战损
                统计，与 ScenEdit_DeleteUnit差别较大（ScenEdit_DeleteUnit 在编辑中立即执行、不会输出
                消息、被删除单元不计入战斗损失统计表）
        @param unit_name:单元名称
        @return:
        """
        return self.mozi_server.send_and_recv("ScenEdit_KillUnit({'{}','{}'})".format(self.strName, unit_name))

    def dele_all_units(self):
        """
        作者：赵俊义
        日期：2020-3-9
        函数类别：编辑所用的函数
        功能说明:删除指定推演方所有单元
        @return:
        """
        return self.mozi_server.send_and_recv("Hs_DeleteAllUnits({})".format(self.strName))

    def remove_zone(self, sideName, zoneGUID):
        """
        作者: 赵俊义
        日期：2020-3-10
        函数功能：删除指定推演方的指定禁航区或封锁区
        函数类型：推演函数
        :param sideName: 方的名称
        :param zoneGUID: 区域guid
        :return:
        """
        return self.mozi_server.send_and_recv("Hs_ScenEdit_RemoveZone('{}','{}')".format(sideName, zoneGUID))

    def delete_reference_point(self, pnt_guid):
        """
        删除参考点
        :return:
        """
        set_str = 'ScenEdit_DeleteReferencePoint({side="%s",guid="%s"})' % (self.strGuid, pnt_guid)
        return self.mozi_server.send_and_recv(set_str)

    def add_plan_way(self, nType, strWayName):
        """
        作者: 赵俊义
        日期：2020-3-10
        函数功能：为指定推演方添加一预设航线（待指定航路点）。
        函数类型：推演函数
        :param nType: 航线类型（0 是单元，1 是武器）
        :param strWayName:航线名称
        :return:
        """
        return self.mozi_server.send_and_recv("Hs_AddPlanWay('{}',{},'{}')".format(self.strName, nType, strWayName))

    def set_plan_way_showing_status(self, strWayNameOrID, bIsShow):
        """
        作者: 赵俊义
        日期：2020-3-10
        函数功能：为控制预设航线的显示或隐藏
        函数类型：推演函数
        :param strWayNameOrID: 预设航线名称或者GUID
        :param bIsShow: 是否显示
        :return:
        """
        return self.mozi_server.send_and_recv(
            "Hs_PlanWayIsShow('{}','{}',{})".format(self.strGuid, strWayNameOrID, bIsShow))

    def rename_plan_way(self, strWayNameOrID, strNewName):
        """
        作者: 赵俊义
        日期：2020-3-11
        函数功能：修改预设航线的名称
        函数类型：推演函数
        :param strWayNameOrID:预设航线名称或者GUID
        :param strNewName:新名称
        :return:
        """
        return self.mozi_server.send_and_recv(
            "Hs_RenamePlanWay('{}','{}','{}')".format(self.strGuid, strWayNameOrID, strNewName))

    def add_plan_way_point(self, strWayNameOrID, dWayPointLongitude, dWayPointLatitude):
        """
        作者: 赵俊义
        日期：2020-3-11
        函数功能：为预设航线添加航路点
        函数类型：推演函数
        :param strWayNameOrID: 预设航线名称或者GUID
        :param dWayPointLongitude:航路点经度
        :param dWayPointLatitude:航路点纬度
        :return:
        """
        return self.mozi_server.send_and_recv(
            "Hs_AddPlanWayPoint('{}','{}',{},{})".format(self.strGuid, strWayNameOrID, dWayPointLongitude,
                                                         dWayPointLatitude))

    def update_plan_way_point(self, strWayNameOrID, strWayPointID, table):
        """
        作者: 赵俊义
        日期：2020-3-11
        函数功能：修改航路点信息
        函数类型：推演函数
        :param strWayNameOrID: 预设航线的名称或者GUID
        :param strWayPointID: 航路点的GUID
        :param table: 航路点的信息 {NAME='12',LONGITUDE = 12.01,LATITUDE=56.32,ALTITUDE=1(为0-7的数值)，THROTTLE = 1(为0-5
                      的数值)，RADAR= 1(为0-2的数值),SONAR=1(为0-2的数值) ,OECM=1(为0-2的数值)},可根据需要自己构造
        :return:
        """
        return self.mozi_server.send_and_recv(
            "Hs_UpDataPlanWayPoint('{}','{}','{}',{})".format(self.strGuid, strWayNameOrID, strWayPointID, table))

    def remove_plan_way_point(self, strWayNameOrID, strWayPointID):
        """
        作者: 赵俊义
        日期：2020-3-11
        函数功能：预设航线删除航路点
        函数类型：推演函数
        :param strWayNameOrID: 预设航线名称或者GUID
        :param strWayPointID: 航路点的ID
        :return:
        """
        return self.mozi_server.send_and_recv(
            "Hs_RemovePlanWayPoint('{}','{}','{}')".format(self.strGuid, strWayNameOrID, strWayPointID))

    def remove_plan_way(self, strWayNameOrID):
        """
        作者: 赵俊义
        日期：2020-3-11
        函数功能：删除预设航线
        函数类型：推演函数
        :param strWayNameOrID: 预设航线名称或者GUID
        :return:
        """
        return self.mozi_server.send_and_recv("Hs_RemovePlanWay('{}','{}')".format(self.strGuid, strWayNameOrID))

    def add_plan_way_to_mission(self, strMissionNameOrID, Type, strWayNameOrID):
        """
        函数功能：为任务分配预设航线
        函数类型：推演函数
        :param strMissionNameOrID: 任务名称或ID
        :param Type: 单元还是武器的航线
        :param strWayNameOrID: 航路名称或id
        :return:
        Hs_AddPlanWayToMission({MISSIONNAME='strike2',MISSIONWAYTYPE=1,PLANWAYNAME='strike2Way'})
        """
        return self.mozi_server.send_and_recv("Hs_AddPlanWayToMission({MISSIONNAME='%s',MISSIONWAYTYPE=%d,PLANWAYNAME='%s'})"%(strMissionNameOrID, Type, strWayNameOrID))

    def add_plan_way_to_target(self, strMissionNameOrId, strWayNameOrID, strTargetNameOrID):
        """
        函数功能：为目标分配预设航线
        函数类型：推演函数
        :param strMissionNameOrId: 任务的名称或GUID
        :param strWayNameOrID: 预设航线的名称或GUID
        :param strTargetNameOrID: 打击目标的名称或GUID
        :return:
        """
        return self.mozi_server.send_and_recv(
            "Hs_AddPlanWayToMissionTarget('{}','{}','{}')".format(strMissionNameOrId, strWayNameOrID,
                                                                  strTargetNameOrID))

    def edit_brief(self, briefing):
        """
        作者：赵俊义
        日期：2020-3-12
        函数功能：修改指定推演方的任务简报
        函数类型：编辑函数
        :param briefing:简报文字
        :return:
        """
        return self.mozi_server.send_and_recv("Hs_EditBriefing('{}','{}')".format(self.strGuid, briefing))

    def is_target_existed(self, target_name):
        """
        类别：推演所用函数
        检查目标是否存在
        param ：
        target_name ：目标名称
        all_info_dict ：所有单元信息字典
        return : true（存在）/false（不存
        """
        ret = self.get_guid_from_name(target_name, self.contacts)
        if ret:
            return True
        return False

    def get_guid_from_name(self, _name, _dic):
        """
        通过名字查找guid
        :param _name:方的名字
        :param _dic:方的字典
        :return:
        """
        for key, value in _dic.items():
            if _name in value.strName:
                return key
        return None

    def group_out(self, air_guid_list):
        """
        编组出动
        :param air_guid_list: 飞机的guid，例子：['71136bf2-58ba-4013-92f5-2effc99d2wds','71136bf2-58ba-4013-92f5-2effc99d2fa0']
        :return:
        """
        table = str(air_guid_list).replace('[', '{').replace(']', '}')
        lua_scrpt = "Hs_LUA_AirOpsGroupOut('{}',{})".format(self.strGuid, table)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def hold_position_all_units(self, status):
        """
        功能：保持所有单元阵位，所有单元停止机动，留在原地
        参数：status: {str: 'true', 'false'}
        返回：执行成功与否
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/26/20
        """
        cmd = "Hs_HoldPositonAllUnit('%s', %s)" % (self.strGuid, status)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def launch_units_singlely(self, unitlist):
        """
        功能：停靠任务单独出航
        参数：
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/28/20
        """
        unitlist = [v.strGuid for v in unitlist]
        cmd = "Hs_ScenEdit_DockingOpsSingleOut({%s})" % (unitlist)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def launch_units_in_group(self, unitlist):
        """
        功能：停靠任务编队出航
        参数：
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/28/20
        """
        unitlist = [v.strGuid for v in unitlist]
        cmd = "Hs_ScenEdit_DockingOpsGroupOut({%s})" % (unitlist)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def lauch_units_abort(self, unitlist):
        """
        功能：停靠任务终止出航
        参数：
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/28/20
        """
        unitlist = [v.strGuid for v in unitlist]
        cmd = "Hs_ScenEdit_DockingOpsAbortLaunch({%s})" % (unitlist)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)
