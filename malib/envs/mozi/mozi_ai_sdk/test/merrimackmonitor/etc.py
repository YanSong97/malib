# 时间 ： 2020/8/15 15:37
# 作者 ： Dixit
# 文件 ： etc.py
# 项目 ： moziAIBT2
# 版权 ： 北京华戍防务技术有限公司


import os

APP_ABSPATH = os.path.dirname(__file__)

#######################
SERVER_IP = "127.0.0.1"
SERVER_PORT = "6060"
PLATFORM = 'windows'
# SCENARIO_NAME = "bt_test.scen"  # 距离近，有任务
SCENARIO_NAME = "南海想定2.scen"  # 没有任务
# 推演档位（0-6）（1秒，2秒，5秒，15秒，30秒，1分钟，5分钟）
SIMULATE_COMPRESSION = 3
# DURATION_INTERVAL 获取一次数据的时间间隔，单位是秒，范围是：1-推演持续时间；
# mozi_server.run_simulate()执行后，服务器在DURATION_INTERVAL间隔之后，会暂停，直到下次调用run_simulate才再开始推演。
DURATION_INTERVAL = 5
SYNCHRONOUS = True
#######################
MAX_EPISODES = 5000
MAX_BUFFER = 1000000
MAX_STEPS = 30
#######################

#######################
TMP_PATH = "%s/%s/tmp" % (APP_ABSPATH, SCENARIO_NAME)
OUTPUT_PATH = "%s/%s/output" % (APP_ABSPATH, SCENARIO_NAME)

CMD_LUA = "%s/cmd_lua" % TMP_PATH
PATH_CSV = "%s/path_csv" % OUTPUT_PATH
MODELS_PATH = "%s/Models/" % OUTPUT_PATH
EPOCH_FILE = "%s/epochs.txt" % OUTPUT_PATH
#######################

TRANS_DATA = True