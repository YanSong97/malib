# -*- coding:utf-8 -*-
##########################################################################################################
# File name : facility.py
# Create date : 2020-1-8
# Modified date : 2020-1-8
# All rights reserved:北京华戍防务技术有限公司
# Author:xy
##########################################################################################################

#from ..entitys.activeunit import CActiveUnit
from malib.envs.mozi.mozi_simu_sdk.activeunit import CActiveUnit


class CFacility(CActiveUnit):
    """地面设施"""

    def __init__(self, strGuid, mozi_server, situation):
        super().__init__(strGuid, mozi_server, situation)
        # 方位类型
        self.m_BearingType = 0
        # 方位
        self.m_Bearing = 0.0
        # 距离（千米）
        self.m_Distance = 0.0
        # 是否高速交替航行
        self.bSprintAndDrift = False
        # 载机按钮的文本描述
        self.strDockAircraft = ""
        # 类别
        self.m_Category = 0
        # 悬停
        self.fHoverSpeed = 0.0
        # 低速
        self.fLowSpeed = 0.0
        # 巡航
        self.fCruiseSpeed = 0.0
        # 军力
        self.fMilitarySpeed = 0.0
        # 载艇按钮的文本描述
        self.strDockShip = ""
        self.m_CommandPost = ""
        # 加油队列明细
        self.m_ShowTanker = ""
        self.ClassName = 'CFacility'

    def get_summary_info(self):
        """
        获取精简信息, 提炼信息进行决策
        :return: dict
        """
        info_dict = {
            "guid": self.strGuid,
            "DBID": self.iDBID,
            "subtype": str(self.m_Category),
            "facilityTypeID": "",
            "name": self.strName,
            "side": self.m_Side,
            "proficiency": self.m_ProficiencyLevel,
            "latitude": self.dLatitude,
            "longitude": self.dLongitude,
            "altitude": self.fAltitude_AGL,
            "altitude_asl": self.iAltitude_ASL,
            "course": self.get_way_points_info(),
            "heading": self.fCurrentHeading,
            "speed": self.fCurrentSpeed,
            "throttle": self.m_CurrentThrottle,
            "autodetectable": self.bAutoDetectable,
            "unitstate": self.strActiveUnitStatus,
            "fuelstate": "",
            "weaponstate": -1,
            "mounts": self.get_mounts(),
            "type": "Facility",
            "fuel": 0,
            "damage": self.strDamageState,
            "sensors": self.get_sensor(),
            "weaponsValid": self.get_weapon_infos()
        }
        return info_dict

    def set_radar_shutdown(self, on_off):
        """
        设置雷达开关机
        :param on_off: str,参数是 ture 或者false
        :return:
        """
        return super().set_radar_shutdown(on_off)

    def set_oecm_shutdown(self, on_off):
        """
        设置干扰开关机
        :param on_off: str, 参数是 ture 或者false
        :return:
        """
        return super().set_oecm_shutdown(on_off)

    def set_desired_speed(self, desired_speed):
        """
        设置单元的期望速度
        :param desired_speed: float, 千米/小时
        :return: 所操作单元的完整描述子
        """
        return super().set_desired_speed(desired_speed)

    def set_desired_height(self, desired_height):
        """
        设置单元的期望高度
        :param desired_height: 期望高度值, 海拔高度：m
        :return:
        """
        return super().set_desired_height(desired_height)

    def set_unit_heading(self, heading):
        """
        设置朝向
        heading 朝向
        exampl
        set_unit_heading(30):
        """
        return super().set_unit_heading(heading)

    def plot_course(self, course_list):
        """
        地面设施航线规划
        :param course_list: list, [(lat, lon)], 例子：[(40, 39.0), (41, 39.0)]
        :return:
        """
        return super().plot_course(course_list)

    def delete_coursed_point(self, point_index):
        """
        单元删除航路点
        :param point_index: list:删除多个航路点 [0, 1], or int：删除一个航路点，
        :param clear: bool, True:清空航路点
        :return:
        """
        return super().delete_coursed_point(point_index, clear=False)

    def assign_unitlist_to_mission(self, mission_name):
        """
        分配加入到任务中
        :param mission_name: str, 任务名称
        :return: table 存放单元的名称或GUID
        """
        return super().assign_unitlist_to_mission(mission_name)

    def auto_attack(self, target_guid):
        """
        自动攻击目标
        :param target_guid: 目标guid
        :return:
        """
        return super().auto_attack(target_guid)

    def manual_attack(self, target_guid, weapon_dbid, weapon_num):
        """
        设置哪个武器被用于攻击
        fire_unit_guid:开火单元guid
        target_guid : 目标guid
        weapon_dbid : 武器的dbid
        weapon_num : 武器数量
        return :
        lua执行成功/lua执行失败
        """
        return super().manual_attack(target_guid, weapon_dbid, weapon_num)

    def allocate_salvo_to_target(self, target, weaponDBID):
        """
        单元手动分配一次齐射攻击(打击情报目标), 或者纯方位攻击(打击一个位置)
        :param target:情报目标guid，例："fruo-fs24-2424jj" 或  坐标-tuple(lat, lon)，例:(40.90,30.0)
        :param weaponDBID:武器型号数据库id
        :return:
        """
        return super().allocate_salvo_to_target(target, weaponDBID)

    def unit_obeys_emcon(self, is_obey):
        """
        单元传感器面板， 单元是否遵循电磁管控条令
        :param is_obey: bool(true 或 false)
        :return: void
        """
        return super().unit_obeys_emcon(is_obey)
