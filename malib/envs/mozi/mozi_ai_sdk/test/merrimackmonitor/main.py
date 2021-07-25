# 时间 ： 2020/8/15 15:36
# 作者 ： Dixit
# 文件 ： main.py
# 项目 ： moziAIBT2
# 版权 ： 北京华戍防务技术有限公司


from malib.envs.mozi.mozi_ai_sdk.test.merrimackmonitor.env import Environment
from malib.envs.mozi.mozi_ai_sdk.test.merrimackmonitor import etc
from malib.envs.mozi.mozi_ai_sdk.test.merrimackmonitor.agent import CAgent
import sys


def run(env):
    env.start()
    agent = CAgent()
    while True:
        env.reset()
        agent.init_bt(env, '蓝方', 0, '')
        i = 0
        while True:
            scenario = env.step()
            agent.update_bt(scenario)
            scenario.mozi_server.run_simulate()
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