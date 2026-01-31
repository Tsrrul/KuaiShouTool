# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # @Date：2025/12/13 15:26
# # @Author : 等待
# # @Version: V1.0
# # @File ：Core_Logic_Interaction.py
#
import logging
import os

from src.core.ks_video_downloader import ShareLink
from src.utils.tool import Download, merge_with_imageio_ffmpeg, extract_audio_from_video, check_ffmpeg_environment, \
    batch_convert
from src.GUI.Set_Processing import set_regulation
import threading
import queue
import webbrowser
import re
from ttkbootstrap.dialogs import Messagebox
from src.core.BiliBili_api import BiliBili
from tkinter import TclError

logger = logging.getLogger(__name__)


class Core_Interaction(object):
    """
    单个视频GUI功能逻辑实现
    """

    def __init__(self, main):
        logger.info("单视频解析逻辑功能初始化成功")
        self.main = main
        self.Configuration_Information = set_regulation()
        self.Switch = None

        # 添加任务队列和工作线程
        self.task_queue = queue.Queue()
        self.worker_thread = None
        self._start_worker()

        # 用于存储异步任务对象
        self.url_object = None
        self.current_task_future = None

    def _start_worker(self):
        """启动工作线程处理异步任务"""
        logger.info("启动工作线程处理异步任务")
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
            self.worker_thread.start()

    def _process_tasks(self):
        """工作线程处理任务"""
        logger.info(f"循环工作线程开启")
        while True:
            try:
                task = self.task_queue.get(timeout=1)
                if task['type'] == 'preview':
                    self._process_preview_task(task)
                elif task['type'] == 'download':
                    self._process_download_task(task)
                self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"工作线程错误: {e}")

    def clear(self):
        """清空输入框"""
        self.main.Var.set('')
        self.main.entry._add_placeholder()
        logger.info("清空输入框")

    def paste(self):
        """粘贴剪贴板内容"""
        try:
            self.main.entry._clear_placeholder()
            self.main.Var.set(self.main.entry.clipboard_get())
            logger.info("粘贴剪贴板内容")
        except TclError:
            print("空剪切板")

    def detection(self, url):
        """检测URL格式"""
        if url == '' or len(url) < 3:
            return None
        elif re.match('https://', url) is None:
            return 'Error'
        return "OK"

    def preview(self, Preview):
        """异步预览/下载入口"""
        # 立即禁用按钮，防止重复点击
        if Preview:
            self._update_button_state(Component=self.main.Analysis_button, disabled=True)
            logger.info("禁用下载按钮")
        else:
            self._update_button_state(Component=self.main.preview_button, disabled=True)
            logger.info("禁用预览按钮")
        self.Switch = Preview

        # 获取URL内容
        url = self.main.entry.get_content()

        # 快速检测URL格式（主线程中，很快）
        judge = self.detection(url=url)

        if judge == "OK":
            # 将耗时任务放入队列
            self.task_queue.put({
                'type': 'preview',
                'preview': Preview,
                'share_url': self.main.Var.get(),
                "selection": self.Configuration_Information["selection"],  # 预先获取值
                "audio_format": self.Configuration_Information["audio_format"],  # 预先获取值
                "mp3": self.Configuration_Information["mp3"]
            })
            logger.info("将耗时任务放入队列")

            # 立即返回，不阻塞主线程
            return

        elif judge is None:
            if Preview:
                self._update_button_state(Component=self.main.Analysis_button, disabled=False)
            else:
                self._update_button_state(Component=self.main.preview_button, disabled=False)

            Messagebox.show_warning(
                message="URL不能为空或非法字符",
                title='错误',
                parent=None,
                alert=True
            )
            logger.warning("URL不能为空或非法字符")
        else:
            if Preview:
                self._update_button_state(Component=self.main.Analysis_button, disabled=False)
            else:
                self._update_button_state(Component=self.main.preview_button, disabled=False)
            Messagebox.show_warning(
                message="URL错误",
                title='错误',
                parent=None,
                alert=True
            )
            logger.warning("URL错误")

    def _process_preview_task(self, task):
        """工作线程处理预览任务"""
        logger.info("工作线程处理预览任务")
        try:
            # 在工作线程中创建对象和解析
            self.url_object = ShareLink(task['share_url'])

            # 解析HTML获取JSON
            result = self.url_object.html_json()

            # 回到主线程处理结果
            self.main.root.after(0, lambda: self._handle_preview_result(
                result, task, task.get('callback')
            ))
        except Exception as e:
            """
            切换到bilbil的api下载
            """
            try:
                logger.error(f"快手解析过程出错: {str(e)}")
                logger.info("切换bilibil视频下载")
                self.main.root.after(0, lambda: self._update_button_state(Component=self.main.Analysis_button,
                                                                          disabled=True, text="下载中..."))
                bilibili_api = BiliBili(task['share_url'])
                vid, aud = bilibili_api.move_audio()
                mp4_content = merge_with_imageio_ffmpeg(vid, aud)
                if task['selection'] == "获取完整视频":
                    Download(mp4_content, ".m4a", save=self.Configuration_Information["SAVELOCATION"])
                else:
                    ot = extract_audio_from_video(video_path=mp4_content,
                                                  output_position=self.Configuration_Information["SAVELOCATION"] + '\\',
                                                  audio_format=task['audio_format'])
                    if ot == None:
                        self.main.root.after(0, lambda: self._handle_preview_error(
                            f"该音频格式并非{task['audio_format']}"
                        ))
                        return None
                    elif ot != None and task["mp3"]:
                        if not check_ffmpeg_environment():
                            self.main.root.after(0, lambda: self._handle_preview_error(
                                f"MP3强制转换失败: 无法找到ffmpeg,请检查资源完整性"
                            ))
                            os.unlink(ot)
                            return None
                        Result, Error_ = batch_convert(ot)
                        os.unlink(ot)
                        if not Result:
                            self.main.root.after(0, lambda: self._handle_preview_error(
                                f"{str(Error_)}"
                            ))
                            return None
                self.main.root.after(0, self._handle_download_complete)
            except Exception as e:
                logger.error(f"bilibili解析过程出错: {str(e)}")
                self.main.root.after(0, lambda e=e: self._handle_preview_error(
                    f"解析过程出错: {str(e)}"
                ))
            finally:
                self.main.root.after(0, lambda: self._update_button_state(Component=self.main.Analysis_button,
                                                                          disabled=False, text="解析下载"))

    def _handle_preview_result(self, result, Switch, callback=None):
        """在主线程处理预览结果"""
        logger.info("在主线程处理预览结果")
        # 恢复按钮状态
        if Switch["preview"]:
            self._update_button_state(Component=self.main.Analysis_button, disabled=False)
        else:
            self._update_button_state(Component=self.main.preview_button, disabled=False)

        try:
            movie_url = result.movieURL
            if movie_url is not None:
                if Switch["preview"]:
                    # 异步下载
                    self._start_download_task(movie_url, Switch=Switch["preview"])
                else:
                    # 打开浏览器
                    webbrowser.open(movie_url)

                # 如果有回调函数，执行回调
            else:
                Messagebox.show_warning(
                    message="解析失败",
                    title='错误',
                    parent=None,
                    alert=True
                )
        except Exception as e:
            self._handle_preview_error(f"处理结果出错: {str(e)}")
            logger.error(f"处理结果出错: {str(e)}")

    def _start_download_task(self, movie_url, Switch):
        """启动下载任务"""
        logger.info('启动下载任务')
        # 显示下载中状态
        if Switch:
            self._update_button_state(Component=self.main.Analysis_button, disabled=True, text="下载中...")

        # 将下载任务放入队列
        self.task_queue.put({
            'type': 'download',
            'movie_url': movie_url,
            "Switch": Switch,
            "selection": self.Configuration_Information["selection"],  # 预先获取值
            "audio_format": self.Configuration_Information["audio_format"], # 预先获取值
            "mp3" : self.Configuration_Information["mp3"]
        })
        logger.info(f"将下载任务放入队列:'type':  'download','movie_url': {movie_url},'Switch': {Switch}")

    def _process_download_task(self, task):
        """工作线程处理下载任务"""
        logger.info("工作线程处理下载任务")
        try:
            # 获取视频数据
            video_content = self.url_object.video_data(task['movie_url'])
            # 下载视频
            if task['selection'] == "获取完整视频":
                Download(content=video_content, Format=".m4a", save=self.Configuration_Information["SAVELOCATION"])
            else:
                ot = extract_audio_from_video(video_path=video_content,
                                              output_position=self.Configuration_Information["SAVELOCATION"] + '\\',
                                              audio_format=task['audio_format']
                                              )
                if ot == None:
                    self.main.root.after(0, lambda: self._handle_preview_error(
                        f"该音频格式并非{task['audio_format']}"
                    ))
                    return
                elif ot != None and task['mp3']:
                        if not check_ffmpeg_environment():
                            self.main.root.after(0, lambda: self._handle_preview_error(
                                f"MP3强制转换失败: 无法找到ffmpeg,请检查资源完整性"
                            ))
                            os.unlink(ot)
                            return None
                        Result, Error_ = batch_convert(ot)
                        os.unlink(ot)
                        if not Result:
                            self.main.root.after(0, lambda: self._handle_preview_error(
                                f"{str(Error_)}"
                            ))
                            return None

            # 回到主线程显示完成消息
            self.main.root.after(0, lambda: self._handle_download_complete())

        except Exception as e:

            # 确保异常变量在正确的范围内被捕获和使用

            error_msg = f"下载失败: {str(e)}"

            logger.error(error_msg)  # 或其他日志记录方式
            self.main.root.after(0, lambda: self._handle_download_error(error_msg))

            # 处理'int' object is not subscriptable错误

            if hasattr(e, '__getitem__'):

                # 只有当对象支持索引时才进行索引操作

                pass

            else:

                # 对于不支持索引的对象，转换为字符串处理

                error_str = str(e)

    def _handle_download_complete(self):
        """处理下载完成"""
        if self.Switch:
            self._update_button_state(Component=self.main.Analysis_button, disabled=False, text="解析下载")
        else:
            self._update_button_state(Component=self.main.preview_button, disabled=False, text="预览")
        Messagebox.show_info(
            message="下载完成",
            title="提示",
            parent=None
        )
        logger.info("下载完成")

    def _handle_download_error(self, error_msg):
        """处理下载错误"""
        if self.Switch:
            self._update_button_state(Component=self.main.Analysis_button, disabled=False, text="解析下载")
        else:
            self._update_button_state(Component=self.main.preview_button, disabled=False, text="预览")
        Messagebox.show_warning(
            message=error_msg,
            title='错误',
            parent=None,
            alert=True
        )
        logger.error("下载错误")

    def _handle_preview_error(self, error_msg):
        """处理预览错误"""
        if self.Switch:
            self._update_button_state(Component=self.main.Analysis_button, disabled=False, text="解析下载")
        else:
            self._update_button_state(Component=self.main.preview_button, disabled=False, text="预览")
        Messagebox.show_warning(
            message=error_msg,
            title='错误',
            parent=None,
            alert=True
        )
        logger.error("预览失败")

    def _update_button_state(self, Component, disabled=True, text=None):
        """更新按钮状态"""
        try:
            if Component:
                if disabled:
                    Component.config(state='disabled')
                else:
                    Component.config(state='normal')

                if text:
                    Component.config(text=text)
        except Exception as e:
            print(f"更新按钮状态失败: {e}")

    def reread_Configuration_file(self):
        """重新读取配置文件"""
        self.Configuration_Information = set_regulation()
        logger.info("重新读取配置文件")

    def cleanup(self):
        """清理资源"""
        if self.worker_thread and self.worker_thread.is_alive():
            # 可以添加停止逻辑，但daemon线程会在主程序退出时自动结束
            pass
