# _*_ coding : utf-8 _*_
'''
作者 : 解洋
时间: 2020-3-24
'''

from malib.envs.mozi.mozi_simu_sdk.args import *

class CAgent():
    def __init__(self):
        self.class_name = 'aircraft_'
        self.doctrine_num = 0
        self.mission_num = 0
        self.contact_num = 0
        self.aircraft_num = 0

    def test(self, scenario):
        for side_k, side_v in scenario.get_sides().items():
            doctrine = air_v.get_doctrine() #amended by aie
            if len(side_v.aircrafts) > 0:
                # 测试飞机
                for air_k, air_v in side_v.aircrafts.items():
                    if self.aircraft_num < 7:
                        self.aircraft_num += 1
                        # 属性
                        print('mount:')
                        mount = air_v.get_mounts()
                        print(mount)
                        for k, v in mount.items():
                            print(v.strName)
                            print(v.m_LoadRatio)
                        print('senaor')
                        print(air_v.get_sensor())
                        print('magazine')
                        print(air_v.get_magazines())
                        print('doctine')
                        print(doctrine)
                        print('loadout')
                        loadout = air_v.get_loadout()
                        for k, v in loadout.items():
                            print(v.strName)
                        print(air_v.get_loadout())
                        print('# 方位类型')
                        print(air_v.m_BearingType)
                        print('# 方位')
                        print(air_v.m_Bearing)
                        print('# 距离（转换为千米）')
                        print(air_v.m_Distance)
                        print('# 高低速交替航行)')
                        print(air_v.bSprintAndDrift)
                        print('# 载机按钮的文本描述')
                        print(air_v.strDockAircraft)
                        print('# 类别')
                        print(air_v.m_Category)
                        print('# 悬停')
                        print(air_v.fHoverSpeed)
                        print('(# 低速')
                        print(air_v.fLowSpeed)
                        print('# 巡航v')
                        print(air_v.fCruiseSpeed)
                        print('# 军力')
                        print(air_v.fMilitarySpeed)
                        print('# 加速')
                        print(air_v.fAddForceSpeed)
                        print('# 机型（战斗机，多用途，加油机...)')
                        print(air_v.m_Type)
                        print('# 宿主单元对象')
                        print(air_v.m_CurrentHostUnit)
                        print('# 挂载方案的DBID')
                        print(air_v.iLoadoutDBID)
                        print('# 挂载方案的GUid')
                        print(air_v.m_LoadoutGuid)
                        print('# 获取当前行动状态')
                        print(air_v.strAirOpsConditionString)
                        print('# 完成准备时间')
                        print(air_v.strFinishPrepareTime)
                        print('# 快速出动信息')
                        print(air_v.strQuickTurnAroundInfo)
                        print('# 显示燃油信息')
                        print(air_v.strFuelState)
                        print('# 期望高度')
                        print(air_v.fDesiredAltitude)
                        print('# 维护状态')
                        print(air_v.m_MaintenanceLevel)
                        print(air_v.fFuelConsumptionCruise)
                        print(air_v.fAbnTime)
                        print(air_v.iFuelRecsMaxQuantity)
                        print('# 当前油量')
                        print(air_v.iCurrentFuelQuantity)
                        print('# 是否快速出动')
                        print(air_v.bQuickTurnaround_Enabled)
                        print('# 是否有空中加油能力')
                        print(air_v.bIsAirRefuelingCapable)
                        print('# 加油队列header)')
                        print(air_v.strShowTankerHeader)
                        print('# 加油队列明细')
                        print(air_v.m_ShowTanker)
                        print('# 可受油探管加油')
                        print(air_v.m_bProbeRefuelling)
                        print('# 可输油管加油')
                        print(air_v.m_bBoomRefuelling)
                        print('# 航路点名称')
                        print(air_v.strWayPointName)
                        print('# 航路点描述')
                        print(air_v.strWayPointDescription)
                        print('# 航路点剩余航行距离')
                        print(air_v.strWayPointDTG)
                        print('# 航路点剩余航行时间')
                        print(air_v.WayPointTTG)
                        print('# 航路点需要燃油数')
                        print(air_v.strWayPointFuel)
                        print(air_v.strGuid)
                        print('# 活动单元传感器列表')
                        print(air_v.sensors)
                        print('# 活动单元挂架')
                        print(air_v.mounts)
                        print('# 活动单元弹药库')
                        print(air_v.magazines)
                        print('# 航路点')
                        print(air_v.way_points)
                        print('# 对象类名')
                        print(air_v.ClassName)
                        print('# 名称')
                        print(air_v.strName)
                        print('# Guid')
                        print(air_v.strGuid)
                        print('# 地理高度')
                        print(air_v.fAltitude_AGL)
                        print('# 海拔高度')
                        print(air_v.iAltitude_ASL)
                        print('# 所在推演方ID')
                        print(air_v.m_Side)
                        print('# 单元类别')
                        print(air_v.strUnitClass)
                        print('# 当前纬度')
                        print(air_v.dLatitude)
                        print('# 当前经度')
                        print(air_v.dLongitude)
                        print('# 当前朝向')
                        print(air_v.fCurrentHeading)
                        print('# 当前速度')
                        print(air_v.fCurrentSpeed)
                        print('# 当前海拔高度')
                        print(air_v.fCurrentAltitude_ASL)
                        print('# 倾斜角')
                        print(air_v.fPitch)
                        print('# 翻转角')
                        print(air_v.fRoll)
                        print('# 获取期望速度')
                        print(air_v.fDesiredSpeed)
                        print('# 获取最大油门')
                        print(air_v.m_MaxThrottle)
                        print('# 最大速度')
                        print(air_v.fMaxSpeed)
                        print('# 最小速度')
                        print(air_v.fMinSpeed)
                        print('# 当前高度')
                        print(air_v.fCurrentAlt)
                        print('# 期望高度')
                        print(air_v.fDesiredAlt)
                        print('# 最大高度')
                        print(air_v.fMaxAltitude)
                        print('# 最小高度')
                        print(air_v.fMinAltitude)
                        print('# 军标ID')
                        print(air_v.strIconType)
                        print('# 普通军标')
                        print(air_v.strCommonIcon)
                        print('# 数据库ID')
                        print(air_v.iDBID)
                        print('# 是否可操作')
                        print(air_v.bIsOperating)
                        print('# 编组ID')
                        print(air_v.m_ParentGroup)
                        print('# 停靠的设施的ID(关系)')
                        print(air_v.m_DockedUnits)
                        print('# 单元的停靠设施(部件)')
                        print(air_v.m_DockFacilitiesComponent)
                        print('# 停靠的飞机的ID(关系)')
                        print(air_v.m_DockAircrafts)
                        print('# 单元的航空设施(部件)')
                        print(air_v.m_AirFacilitiesComponent)
                        print('# 单元的通信设备及数据链(部件)')
                        print(air_v.m_CommDevices)
                        print('# 单元的引擎(部件')
                        print(air_v.m_Engines)
                        print('# 传感器，需要构建对象类,所以只传ID')
                        print(air_v.m_Sensors)
                        print('# 挂架')
                        print(air_v.m_Mounts)
                        print('# 毁伤状态')
                        print(air_v.strDamageState)
                        print('# 失火')
                        print(air_v.iFireIntensityLevel)
                        print('# 进水')
                        print(air_v.iFloodingIntensityLevel)
                        print('# 分配的任务')
                        print(air_v.m_AssignedMission)
                        print('# 作战条令')
                        print(air_v.m_Doctrine)
                        print('# 系统右栏->对象信息->作战单元武器')
                        print(air_v.m_UnitWeapons)
                        print('# 路径点')
                        print(air_v.m_WayPoints)
                        print('# 训练水平')
                        print(air_v.m_ProficiencyLevel)
                        print('# 是否是护卫角色')
                        print(air_v.bIsEscortRole)
                        print('# 当前油门')
                        print(air_v.m_CurrentThrottle)
                        print('# 通讯设备是否断开')
                        print(air_v.bIsCommsOnLine)
                        print(air_v.bIsIsolatedPOVObject)
                        print('# 地形跟随')
                        print(air_v.bTerrainFollowing)
                        print(air_v.bIsRegroupNeeded)
                        print('# 保持阵位')
                        print(air_v.bHoldPosition)
                        print('# 是否可自动探测')
                        print(air_v.bAutoDetectable)
                        print('# 当前货物')
                        print(air_v.m_Cargo)
                        print('# 燃油百分比，作战单元燃油栏第一个进度条的值')
                        print(air_v.dFuelPercentage)
                        print('# 获取AI对象的目标集合# 获取活动单元AI对象的每个目标对应显示不同的颜色集合')
                        print(air_v.m_AITargets)
                        print('# 获取活动单元AI对象的每个目标对应显示不同的颜色集合')
                        print(air_v.m_AITargetsCanFiretheTargetByWCSAndWeaponQty)
                        print('# 获取单元的通讯链集合')
                        print(air_v.m_CommLink)
                        print('# 获取传感器0')
                        print(air_v.m_NoneMCMSensors)
                        print('# 获取显示"干扰"或"被干扰"')
                        print(air_v.iDisturbState)
                        print('# 单元所属多个任务数量')
                        print(air_v.iMultipleMissionCount)
                        print('# 单元所属多个任务guid拼接')
                        print(air_v.m_MultipleMissionGUIDs)
                        print('# 是否遵守电磁管控')
                        print(air_v.bObeysEMCON)
                        print('# 武器预设的打击航线')
                        print(air_v.m_strContactWeaponWayGuid)
                        print('# 停靠参数是否包含码头')
                        print(air_v.bDockingOpsHasPier)
                        print('弹药库')
                        print(air_v.m_Magazines)
                        print('被摧毁')
                        print(air_v.dPBComponentsDestroyedWidth)
                        print("轻度")
                        print(air_v.dPBComponentsLightDamageWidth)
                        print('# 中度')
                        print(air_v.dPBComponentsMediumDamageWidth)
                        print('''# 重度''')
                        print(air_v.dPBComponentsHeavyDamageWidth)
                        print('''# 重度''')
                        print(air_v.dPBComponentsHeavyDamageWidth)
                        print('''# 正常''')
                        print(air_v.dPBComponentsOKWidth)
                        print('''# 配属基地''')
                        print(air_v.m_HostActiveUnit)
                        print(''' # 状态''')
                        print(air_v.strActiveUnitStatus)
                        print('''# 精简''')
                        print(air_v.doctrine)
                    # 任务
                    if self.mission_num == 0:
                        self.mission_num = 1
                        # 分配加入到任务中
                        air_v.assign_unitlist_to_mission('打击任务')
                        # 将单元分配为某打击任务的护航任务
                        air_v.assign_unitlist_to_mission_escort('打击任务')
                        strike = side_v.get_strike_missions()
                        for k, v in strike.items():
                            v.get_assigned_units()
                            v.get_unassigned_units()
                            v.get_doctrine()
                            v.is_active(False)
                            v.set_start_time('03/25/2020 15:06:29')
                            v.set_end_time('03/25/2020 18:06:29')
                            v.set_one_third_rule(False)
                            v.switch_radar(True)
                            v.assign_targets(side_v.contacts)       #amended by aie
                            v.get_targets() #amended by aie
                            v.set_preplan(True) #amended by aie
                            v.set_strike_max(2) #amended by aie
                            v.set_flight_size(2)    #amended by aie
                            v.set_min_aircrafts_required(2) #amended by aie
                            v.set_radar_usage(2)    #amended by aie
                            v.set_fuel_ammo(2)  #amended by aie
                    # 条令
                    if self.doctrine_num == 0:
                        # 设置电磁管控是否与上级一致
                        doctrine.set_emcon_according_to_superiors('no')
                        # 设置对空武器使用规则
                        doctrine.set_weapon_control_status_air(1) #amended by aie
                        # 设置海武器使用规则
                        doctrine.set_weapon_control_status_surface(1) #amended by aie
                        # 设置对潜武器使用规则
                        doctrine.set_weapon_control_status_subsurface(1) #amended by aie
                        # 设置对陆武器使用规则
                        doctrine.set_weapon_control_status_land(1) #amended by aie
                    # 动作
                    # 设置一个航路点
                    air_v.set_waypoint(35.0, 230.12)

                    # 设置自动打击和手动打击
                    for contact_k, contact_v in side_v.contacts.items():
                        if self.aircraft_num == 1:
                            air_v.auto_attack_target(contact_k)
                        if self.aircraft_num == 1:
                            air_v.manual_attack(contact_k, 20, 1)
                        break
                    # 设置油门
                    air_v.set_throttle(2)
                    # 设置雷达开机
                    air_v.set_radar_shutdown('true')
                    # 设置高度
                    air_v.set_desired_height(3000)
                    # 吊放声呐
                    air_v.deploy_dipping_sonar()
                    # 将单元取消分配任务
                    air_v.cancel_assign_unitlist_to_mission()
                    # 设置单元燃油量
                    air_v.set_fuel_qty(1000)
                    # 设置朝向
                    air_v.set_unit_heading(30)
                    # 设置航线
                    air_v.plot_course([(40, 39.0), (41, 39.0)])
                    # 投放主动声呐
                    air_v.drop_active_sonobuoy('deep')
                    # 投放被动声呐
                    air_v.drop_passive_sonobuoy('deep')
                    # 设置留空时间
                    air_v.set_airborne_time(2, 1, 1)
                    # 设置出动准备时间
                    air_v.time_To_ready('00:01:00')
                    # 让指定飞机快速出动
                    air_v.quick_turnaround('true', 1)
                    # 让正在出动中的飞机立即终止出动
                    air_v.abort_launch()
                    # 返航
                    air_v.return_to_base()

