# -*- coding:utf-8 -*-
##########################################################################################################
# File name : activeunit.py
# Create date : 2020-1-8
# Modified date : 2020-1-8
# All rights reserved:北京华戍防务技术有限公司
# Author:xy
##########################################################################################################
import re


class CActiveUnit:
    """
    活动单元（潜艇、水面舰艇、地面兵力及设施、飞机、卫星、离开平台射向目标的武器，不包含目标、传感器等）的父类
    """

    def __init__(self, strGuid, mozi_server, situation):
        # GUID
        self.strGuid = strGuid
        # 仿真服务类MoziServer实例
        self.mozi_server = mozi_server
        # 态势
        self.situation = situation
        # 活动单元传感器列表
        self.sensors = {}
        # 活动单元挂架
        self.mounts = {}
        # 活动单元挂载
        self.loadout = {}
        # 挂载方案的GUid
        self.m_LoadoutGuid = ""
        # 活动单元弹药库
        self.magazines = {}
        # 航路点
        self.way_points = {}
        # 对象类名
        self.ClassName = ""
        # 名称
        self.strName = ""
        # 地理高度
        self.fAltitude_AGL = 0.0
        # 海拔高度
        self.iAltitude_ASL = 0
        # 所在推演方ID
        self.m_Side = ""
        # 单元类别
        self.strUnitClass = ""
        # 当前纬度
        self.dLatitude = 0.0
        # 当前经度
        self.dLongitude = 0.0
        # 当前朝向
        self.fCurrentHeading = 0.0
        # 当前速度
        self.fCurrentSpeed = 0.0
        # 当前海拔高度
        self.fCurrentAltitude_ASL = 0.0
        # 倾斜角
        self.fPitch = 0.0
        # 翻转角
        self.fRoll = 0.0
        # 获取期望速度
        self.fDesiredSpeed = 0.0
        # 获取最大油门
        self.m_MaxThrottle = 0
        # 最大速度
        self.fMaxSpeed = 0.0
        # 最小速度
        self.fMinSpeed = 0.0
        # 当前高度
        self.fCurrentAlt = 0.0
        # 期望高度
        self.fDesiredAlt = 0.0
        # 最大高度
        self.fMaxAltitude = 0.0
        # 最小高度
        self.fMinAltitude = 0.0
        # 军标ID
        self.strIconType = ""
        # 普通军标
        self.strCommonIcon = ""
        # 数据库ID
        self.iDBID = 0
        # 是否可操作
        self.bIsOperating = False
        # 编组ID
        self.m_ParentGroup = ""
        # 停靠的设施的ID(关系)
        self.m_DockedUnits = ""
        # 单元的停靠设施(部件)
        self.m_DockFacilitiesComponent = ""
        # 停靠的飞机的ID(关系)
        self.m_DockAircrafts = ""
        # 单元的航空设施(部件)
        self.m_AirFacilitiesComponent = ""
        # 单元的通信设备及数据链(部件)
        self.m_CommDevices = ""
        # 单元的引擎(部件)
        self.m_Engines = ""
        # 传感器，需要构建对象类,所以只传ID
        self.m_Sensors = ""
        # 挂架
        self.m_Mounts = ""
        # 毁伤状态
        self.strDamageState = ""
        # 失火
        self.iFireIntensityLevel = 0
        # 进水
        self.iFloodingIntensityLevel = 0
        # 分配的任务
        self.m_AssignedMission = ""
        # 作战条令
        self.m_Doctrine = None
        # 系统右栏->对象信息->作战单元武器
        self.m_UnitWeapons = ""
        # 路径点
        self.m_WayPoints = ""
        # 训练水平
        self.m_ProficiencyLevel = 0
        # 是否是护卫角色
        self.bIsEscortRole = False
        # 当前油门
        self.m_CurrentThrottle = 0
        # 通讯设备是否断开
        self.bIsCommsOnLine = False
        self.bIsIsolatedPOVObject = False
        # 地形跟随
        self.bTerrainFollowing = False
        self.bIsRegroupNeeded = False
        # 保持阵位
        self.bHoldPosition = False
        # 是否可自动探测
        self.bAutoDetectable = False
        # 当前货物
        self.m_Cargo = ""
        # 燃油百分比，作战单元燃油栏第一个进度条的值
        self.dFuelPercentage = 0.0
        # 获取AI对象的目标集合# 获取活动单元AI对象的每个目标对应显示不同的颜色集合
        self.m_AITargets = ""
        # 获取活动单元AI对象的每个目标对应显示不同的颜色集合
        self.m_AITargetsCanFiretheTargetByWCSAndWeaponQty = ""
        # 获取单元的通讯链集合
        self.m_CommLink = ""
        # 获取传感器
        self.m_NoneMCMSensors = ""
        # 获取显示"干扰"或"被干扰"
        self.iDisturbState = 0
        # 单元所属多个任务数量
        self.iMultipleMissionCount = 0
        # 单元所属多个任务guid拼接
        self.m_MultipleMissionGUIDs = ""
        # 是否遵守电磁管控
        self.bObeysEMCON = False
        # 武器预设的打击航线
        self.m_strContactWeaponWayGuid = ""
        # 停靠参数是否包含码头
        self.bDockingOpsHasPier = False
        # 弹药库
        self.m_Magazines = ""
        # 被摧毁
        self.dPBComponentsDestroyedWidth = 0.0
        # 轻度
        self.dPBComponentsLightDamageWidth = 0.0
        # 中度
        self.dPBComponentsMediumDamageWidth = 0.0
        # 重度
        self.dPBComponentsHeavyDamageWidth = 0.0
        # 正常
        self.dPBComponentsOKWidth = 0.0
        # 配属基地
        self.m_HostActiveUnit = ""
        # 状态
        self.strActiveUnitStatus = ""
        # 精简
        self.doctrine = None

    def get_assigned_mission(self):
        """
        获取分配的任务
        :return:
        """
        return self.situation.get_obj_by_guid(self.m_AssignedMission)

    def get_original_detector_side(self):
        """
        获取单元所在方
        :return:
        """
        return self.situation.side_dic[self.m_Side]

    def get_par_group(self):
        """
        获取父级编组
        :return:
        """
        return self.situation.group_dic[self.m_ParentGroup]

    def get_docked_units(self):
        """
        获取停靠单元
        :return:
        """
        docked_units = {}
        docked_units_guid = self.m_DockedUnits.split("@")
        for guid in docked_units_guid:
            if guid in self.situation.submarine_dic:
                docked_units[guid] = self.situation.submarine_dic[guid]
            elif guid in self.situation.ship_dic:
                docked_units[guid] = self.situation.ship_dic[guid]
            elif guid in self.situation.facility_dic:
                docked_units[guid] = self.situation.facility_dic[guid]
            elif guid in self.situation.aircraft_dic:
                docked_units[guid] = self.situation.aircraft_dic[guid]
            elif guid in self.situation.satellite_dic:
                docked_units[guid] = self.situation.satellite_dic[guid]

    def get_doctrine(self):
        """
        获取推演方条令
        by aie
        """
        if self.m_Doctrine in self.situation.doctrine_dic:
            doctrine = self.situation.doctrine_dic[self.m_Doctrine]
            doctrine.category = 'Unit'  # 需求来源：20200331-2/2:Xy
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
        kinds = ['CWeapon', 'CUnguidedWeapon', 'CWeaponImpact']
        if self.ClassName in kinds:
            return '本身是武器实体'
        weapon_record = self.m_UnitWeapons
        lst = weapon_record.split('@')
        lst1 = [k.split('$') for k in lst]
        return [x for x in lst1 if x != ['']]

    def get_valid_weapon_load(self):
        mnts = self.get_mounts()
        # mnts_lr = list({v.m_LoadRatio: k for k, v in mnts.items()})
        mnts_lr = list(v.m_LoadRatio for k, v in mnts.items())
        rcrds = []
        for k in mnts_lr:
            rcrds.extend(k.split('@'))
        if self.ClassName == 'CAircraft':
            ldt = self.get_loadout()
            ldt_lr = list({v.m_LoadRatio: k for k, v in ldt.items()})
            for k in ldt_lr:
                rcrds.extend(k.split('@'))
        load_ratios = [k.split('$') for k in rcrds]
        wpn_dbids = self.get_weapon_dbids()
        titles = ['strGuid', 'dbid', 'validLoad', 'maxLoad']
        wpn_ldr = {k[1]: {titles[i]: k[i] for i in range(len(titles))} for k in load_ratios if k[1] in wpn_dbids}
        wpn_infos = self.get_weapon_infos()
        # {wpn_ldr[k[1]].update({'strName': k[0]}) for k in wpn_infos}
        wpn_valid_ldr = {v['strGuid']: v for v in wpn_ldr.values()}
        return wpn_valid_ldr

    def get_mounts(self):
        """
        获取挂架信息
        :return:
        """
        mounts_guid = self.m_Mounts.split('@')
        mounts_dic = {}
        for guid in mounts_guid:
            if guid in self.situation.mount_dic:
                mounts_dic[guid] = self.situation.mount_dic[guid]
        return mounts_dic

    def get_loadout(self):
        """
        获取挂载
        :return:
        """
        loadout_dic = {}
        loadout_guid = self.m_LoadoutGuid.split('@')
        for guid in loadout_guid:
            if guid in self.situation.loadout_dic:
                loadout_dic[guid] = self.situation.loadout_dic[guid]
        return loadout_dic

    def get_magazines(self):
        """
        获取弹药库
        """
        magazines_dic = {}
        magazines_guid = self.m_Magazines.split('@')
        for guid in magazines_guid:
            if guid in self.situation.magazine_dic:
                magazines_dic[guid] = self.situation.magazine_dic[guid]
        return magazines_dic

    def get_sensor(self):
        """
        获取传感器
        :return:
        """
        sensors_guid = self.m_NoneMCMSensors.split('@')
        sensors_dic = {}
        for guid in sensors_guid:
            if guid in self.situation.sensor_dic:
                sensors_dic[guid] = self.situation.sensor_dic[guid]
        return sensors_dic

    def get_range_to_contact(self, contact_guid):
        """
        功能：
        参数：
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：
        """
        cmd = "print(Tool_Range('{}','{}'))".format(self.strGuid, contact_guid)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def plot_course(self, course_list):
        """
        规划单元航线
        :param course_list: list, [(lat, lon)]
        例子：[(40, 39.0), (41, 39.0)]
        :return:
        """
        if not course_list:
            return
        course_para = "{ longitude=" + str(course_list[0][1]) + ",latitude=" + str(course_list[0][0]) + "}"
        for point in course_list[1:]:
            latitude = point[0]
            longitude = point[1]
            course_para = course_para + ",{ longitude=" + str(longitude) + ",latitude=" + str(latitude) + "}"
        cmd_str = "HS_LUA_SetUnit({side='" + self.m_Side + "', guid='" + self.strGuid + "', course={" + course_para + \
                  "}})"
        return self.mozi_server.send_and_recv(cmd_str)

    def get_way_points_info(self):
        """
        获取本单元航路点信息
        retutn : list
        """
        way_points = []
        if self.m_WayPoints != "":
            guid_list = self.m_WayPoints.split("@")
            for guid in guid_list:
                point_obj = self.situation.waypoint_dic[guid]
                way_points.append({
                    "latitude": point_obj.dLatitude,
                    "longitude": point_obj.dLongitude,
                    "Description": point_obj.strWayPointDescription
                })
        return way_points

    def get_ai_targets(self):
        """
        获取活动单元的Ai目标集合
        return : list
        """
        contacts_dic = {}
        tar_guid_list = self.m_AITargets.split('@')
        for tar_guid in tar_guid_list:
            if tar_guid in self.situation.contact_dic:
                contacts_dic[tar_guid] = self.situation.contact_dic[tar_guid]
        return contacts_dic

    def unit_obeys_emcon(self, is_obey):
        """
        单元传感器面板， 单元是否遵循电磁管控条令
        :param is_obey: bool(True 或 False)
        :return: void
        """
        state = str(is_obey).lower()
        return self.mozi_server.send_and_recv("Hs_UnitObeysEMCON('{}', {})".format(self.strGuid, state))

    def allocate_weapon_to_target(self, target, weaponDBID, weapon_count):
        """
        单元手动攻击(打击情报目标), 或者纯方位攻击(打击一个位置)
        :param target: 情报目标guid 或  坐标-tuple(lat, lon)
        :param weaponDBID: int, 武器型号数据库id
        :param weapon_count: int, 分配数量
        :return:
        """
        if type(target) == str:
            table = "{TargetGUID ='" + target + "'}"
        elif type(target) == tuple:
            table = "{TargetLatitude =" + str(target[0]) + ", TargetLongitude = " + str(target[1]) + "}"
        else:
            raise Exception("target 参数错误")
        return self.mozi_server.send_and_recv("Hs_ScenEdit_AllocateWeaponToTarget('{}',{},{},{})".format(
            self.strGuid, table, str(weaponDBID), str(weapon_count)))

    def unit_auto_detectable(self, isAutoDetectable):
        """
        单元自动探测到
        isAutoDetectable：是否探测到 true?false complate
        """
        unitAutoDetectable = "ScenEdit_SetUnit({guid='%s',autodetectable=%s})" % (self.strGuid, isAutoDetectable)
        return self.mozi_server.send_and_recv(unitAutoDetectable)

    def unit_drop_target_contact(self, contact_guid):
        """
        函数功能：放弃对指定目标进行攻击。 
        参数说明： 
        1）ContactID：字符串。目标 GUID
        修订：aie
        时间：4/8/20
        """
        lua_scrpt = "Hs_UnitDropTargetContact('{}','{}','{}')".format(self.m_Side, self.strGuid, contact_guid)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def unit_drop_target_all_contact(self):
        """
        函数功能：放弃对所有目标进行攻击，脱离交战状态。 
        参数说明： 
        1）UnitNameOrID：字符串。单元名称或 GUID
        """
        return self.mozi_server.send_and_recv("Hs_UnitDropTargetAllContact('{}')".format(self.strGuid))

    def ignore_plotted_course_when_attacking(self, enum_ignore_plotted):
        """
        在攻击时是否忽略计划航线，是、否、与上级一致
        :param enum_ignore_plotted:IgnorePlottedCourseWhenAttacking
        :return:
        """
        if enum_ignore_plotted.value == 999:
            para_str = 'Inherited'
        else:
            para_str = enum_ignore_plotted
        return self.mozi_server.send_and_recv(
            "Hs_LPCWAttackSUnit('{}','{}','{}')".format(self.strName, self.strGuid, para_str))

    def follow_terrain(self, is_followed):
        """
        设置当前单元（飞机）的飞行高度跟随地形
        :param is_followed:bool, True:跟随地形
        :return:
        """
        set_str = str(is_followed).lower()
        lua_scrpt = "ScenEdit_SetUnit(guid='%s',  TEEEAINFOLLOWING = %s})" % (str(self.strGuid), set_str)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def delete_coursed_point(self, point_index=None, clear=False):
        """
        单元删除航路点
        :param point_index: list:删除多个航路点 [0, 1], or int：删除一个航路点，
        :param clear: bool, True:清空航路点
        :return:
        """
        lua_scrpt = ""
        if clear:
            if self.m_WayPoints != "":
                point_count = len(self.m_WayPoints.split("@"))
                for point in range(point_count - 1, -1, -1):
                    lua_scrpt += ('Hs_UnitOperateCourse("%s",%d,0.0,0.0,"Delete")' % (self.strGuid, point))
        else:
            if isinstance(point_index, list):
                if len(point_index) > 1 and point_index[-1] > point_index[0]:
                    point_index.reverse()
                for point in point_index:
                    lua_scrpt += ('Hs_UnitOperateCourse("%s",%d,0.0,0.0,"Delete")' % (self.strGuid, point))
            elif isinstance(point_index, int):
                lua_scrpt = "Hs_UnitOperateCourse('%s',%d,0.0,0.0,'Delete')" % (self.strGuid, point_index)
            return self.mozi_server.send_and_recv(lua_scrpt)

    def return_to_base(self):
        """
        单元返航
        :return:
        """
        return self.mozi_server.send_and_recv("HS_ReturnToBase('{}')".format(self.strGuid))

    def select_new_base(self, base_guid):
        """
        单元选择新基地/新港口
        :param base_guid: 新基地的guid
        :return:
        """
        lua_scrpt = "ScenEdit_SetUnit({unitname='%s',base='%s'})" % (self.strGuid, base_guid)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def hold_positon(self, is_hold):
        """
        函数功能：命令面上指定单元设置是否保持阵位。
        参数说明：
        1）is_hold：布尔值。状态标识符（true：是，false：否）
        """
        bTrueOrFalse = str(is_hold).lower()
        return self.mozi_server.send_and_recv("Hs_HoldPositonSelectedUnit('{}',{})".format(self.strGuid, bTrueOrFalse))

    def leave_dock_alone(self):
        """
        功能：单独出航
        参数：
        返回：
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/28/20
        """
        cmd = "Hs_ScenEdit_DockingOpsGroupOut({'%s'})" % (self.strGuid)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def assign_unitlist_to_mission(self, mission_name):
        """
        分配加入到任务中
        :param mission_name: str, 任务名称
        """
        lua_scrpt = "ScenEdit_AssignUnitToMission('{}', '{}')".format(self.strGuid, mission_name)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def assign_unitlist_to_mission_escort(self, mission_name):
        """
        将单元分配为某打击任务的护航任务
        :param mission_name: 任务名称
        :return: table 存放单元的名称或者GUID
        """
        lua_scrpt = "Hs_AssignUnitListToMission('{}', '{}')".format(self.strGuid, mission_name)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def cancel_assign_unitlist_to_mission(self):
        """
        将单元取消分配任务
        :return:
        """
        lua_scrpt = "ScenEdit_AssignUnitToMission('{}', 'none')".format(self.strGuid)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def set_fuel_qty(self, remainingFuel):
        """
        类型:编辑所有函数
        设置单元燃油量
        strRemainingFuel 油量
        """
        return self.mozi_server.send_and_recv("Hs_SetFuelQty('{}','{}')".format(self.strGuid, remainingFuel))

    def set_unit_heading(self, heading):
        """
        设置朝向
        heading 朝向
        exampl
        set_unit_heading('016b72ba-2ab2-464a-a340-3cfbfb133ed1',30):
        修订：aie
        时间：4/8/20
        """

        lua_scrpt = "ScenEdit_SetUnit({guid ='%s' ,heading = %s})" % (self.strGuid, heading)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def auto_attack(self, contact_guid):
        """
        自动攻击目标
        :param contact_guid: 目标guid
        :return:
        """
        cmd = self.mozi_server.send_and_recv(
            "ScenEdit_AttackContact(%s, %s, {mode=%s})" % (self.strGuid, contact_guid, 0))
        return self.mozi_server.send_and_recv(cmd)

    def set_desired_speed(self, desired_speed):
        """
        设置单元的期望速度
        :param desired_speed: float, 千米/小时
        :return: 所操作单元的完整描述子
        """
        if isinstance(desired_speed, int) or isinstance(desired_speed, float):
            lua_scrpt = "ScenEdit_SetUnit({guid='" + str(self.strGuid) + "', manualSpeed='" + str(
                desired_speed / 1.852) + "'})"
            return self.mozi_server.send_and_recv(lua_scrpt)

    def set_throttle(self, enum_throttle):
        """
        设置单元油门
        :param enum_throttle: Throttle, 油门选择
        :return:
        修订：aie
        时间：4/8/20
        """
        lua_scrpt = "ScenEdit_SetUnit({guid='%s', throttle=%s})" % (self.strGuid, enum_throttle)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def set_desired_height(self, desired_height, moveto):
        """
        设置单元的期望高度
        :param desired_height: 期望高度值, 海拔高度：m
        :return:
        """
        if isinstance(desired_height, int) or isinstance(desired_height, float):
            lua_scrpt = "ScenEdit_SetUnit({guid='" + str(self.strGuid) + "',  altitude ='" + str(
                desired_height) + "', moveto='" + moveto + "'}) "
            return self.mozi_server.send_and_recv(lua_scrpt)
        else:
            pass

    def set_radar_shutdown(self, on_off):
        """
        设置雷达开关机
        :param on_off: 开关机 true 开机  false 关机
        :return: 
        """
        lua_scrpt = "Hs_ScenEdit_SetUnitSensorSwitch({guid = '%s',rader = %s })" % (self.strGuid, on_off)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def set_sonar_shutdown(self, on_off):
        """
        
        :param on_off: 开关机 true 开机  false 关机
        :return: 
        """
        lua_scrpt = "Hs_ScenEdit_SetUnitSensorSwitch({guid = '%s',sensor = %s })" % (self.strGuid, on_off)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def set_oecm_shutdown(self, on_off):
        """
        设置干扰开关机
        :param on_off: 开关机 true 开机  false 关机
        :return: 
        """
        lua_scrpt = "Hs_ScenEdit_SetUnitSensorSwitch({guid = '%s',OECM = %s})" % (self.strGuid, on_off)
        return self.mozi_server.send_and_recv(lua_scrpt)

    def manual_attack(self, target_guid, weapon_dbid, weapon_num):
        """
        手动开火函数
        作者：解洋
        target_guid : 目标guid
        weapon_dbid : 武器的dbid
        weapon_num : 武器数量strWeaponInfo
        """
        manual_lua = 'Hs_ScenEdit_AllocateWeaponToTarget(\'%s\',{TargetGUID=\'%s\'},%s,%s)' % (
            self.strGuid, target_guid, weapon_dbid, weapon_num)
        return self.mozi_server.send_and_recv(manual_lua)

    def set_single_out(self, unit_class_name):
        """
        设置在基地内单元出动
        base_guid : 单元所在机场的guid
        unit_guid : 单元的guid
        return :
        lua执行成功/lua执行失败
        """
        if unit_class_name == 'CAircraft':
            lua_scrpt = "Hs_ScenEdit_AirOpsSingleOut({'%s'})" % self.strGuid
        else:
            return "不是飞机"
        return self.mozi_server.send_and_recv(lua_scrpt)

    def drop_active_sonobuoy(self, deepOrShallow):
        """
        类别：推演所用函数
        投放主动声呐
        deepOrShallow 投放深浅 例: dedp ，shallow
        修订：aie
        时间：4/9/20
        """
        side = self.situation.side_dic[self.m_Side]
        cmd = "Hs_DropActiveSonobuoy('{}','{}','{}')".format(side.strName, self.strGuid, deepOrShallow)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def drop_passive_sonobuoy(self, deepOrShallow):
        """
        类别：推演所用函数
        投放被动声呐
        sidename 方的名称
        deepOrShallow 投放深浅 例: dedp ，shallow
        修订：aie
        时间：4/9/20
        """
        side = self.situation.side_dic[self.m_Side]
        cmd = "Hs_DropPassiveSonobuoy('{}','{}','{}')".format(side.strName, self.strGuid, deepOrShallow)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def drop_sonobuoy(self, sideName, deepOrShallow, passiveOrActive):
        """
        投放声呐,目前只能飞机投放声纳
        :param sideName: 方的名称
        :param deepOrShallow: 深浅类型（'deep'：温跃层之下，'shallow'：温跃层之上）
        :param passiveOrActive: 主被动类型（'active'：主动声呐，'passive'：被动声呐）
        :return: 
        """
        return self.mozi_server.send_and_recv(
            "Hs_DropSonobuoy('{}','{}','{}','{}')".format(sideName, self.strGuid, deepOrShallow, passiveOrActive))

    def set_own_side(self, oldside, newSide):
        """
        类别：编辑所用函数
        改变单元所属阵营
        oldside 现在的方名称
        newSide 新的方名称
        案例：
        ScenEdit_SetUnitSide({side=' 红 方 ',name=' F-14E 型 “ 超 级 雄 猫 ” 战 斗 机',newside='蓝方'}
        """
        return self.mozi_server.send_and_recv(
            "ScenEdit_SetUnitSide({side='%s',name='%s',newside='%s'})" % (oldside, self.strName, newSide))

    def set_loadout(self, loadoutId, timeToReady_Minutes, ignoreMagazines, excludeOptionalWeapons):
        """
        函数功能：将添加/改变的载荷
        UnitName string 要改变载荷的单元名称/GUID
        LoadoutID number 新载荷的 ID，0 = 使用当前载荷
        TimeToReady_Minutes number 载荷准备时间（分钟）
        IgnoreMagazines bool 新载荷是否依赖于已准备好武器的弹仓
        ExcludeOptionalWeapons bool 从载荷中排除可选武器（可选）
        """
        return self.mozi_server.send_and_recv(
            "ScenEdit_SetLoadout ({UnitName='%s',LoadoutID='%s',TimeToReady_Minutes='%s',IgnoreMagazines=%s,"
            "ExcludeOptionalWeapons=%s)" % (
                self.strName, loadoutId, timeToReady_Minutes, ignoreMagazines, excludeOptionalWeapons))

    def reload_weapon(self, weapon_dbid, number, weapon_max):
        """
        将武器加入装具
        weapon_dbid 武器 DBID
        number 要添加的数量
        weapon_max 装载武器的最大容量
        """
        return self.mozi_server.send_and_recv(
            "ScenEdit_AddReloadsToUnit({guid='%s', w_dbid=%s, number=%s, w_max=%s})" % (
                self.strGuid, weapon_dbid, number, weapon_max))

    def load_cargo(self, cargo_dbid):
        """
        函数功能：添加货物
        函数类型：推演类型
        cargoDBID 货物dbid
        """
        return self.mozi_server.send_and_recv("Hs_AddCargoToUnit('{}',{})".format(self.strGuid, cargo_dbid))

    def remove_cargo(self, cargo_dbid):
        """
        函数功能：删除货物
        函数类型：推演类型
        cargoDBID 货物dbid
        """
        return self.mozi_server.send_and_recv("Hs_RemoveCargoToUnit('{}',{})".format(self.strGuid, cargo_dbid))

    def set_magazine_weapon_current_load(self, wpnrec_guid, current_load):
        """
        函数类别：编辑函数
        函数功能：设置弹药库武器数量
        Hs_ScenEdit_SetMagazineWeaponCurrentLoad({guid='%1',WPNREC_GUID='%2',currentLoad=%3})
        guid 单元
        wpnrec_guid 武器guid
        currentLoad 当前挂载
        """
        return self.mozi_server.send_and_recv(
            "Hs_ScenEdit_SetMagazineWeaponCurrentLoad({guid='%s',WPNREC_GUID='%s',currentLoad=%s})" % (
                self.strGuid, wpnrec_guid, current_load))

    def remove_magazine(self, magazine_guid):
        """
        删除弹药库
        Hs_ScenEdit_RemoveMagazine({guid='%1', magazine_guid='%2'})
        guid 单元
        magazine_guid 弹药库
        """
        return self.mozi_server.send_and_recv(
            "Hs_ScenEdit_RemoveMagazine({guid='%s', magazine_guid='%s'})" % (self.strGuid, magazine_guid))

    def set_magazine_state(self, magazine_guid, state):
        """
        设置弹药库状态
        guid 单元
        magazine_guid 弹药库guid
        state  状态
        """
        return self.mozi_server.send_and_recv(
            "Hs_ScenEdit_SetMagazineState({guid='%s', magazine_guid='%s',state='%s'}" % (
                self.strGuid, magazine_guid, state))

    def set_weapon_current_load(self, wpn_guid, number):
        """
        设置武器数量
        unitname   单元名称
        wpn_guid   武器guid
        number     数量
        """
        return self.mozi_server.send_and_recv(
            "Hs_ScenEdit_SetWeaponCurrentLoad({guid='%s',wpn_guid='%s',%s})" % (self.strGuid, wpn_guid, number))

    def set_weapon_reload_priority(self, wpnrec_guid, priority):
        """
        设置武器重新装载优先级
        guid 单元guid
        WPNREC_GUID 弹药库guid
        priority
        """
        return self.mozi_server.send_and_recv(
            "Hs_ScenEdit_SetWeaponReloadPriority({guid='%s',WPNREC_GUID='%s',IsReloadPriority=%s})" % (
                self.strGuid, wpnrec_guid, priority))

    def add_weapon_to_unit_magazine(self, mag_guid, wpn_dbid, number):
        """
       函数类别：编辑所用的函数
       功能说明：往弹药库内添加武器
        side 方
        guid 单元
        mag_guid 弹药库
        wpn_dbid 武器dbid
        number 数量
        """
        return self.mozi_server.send_and_recv(
            "Hs_AddWeaponToUnitMagazine({side='%s',guid='%s',mag_guid='%s',wpn_dbid=%s,number=%s})" % (
                self.m_Side, self.strGuid, mag_guid, wpn_dbid, number))

    def switch_sensor(self, radar='false', sonar='false', oecm='false'):
        """
        函数功能：同时设置单元上多种类型传感器的开关状态。
        参数说明：
        1）table：表对象：
         RADER：布尔值。雷达开关状态标识符（true：开，false：关）；
         SONAR：布尔值。声呐开关状态标识符（true：开，false：关）；
         OECM：布尔值。攻击性电子对抗手段（即电子干扰）开关状态标识符（true：开，false：关）。
        """
        lua = "Hs_ScenEdit_SetUnitSensorSwitch({guid='%s', RADER=%s,SONAR=%s,OECM=%s})" % (
            self.strGuid, radar, sonar, oecm)
        return self.mozi_server.send_and_recv(lua)

    def wcsf_contact_types_unit(self, holdTightFreeInherited):
        """
        函数功能：控制指定单元对所有目标类型的攻击状态。
        参数说明：
        1）HoldTightFreeInherited：控制状态标识符（'Hold'：禁止，'Tight'：限制，
        'Free'：自由，'Inherited'：按上级条令执行）。
        """
        lua = "Hs_WCSFAContactTypesSUnit('%s','%s','%s')" % (self.m_Side, self.strGuid, holdTightFreeInherited)
        return self.mozi_server.send_and_recv(lua)

    def allocate_all_weapons_to_target(self, targetGuid, weaponDbid):
        """
        函数功能：为手动交战分配同类型所有武器。
        参数说明：
        1）actriveUnitGuid：字符串。活动单元 GUID；
        2）targetGuid：字符串。目标单元 GUID；
        3）weaponDbid：数值型。武器数据库 GUID
        """
        lua = "Hs_ScenEdit_AllocateAllWeaponsToTarget('%s','%s',%s)" % (self.strGuid, targetGuid, weaponDbid)
        return self.mozi_server.send_and_recv(lua)

    def remove_salvo_target(self, weaponSalvoGuid):
        """
        函数功能：取消手动交战时齐射攻击目标。
        参数说明：
        1）WeaponSalvoGUID：字符串。武器齐射 GUID。
        """
        lua = "Hs_ScenEdit_RemoveWeapons_Target('%s','%s')" % (self.strGuid, weaponSalvoGuid)
        return self.mozi_server.send_and_recv(lua)

    def set_salvo_timeout(self, b_isSalvoTimeout='false'):
        """
        作者：解洋
        时间：2020-3-11
        类别：推演使用函数
        函数功能：控制手动交战是否设置齐射间隔。
        参数说明：
        1）b_isSalvoTimeout：是否设置齐射间隔的状态标识符（true：是，false：
        否）
        """
        lua = "Hs_ScenEdit_SetSalvoTimeout(%s) " % b_isSalvoTimeout
        return self.mozi_server.send_and_recv(lua)

    def allocate_salvo_to_target(self, target, weaponDBID):
        """
        单元手动分配一次齐射攻击(打击情报目标), 或者纯方位攻击(打击一个位置)
        :param target:情报目标guid，例："fruo-fs24-2424jj" 或  坐标-tuple(lat, lon)，例:(40.90,30.0)
        :param weaponDBID:武器型号数据库id
        :return:
        """
        if type(target) == str:
            table = "{TargetGUID ='" + target + "'}"
        elif type(target) == tuple:
            table = "{TargetLatitude =" + str(target[0]) + ", TargetLongitude = " + str(target[1]) + "}"
        else:
            raise Exception("target 参数错误")
        lua_scrpt = "Hs_ScenEdit_AllocateSalvoToTarget('{}',{},{})".format(self.strGuid, table, str(weaponDBID))
        return self.mozi_server.send_and_recv(lua_scrpt)

    def allocate_weapon_auto_targeted(self, target_guids, weapon_dbid, num):
        """
        函数功能：为自动交战进行弹目匹配。此时自动交战意义在于不用指定对多
        个目标的攻击顺序。
        参数说明：
        1）actriveUnitGuid：字符串。活动单元 GUID；
        2）{contactGuids}：表对象。目标单元 GUID 组成的表对象。
        3）weaponDbid：数值型。武器数据库 GUID；
        4）Num：数值型。武器发射数量
        """
        targets = None
        for target_guid in target_guids:
            if targets:
                targets += ",'%s'" % target_guid
            else:
                targets = "'%s'" % target_guid
        lua = "Hs_AllocateWeaponAutoTargeted(%s,{%s},%s,%s)" % (self.strGuid, targets, weapon_dbid, num)
        return self.mozi_server.send_and_recv(lua)

    def auto_target(self, contacts):
        """
        函数功能：让单元自动进行弹目匹配并攻击目标。
        参数说明：
        1）actriveUnitGuid：字符串。活动单元 GUID；
        2）{contactGuids}：表对象。目标单元 GUID 组成的表对象
        修订：aie
        时间：4/8/20
        """
        contacts_guids = []
        for k, v in contacts.items():
            s = "'%s'" % k
            contacts_guids.append(s)
        contacts_guids = ','.join(contacts_guids)
        if contacts_guids == '':
            contacts_guids = None
        cmd = "Hs_AutoTargeted('%s',{%s})" % (self.strGuid, contacts_guids)
        self.mozi_server.throw_into_pool(cmd)
        return self.mozi_server.send_and_recv(cmd)

    def add_to_host(self, base_guid):
        """
       作者：赵俊义
       日期：2020-3-9
       函数类别：编辑所用的函数
       功能说明：将单元部署进基地
        @param base_guid:基地的guid
        @return:
        """
        return self.mozi_server.send_and_recv("ScenEdit_HostUnitToParent('{}','{}')".format(self.strGuid, base_guid))

    def set_attribute(self, **kwargs):
        """
       作者：赵俊义
       日期：2020-3-9
       函数类别：编辑所用的函数
       功能说明：设置已有单元的属性
        @param kwargs: 不同的属性和属性值
        @return:表对象。单元属性的详细信息
        """
        (key, value), = kwargs.items()
        return self.mozi_server.send_and_recv("ScenEdit_SetUnit({%s,%s =%r})" % (self.strGuid, key, value))

    def set_component_damage(self, **kwargs):
        """
       作者：赵俊义
       日期：2020-3-9
       函数类别：编辑所用的函数
       功能说明：设置单元各组件的毁伤状态
        @param kwargs: 组件的名称和毁伤状态组成的字典
        @return:
        """
        key, value = kwargs.items()
        return self.mozi_server.send_and_recv(
            "ScenEdit_SetUnitDamage({%s, %s,  {{%s, %r}}})" % (self.m_Side, self.strGuid, key, value))

    def self_update(self, options):
        result = self.mozi_server.send_and_recv(" ReturnObj(scenEdit_UpdateUnit({}))".format(options))
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

    def add_mount(self, **kwargs):
        """
       作者：赵俊义
       日期：2020-3-9
       函数类别：编辑所用的函数
       功能说明：为单元添加武器挂架
        @param kwargs:挂架
        @return:
        """
        for key, value in kwargs:
            self.mozi_server.send_and_recv("Hs_ScenEdit_AddMount({{},m{},{}})".format(self.strName, key, value))

    def remove_mount(self, i):
        """
       作者：赵俊义
       日期：2020-3-9
       函数类别：编辑所用的函数
       功能说明：删除单元中指定的武器挂架
        @param i:武器挂架的索引值
        @return:
        """
        return self.mozi_server.send_and_recv(
            "Hs_ScenEdit_RemoveMount({unitname='%s',mout_guid=%s})" % (self.strName, self.mounts[i].mount_guid))

    def add_weapon(self, guid, wpn_dbid, MOUNT_GUID):
        """
       函数类别：编辑所用的函数
       功能说明：给单元挂架或飞机当前挂载方案中添加武器
        @param guid:单元guid
        @param wpn_dbid:武器dbid
        @param MOUNT_GUID:挂架guid
        @return:
        """
        return self.mozi_server.send_and_recv(
            "Hs_ScenEdit_AddWeapon({guid='%s',wpn_dbid=%s,MOUNT_GUID = '%s',IsTenThousand=true})" % (
                guid, wpn_dbid, MOUNT_GUID))

    def remove_weapon(self, unitname, wpn_guid):
        """
       函数类别：编辑所用的函数
       功能说明：通过武器属性删除单元的武器
        @param unitname: 单元名称
        @param wpn_guid: 武器guid
        @return:
        """
        return self.mozi_server.send_and_recv(
            "Hs_ScenEdit_RemoveWeapon({unitname='%s', wpn_guid='%s'})" % (unitname, wpn_guid))

    def update_way_point(self, wayPointIndex, lat, lon, **kwargs):
        """
        作者：赵俊义
        日期：2020-3-11
        函数功能：更新单元航路点的具体信息,必须首先有一个航路点
        函数类别：推演函数
        :param wayPointIndex: 数值型。航路点在航路点序列（以 0 为起始序号）中的序号
        :param lat: 纬度
        :param lon: 经度
        :param kwargs
        :return:
        """
        tmp = [(k, v) for k, v in kwargs.items()]
        return self.mozi_server.send_and_recv(
            r'Hs_UpdateWayPoint("%s",%s,{latitude="%s",longitude="%s", %s=%s,%s=%s})' % (
                self.strGuid, wayPointIndex, lat, lon, tmp[0][0], tmp[0][1], tmp[1][0], tmp[1][1]))

    def set_way_point_sensor(self, wayPointIndex, sensor, sensorStatus):
        """
        函数功能：设置航路点传感器的开关状态
        函数类别：推演函数
        :param wayPointIndex:航路点顺序
        :param sensor:传感器
        :param sensorStatus:传感器状态
        :return:
        """
        return self.mozi_server.send_and_recv(
            "updateWayPointSensorStatus('{}',{},'{}','{}')".format(self.strGuid, wayPointIndex, sensor, sensorStatus))

    def set_unit_damage(self, overalldamage, comp_guid, level):
        """
        作者：赵俊义
        日期：2020-3-12
        函数功能：设置单元各组件的毁伤值
        函数类别：编辑函数
        :param overalldamage:数值型。总体毁伤
        :param comp_guid: 组件的guid
        :param level: 毁伤级别
        :return:
        """
        return self.mozi_server.send_and_recv("HS_SetUnitDamage({guid={},OVERALLDEMAGE={},components={{},'{}'}})"
                                              .format(self.strGuid, overalldamage, comp_guid, level))

    def set_magazine_weapon_number(self, mag_guid, wpn_dbid, number):
        """
        作者：赵俊义
        日期：2020-3-12
        函数功能：往单元的弹药库中添加指定数量的武器
        函数类别：编辑函数
        :param mag_guid:弹药库guid
        :param wpn_dbid:数值型。武器 dbid；
        :param number:数值型。武器数量。
        :return:
        """
        return self.mozi_server.send_and_recv(
            "ScenEdit_AddWeaponToUnitMagazine({name={},mag_guid={},wpn_dbid={},number={}})".format(self.strGuid,
                                                                                                   mag_guid, wpn_dbid,
                                                                                                   number))

    def set_unit_doctrine(self, num):
        cmd = "ScenEdit_SetDoctrine({guid='%s'},{weapon_control_status_air=%s})" % (self.strGuid, num)
        return self.mozi_server.send_and_recv(cmd)
