# 时间 ： 2020/7/20 17:03
# 作者 ： Dixit
# 文件 ： bt_agent_antiship.py
# 项目 ： moziAIBT
# 版权 ： 北京华戍防务技术有限公司

from malib.envs.mozi.mozi_ai_sdk.test.bt_test2.leaf_nodes_eg import *
from malib.envs.mozi.mozi_ai_sdk.btmodel.bt.bt_nodes import BT


class CAgent:
    def __init__(self):
        self.class_name = 'bt_'
        self.bt = None
        self.nonavbt = None

    def init_bt(self, env, sideName, lenAI, options):
        side = env.scenario.get_side_by_name(sideName)
        sideGuid = side.strGuid
        shortSideKey = "a" + str(lenAI + 1)
        attributes = options
        # 行为树的节点
        hxSequence = BT()
        missionSelector = BT()
        missionSelectorCondition = BT()
        patrolMissionSelector = BT()
        createPatrolMission = BT()
        updatePatrolMission = BT()

        # 反舰节点
        AntiSurfaceShipMissionSelector = BT()
        CreateAntiSurfaceShipMission = BT()
        UpdateAntiSurfaceShipMission = BT()

        # 连接节点形成树
        hxSequence.add_child(missionSelector)
        hxSequence.add_child(AntiSurfaceShipMissionSelector)
        missionSelector.add_child(missionSelectorCondition)
        missionSelector.add_child(patrolMissionSelector)

        patrolMissionSelector.add_child(updatePatrolMission)
        patrolMissionSelector.add_child(createPatrolMission)

        AntiSurfaceShipMissionSelector.add_child(CreateAntiSurfaceShipMission)
        AntiSurfaceShipMissionSelector.add_child(UpdateAntiSurfaceShipMission)
        AntiSurfaceShipMissionSelector.add_child(updatePatrolMission)

        # 每个节点执行的动作
        hxSequence.set_action(hxSequence.sequence, sideGuid, shortSideKey, attributes)
        missionSelector.set_action(missionSelector.select, sideGuid, shortSideKey, attributes)
        missionSelectorCondition.set_action(antiship_condition_check, sideGuid, shortSideKey, attributes)

        patrolMissionSelector.set_action(patrolMissionSelector.select, sideGuid, shortSideKey, attributes)

        updatePatrolMission.set_action(update_patrol_mission, sideGuid, shortSideKey, attributes)
        createPatrolMission.set_action(create_patrol_mission, sideGuid, shortSideKey, attributes)

        AntiSurfaceShipMissionSelector.set_action(AntiSurfaceShipMissionSelector.select, sideGuid, shortSideKey,
                                                  attributes)
        CreateAntiSurfaceShipMission.set_action(create_antisurfaceship_mission, sideGuid, shortSideKey, attributes)
        UpdateAntiSurfaceShipMission.set_action(update_antisurfaceship_mission, sideGuid, shortSideKey, attributes)
        self.bt = hxSequence

        # 规避树
        AirNoNavSelector = BT()
        CreateAirNoNavMission = BT()
        UpdateAirNoNavMission = BT()

        AirNoNavSelector.add_child(CreateAirNoNavMission)
        AirNoNavSelector.add_child(UpdateAirNoNavMission)

        AirNoNavSelector.set_action(AirNoNavSelector.select, sideGuid, shortSideKey, attributes)
        CreateAirNoNavMission.set_action(create_antisurfaceship_mission, sideGuid, shortSideKey, attributes)
        UpdateAirNoNavMission.set_action(update_antisurfaceship_mission, sideGuid, shortSideKey, attributes)
        self.nonavbt = AirNoNavSelector

    def update_bt(self, scenario):
        return self.bt.run(scenario)
