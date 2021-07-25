# 时间 ： 2020/8/15 19:13
# 作者 ： Dixit
# 文件 ： agent.py
# 项目 ： moziAIBT2
# 版权 ： 北京华戍防务技术有限公司

from malib.envs.mozi.mozi_ai_sdk.test.merrimackmonitor.actions import *
from malib.envs.mozi.mozi_ai_sdk.btmodel.bt.bt_nodes import BT


class CAgent:
    def __init__(self):
        self.class_name = 'bt_'
        self.bt = None

    def init_bt(self, env, sideName, lenAI, options):
        side = env.scenario.get_side_by_name(sideName)
        sideGuid = side.strGuid
        shortSideKey = "a" + str(lenAI + 1)
        attributes = options
        # main node sequence
        merimackSelector = BT()

        # doctrine sequences
        offensiveDoctrineSequence = BT()
        defensiveDoctrineSequence = BT()

        # doctrine sequences children
        offensiveDoctrineConditionalBT = BT()
        defensiveDoctrineConditionalBT = BT()
        offensiveDoctrineSelector = BT()
        # defensiveDoctrineSelector = BT()

        # sub doctrine sequences
        reconDoctrineSelector = BT()
        attackDoctrineSelector = BT()
        defendDoctrineSelector = BT()
        supportTankerDoctrineSelector = BT()
        supportAEWDoctrineSelector = BT()

        # recon doctrine BT
        reconDoctrineUpdateMissionBT = BT()
        reconDoctrineCreateMissionBT = BT()

        # attack doctrine BT
        attackDoctrineUpdateAirMissionBT = BT()
        attackDoctrineCreateAirMissionBT = BT()
        attackDoctrineUpdateStealthAirMissionBT = BT()
        attackDoctrineCreateStealthAirMissionBT = BT()
        attackDoctrineCreateAEWMissionBT = BT()
        attackDoctrineUpdateAEWMissionBT = BT()
        attackDoctrineUpdateAntiSurfaceShipMissionBT = BT()
        attackDoctrineCreateAntiSurfaceShipMissionBT = BT()
        # attackDoctrineUpdateSeadMissionBT = BT()
        # attackDoctrineCreateSeadMissionBT = BT()
        # attackDoctrineCreateLandAttackMissionBT = BT()
        # attackDoctrineUpdateLandAttackMissionBT = BT()

        # defend doctrine BT
        defendDoctrineUpdateAirMissionBT = BT()
        defendDoctrineCreateAirMissionBT = BT()

        # support tanker doctrine BT
        supportTankerDoctrineUpdateMissionBT = BT()
        supportTankerDoctrineCreateMissionBT = BT()

        # support AEW doctrine BT
        supportAEWDoctrineUpdateMissionBT = BT()
        supportAEWDoctrineCreateMissionBT = BT()

        # 构建行为树
        merimackSelector.add_child(offensiveDoctrineSequence)
        merimackSelector.add_child(defensiveDoctrineSequence)

        # offensive and defensive sequence
        offensiveDoctrineSequence.add_child(offensiveDoctrineConditionalBT)
        offensiveDoctrineSequence.add_child(offensiveDoctrineSelector)
        defensiveDoctrineSequence.add_child(defensiveDoctrineConditionalBT)
        # defensiveDoctrineSequence.add_child(defensiveDoctrineSelector)

        # offensive selector
        offensiveDoctrineSelector.add_child(reconDoctrineSelector)
        offensiveDoctrineSelector.add_child(attackDoctrineSelector)
        offensiveDoctrineSelector.add_child(supportAEWDoctrineSelector)
        offensiveDoctrineSelector.add_child(supportTankerDoctrineSelector)
        offensiveDoctrineSelector.add_child(defendDoctrineSelector)

        # defensive selector
        # defensiveDoctrineSelector.add_child(defendDoctrineSelector)
        # defensiveDoctrineSelector.add_child(reconDoctrineSelector)
        # defensiveDoctrineSelector.add_child(supportAEWDoctrineSelector)
        # defensiveDoctrineSelector.add_child(supportTankerDoctrineSelector)

        # recon doctrine sequence
        reconDoctrineSelector.add_child(reconDoctrineUpdateMissionBT)
        reconDoctrineSelector.add_child(reconDoctrineCreateMissionBT)

        # attack doctrine sequence
        attackDoctrineSelector.add_child(attackDoctrineUpdateAirMissionBT)
        attackDoctrineSelector.add_child(attackDoctrineCreateAirMissionBT)
        attackDoctrineSelector.add_child(attackDoctrineUpdateStealthAirMissionBT)
        attackDoctrineSelector.add_child(attackDoctrineCreateStealthAirMissionBT)
        attackDoctrineSelector.add_child(attackDoctrineUpdateAEWMissionBT)
        attackDoctrineSelector.add_child(attackDoctrineCreateAEWMissionBT)
        attackDoctrineSelector.add_child(attackDoctrineUpdateAntiSurfaceShipMissionBT)
        attackDoctrineSelector.add_child(attackDoctrineCreateAntiSurfaceShipMissionBT)
        # attackDoctrineSelector.add_child(attackDoctrineUpdateSeadMissionBT)
        # attackDoctrineSelector.add_child(attackDoctrineCreateSeadMissionBT)
        # attackDoctrineSelector.add_child(attackDoctrineUpdateLandAttackMissionBT)
        # attackDoctrineSelector.add_child(attackDoctrineUpdateLandAttackMissionBT)

        # defend doctrine sequence
        defendDoctrineSelector.add_child(defendDoctrineUpdateAirMissionBT)
        defendDoctrineSelector.add_child(defendDoctrineCreateAirMissionBT)

        # support Tanker doctrine sequence 加油任务
        supportTankerDoctrineSelector.add_child(supportTankerDoctrineUpdateMissionBT)
        supportTankerDoctrineSelector.add_child(supportTankerDoctrineCreateMissionBT)

        # support AEW doctrine sequence
        supportAEWDoctrineSelector.add_child(supportAEWDoctrineUpdateMissionBT)
        supportAEWDoctrineSelector.add_child(supportAEWDoctrineCreateMissionBT)

        # 行为树节点设置动作
        merimackSelector.set_action(merimackSelector.select, sideGuid, shortSideKey, attributes)

        offensiveDoctrineSequence.set_action(offensiveDoctrineSequence.sequence, sideGuid, shortSideKey, attributes)
        defensiveDoctrineSequence.set_action(defensiveDoctrineSequence.sequence, sideGuid, shortSideKey, attributes)

        offensiveDoctrineConditionalBT.set_action(OffensiveConditionalCheck, sideGuid, shortSideKey, attributes)
        defensiveDoctrineConditionalBT.set_action(DefensiveConditionalCheck, sideGuid, shortSideKey, attributes)
        offensiveDoctrineSelector.set_action(offensiveDoctrineSelector.select, sideGuid, shortSideKey, attributes)
        # defensiveDoctrineSelector.set_action(defensiveDoctrineSelector.select, sideGuid, shortSideKey, attributes)

        reconDoctrineSelector.set_action(reconDoctrineSelector.select, sideGuid, shortSideKey, attributes)
        attackDoctrineSelector.set_action(attackDoctrineSelector.select, sideGuid, shortSideKey, attributes)
        defendDoctrineSelector.set_action(defendDoctrineSelector.select, sideGuid, shortSideKey, attributes)
        supportTankerDoctrineSelector.set_action(supportTankerDoctrineSelector.select, sideGuid, shortSideKey, attributes)
        supportAEWDoctrineSelector.set_action(supportAEWDoctrineSelector.select, sideGuid, shortSideKey, attributes)

        reconDoctrineUpdateMissionBT.set_action(ReconDoctrineUpdateMissionAction, sideGuid, shortSideKey, attributes)
        reconDoctrineCreateMissionBT.set_action(ReconDoctrineCreateMissionAction, sideGuid, shortSideKey, attributes)

        attackDoctrineUpdateAirMissionBT.set_action(AttackDoctrineUpdateAirMissionAction, sideGuid, shortSideKey, attributes)
        attackDoctrineCreateAirMissionBT.set_action(AttackDoctrineCreateAirMissionAction, sideGuid, shortSideKey, attributes)
        attackDoctrineUpdateStealthAirMissionBT.set_action(AttackDoctrineUpdateStealthAirMissionAction, sideGuid, shortSideKey, attributes)
        attackDoctrineCreateStealthAirMissionBT.set_action(AttackDoctrineCreateStealthAirMissionAction, sideGuid, shortSideKey, attributes)
        attackDoctrineCreateAEWMissionBT.set_action(AttackDoctrineCreateAEWMissionAction, sideGuid, shortSideKey, attributes)
        attackDoctrineUpdateAEWMissionBT.set_action(AttackDoctrineUpdateAEWAirMissionAction, sideGuid, shortSideKey, attributes)
        attackDoctrineUpdateAntiSurfaceShipMissionBT.set_action(AttackDoctrineUpdateAntiSurfaceShipMissionAction, sideGuid, shortSideKey, attributes)
        attackDoctrineCreateAntiSurfaceShipMissionBT.set_action(AttackDoctrineCreateAntiSurfaceShipMissionAction, sideGuid, shortSideKey, attributes)
        # attackDoctrineUpdateSeadMissionBT.set_action(AttackDoctrineUpdateSeadMissionAction, sideGuid, shortSideKey, attributes)
        # attackDoctrineCreateSeadMissionBT.set_action(AttackDoctrineCreateSeadMissionAction, sideGuid, shortSideKey, attributes)
        # attackDoctrineCreateLandAttackMissionBT.set_action(AttackDoctrineCreateLandAttackMissionAction, sideGuid, shortSideKey, attributes)
        # attackDoctrineUpdateLandAttackMissionBT.set_action(AttackDoctrineUpdateLandAttackMissionAction, sideGuid, shortSideKey, attributes)

        defendDoctrineUpdateAirMissionBT.set_action(DefendDoctrineUpdateAirMissionAction, sideGuid, shortSideKey, attributes)
        defendDoctrineCreateAirMissionBT.set_action(DefendDoctrineCreateAirMissionAction, sideGuid, shortSideKey, attributes)

        supportTankerDoctrineUpdateMissionBT.set_action(SupportTankerDoctrineUpdateMissionAction, sideGuid, shortSideKey, attributes)
        supportTankerDoctrineCreateMissionBT.set_action(SupportTankerDoctrineCreateMissionAction, sideGuid, shortSideKey, attributes)

        supportAEWDoctrineUpdateMissionBT.set_action(SupportAEWDoctrineUpdateMissionAction, sideGuid, shortSideKey, attributes)
        supportAEWDoctrineCreateMissionBT.set_action(SupportAEWDoctrineCreateMissionAction, sideGuid, shortSideKey, attributes)

        self.bt = merimackSelector

    def update_bt(self, scenario):
        return self.bt.run(scenario)