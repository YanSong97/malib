from malib.envs.mozi.mozi_simu_sdk.activeunit import CActiveUnit
from malib.envs.mozi.mozi_simu_sdk.aircraft import CAircraft
import re
import os
from malib.envs.mozi.mozi_ai_sdk.examples.rule_bot.env import Environment
from malib.envs.mozi.mozi_ai_sdk.examples.rule_bot import etc
from malib.envs.mozi.mozi_ai_sdk.examples.rule_bot import agent
from malib.envs.mozi.mozi_simu_sdk.geo import *
from malib.envs.mozi.mozi_simu_sdk.mssnpatrol import CPatrolMission
from malib.envs.mozi.mozi_simu_sdk.args import Throttle
from malib.envs.mozi.mozi_simu_sdk.mission import CMission

#  设置墨子安装目录下bin目录为MOZIPATH，程序会自动启动墨子
# os.environ['MOZIPATH'] = 'D:\\mozi_4p\\mozi\\Mozi\\MoziServer\\bin'

"""
主函数
"""

# 建立飞机列表
air_list1 = ['歼-16 #1']


# 选飞机
def get_air(airs):
    for k, v in airs.items():
        if v.strName in air_list1:
            return v


# run函数
def run(env):
    env.start()
    env.reset()
    # 获取态势
    scenario = env.step()

    # 得到推演对象
    red_side = scenario.get_side_by_name('红方')
    print('进入推演方红方')

    """
    总条令
    """
    # 转
    doctrine = red_side.get_doctrine()
    agent.edit_side_doctrine(doctrine)

    # 得到飞机
    JJJ1 = get_air(red_side.aircrafts)
    print(JJJ1.strName)

    """
    #换挂载*********************
    i=JJJ1.set_loadout(26234,1,'Yes','')
    print(i)
    """

    patrol_area, cordon_area = agent.add_rp(red_side)

    # 建立空战巡逻任务
    red_side.add_mission_patrol('歼-16单机', 0, patrol_area)

    # 类的实例化
    patrol_mission = CPatrolMission('歼-16单机', scenario.mozi_server, scenario.situation)

    # 改
    patrol_mission.strName = '歼-16单机'
    patrol_mission.m_Side = '红方'

    agent.edit_mission(patrol_mission, cordon_area)

    """
    任务条令
    """
    # 获取态势
    scenario.mozi_server.run_grpc_simulate()
    scenario = env.step()
    # 转
    patrol_mission = red_side.get_missions_by_name('歼-16单机')
    Ddoctrine = patrol_mission.get_doctrine()
    agent.edit_mission_doctrine(Ddoctrine)

    while True:
        scenario.mozi_server.run_grpc_simulate()
        scenario = env.step()


def main():
    env = Environment(etc.SERVER_IP, etc.SERVER_PORT, etc.PLATFORM, etc.SCENARIO_NAME, etc.SIMULATE_COMPRESSION,
                      etc.DURATION_INTERVAL, etc.SYNCHRONOUS)
    run(env)


if __name__ == '__main__':
    main()
