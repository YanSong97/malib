# _*_ coding : utf-8 _*_
'''
作者 : 解洋
时间: 2020-3-25
'''
# _*_ coding : utf-8 _*_
from malib.envs.mozi.mozi_simu_sdk.args import FuelState, WeaponStatePlanned, DamageThreshold, FuelQuantityThreshold, \
    WeaponQuantityThreshold, StrikeMinimumTrigger, FlightSizeNum, StrikeMinAircraftReq, StrikeRadarUsage, \
    StrikeFuleAmmo, Throttle


class CAgent:
    def __init__(self):
        self.class_name = 'ship_'

    def test(self, scenario):
        for side_k, side_v in scenario.get_sides().items():
            # 方的条令
            doctrine = side_v.get_doctrine()
            print(doctrine)
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
            # doctrine.set_weapon_release_authority()
            doctrine.withdraw_on_damage(DamageThreshold.Percent25.value)
            doctrine.withdraw_on_fuel(FuelQuantityThreshold.Inherit.value)
            doctrine.withdraw_on_attack_weapon(WeaponQuantityThreshold.Percent50.value)
            doctrine.withdraw_on_defence_weapon(WeaponQuantityThreshold.Percent50.value)
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
            if len(side_v.ships) > 1:
                # 测试水面舰船
                print(4)
                for ship_k, ship_v in side_v.ships.items():
                    if ship_v.strName == 'DD 151型“朝雾号”驱逐舰':
                        ret = ship_v.set_radar_shutdown('true')  # lua执行成功
                        print(ret)
                        ret = ship_v.set_sonar_shutdown('true')  # lua执行成功
                        print(ret)
                        ret = ship_v.set_oecm_shutdown('true')  # lua执行成功
                        print(ret)
                        ret = ship_v.return_to_base()  # lua执行成功
                        print(ret)
                        ret = ship_v.drop_active_sonobuoy('shallow')  # lua执行成功
                        print(ret)

                        ret = ship_v.plot_course([(31.46, 16.16)])  # 这个经纬度必须在水面上，否则lua报错。
                        print(ret)

                        doctrine = ship_v.get_doctrine()
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

                        for contact_k, contact_v in side_v.contacts.items():
                            ret = ship_v.manual_attack(contact_k, 858, 10)
                            print(ret)
                            ret = ship_v.auto_attack(contact_k)
                            print(ret)
                            pass
                        ship_v.mozi_server.update_situation(scenario)
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
                        target = ship_v.m_AITargets
                        targetList.append(target)
                        strike = side_v.get_strike_missions()
                        for k, v in strike.items():
                            v.add_target(targetList)
                            v.remove_target(targetList)
                            t = v.get_targets()
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

                    if ship_v.strName == 'D 620“福尔宾”号导弹驱逐舰[地平线级驱逐舰] #1':
                        base_guid = list(side_v.facilities)[0]
                        ret = ship_v.leave_dock_alone()
                        print(ret)

            scenario.mozi_server.run_simulate()

