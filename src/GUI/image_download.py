#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date：2025/12/14 11:05
# @Author : 等待
# @Version: V1.0
# @File ：image_download.py

import logging
import threading
import execjs
import requests
from PIL import Image, ImageTk
import io
import tkinter as tk
import ttkbootstrap as ttk
from src.core.ks_image_parser import KsImage
from src.GUI.Core_Logic_Interaction import Core_Interaction
from queue import Queue
from src.GUI.Set_Processing import set_regulation
from src.utils.tool import Download, MessageBox
import time

loger = logging.getLogger(__name__)

def image_Binary(url):
    """
    :param url:  用户输入网链
    :return:  解析图片返回所有图片二进制列表
    # """
    try:
        a = KsImage(url=url)
        c = a.get_image()
        image_content = [requests.get(i, timeout=5).content for i in c.image_url]
        return image_content, c.title
    except requests.exceptions.ConnectionError as e:
        loger.error(f"网络错误:{e}")
        print("网络错误")
        return 404
    except execjs._exceptions.ProgramError as e:
        loger.error(f"JavaScript执行错误: {e}")
        print(f"JavaScript执行错误: {e}")
        return None
    except Exception as e:
        loger.error(f"未知错误: {e}")
        print(f"未知错误: {e}")
        return "UnknownError"


class Image_Download(Core_Interaction):
    """
    图片GUI功能逻辑实现
    """

    def __init__(self, main):
            self.main = main
            self.Configuration = {}
            self.get_configuration()
            self.messagebox = MessageBox()
            # 添加默认图片尺寸配置
            self.image_preview_width = 500
            self.image_preview_height = 490
            # 添加窗口调整绑定
            self.main.root.bind('<Configure>', self.on_window_resize)
            # 存储上次的窗口尺寸，避免频繁调整
            self.last_window_size = (self.main.root.winfo_width(), self.main.root.winfo_height())
            self.resize_timer = None


    def on_window_resize(self, event=None):
        """
        窗口调整大小时触发，延迟重绘图片
        """
        if event.widget == self.main.root:  # 只响应主窗口的调整
            # 使用定时器延迟处理，避免频繁重绘
            if self.resize_timer:
                self.main.root.after_cancel(self.resize_timer)
            self.resize_timer = self.main.root.after(200, self._handle_resize)

    def _handle_resize(self):
        """
        实际处理窗口调整的函数
        """
        # 获取当前预览区域的大小
        self.resize_timer = None
        preview_frame_width = self.main.preview_section.winfo_width()
        preview_frame_height = self.main.preview_section.winfo_height()

        # 如果尺寸太小或窗口最小化，不进行处理
        if preview_frame_width < 100 or preview_frame_height < 100:
            return

        # 计算新的图片预览尺寸（留出一些边距）
        new_width = max(300, preview_frame_width - 40)  # 最小宽度300，留20像素边距
        new_height = max(300, preview_frame_height - 40)  # 最小高度300

        # 只有当尺寸变化足够大时才更新图片（避免微小调整的频繁重绘）
        width_diff = abs(new_width - self.image_preview_width)
        height_diff = abs(new_height - self.image_preview_height)

        if width_diff > 20 or height_diff > 20:  # 变化超过20像素才更新
            self.image_preview_width = new_width
            self.image_preview_height = new_height

            # 如果有当前图片内容，重新加载并显示
            if hasattr(self, 'current_image_content'):
                self.main.root.after(0, lambda: self._refresh_preview_images())

    def _refresh_preview_images(self):
        """
        刷新预览图片（使用当前尺寸）
        """
        if hasattr(self, 'current_image_content') and hasattr(self, 'current_image_label'):
            self.update_preview_images(self.current_image_content, self.current_image_label)

    def on_preview_frame_configure(self, event=None):
        """
        更新画布滚动区域
        """
        self.main.preview_canvas.configure(scrollregion=self.main.preview_canvas.bbox("all"))

    def network_request(self, url):
        """
        :param url:用户输入网链
        :return: 预览图片
        """
        try:
            image_content_list, title = image_Binary(url)
            self.main.root.after(0, lambda: self.update_preview_images(content=image_content_list, label=title))
        except Exception:
            error = image_Binary(url)
            if error == 404:
                self.main.root.after(0, lambda: self.messagebox.show_error(message="网络异常(错误码：102)", title="报错",
                                                                           parent=self.main.root))
            elif error == None:
                self.main.root.after(0, lambda: self.messagebox.show_error(message="无法识别链接", title="报错",
                                                                           parent=self.main.root))
            else:
                self.main.root.after(0, lambda: self.messagebox.show_error(message="未知错误", title="报错",
                                                                           parent=self.main.root))
            self.main.root.after(0, lambda: self._update_button_state(self.main.image_preview_button, disabled=False,
                                                                      text="预览"))

    def IO_image_download(self, url):
        """
        :param url:用户输入网链
        :return: 下载图片
        """
        try:
            image_content_list, title = image_Binary(url)

            Number_tasks = len(image_content_list)

            for perform, content in enumerate(image_content_list):
                Download(content, ".jpg", save=self.Configuration["SAVELOCATION"])
            self.main.root.after(0, lambda: self.messagebox.show_info(title="下载", message="下载完成"))
            self.main.root.after(0, lambda: self._update_button_state(self.main.image_Analysis_button, disabled=False,
                                                                      text="解析下载"))
        except Exception:
            error = image_Binary(url)
            if error == 404:
                self.main.root.after(0, lambda: self.messagebox.show_error(message="网络异常(错误码：102)", title="报错",
                                                                           parent=self.main.root))
            elif error == None:
                self.main.root.after(0, lambda: self.messagebox.show_error(message="无法识别链接", title="报错",
                                                                           parent=self.main.root))
            else:
                self.main.root.after(0, lambda: self.messagebox.show_error(message="未知错误", title="报错",
                                                                           parent=self.main.root))
            self.main.root.after(0, lambda: self._update_button_state(self.main.image_Analysis_button, disabled=False,
                                                                      text="解析下载"))

    def preview(self, Choose):
        """
        :param Choose:下载 or 预览
        :return: 任务分配： 预览（network_request） 下载（IO_image_download）
        """
        loger.info(f"启动任务：{Choose}-1代表下载，0代表预览")
        # 获取URL内容
        url = self.main.image_entry.get_content()

        # 快速检测URL格式（主线程中，很快）
        judge = self.detection(url=url)

        if judge == "OK":
            # 任务分配
            if Choose:
                loger.info("启动任务：下载")
                self._update_button_state(self.main.image_Analysis_button, disabled=True, text="下载中")
                threading.Thread(target=self.IO_image_download, args=(url,), daemon=True).start()
            else:
                loger.info("启动任务：预览")
                self._update_button_state(self.main.image_preview_button, disabled=True, text="加载中...")
                threading.Thread(target=self.network_request, args=(url,), daemon=True).start()
            # 立即返回，不阻塞主线程
            return

        elif judge is None:
            # 对于不符合的输入报错
            self.messagebox.show_warning(
                message="URL不能为空或非法字符",
                title='错误',
                parent=self.main.root,
            )
            loger.warning("URL不能为空或非法字符")

        else:
            loger.warning("URL错误")
            self.messagebox.show_warning(
                message="URL错误",
                title='错误',
                parent=self.main.root,
            )

    def update_preview_images(self, content, label):
        """
        更新预览图片

        Args:
            content (list): 图片二进制数据
            label: 标题
        """
        # 保存当前内容，以便窗口调整时重新加载
        self.current_image_content = content
        self.current_image_label = label

        loger.info("更新预览图片")
        # 清除现有预览图片
        for preview_label in self.main.preview_image_labels:
            preview_label.destroy()
        self.main.preview_image_labels.clear()

        # 显示图片标题
        try:
            self.main.preview_inner_frame.config(text=label[0])
        except Exception as e:
            self.main.preview_inner_frame.config(text="加载标题失败")
            loger.error(f"加载标题失败:{e}")

        # 获取当前预览框架的实际可用大小
        frame_width = self.main.preview_section.winfo_width()
        frame_height = self.main.preview_section.winfo_height()

        # 如果框架大小有效，则使用框架大小，否则使用默认大小
        if frame_width > 100 and frame_height > 100:
            available_width = frame_width - 40  # 留出边距
            available_height = frame_height - 40
        else:
            available_width = self.image_preview_width
            available_height = self.image_preview_height

        # 加载并显示新图片
        for url in content:
            try:
                pil_image = Image.open(io.BytesIO(url))

                # 根据原始比例调整图片大小，保持宽高比
                original_width, original_height = pil_image.size
                aspect_ratio = original_width / original_height

                # 计算新的尺寸，保持宽高比
                # 限制最大宽度为可用宽度的80%（为多张图片并排留空间）
                max_img_width = int(available_width * 0.8)
                max_img_height = available_height - 50  # 留出标题空间

                new_width = max_img_width
                new_height = int(new_width / aspect_ratio)

                # 如果高度超出限制，则按高度调整
                if new_height > max_img_height:
                    new_height = max_img_height
                    new_width = int(new_height * aspect_ratio)

                # 确保最小尺寸
                new_width = max(100, new_width)
                new_height = max(100, new_height)

                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo_image = ImageTk.PhotoImage(pil_image)

                # 创建标签显示图片
                label = ttk.Label(self.main.preview_inner_frame, image=photo_image)
                label.image = photo_image  # 保持引用防止被垃圾回收
                label.pack(side=tk.LEFT, fill=tk.Y, padx=5, expand=True)
                self.main.preview_image_labels.append(label)

            except Exception as e:
                # 出错时显示占位符
                placeholder = ttk.Label(self.main.preview_inner_frame, text="❌",
                                        font=("Arial", min(190, available_height // 3)),
                                        padding=(10, available_height // 2))
                placeholder.pack(side=tk.LEFT, padx=5, fill=tk.Y)
                self.main.preview_image_labels.append(placeholder)
                loger.error(f'图片加载失败：{e}')

        # 更新滚动区域
        self.main.preview_inner_frame.update_idletasks()
        self.on_preview_frame_configure()
        self._update_button_state(self.main.image_preview_button, disabled=False, text="预览")

    def clear(self):
        """清空输入框"""
        self.main.image_Var.set('')
        self.main.image_entry._add_placeholder()

    def paste(self):
        """粘贴剪贴板内容"""
        self.main.image_entry._clear_placeholder()
        self.main.image_Var.set(self.main.entry.clipboard_get())

    def get_configuration(self):
        """
        :return:获取配置
        """
        loger.info("image获取配置")
        self.Configuration = set_regulation()






