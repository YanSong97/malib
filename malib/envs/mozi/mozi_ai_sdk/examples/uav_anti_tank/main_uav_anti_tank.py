#!/usr/bin/python
# -*- coding: utf-8 -*-
######################################
# File name : main_uav_anti_tank.py
# Create date : 2019-10-20 19:37
# Modified date : 2020-04-29 21:55
# Author : liuzy
# Describe : not set
# Email : lzygzh@126.com
######################################

# 系统或第三方包
import os
import time
import psutil
import datetime
import numpy as np

# 墨子Utils
from malib.envs.mozi.mozi_utils.pyfile import read_start_epoch
from malib.envs.mozi.mozi_utils.pyfile import read_start_step
from malib.envs.mozi.mozi_utils.pyfile import write_start_step_file
from malib.envs.mozi.mozi_utils.pyfile import read_start_epoch_file
from malib.envs.mozi.mozi_utils.pyfile import write_start_epoch_file

# 墨子AI SDK
from malib.envs.mozi.mozi_ai_sdk.rlmodel.ddpg import train
from malib.envs.mozi.mozi_ai_sdk.rlmodel.ddpg import buffer
from malib.envs.mozi.mozi_ai_sdk.examples.uav_anti_tank.env_uav_anti_tank import EnvUavAntiTank as Environment
from malib.envs.mozi.mozi_ai_sdk.examples.uav_anti_tank import etc_uav_anti_tank as etc
from malib.envs.mozi.mozi_ai_sdk.examples.uav_anti_tank.agent_uav_anti_tank import AgentUavAntiTank
from malib.envs.mozi.mozi_ai_sdk.examples.uav_anti_tank.pic import show_pic, write_final_reward
#  设置墨子安装目录下bin目录为MOZIPATH，程序会自动启动墨子
os.environ['MOZIPATH'] = 'D:\\mozi_4p\\mozi\\Mozi\\MoziServer\\bin'


def main():
    """主函数，用于构建训练环境及智能体，并进行训练"""

    # 创建环境对象, 并启动之。仿真服务器是环境的一部分，它也在环境中启动了
    env = Environment(
        etc.SERVER_IP,
        etc.SERVER_PORT,
        etc.SCENARIO_NAME,
        etc.SIMULATE_COMPRESSION,
        etc.DURATION_INTERVAL,
        etc.SERVER_PLAT)

    # 开始的轮数
    epoch_file_path = "%s/epoch.txt" % etc.OUTPUT_PATH
    # start_epoch = read_start_epoch(epoch_file_path) # 目前已经训练的轮数
    #
    # 开始步数
    step_file_path = "%s/step.txt" % etc.OUTPUT_PATH
    # start_step = read_start_step(step_file_path)
    # cur_step = start_step
    # print("start step: %s" % cur_step)

    start_epoch = 0
    start_step = 0
    cur_step = 0

    # 创建智能体对象
    agent = AgentUavAntiTank(env, start_epoch)

    # 启动训练
    try:
        for _ep in range(start_epoch, etc.MAX_EPISODES):
            print(" ")
            print("%s：第%s轮训练开始======================================" % (datetime.datetime.now(), _ep))

            # 重置智能体、环境、训练器
            state_now, reward_now = env.reset()
            agent.reset()

            final_reward = reward_now
            # 智能体作决策，产生动作，动作影响环境，智能体根据动作的效果进行训练优化
            for step in range(etc.MAX_STEPS):
                # 智能体根据当前的状态及回报值，进行决策，生成下一步的动作
                action_new = agent.make_decision(np.float32(state_now), reward_now)

                # 环境执行动作，生成下一步的状态及回报值
                state_new, reward_new = env.execute_action(action_new)

                # 根据推演结果，训练一次智能体
                agent.train(
                    np.float32(state_now),
                    action_new,
                    reward_new,
                    np.float32(state_new),
                    cur_step)

                cur_step += 1
                write_start_step_file(step_file_path, str(cur_step))
                # 更新状态、回报值
                state_now = state_new
                reward_now = reward_new
                final_reward += reward_now

                # 打印提示
                print("%s：轮数:%s 决策步数:%s  Reward:%.2f" % (datetime.datetime.now(),_ep, step, reward_now))

                # 检查是否结束本轮推演
                if env.check_done():
                    break
                if cur_step % 100 == 0:
                    show_pic()
            write_final_reward(final_reward, _ep)
            write_start_epoch_file(epoch_file_path, str(_ep))

    except KeyboardInterrupt:
        pass

main()