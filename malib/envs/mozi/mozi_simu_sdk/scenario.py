# -*- coding:utf-8 -*-
##########################################################################################################
# File name : scenario.py
# Create date : 2020-1-8
# Modified date : 2020-1-8
# All rights reserved:北京华戍防务技术有限公司
# Author:xy
##########################################################################################################

#from ..entitys.situation import CSituation
from malib.envs.mozi.mozi_simu_sdk.situation import CSituation
#from ..entitys.side import CSide
from malib.envs.mozi.mozi_simu_sdk.side import CSide


class CScenario:
    """想定"""

    def __init__(self, mozi_server):
        self.mozi_server = mozi_server
        # 类名
        self.ClassName = "CCurrentScenario"
        # GUID
        self.strGuid = ""
        # 标题
        self.strTitle = ""
        # 想定文件名
        self.strScenFileName = ""
        # 描述
        self.strDescription = ""
        # 当前时间
        self.m_Time = ""
        # 是否是夏令时
        self.bDaylightSavingTime = False
        # 当前想定第一次启动的开始时间
        self.m_FirstTimeRunDateTime = ""
        # 用不上
        self.m_FirstTimeLastProcessed = 0.0
        # 用不上
        self.m_grandTimeLastProcessed = 0.0
        # 夏令时开始时间（基本不用）
        self.strDaylightSavingTime_Start = 0.0
        # 夏令结束时间（基本不用）
        self.strDaylightSavingTime_End = 0.0
        # 想定开始时间
        self.m_StartTime = ""
        # 想定持续时间
        self.m_Duration = ""
        # 想定精细度
        self.sMeta_Complexity = 1
        # 想定困难度
        self.sMeta_Difficulty = 1
        # 想定发生地
        self.strMeta_ScenSetting = ""
        # 想定精细度的枚举类集合
        self.strDeclaredFeatures = ""
        # 想定的名称
        self.strCustomFileName = ""
        # 编辑模式剩余时间
        self.iEditCountDown = 0
        # 推演模式剩余时间
        self.iStartCountDown = 0
        # 暂停剩余时间
        self.iSuspendCountDown = 0
        # 获取推演的阶段模式
        self.m_CurrentStage = 0
        # 态势
        self.situation = CSituation(mozi_server)
        self.sides = self.get_sides()  # by aie

    def get_sides(self):
        """
        功能：获取所有推演方
        编写：aie
        时间：20200330
        返回：所有推演方（类型：dict）
        """
        return self.situation.side_dic

    def get_title(self):
        """
        作者：赵俊义; amended by aie
        日期：2020-3-7;amended on 2020-4-26
        功能说明：想定的描述表述
        函数类别：推演所用的函数
        """
        return self.strTitle

    def get_weather(self):
        """
        功能：获取天气条件。
        编写：aie
        时间：20200401
        返回：天气条件（类型：CWeather）
        """
        return self.situation.weather

    def get_responses(self):
        """
        功能：获取仿真响应信息。
        编写：aie
        时间：20200401
        返回：仿真响应信息（类型：dict）
        """
        return self.situation.response_dic

    def get_weapon_impacts(self):
        """
        功能：获取所有武器冲击。
        编写：aie
        时间：20200401
        返回：所有武器冲击（类型：dict）
        """
        return self.situation.wpnimpact_dic

    def get_events(self):
        """
        功能：获取所有事件。
        编写：aie
        时间：20200401
        返回：所有事件（类型：dict）
        """
        return self.situation.simevent_dic

    def get_units_by_name(self, name):
        """
        功能：从上帝视角用名称获取单元。
        编写：aie
        时间：20200330
        :param name:
        :return:
        """
        # 需求来源：20200330-1.1/3:lzy
        units = {}
        sbmrns = {k: v for k, v in self.situation.submarine_dic.items() if v.strName == name}
        shps = {k: v for k, v in self.situation.ship_dic.items() if v.strName == name}
        fclts = {k: v for k, v in self.situation.facility_dic.items() if v.strName == name}
        airs = {k: v for k, v in self.situation.aircraft_dic.items() if v.strName == name}
        stllts = {k: v for k, v in self.situation.satellite_dic.items() if v.strName == name}
        wpns = {k: v for k, v in self.situation.weapon_dic.items() if v.strName == name}
        ungddwpns = {k: v for k, v in self.situation.unguidedwpn_dic.items() if v.strName == name}
        units.update(sbmrns)
        units.update(shps)
        units.update(fclts)
        units.update(airs)
        units.update(stllts)
        units.update(wpns)
        units.update(ungddwpns)
        return units

    def unit_is_alive(self, guid):
        """
        功能：从上帝视角用uid判断实体单元是否存在
        编写：aie
        时间：20200330
        :param guid:实体单元guid
        :return:
        """
        # 需求来源：20200330-1.2/3:lzy
        if guid in self.situation.all_guid:
            return True
        else:
            return False

    def get_side_by_name(self, name):
        """
        根据名字获取推演方信息
        :param name:推演方名字
        :return:
        """
        for k, v in self.situation.side_dic.items():
            if v.strName == name:
                return v

    def add_side(self, side_name):
        """
        类别：编辑使用函数
        功能：添加方
        :param side_name: f放的名字
        :return:
        """
        return self.mozi_server.send_and_recv("HS_LUA_AddSide({side='%s'})" % side_name)

    def remove_side(self, side):
        """
        类别：编辑使用函数
        移除推演方
        :param side:方的名字
        :return:
        """
        return self.mozi_server.send_and_recv("ScenEdit_RemoveSide({side='%s'})" % side)

    def set_side_posture(self, sideAName, sideBName, relation):
        """
        类别：编辑使用函数
        设置对抗关系 complate
        :param sideAName:
        :param sideBName:
        :param relation:：字符串。立场编码（'F'-友好，'H'-敌对，'N'-中立，'U'-非友）
        :return:
        """
        return self.mozi_server.send_and_recv(
            "ScenEdit_SetSidePosture('{}','{}','{}')".format(sideAName, sideBName, relation))

    def reset_all_sides_scores(self):
        """
        重置所有推演方分数
        """
        return self.mozi_server.send_and_recv("Hs_ResetAllSideScores()")

    def reset_all_losses_expenditures(self):
        """
        类别：编辑使用函数
        将各推演方所有战斗损失、战斗消耗、单元损伤等均清零。
        """
        return self.mozi_server.send_and_recv("Hs_ResetAllLossesExpenditures()")

    def set_scenario_time(self, set_time):
        """
        作者：赵俊义
        日期：2020-3-7
        功能说明：设置想定时间
        函数类别：推演所用的函数
        """
        return self.mozi_server.send_and_recv("Hs_SetScenarioTime('{}')".format(set_time))

    def get_current_time(self):
        """
        作者：赵俊义
        日期：2020-3-7
        功能说明：获得当前想定时间
        函数类别：推演所用的函数
        """
        lua = "ReturnObj(ScenEdit_CurrentTime())"
        ret_time = self.mozi_server.send_and_recv(lua)
        return ret_time

    def get_player_name(self):
        """
        作者：赵俊义
        日期：2020-3-7
        函数类别：推演函数
        功能说明：获取推演方名称
        """
        return self.mozi_server.send_and_recv("ScenEdit_PlayerSide()")

    def add_player_side(self,side_name):
        """
        功能：添加推演方
        :return:
        """
        return self.mozi_server.send_and_recv("ScenEdit_AddSide({side='%s'})" % side_name)

    def get_side_posture(self, sideA, sideB):
        """
       作者：赵俊义
       日期：2020-3-9
       函数类别：推演所用的函数
       功能说明：获取一方对另一方的立场
       :param sideA:一方的名称
       :param sideB:另一方的名称
       """
        return self.mozi_server.send_and_recv("ScenEdit_GetSidePosture('{}','{}')".format(sideA, sideB))

    def change_unit_side(self, strName, sideA, sideB):
        """
        作者：赵俊义
       日期：2020-3-9
       函数类别：推演所用的函数
       功能说明：改变单元的方
        @param sideA: 单元所在的方
        @param sideB: 单元要改变的方
        @param strName: 单元名称
        @return:
        """
        return self.mozi_server.send_and_recv(
            "ScenEdit_SetUnitSide({{name='{}',side='{}',newside='{}'}})".format(strName, sideA,
                                                                                sideB))  # ammended by aie
    def dump_rules(self):
        """
        作者：赵俊义
        日期：2020-3-10
        函数类别：推演所用的函数
        功能说明：向系统安装目录下想定默认文件夹以 xml 文件的方式导出事件、条件、触发器、动作、特殊动作。
        @return:由事件内容组成、以 xml 文件格式输出的字符串。
        """
        return self.mozi_server.send_and_recv("Tool_DumpEvents()")

    def set_decription(self, scenariotitle, setdescription):
        """
        作者：赵俊义
        日期：2020-3-7
        功能说明：想定的描述
        函数类别：推演所用的函数
        """
        return self.mozi_server.send_and_recv("Hs_SetScenarioDescribe({'{}','{}')".format(scenariotitle, setdescription))

    def set_realism(self, gunfireControl, unlimitedBaseMags, aCDamage):
        """
        作者：赵俊义
        日期：2020-3-7
        功能说明：设置仿真精细度
        函数类别：推演所用的函数
        gunfireControl ：高精度火控算法
        unlimitedBaseMags： 海空弹药不受限
        aCDamage ：飞机高精度毁伤模型

        """
        return self.mozi_server.send_and_recv(
            " Hs_FeaturesReakismSet({DetailedGunFirControl =%s,UnlimitedBaseMags = %s,AircraftDamage = %s})" % (
                gunfireControl, unlimitedBaseMags, aCDamage))

    def set_cur_side_and_dir_view(self, side_name_or_guid, open_or_close_dir_view):
        """
        作者：董卓
        日期：2020-5-3
        功能说明：设置服务端当前推演方,便于用户观察态势。
        函数类别：推演所用的函数
        side_name_or_guid ：推演方的名称或者GUID
        open_or_close_dir_view : 是否开启导演视图，是：true(字符串)，否：false(字符串)
        """
        return self.mozi_server.send_and_recv("ScenEdit_SetCurSideAndDirView('%s',%s)" % (side_name_or_guid, open_or_close_dir_view))

    def end_scenario(self):
        """
        函数功能：终止当前想定，进入参演方评估并给出评估结果
        函数类别：推演函数
        :return:
        """
        return self.mozi_server.send_and_recv("ScenEdit_EndScenario()")

    def save_scenario(self):
        """
        作者：赵俊义
        日期：2020-3-7
        功能说明：保存当前已经加载的想定
        函数类别：推演所用的函数
        """
        return self.mozi_server.send_and_recv("Hs_ScenEdit_SaveScenario()")

    def save_as(self, scenario_name):
        """
        作者：赵俊义
        日期：2020-3-7
        功能说明：另存当前已经加载的想定
        函数类别：推演所用的函数
        """
        return self.mozi_server.send_and_recv("Hs_ScenEdit_SaveAsScenario('{}')".format(scenario_name))

