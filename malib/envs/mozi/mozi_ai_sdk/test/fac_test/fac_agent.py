# _*_ coding : utf-8 _*_
'''
作者 : 解洋
'''
# from MoZiAI_SDK.core.entitys import mission
from malib.envs.mozi.mozi_simu_sdk.args import Throttle, StrikeMinimumTrigger, FlightSizeNum, FuelState, \
    WeaponStatePlanned, DamageThreshold, FuelQuantityThreshold, WeaponQuantityThreshold, StrikeMinAircraftReq, \
    StrikeRadarUsage, StrikeFuleAmmo
from malib.envs.mozi.mozi_simu_sdk.mission import CMission
from malib.envs.mozi.mozi_simu_sdk.mssnpatrol import CPatrolMission


class CAgent:
    def __init__(self):
        self.class_name = 'facility_'

    def test(self, scenario):
        for side_k, side_v in scenario.get_sides().items():

            # 方的条令
            doctrine = side_v.get_doctrine()
            print(doctrine)
            # doctrine.use_nuclear_weapons('yes')
            doctrine.set_weapon_control_status_subsurface('0')
            doctrine.set_weapon_control_status_surface('1')
            doctrine.set_weapon_control_status_land('2')
            doctrine.set_weapon_control_status_air('0')
            doctrine.ignore_plotted_course('yes')
            doctrine.set_ambiguous_targets_engaging_status('0')
            doctrine.set_opportunity_targets_engaging_status('true')
            doctrine.ignore_emcon_while_under_attack('true')
            doctrine.use_kinematic_range_for_torpedoes(1)
            doctrine.evade_automatically('true')
            doctrine.use_refuel_supply('0')
            doctrine.select_refuel_supply_object('0')
            doctrine.refuel_supply_allies('0')
            doctrine.set_air_operations_tempo('1')
            doctrine.quick_turnaround_for_aircraft('1')

            doctrine.set_fuel_state_for_aircraft(FuelState.Joker10Percent.value)
            doctrine.set_fuel_state_for_air_group('1')
            doctrine.set_weapon_state_for_aircraft(WeaponStatePlanned.Shotgun75Disengage.value)
            doctrine.set_weapon_state_for_air_group('1')
            doctrine.gun_strafe_for_aircraft('Yes')
            doctrine.jettison_ordnance_for_aircraft('Yes')
            doctrine.use_sams_to_anti_surface('true')
            doctrine.maintain_standoff('true')
            doctrine.avoid_being_searched_for_submarine('No')
            doctrine.dive_on_threat('0')
            doctrine.set_recharging_condition_on_patrol('20')
            doctrine.set_recharging_condition_on_attack('30')
            doctrine.use_aip('1')
            doctrine.use_dipping_sonar('1')

            # 4/8 测试
            doctrine.set_em_control_status(1, 'true')
            # doctrine.set_weapon_release_authority()  # 暂时不考虑
            doctrine.withdraw_on_damage(DamageThreshold.Percent25.value)
            doctrine.withdraw_on_fuel(FuelQuantityThreshold.Inherit.value)
            doctrine.withdraw_on_attack_weapon(WeaponQuantityThreshold.Percent50.value)
            doctrine.withdraw_on_defence_weapon(WeaponQuantityThreshold.Percent50.value)  # 没有value
            doctrine.redeploy_on_damage(DamageThreshold.Percent50.value)
            doctrine.redeploy_on_fuel(FuelQuantityThreshold.Percent25.value)
            doctrine.redeploy_on_attack_weapon(WeaponQuantityThreshold.Percent25.value)
            doctrine.redeploy_on_defence_weapon(WeaponQuantityThreshold.Percent50.value)
            doctrine.reset('Left', 'Ensemble', escort_status='false')
            doctrine.set_emcon_according_to_superiors('yes', 'true')

            # 任务的条令
            for m, mv in side_v.missions.items():
                doctrine = mv.get_doctrine()
                doctrine.use_nuclear_weapons('yes')
                doctrine.set_weapon_control_status_subsurface('0')
                doctrine.set_weapon_control_status_surface('1')
                doctrine.set_weapon_control_status_land('2')
                doctrine.set_weapon_control_status_air('0')
                doctrine.ignore_plotted_course('yes')
                doctrine.set_ambiguous_targets_engaging_status('0')
                doctrine.set_opportunity_targets_engaging_status('true')
                doctrine.ignore_emcon_while_under_attack('true')
                doctrine.use_kinematic_range_for_torpedoes(1)
                doctrine.evade_automatically('true')
                doctrine.use_refuel_supply('0')
                doctrine.select_refuel_supply_object('0')
                doctrine.refuel_supply_allies('0')
                doctrine.set_air_operations_tempo('1')
                doctrine.quick_turnaround_for_aircraft('1')
                doctrine.set_fuel_state_for_aircraft(FuelState.Joker10Percent.value)
                doctrine.set_fuel_state_for_air_group('1')
                doctrine.set_weapon_state_for_aircraft(WeaponStatePlanned.Shotgun75Disengage.value)
                doctrine.set_weapon_state_for_air_group('1')
                doctrine.gun_strafe_for_aircraft('Yes')
                doctrine.jettison_ordnance_for_aircraft('Yes')
                doctrine.use_sams_to_anti_surface('true')
                doctrine.maintain_standoff('true')
                doctrine.avoid_being_searched_for_submarine('No')
                doctrine.dive_on_threat('0')
                doctrine.set_recharging_condition_on_patrol('20')
                doctrine.set_recharging_condition_on_attack('30')
                doctrine.use_aip('1')
                doctrine.use_dipping_sonar('1')

                # 4/8 测试
                doctrine.set_em_control_status(1, 'true')
                # doctrine.set_weapon_release_authority()  # 暂时不考虑
                doctrine.withdraw_on_damage(DamageThreshold.Percent25.value)
                doctrine.withdraw_on_fuel(FuelQuantityThreshold.Inherit.value)
                doctrine.withdraw_on_attack_weapon(WeaponQuantityThreshold.Percent50.value)
                doctrine.withdraw_on_defence_weapon(WeaponQuantityThreshold.Percent50.value)  # 没有value
                doctrine.redeploy_on_damage(DamageThreshold.Percent50.value)
                doctrine.redeploy_on_fuel(FuelQuantityThreshold.Percent25.value)
                doctrine.redeploy_on_attack_weapon(WeaponQuantityThreshold.Percent25.value)
                doctrine.redeploy_on_defence_weapon(WeaponQuantityThreshold.Percent50.value)
                doctrine.reset('Left', 'Ensemble', escort_status='false')
                doctrine.set_emcon_according_to_superiors('yes', 'true')

            if len(side_v.get_facilities()) > 2:
                # 测试地面单元
                print(11)
                for fac_k, fac_v in side_v.facilities.items():
                    sumary_info = fac_v.get_summary_info()
                    print(sumary_info)

                    if sumary_info['name'] == '萨姆-3B“果阿”型地空导弹营[S-125M]':
                        # fac_v.set_throttle(4)
                        # aa = fac_v.get_summary_info()
                        # fac_v.set_rader_shutdown('true')  # 地空导弹营可以打开，坦克排看不到
                        # fac_v.set_desired_speed(20)
                        fac_v.set_unit_heading(35)  # lua执行成功， 看不到
                        fac_v.plot_course([(47.12, 40.15)])
                        doctrine = fac_v.get_doctrine()
                        print(doctrine)

                        # 测试side， mission, 方，组， 单元， 任务都测试
                        doctrine.use_nuclear_weapons('yes')
                        doctrine.set_weapon_control_status_subsurface('0')
                        doctrine.set_weapon_control_status_surface('1')
                        doctrine.set_weapon_control_status_land('2')
                        doctrine.set_weapon_control_status_air('0')
                        doctrine.ignore_plotted_course('yes')
                        doctrine.set_ambiguous_targets_engaging_status('0')  # str:'Ignore'('0')
                        doctrine.set_opportunity_targets_engaging_status('true')
                        doctrine.ignore_emcon_while_under_attack('true')
                        doctrine.use_kinematic_range_for_torpedoes(1)
                        doctrine.evade_automatically('true')
                        doctrine.use_refuel_supply('0')
                        doctrine.select_refuel_supply_object('0')
                        doctrine.refuel_supply_allies('0')
                        doctrine.set_air_operations_tempo('1')
                        doctrine.quick_turnaround_for_aircraft('1')
                        doctrine.set_fuel_state_for_aircraft(FuelState.Joker10Percent.value)
                        doctrine.set_fuel_state_for_air_group('1')
                        doctrine.set_weapon_state_for_aircraft(WeaponStatePlanned.Shotgun75Disengage.value)
                        doctrine.set_weapon_state_for_air_group('1')
                        doctrine.gun_strafe_for_aircraft('Yes')
                        doctrine.jettison_ordnance_for_aircraft('Yes')
                        doctrine.use_sams_to_anti_surface('true')
                        doctrine.maintain_standoff('true')
                        doctrine.avoid_being_searched_for_submarine('No')
                        doctrine.dive_on_threat('0')
                        doctrine.set_recharging_condition_on_patrol('20')
                        doctrine.set_recharging_condition_on_attack('30')
                        doctrine.use_aip('1')
                        doctrine.use_dipping_sonar('1')

                        # 4/8 测试
                        doctrine.set_em_control_status(1, 'true')
                        doctrine.withdraw_on_damage(DamageThreshold.Percent25.value)
                        doctrine.withdraw_on_fuel(FuelQuantityThreshold.Inherit.value) #?
                        doctrine.withdraw_on_attack_weapon(WeaponQuantityThreshold.Percent50.value)
                        doctrine.withdraw_on_defence_weapon(WeaponQuantityThreshold.Percent50.value)
                        doctrine.redeploy_on_damage(DamageThreshold.Percent50.value)
                        doctrine.redeploy_on_fuel(FuelQuantityThreshold.Percent25.value)
                        doctrine.redeploy_on_attack_weapon(WeaponQuantityThreshold.Percent25.value)
                        doctrine.redeploy_on_defence_weapon(WeaponQuantityThreshold.Percent50.value)
                        doctrine.reset('Left', 'Ensemble', escort_status='false')
                        doctrine.set_emcon_according_to_superiors('yes', 'true')

                        # 条令
                        # 设置电磁管控是否与上级一致, 以下3个调用lua 一致。
                        # doctrine.doctrine_set_emcon_inherit(False)  # lua执行正确，没有效果
                        # doctrine.set_in_line_with_superiors(fac_v.strGuid, 'no')
                        # doctrine.doctrine_set_emcon_inherit('yes')

                        # # 设置对空武器使用规则
                        # doctrine.set_doctrine_air(fac_v.strGuid, 1)
                        # # 设置海武器使用规则
                        # doctrine.set_doctrine_surface(fac_v.strGuid, 1)
                        # # 设置对潜武器使用规则
                        # doctrine.set_doctrine_subsurface(fac_v.strGuid, 1)
                        # # 设置对陆武器使用规则
                        # doctrine.set_doctrine_land(fac_v.strGuid, 1)

                        # 获取条令所有者
                        doctrine.get_doctrine_owner()
                        # doctrine.doctrine_switch_radar(fac_v.strGuid, True)

                        # doctrine.doctrine_engaging_ambiguous_targets(1)  # 需要枚举值，
                        #
                        # doctrine.doctrine_ignore_plotted_course(fac_v.strGuid, 0) # 跑通，但是还需要修改
                        # doctrine.doctrine_engage_opportunity_targets()  # 需要枚举值
                        #
                        # doctrine.doctrine_ignore_emcon_under_attack(fac_v.strGuid, 0) # 需要枚举值，修改参数为单元的id
                        # doctrine.doctrine_automatic_evasion(1)  # 枚举值，m_Side的获得， strName属性添加
                        #
                        # doctrine.strike_addTarget()

                        # 任务接口
                        # fac_v.assign_unitList_to_mission('空中拦截')

                        fac_v.mozi_server.suspend_simulate()
                        fac_v.mozi_server.update_situation(scenario)
                        # 巡逻任务
                        patrol = side_v.get_missions_by_name('空中拦截')
                        for k, v in patrol.items():
                            get_mission = v.get_assigned_units()
                            v.get_unassigned_units()
                            v.get_doctrine()
                            v.is_active(False)
                            v.set_start_time('03/25/2020 15:06:29')
                            v.set_end_time('03/25/2020 18:06:29')
                            v.set_one_third_rule(False)
                            # v.set_mission_switch_radar(True)
                            v.get_side()
                            for key in get_mission.keys():
                                # 单元从任务中移除
                                v.unassign_unit(key)
                            v.is_area_valid()
                            v.set_maintain_unit_number(2)
                            v.set_opa_check(True)
                            v.set_emcon_usage(True)
                            v.set_wwr_check(True)
                            v.set_throttle_transit(Throttle.Loiter)
                            v.set_throttle_station(Throttle.Cruise)
                            v.set_throttle_attack(Throttle.Full)
                            v.set_attack_distance(Throttle.Flank)

                        # strike 功能
                        targetList = []
                        target = fac_v.m_AITargets
                        targetList.append(target)
                        strike = side_v.get_strike_missions()
                        for k, v in strike.items():
                            v.add_target(targetList)
                            v.remove_target(targetList)
                            t = v.get_targets()
                            # v.assign_targets(targets)
                            # v.assign_units(units)
                            # v.add_target(target_list)
                            v.set_minimum_trigger(StrikeMinimumTrigger.Nil)
                            v.set_preplan(True)
                            v.set_flight_size(FlightSizeNum.ThreeAircraft)
                            v.set_min_aircrafts_required(StrikeMinAircraftReq.FOUR)
                            v.set_radar_usage(StrikeRadarUsage.ATTACK_START_WINCHESTER)
                            v.set_strike_one_time_only('false')
                            v.set_fuel_ammo(StrikeFuleAmmo.FAR_DIST)
                            v.set_min_strike_radius(10)
                            v.set_max_strike_radius(15)
                            v.set_flight_size_check('true')
                            v.set_auto_planner('true')
                        # support 功能
                        support = side_v.get_support_missions()
                        for k, v in support.items():
                            v.set_maintain_unit_number(2)
                            v.set_one_time_only('true')
                            v.set_emcon_usage('true')
                            v.set_loop_type('true')
                            v.set_flight_size(FlightSizeNum.TwoAircraft)  # ?
                            v.set_flight_size_check('true')
                            v.set_throttle_transit(Throttle.Flank)
                            v.set_throttle_station(Throttle.Cruise)
                            v.set_transit_altitude(1500)
                            v.set_station_altitude(9000)


                        # 动作接口
                        ret = fac_v.get_way_points_info()  # 初始想定里边没有航路点，接口添加航路点之后，并没有放到单元里边
                        print(ret)
                        fac_v.delete_coursed_point(0)
                        fac_v.assign_unitlist_to_mission('空中拦截')
                        #mssn = side_v.get_missions_by_name('空中拦截')
                        #ret = mssn.get_assigned_units()  # 目前是T+1模式,mssn中还没有
                        #print(ret)
                        ret = fac_v.get_doctrine()
                        print(ret)

                        for contact_k, contact_v in side_v.contacts.items():
                            ret = fac_v.get_ai_targets()
                            print(ret)
                            fac_v.auto_attack(contact_k)
                            fac_v.allocate_salvo_to_target(contact_k, 1852)
                            fac_v.allocate_salvo_to_target((40.06, 46.26), 1852)
                            fac_v.manual_attack(contact_k, 1852, 1)
                    if sumary_info['name'] == 'Vehicle (1L222 Kvant [Apure/Avtobaza] Mobile Jammer+ELINT)':
                        fac_v.set_oecm_shutdown('false')
                        fac_v.unit_obeys_emcon('true')  # lua返回正确，但是没有起效， 在客户端操作，lua是设置单元是否遵循电磁管控，客户端显示所有单元都会改变。

                    for contact_k, contact_v in side_v.contacts.items():
                        fac_v.auto_attack(contact_k)
                        fac_v.manual_attack(contact_k, 20, 1)
                        break
                    fac_v.set_throttle(2)
                    fac_v.set_radar_shutdown('true')
                    fac_v.return_to_base()
                    fac_v.assign_unitlist_to_mission('打击任务')
                    fac_v.cancel_assign_unitlist_to_mission()
                    fac_v.set_fuel_qty(1000)
                    fac_v.set_unit_heading(30)
                    fac_v.plot_course([(40, 39.0), (41, 39.0)])
                    fac_v.assign_unitlist_to_mission_escort('打击任务')

            # self.mozi_server.run_simulate()
            # if len(side_v.ships) > 0:
            #     #测试水面舰船
            #     print(4)
