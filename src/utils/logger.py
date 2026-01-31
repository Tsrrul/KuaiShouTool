#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date：2025/12/20 17:40
# @Author : 等待
# @Version: V1.0
# @File ：logger.py
# 日志配置
import logging
import time


year, month, day, hour, minute, second, weekday, yearday, isdst = time.localtime()
FORMAT = "%(asctime)s - %(levelname)s(%(levelno)s) - %(name)s - %(message)s(%(funcName)s) "


def log_Configuration(start, path):
    """
    :param start: 开关
    :param path:  保存路径
    :return:  配置并记录日志
    """
    if start:
        if path == None:
            logging.basicConfig(
                filename=f"{year}-{month}-{day}.log",
                filemode="a",
                level=logging.DEBUG,
                encoding="utf-8",
                format=FORMAT
            )
        else:
            logging.basicConfig(
                filename=path+"//"+f"{year}-{month}-{day}.log",
                filemode="a",
                level=logging.DEBUG,
                encoding="utf-8",
                format=FORMAT
            )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format=FORMAT
        )




