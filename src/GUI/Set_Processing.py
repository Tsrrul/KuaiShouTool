#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date：2025/12/13 15:20
# @Author : 等待
# @Version: V1.0
# @File ：Set_Processing.py

import os
import sys
from pathlib import Path
import ast
import threading


def set_regulation():
    """
    :return:配置初始化
    """
    try:
        if os.path.exists("ConfigurationFile.txt"):
            with open("ConfigurationFile.txt", "r", encoding="utf-8") as ConfigurationFile:
                INITIAL_DICT = ConfigurationFile.read()
                INITIAL_DICT = ast.literal_eval(INITIAL_DICT)
                for i in ["LOGFILE", "LOGPATH", "SAVELOCATION", "UPDATE", "POSITION", "IPproxy", "IP", "selection", "audio_format", "mp3"]:
                    var = INITIAL_DICT[i]
        else:
            INITIAL_DICT = {
                "LOGFILE": True,
                'LOGPATH': None,
                "SAVELOCATION": None,
                'UPDATE': True,
                "POSITION": False,
                "IPproxy": False,
                "IP": None,
                "selection": "获取完整视频",
                'audio_format': "mp3",
                'mp3' : False
            }

    except Exception:
        INITIAL_DICT = {
            "LOGFILE": True,
            'LOGPATH': None,
            "SAVELOCATION": None,
            'UPDATE': True,
            "POSITION": False,
            "IPproxy": False,
            "IP": None,
            "selection": "获取完整视频",
            'audio_format': "mp3",
            "mp3" : False
        }
        print("读写失败，使用默认配置")
    return INITIAL_DICT


class SettingsLogic(object):
    """
    设置保存及管理
    """
    def __init__(self, main=None, Core=None):
        self.main = main
        self.core = Core.Download_Preview
        self.image = Core.image_down
        self.Settings_page = None

    def write_configuration(self, configuration):
        with open("ConfigurationFile.txt", "w", encoding="utf-8") as ConfigurationFile:
            ConfigurationFile.write(str(configuration))

    def pathdefault(self):
        if not getattr(sys, "frozen", False):
            return os.getcwd()
        else:
            return Path(sys.executable).parent

    def save(self):
        if self.Settings_page == "download":
            self.main.INITIAL_DICT["SAVELOCATION"] = self.main.path_var.get()
            self.main.INITIAL_DICT["selection"] = self.main.get_object.get()
            self.main.INITIAL_DICT["audio_format"] = self.main.Audio_format.get()
            self.main.INITIAL_DICT["mp3"] = self.main.e_.get()

        if self.Settings_page == "general":
            self.main.INITIAL_DICT["UPDATE"] = self.main.update_check_var.get()
            self.main.INITIAL_DICT["POSITION"] = self.main.position_check_var.get()
            self.main.INITIAL_DICT["LOGFILE"] = self.main.log_check_var.get()
            self.main.INITIAL_DICT["LOGPATH"] = self.main.log_var.get()

        if self.Settings_page == "network":
            self.main.INITIAL_DICT['IPproxy'] = self.main.use_proxy_var.get()
            self.main.INITIAL_DICT["IP"] = self.main.proxy_address_var.get()

        self.write_configuration(self.main.INITIAL_DICT)
        threading.Thread(
            target=self.core.reread_Configuration_file
        ).start()

        threading.Thread(
            target=self.image.get_configuration
        ).start()
        print(self.main.INITIAL_DICT)
