#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date：2025/12/20 18:49
# @Author : 等待
# @Version: V1.0
# @File ：main.py
import logging
from src import *
import threading
import msvcrt
import os
import tkinter as tk
import sys


class SingleInstance:
    def __init__(self, lock_file="app.lock"):
        self.lock_file = lock_file
        self.lock_fd = None

    def acquire(self):
        """获取文件锁，失败则说明已存在实例"""
        try:
            self.lock_fd = open(self.lock_file, 'w')
            msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_NBLCK, 1)  # 非阻塞锁
        except (IOError, BlockingIOError):
            return False
        return True

    def release(self):
        """释放文件锁（兼容文件已被删除的情况）"""
        if self.lock_fd:
            try:
                msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
            except:
                pass
            self.lock_fd.close()
        if os.path.exists(self.lock_file):
            try:
                os.remove(self.lock_file)
            except:
                pass


# -------------------------- 配置信息 --------------------------

if __name__ == "__main__":
    # 1. 单实例检查（优先执行，避免重复启动）
    single_instance = SingleInstance()
    try:
        if not single_instance.acquire():
            temp_root = tk.Tk()
            temp_root.withdraw()
            Messagebox.show_info(title="提示", message="应用已在运行中，请勿重复启动！")
            sys.exit()  # 2. 用 sys.exit() 替代 exit()
        else:
            threading.Thread(target=log_Configuration, args=(INITIAL_DICT["LOGFILE"], INITIAL_DICT["LOGPATH"]),
                             daemon=True).start()
            logger = logging.getLogger(__name__)
            logger.info("日志开启")
            app = KsParserGUI()
            try:
                app.run()
            except Exception:
                logger.info("程序结束")
                sys.exit(0)
    finally:
        single_instance.release()

