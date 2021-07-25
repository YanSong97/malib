# -*- coding:utf-8 -*-
##########################################################################################################
# File name : group.py
# Create date : 2020-1-8
# Modified date : 2020-1-8
# All rights reserved:北京华戍防务技术有限公司
# Author:xy
##########################################################################################################

#from ..entitys.activeunit import CActiveUnit
from .activeunit import CActiveUnit
import re


class CGroup(CActiveUnit):
    """
    编组类
    """

    def __init__(self, strGuid, mozi_server, situation):
        super().__init__(strGuid, mozi_server, situation)
        # 悬停
        self.fHoverSpeed = 0.0
        # 低速
        self.fLowSpeed = 0.0
        # 巡航
        self.fCruiseSpeed = 0.0
        # 军力
        self.fMilitarySpeed = 0.0
        # 加速
        self.fAddForceSpeed = 0.0
        # 是否在作战中
        self.bIsOperating = False
        # 停靠的单元GUID集合
        self.m_DockedUnits = ''
        # 实体的停靠设施(部件)
        # 集合
        self.m_DockFacilitiesComponent = ''
        # 停靠的飞机的GUID集合
        self.m_DockAircrafts = ''
        # 实体的航空设施(部件)
        # 集合
        self.m_AirFacilitiesComponent = ''
        # 实体的通信设备及数据链（部件）
        self.m_CommDevices = ''
        # 单元搭载武器
        self.m_UnitWeapons = ''
        # 状态
        self.strActiveUnitStatus = ''
        # 训练水平
        self.m_ProficiencyLevel = ''
        # 是否是护卫角色
        self.bIsEscortRole = False
        # 当前油门
        self.m_CurrentThrottle = ''
        # 通讯设备是否断开
        self.bIsCommsOnLine = False
        # 是否视图隔离
        self.bIsIsolatedPOVObject = False
        # 是否地形跟随
        self.bTerrainFollowing = False
        # 是否是领队
        self.bIsRegroupNeeded = False
        # 是否保持阵位
        self.bHoldPosition = False
        # 是否可自动探测
        self.bAutoDetectable = False
        # 燃油百分比，作战单元燃油栏第一个进度条的值
        self.dFuelPercentage = False
        # 单元的通讯链集合
        self.m_CommLink = ''
        # 传感器GUID集合
        self.m_NoneMCMSensors = ''
        # 显示“干扰”或“被干扰”
        self.iDisturbState = 0
        # 单元所属多个任务数量
        self.iMultipleMissionCount = 0
        # 单元所属多个任务guid集合
        self.m_MultipleMissionGUIDs = ''
        # 弹药库GUID集合
        self.m_Magazines = ''
        # 编组类型
        self.m_GroupType = ''
        # 编组中心点
        self.m_GroupCenter = ''
        # 编组领队
        self.m_GroupLead = ''
        # 编组所有单元
        self.m_UnitsInGroup = ''
        # 航路点名称
        self.strWayPointName = ''
        # 航路点描述
        self.strWayPointDescription = ''
        # 航路点剩余航行距离
        self.WayPointDTG = ''
        # 航路点剩余航行时间
        self.WayPointTTG = ''
        # 航路点需要燃油数
        self.WayPointFuel = ''
        # 发送队形方案选择的索引
        self.iFormationSelectedIndex = ''
        # 发送队形方案详情
        self.m_FormationFormula = ''
        # 载机按钮的文本描述
        self.strDockAircraft = ''
        # 载艇按钮的文本描述
        self.strDockShip = ''

    def get_units(self):
        """
        获取编组下单元
        :return:
        """
        units_guid = self.m_UnitsInGroup.split('@')
        units_group = {}
        for guid in units_guid:
            units_group[guid] = self.situation.get_obj_by_guid(guid)
        return units_group

    def get_doctrine(self):
        """
        获取条令
        by aie
        """
        if self.m_Doctrine in self.situation.doctrine_dic:
            doctrine = self.situation.doctrine_dic[self.m_Doctrine]
            doctrine.category = 'Group'  # 需求来源：20200331-2/2:Xy
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
        weapon_record = self.m_UnitWeapons
        lst = re.findall(r"\$[0-9]*", weapon_record)
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
        weapon_record = self.m_UnitWeapons
        lst = weapon_record.split('@')
        lst1 = [k.split('$') for k in lst]
        return [x for x in lst1 if x != ['']]

    def add_unit(self, unit_guid):
        """
        编队添加一个单元
        :param unit_guid: 作战单元guid
        :return:
        """
        lua_scrpt = "ScenEdit_SetUnit({group='%s',guid='%s'})"%(self.strGuid, unit_guid)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def remove_unit(self, unitId):
        """
        类别：编辑所用函数
        将单元移除编组
        unitId 单元ID
        """
        return self.mozi_server.send_and_recv("Hs_RemoveUnitFromGroup('{}')".format(unitId))


    def set_formation(self, table):
        """
        类别：推演所用函数
        函数功能：设置编队领队及队形。
        参数说明：
        1）table：编队成员队形信息组成的表对象：
         NAME：字符串。单元名称；
         SETTOGROUPLEAD：是否担当领队（'Yes'：是，'No'：否）；
         TYPE：与领队的空间相对关系的维持模式（'FIXED'：维持平动，'Rotating'：+ASD
        同步转动）；
         BEARING：数值型。与领队的相对方位；
         DISTANCE：数值型。与领队的距离。
        2）返回参数：编队队形信息组成的表对象
        """
        return self.mozi_server.send_and_recv("Hs_GroupFormation({})".format(table))

    def set_unit_sprint_and_drift(self, unitNameOrID, trueOrFalse):
        """
        函数功能：控制编队内非领队单元相对于编队是否进行高低速交替航行。
        参数说明：
        1）UnitNameOrID：字符串。单元名称或 GUID；
        2）TrueOrFalse：布尔值。是否交替航行的状态标识符（true：是，false：否）。
        """
        return self.mozi_server.send_and_recv("Hs_SetUnitSprintAndDrift('{}',{})".format(unitNameOrID, trueOrFalse))
