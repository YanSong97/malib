# -*- coding:utf-8 -*-
# coding=utf-8
import time
import datetime
# from datetime import datetime
import json
import grpc
import psutil
import os

from malib.envs.mozi.mozi_utils import pylog
from malib.envs.mozi.mozi_simu_sdk.scenario import CScenario
from malib.envs.mozi.mozi_simu_sdk.comm import GRPCServerBase_pb2
from malib.envs.mozi.mozi_simu_sdk.comm import GRPCServerBase_pb2_grpc


class MoziServer:
    """
    仿真服务类，墨子仿真服务器类
    """

    # def __init__(self, server_ip, server_port, platform, scenario_name='', compression=5, synchronous=True):
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        # self.platform = platform
        # self.scenario_name = scenario_name
        # self.compression = compression
        # self.synchronous = synchronous  # True 同步 ,False 异步

        # grpc客户端
        self.grpc_client = None
        self.is_connected = None  # = self.connect_grpc_server() # 这应该时初始化GRPC客户端

        # 命令池
        self.exect_flag = True
        self.command_pool = []
        self.command_num = 0

        # 启动墨子仿真服务器
        self.start_mozi_server()

    def start_mozi_server(self):
        """
        作者：许怀阳
        日期：2020.05.04
        功能：启动墨子仿真服务端
        :return:
        """
        # 判断墨子是否已经启动
        # is_mozi_server_started = False
        # for i in psutil.process_iter():
        #     if i.name() == 'MoziServer.exe':
        #         str_tmp = str(i.name()) + "-" + str(i.pid) + "-" + str(i.status())
        #         print("墨子已启动")
        #         is_mozi_server_started = True
        #         break
        #
        # 启动墨子
        # if is_mozi_server_started == False:
        #     mozi_path = os.environ['MOZIPATH']
        #     mozi_server_exe_file = mozi_path + '\\' + 'MoziServer.exe'
        #     os.popen(mozi_server_exe_file)
        #     print("%s：墨子推演方服务端已启动" % (datetime.datetime.now()))
        #
        # 启动墨子后，稍微等一会，让它初始化一下
        # time.sleep(10)

        # 初始化GRPC客户端??????
        self.connect_grpc_server()
        # 测试墨子服务端是否启动成功，如果没有启动成功，则等待
        is_connected = False
        connect_cout = 0  # 连接次数
        while not is_connected:
            is_connected = self.is_server_connected()
            self.is_connected = is_connected
            connect_cout = connect_cout + 1
            if connect_cout > 20:
                break
            print("%s：还没连接上墨子推演服务器，再等1秒" % (datetime.datetime.now()))
            time.sleep(1)

        if is_connected:
            print("%s：成功连接墨子推演服务器！" % (datetime.datetime.now()))
        else:
            print("%s：连接墨子推演服务器失败（20秒）！" % (datetime.datetime.now()))

    def is_server_connected(self):
        """
        作者：许怀阳
        日期：2020.5.5 22：10
        功能：判断是否已经连接上墨子服务器。使用笨办法，如果发送数据时发生异常，则认为墨子服务器未启动。
        """
        try:
            self.send_and_recv("test")
        except Exception:
            return False
        return True

    def connect_grpc_server(self):
        """
        连接墨子服务器
        :return:
        """
        # pylog.info("正在连接服务器......")
        conn = grpc.insecure_channel(self.server_ip + ':' + str(self.server_port))
        self.grpc_client = GRPCServerBase_pb2_grpc.gRPCStub(channel=conn)
        if 'gRPCStub object' in self.grpc_client.__str__():
            # pylog.info("墨子服务器连接成功! 注意这里的判断很不靠谱，就算服务器没启动，也会报连接成功！")
            return True
        else:
            # pylog.info(("墨子服务器连接失败."))
            return False

    def load_scenario(self):
        """
        加载想定
        plat 服务器是Windows版还是Linux版
        """
        # scenario_file = self.scenario_name
        # ret = None
        # if self.platform == "windows":
        #     ret = self.load_scenario_in_windows(scenario_file, "false")
        # else:
        #     ret = self.load_scenario_in_linux(scenario_file, "Edit")
        #
        # if ret == "数据错误":
        #     print("%s：发送想定加载LUA指令给服务器，服务器返回异常！" % (datetime.datetime.now()))
        #
        # load_success = False
        # for i in range(60):
        #     value = self.is_scenario_loaded()
        #     if str(value) == "'Yes'":
        #         print("%s：想定加载成功！" % (datetime.datetime.now()))
        #         load_success = True
        #         break
        #     print("%s：想定还没有加载完毕，再等一秒！可能原因，1）时间太短；2）服务端没有想定%s！" % (datetime.datetime.now(), self.scenario_name))
        #     time.sleep(1)
        #
        # # 如果想定加载失败
        # if not load_success:
        #     # pylog.error("超过50秒，想定没有加载成功。可能是服务端没有想定:%s" % scenario_file)
        #     print("%s：超过50秒，想定没有加载成功。可能是服务端没有想定:%s！" % (datetime.datetime.now(), scenario_file))
        #     return None

        scenario = CScenario(self)
        return scenario

    def load_scenario_in_windows(self, scenPath, isDeduce):
        """
        函数功能：载入windows版mozi_server的想定。
        scenPath 想定文件的相对路径（仅支持.scen文件）
        isDeduce 模式 "false"想定编辑模式 "true"想定推演模式
        """
        return self.send_and_recv("Hs_ScenEdit_LoadScenario('{}', {})".format(scenPath, isDeduce))

    def load_scenario_in_linux(self, path, model):
        """
        path 想定文件的相对路径（仅支持XML文件）
        model 模式 "Edit"想定编辑模式 "Play"想定推演模式
        """
        return self.send_and_recv("Hs_PythonLoadScenario('{}', '{}')".format(path, model))

    def send_and_recv(self, cmd):
        """
        gRPC发送和接收服务端消息方法
        """
        if self.exect_flag:
            response = self.grpc_client.GrpcConnect(GRPCServerBase_pb2.GrpcRequest(name=cmd))
            length = response.length
            if len(response.message) == length:
                # print(response.message)
                return response.message
            else:
                return "数据错误"
        else:
            self.command_num += 1
            self.throw_into_pool(cmd)

    def throw_into_pool(self, cmd):
        """
        功能：将命令投入命令池。
        参数：cmd：{类型：str，内容：lua命令}
        返回：无
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/2/20
        """
        self.command_pool.append(cmd)

    def transmit_pool(self):
        """
        功能：将命令池倾泄到墨子服务端
        参数：无
        返回：'lua执行成功'或'脚本执行出错'
        作者：aie
        单位：北京华戍防务技术有限公司
        时间：4/2/20
        """
        joiner = '\r\n'
        cmds = joiner.join(self.command_pool)
        return self.send_and_recv(cmds)

    def is_scenario_loaded(self):
        """
        获取想定是否加载
        """
        return self.send_and_recv("print(Hs_GetScenarioIsLoad())")

    def creat_new_scenario(self):
        """
        作者：赵俊义
        日期：2020-3-7
        功能说明：新建想定
        函数类别：推演所用的函数
        """
        return self.send_and_recv("Hs_ScenEdit_CreateNewScenario()")

    def set_simulate_compression(self, n_compression=4):
        """
        函数功能：设置想定推演倍速
        函数类型：推演函数
        param ：n_compression推演时间步长档位（0：1 秒，1：2 秒，2：5 秒，3：15 秒，4：30 秒，
                5：1 分钟，6：5 分钟，7：15 分钟，8：30 分钟）。
        return ： lua执行成功/lua执行失败
        """
        lua_str = "ReturnObj(Hs_SetSimCompression(%d))" % n_compression
        ret = self.send_and_recv(lua_str)
        return ret

    def increase_simulate_compression(self):
        """
        作者：赵俊义
        日期: 2020-3-11
        函数功能：将推演时间步长提高 1 个档位
        函数类别: 推演函数
        :return:
        """
        return self.send_and_recv("Hs_SimIncreaseCompression()")

    def decrease_simulate_compression(self):
        """
        作者：赵俊义
        日期: 2020-3-11
        函数功能：将推演时间步长提高 1 个档位
        函数类别: 推演函数
        :return:
        """
        return self.send_and_recv("Hs_SimDecreaseCompression()")

    def set_simulate_mode(self, b_mode):
        """
        函数功能：设置想定推演模式
        函数类别：推演函数
        :param b_mode: True：非脉冲，False:脉冲
        :return:
        """
        lua_str = "Hs_SetSimMode(%s)" % str(b_mode).lower()
        return self.send_and_recv(lua_str)

    def set_run_mode(self, synchronous):
        """
        设置pyhon端与墨子服务端的交互模式，智能体决策想定是否暂停
        synchronous: true 同步模式,false 异步模式
        """
        if synchronous:
            return self.send_and_recv("SETRUNMODE(FALSE)")
        else:
            return self.send_and_recv("SETRUNMODE(TRUE)")

    def set_decision_step_length(self, step_interval):
        """
        设置决策间隔
        :param step_interval:
        :return:
        """
        self.send_and_recv("Hs_OneTimeStop('Stop', %d)" % step_interval)

    def suspend_simulate(self):
        """
        函数功能：设置环境暂停
        函数类别：推演函数
        return ：
        """
        lua_str = "Hs_SimStop()"
        self.send_and_recv(lua_str)

    def run_grpc_simulate(self):
        """
        数功能：开始推演，（之前设置的打开雷达消失）
        函数类型：推演函数
        param :
        return : lua执行成功/lua执行失败
        """
        # lua_str = "ReturnObj(Hs_SimRun(true))"
        lua_str = "ReturnObj(Hs_GRPCSimRun())"
        return self.send_and_recv(lua_str)

    def run_simulate(self):
        """
        数功能：开始推演，（之前设置的打开雷达消失）
        函数类型：推演函数
        param :
        return : lua执行成功/lua执行失败
        """
        lua_str = "ReturnObj(Hs_SimRun(true))"
        return self.send_and_recv(lua_str)

    def init_situation(self, scenario, app_mode):
        """
        初始化态势
        """
        bInitSuccess = scenario.situation.init_situation(self, scenario, app_mode)
        return bInitSuccess


    def update_situation(self, scenario):
        """
        更新态势
        :return:
        """
        return scenario.situation.update_situation(self, scenario)

    def emulate_no_console(self):
        """
        作者：解洋
        日期：2020-3-12
        函数功能：模拟无平台推演
        函数类型：编辑函数
        :return:
        """
        return self.send_and_recv("Tool_EmulateNoConsole()")

    def run_script(self, script):
        """
        作者：解洋
        日期：2020-3-11
        函数功能：运行服务端 Lua 文件夹下的 Lua 文件（*.lua）。
        函数类型：推演函数
        :param script:字符串。服务端 Lua 文件夹下包括 Lua 文件名在内的相对路径
        :return:
        """
        return self.send_and_recv("ScenEdit_RunScript('{}')".format(script))

    def set_key_value(self, key, value):
        """
        作者：解洋
        日期：2020-3-11
        函数功能：在系统中有一预设的“键-值”表，本函数向“键-值”表添加一条记录。
        函数类型：推演函数
        :param key:键”的内容
        :param value:“值”的内容
        :return:
        """
        return self.send_and_recv("ScenEdit_SetKeyValue('{}','{}')".format(key, value))

    def get_current_time(self):
        """
        作者：赵俊义
        日期：2020-3-7
        功能说明：获得当前想定时间
        函数类别：推演所用的函数
        """
        lua = "ReturnObj(ScenEdit_CurrentTime())"
        ret_time = self.send_and_recv(lua)
        return ret_time
