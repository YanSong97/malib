# 时间 ： 2020/7/20 17:03
# 作者 ： Dixit
# 文件 ： bt_main_antiship.py
# 项目 ： moziAIBT
# 版权 ： 北京华戍防务技术有限公司


from malib.envs.mozi.mozi_ai_sdk.test.bt_test2.bt_env import Environment
from malib.envs.mozi.mozi_ai_sdk.test.bt_test2 import bt_etc_antiship as etc
from malib.envs.mozi.mozi_ai_sdk.test.bt_test2.bt_agent_antiship import CAgent
import sys
import os
#  设置墨子安装目录下bin目录为MOZIPATH，程序会自动启动墨子
os.environ['MOZIPATH'] = 'D:\\mozi_4p\\mozi\\Mozi\\MoziServer\\bin'

def run(env):
    """
       行为树运行的起始函数
       :param env: 墨子环境
       :return:
       """
    # 连接服务器，产生mozi_server
    env.start()
    # 实例化智能体
    agent = CAgent()
    while True:
        # 重置函数，加载想定,拿到想定发送的数据
        env.reset(etc.app_mode)
        # 初始化行为树
        agent.init_bt(env, '红方', 0, '')
        i = 0
        while True:
            scenario = env.step()
            # 更新动作
            agent.update_bt(scenario)
            scenario.mozi_server.run_grpc_simulate()
            print('推演步数：%s,红方得分：%s' % (i, env.redside.iTotalScore))
            i += 1

            time = scenario.m_Duration.split('@')
            duration = int(time[0])*86400 + int(time[1])*3600 + int(time[2])*60
            if scenario.m_StartTime + duration <= scenario.m_Time:
                print('推演已结束！')
                sys.exit(0)
            else:
                pass


def main():
    env = Environment(etc.SERVER_IP, etc.SERVER_PORT, etc.PLATFORM, etc.SCENARIO_NAME, etc.SIMULATE_COMPRESSION,
                      etc.DURATION_INTERVAL,
                      etc.SYNCHRONOUS)
    run(env)


main()
