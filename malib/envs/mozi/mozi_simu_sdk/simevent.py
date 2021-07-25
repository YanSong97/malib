#!/usr/bin/env python3
# -*- coding:utf-8 -*-
##########################################################################################################
# File name : side.py
# Create date : 2020-1-8
# Modified date : 2020-1-8
# All rights reserved:北京华戍防务技术有限公司
# Author:xy
##########################################################################################################
from abc import ABCMeta, abstractmethod
import re
import logging


########################################################################
class CSimEvent:
    """
    事件类
    """

    def __init__(self, strGuid, mozi_server, situation):
        # GUID
        self.strGuid = strGuid
        # 仿真服务类MoziServer实例
        self.mozi_server = mozi_server
        # 态势
        self.situation = situation
        # 名称
        self.strName = ""
        # 描述文本
        self.strDescription = ""
        # 是否重复使用
        self.bIsRepeatable = ""
        # 是否激活
        self.bIsActive = ""
        # 是否在消息中显示
        self.bIsMessageShown = ""
        # 发生概率
        self.sProbability = ""
        # 所属触发器
        self.m_Triggers = ""
        # 所属条件
        self.m_Conditions = ""
        # 所属动作
        self.m_Actions = ""

    def get_triggers(self):
        """
        功能：获取所有触发器。
        编写：aie
        时间：20200401
        返回：所有触发器（类型：dict）
        """
        triggers = {}
        triggers.update(self.situation.trgunitdtcd_dic)
        triggers.update(self.situation.trgunitdmgd_dic)
        triggers.update(self.situation.trgunitdstrd_dic)
        triggers.update(self.situation.trgpoints_dic)
        triggers.update(self.situation.trgtime_dic)
        triggers.update(self.situation.trgrglrtime_dic)
        triggers.update(self.situation.trgrndmtime_dic)
        triggers.update(self.situation.trgscenldd_dic)
        triggers.update(self.situation.trgunitrmns_dic)
        return triggers

    def get_conditions(self):
        """
        功能：获取所有条件。
        编写：aie
        时间：20200401
        返回：所有条件（类型：dict）
        """
        conditions = {}
        conditions.update(self.situation.cndscenhsstrtd_dic)
        conditions.update(self.situation.cndsidepstr_dic)
        conditions.update(self.situation.cndluascrpt_dic)
        return conditions

    def get_actions(self):
        """
        功能：获取所有动作。
        编写：aie
        时间：20200401
        返回：所有动作（类型：dict）
        """
        actions = {}
        actions.update(self.situation.actionmssg_dic)
        actions.update(self.situation.actionpnts_dic)
        actions.update(self.situation.actiontlprt_dic)
        actions.update(self.situation.actionchngms_dic)
        actions.update(self.situation.actionendscnr_dic)
        actions.update(self.situation.actionlscrpt_dic)
        return actions


    def execute_action(self):
        """
       作者：赵俊义
       日期：2020-3-10
       函数类别：推演所用的函数
       功能说明：执行某个 lua 类型的动作，会将动作中的 lua 脚本运行一次，可
                以查验动作中 lua 脚本效果
        @return:
        """
        return self.mozi_server.send_and_recv("ScenEdit_ExecuteEventAction ('{}')".format(self.strGuid))

    def update_setting(self, newName, description, isActive, isShow, isReatable, prob):
        """
       作者：赵俊义;amended by aie
       日期：2020-3-10;amended on 2020-4-26
       函数类别：推演所用的函数
       功能说明：更新事件的属性
        @param eventGuid: 要更新事件的guid
        @param newName:新事件名称
        @param description:事件说明
        @param isActive:是否启用
        @param isShow:是否显示
        @param isReatable:是否可重复
        @param prob:发生概率
        @return:
        """
        lua_scrpt = "ScenEdit_UpdateEvent('{}',{'{}', '{}',{},{},{},{}})".format(self.strGuid, newName, description,
                                                                                 isActive, isShow, isReatable, prob)
        return self.mozi_server.send_and_recv(lua_scrpt)
