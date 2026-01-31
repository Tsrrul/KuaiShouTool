#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date：2025/12/6 18:55
# @Author : 等待
# @Version: V1.0
# @File ：ks_parser_gui.py
import logging
import sys
import os
import webbrowser
from gc import get_objects
from pathlib import Path
import tkinter as tk
import ttkbootstrap as ttk
from src.utils.tool import size_tool, window_out
from src.GUI.Set_Processing import SettingsLogic, set_regulation
from src.GUI.Core_Logic_Interaction import Core_Interaction
from src.GUI.image_download import Image_Download
from ttkbootstrap.dialogs import Messagebox
from docs.Network_backend import Network_Backend

logger = logging.getLogger(__name__)

__version__ = '1.0.0'
INITIAL_DICT = set_regulation()
logger.info("获取配置成功")


def style():
    _style = ttk.Style()
    _style.configure(
        'Custom.TEntry'
    )
    _style.map(
        'Custom.TEntry',
        foreground=[('disabled', 'black')],  # 禁用时仍保持黑色
    )
    logger.info("样式配置成功")


def set_ico(window):
    try:
        if not getattr(sys, "frozen", False):
            path = os.path.join(os.getcwd(), "docs", "images", "favicon.ico")
            if os.path.exists(path):
                window.iconbitmap(path)
        else:
            path = os.path.join(Path(sys.executable).parent, "docs", "images", "favicon.ico")
            if os.path.exists(path):
                window.iconbitmap(path)
        logger.info("图标加载成功")
    except Exception as e:
        print(f"图标加载失败：{e}")
        logger.warning(f"图标加载失败：{e}")
        # 可以选择不设置图标，使用默认图标


class PlaceholderEntry(ttk.Entry):
    def __init__(self, master, placeholder="", color="grey", **kwargs):
        logger.info("PlaceholderEntry类构造成功")
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = "black"  # 默认文本颜色

        # 插入占位符文本并设置灰色
        self.insert(0, self.placeholder)
        self.config(foreground=self.placeholder_color)

        # 绑定事件
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, event=None):
        """获得焦点时清除占位符"""
        if self.get() == self.placeholder:
            self.delete(0, "end")
            self.config(foreground=self.default_fg_color)

    def _add_placeholder(self, event=None):
        """失去焦点时添加占位符"""
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(foreground=self.placeholder_color)

    def get_content(self):
        """获取实际输入内容（不包括占位符）"""
        content = self.get()
        if content == self.placeholder:
            return ""
        return content


class KsParserGUI(object):
    def __init__(self):
        self.update = Network_Backend()
        self.preview_image_labels = None
        self.root = None
        self.window_set()
        style()
        self.image_down = Image_Download(self)
        self.Download_Preview = Core_Interaction(self)
        self.set = Settings(self)
        self.menu()
        self.video_main()
        self.video_Entry()
        self.video_button()
        self.image_Entry()
        self.image_button()
        self.preview_frame()
        self.update_messagebox()

    def window_set(self, event=None):
        """
        :return:设置窗口配置
        """
        if event != None:
            notebook_widget = event.widget
            current_tab_index = notebook_widget.index("current")
            # 获取当前选中的frame
            current_frame = notebook_widget.nametowidget(notebook_widget.select())

            # 根据页面类型调整内部组件布局
            if current_tab_index == 0:  # 视频解析页面
                logger.info("切换布局1")
                self.root.state('normal')
                w, h = size_tool(self.root, 800, 220)
                self.root.geometry(f"800x220+{w}+{h}")
                self.root.resizable(0, 0)

            elif current_tab_index == 1 or current_tab_index == 2:  # 主页视频解析页面
                logger.info("切换布局2-3")
                w, h = size_tool(self.root, 1200, 800)
                self.root.geometry(f"1200x800+{w}+{h}")
                if self.root.resizable() == (0, 0):
                    self.root.resizable(True, True)
        else:
            logger.info("主窗口初始化")
            self.root = ttk.Window()
            ttk.Style('united')
            self.root.title('快手无水印解析Tool')  # 标题
            w, h = size_tool(self.root, 800, 150)
            self.root.geometry(f"800x150+{w}+{h}")
            set_ico(self.root)

    def run(self):
        try:
            logger.info("程序启动")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n程序已被用户中断")
            # 可以在这里添加清理资源的代码
            sys.exit(0)




    def video_main(self):
        """创建现代化主界面GUI"""
        # 创建主框架 - 增加圆角和阴影效果
        logger.info("创建总体GUI布局")
        notbook = ttk.Notebook(self.root)
        notbook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        notbook.bind("<<NotebookTabChanged>>", lambda event: self.window_set(event=event))

        # 使用卡片样式框架
        frame1 = ttk.Frame(notbook, bootstyle="light")
        frame3 = ttk.Frame(notbook, bootstyle="light")
        notbook.add(frame1, text='🎬 视频解析')
        notbook.add(frame3, text='🖼️ 图片解析')

        # 创建现代化主容器框架 - 增加内边距和背景
        self.main_container = ttk.Frame(frame1, padding=20)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.image_container = ttk.Frame(frame3, padding=20)
        self.image_container.pack(fill=tk.BOTH, expand=True)

    def video_Entry(self):
        logger.info("ui初始化视频输入")
        # 现代化输入框部分 - 增强视觉效果
        input_frame = ttk.Labelframe(
            self.main_container,
            text="🔗 视频链接输入",
            bootstyle="secondary",
            padding=(10, 10)
        )
        input_frame.pack(fill=tk.X, pady=(0, 0))

        # 创建现代化输入框 - 增加更多样式
        self.Var = tk.StringVar()
        self.entry = PlaceholderEntry(
            input_frame,
            textvariable=self.Var,
            placeholder=" 请输入分享链接...",
            bootstyle="primary"
        )
        self.entry.pack(fill=tk.X, ipady=10, ipadx=10)  # 增加内部填充

    def video_button(self):
        logger.info("ui初始化视频按钮")
        # 现代化按钮区域
        button_frame = ttk.Frame(self.main_container)
        button_frame.pack(fill=tk.X, pady=(10, 0), padx=(0, 0))

        # 主操作按钮 - 更突出的样式
        main_buttons = ttk.Frame(button_frame)
        main_buttons.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 辅助按钮组
        action_buttons = ttk.Frame(button_frame)
        action_buttons.pack(side=tk.RIGHT, padx=(0, 0))

        # 下载按钮 - 使用更大的尺寸和强调色
        self.Analysis_button = ttk.Button(
            main_buttons,
            text='🚀 解析下载',
            bootstyle='success-lg',  # 更大的按钮样式
            command=lambda: self.Download_Preview.preview(Preview=1),
            padding=(20, 7)
        )
        self.Analysis_button.pack(fill=tk.X, pady=0)

        # 预览按钮
        self.preview_button = ttk.Button(
            action_buttons,
            text='👁️ 预览',
            bootstyle='outline-info',
            command=lambda: self.Download_Preview.preview(Preview=0),
            padding=(15, 7)
        )
        self.preview_button.pack(side=tk.LEFT, padx=5)

        # 粘贴按钮
        Paste_button = ttk.Button(
            action_buttons,
            text='📋   粘贴',
            bootstyle='outline-secondary',
            command=self.Download_Preview.paste,
            padding=(20, 7)
        )
        Paste_button.pack(side=tk.LEFT, padx=5)

        # 清空按钮
        Clear_button = ttk.Button(
            action_buttons,
            text='🗑️ 清空',
            bootstyle='outline-danger',
            command=self.Download_Preview.clear,
            padding=(15, 7)
        )
        Clear_button.pack(side=tk.LEFT, padx=5)

    def image_Entry(self):
        logger.info("ui初始化图片输入")
        # 现代化输入框部分 - 增强视觉效果
        input_frame = ttk.Labelframe(
            self.image_container,
            text="🔗 图片链接输入",
            bootstyle="secondary",
            padding=(10, 10)
        )
        input_frame.pack(fill=tk.X, pady=(0, 0))

        # 创建现代化输入框 - 增加更多样式
        self.image_Var = tk.StringVar()
        self.image_entry = PlaceholderEntry(
            input_frame,
            textvariable=self.image_Var,
            placeholder=" 请输入分享链接...",
            bootstyle="primary"
        )
        self.image_entry.pack(fill=tk.X, ipady=10, ipadx=10)  # 增加内部填充

    def image_button(self):
        logger.info("ui初始化图片按钮")
        # 现代化按钮区域
        button_frame = ttk.Frame(self.image_container)
        button_frame.pack(fill=tk.X, pady=(10, 0), padx=(0, 0))

        # 主操作按钮 - 更突出的样式
        main_buttons = ttk.Frame(button_frame)
        main_buttons.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 辅助按钮组
        action_buttons = ttk.Frame(button_frame)
        action_buttons.pack(side=tk.RIGHT, padx=(0, 0))

        # 下载按钮 - 使用更大的尺寸和强调色
        self.image_Analysis_button = ttk.Button(
            main_buttons,
            text='🚀 解析下载',
            bootstyle='success-lg',  # 更大的按钮样式
            command=lambda: self.image_down.preview(1),
            padding=(20, 7)
        )
        self.image_Analysis_button.pack(fill=tk.X, pady=0)

        # 预览按钮
        self.image_preview_button = ttk.Button(
            action_buttons,
            text='👁️ 预览',
            bootstyle='outline-info',
            command=lambda: self.image_down.preview(0),
            padding=(15, 7)
        )
        self.image_preview_button.pack(side=tk.LEFT, padx=5)

        # 粘贴按钮
        Paste_button = ttk.Button(
            action_buttons,
            text='📋   粘贴',
            bootstyle='outline-secondary',
            command=self.image_down.paste,
            padding=(20, 7)
        )
        Paste_button.pack(side=tk.LEFT, padx=5)

        # 清空按钮
        Clear_button = ttk.Button(
            action_buttons,
            text='🗑️ 清空',
            bootstyle='outline-danger',
            command=self.image_down.clear,
            padding=(15, 7)
        )
        Clear_button.pack(side=tk.LEFT, padx=5)

    def preview_frame(self):
        """
        创建图片预览区域，支持多图展示和横向滚动
        """
        logger.info("构建展示区域")
        # 在image_container中创建预览框架
        self.preview_section = ttk.Labelframe(
            self.image_container,
            text="🖼️图片预览区",
            bootstyle="secondary",
            padding=(10, 10)
        )
        self.preview_section.pack(fill=tk.BOTH, pady=(10, 0), expand=True)

        # 创建画布和滚动条实现横向滚动
        canvas_frame = ttk.Frame(self.preview_section)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # 创建画布用于显示图片
        self.preview_canvas = tk.Canvas(canvas_frame, height=500)
        self.preview_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 添加滚动条
        preview_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, bootstyle="default-round",
                                          command=self.preview_canvas.xview)
        preview_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.preview_canvas.configure(xscrollcommand=preview_scrollbar.set)

        # 创建内部框架用于放置图片
        self.preview_inner_frame = ttk.Labelframe(self.preview_canvas)
        self.preview_canvas.create_window((0, 0), window=self.preview_inner_frame, anchor="nw")

        # 绑定配置变化事件以更新滚动区域
        self.preview_inner_frame.bind("<Configure>", self.image_down.on_preview_frame_configure)

        # 存储预览图片的标签列表
        self.preview_image_labels = []

    def menu(self):
        logger.info("初始化菜单")
        """创建现代化菜单栏"""
        # 创建主菜单栏
        menubar = ttk.Menu(self.root)

        # 工具菜单
        menubar.add_command(label="⚙️ 设置", command=self.set.setup_ui)

        # 帮助菜单
        help_menu = ttk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ 帮助", menu=help_menu)
        help_menu.add_command(label="📖 使用说明", command=lambda: Messagebox.show_info(title="使用说明",
                                                                                       message="1.视频解析：直接在视频输入框内输入快手的分享链接(输入B站的分享链接也能解析哦)\n2.图片解析：在图片输入框中输入图片视频的分享链接即可\n3.关于log设置：建议开启log，在软件出错时，可以通过log日志排查问题"))
        help_menu.add_command(label="ℹ️ 关于作者",
                              command=lambda: webbrowser.open("https://space.bilibili.com/490021190"))

        self.root.config(menu=menubar)

    def update_messagebox(self):
        if INITIAL_DICT["UPDATE"]:
            print(INITIAL_DICT["UPDATE"])
            update_Configuration = self.update.requests_version()
            if __version__ != update_Configuration.version:
                Choose = Messagebox.okcancel(title="更新", message=f"检测到最新版本：{update_Configuration.version}")
                if Choose == "确定":
                    webbrowser.open(update_Configuration.update_url)


class Settings(object):
    def __init__(self, main):
        logger.info("设置初始化")
        self.content_frame = None
        self.Save_frame = None
        self.current_page = None
        self.settings_pages = None
        self.root = None
        self.INITIAL_DICT = INITIAL_DICT
        self.main = main.root
        self.set_Features = SettingsLogic(main=self, Core=main)

    def setup_ui(self):
        logger.info("设置窗口初始化")
        self.root = ttk.Toplevel(self.main)
        self.root.title('设置')  # 标题
        w, h = size_tool(self.root, 800, 400)
        self.root.geometry(f"800x400+{w}+{h}")
        self.root.resizable(0, 0)
        self.root.transient(self.main)
        self.root.grab_set()
        self.root.attributes("-topmost", 0)
        self.root.focus_set()
        set_ico(self.root)

        # 初始化设置页面字典
        self.settings_pages = {}
        self.current_page = None

        # 创建左右分割的框架
        # 左侧导航框架
        nav_frame = ttk.Frame(self.root, width=200)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        nav_frame.pack_propagate(False)  # 固定宽度

        # 底层框架
        self.Save_frame = ttk.Frame(self.root)
        self.Save_frame.pack(side=tk.BOTTOM, fill=tk.X, anchor='se', expand=True, padx=5, pady=5)

        # 右侧内容框架
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建导航按钮
        self.create_nav_buttons(nav_frame)

        # 创建保存按钮
        self.save(self.Save_frame)

        # 默认显示第一个设置页面
        self.show_general_settings()

    def create_nav_buttons(self, parent):
        """创建左侧导航按钮"""
        ttk.Label(parent, text="设置分类", font=("微软黑体", 15, "bold"),
                  bootstyle="primary").pack(pady=10)

        buttons = [
            ("通用设置", self.show_general_settings),
            ("下载设置", self.show_download_settings),
            ("网络设置", self.show_network_settings),
            ("关于版本", self.show_about_settings)
        ]

        for text, command in buttons:
            btn = ttk.Button(parent, text=text, command=command,
                             bootstyle="outline-primary", width=20)
            btn.pack(pady=2, padx=5, fill=tk.X)

    def save(self, parent):
        save_button = [
            ("保存", self.set_Features.save),
            ("取消", lambda: window_out(self.root))
        ]
        for i, e in save_button:
            ttk.Button(
                parent,
                text=i,
                bootstyle="outline-primary",
                command=e
            ).pack(side=tk.RIGHT, padx=5, pady=5)

    def switch_to_settings(self, settings_type):
        """切换到指定设置页面，保留用户输入的内容"""
        # 如果当前页面存在，先保存当前页面的输入内容
        if hasattr(self, 'current_settings_widget'):
            self.save_current_settings()

        # 如果要切换到的页面已存在，直接显示
        if settings_type in self.settings_pages and self.settings_pages[settings_type] is not None:
            # 隐藏当前显示的控件
            if hasattr(self, 'current_settings_widget'):
                self.current_settings_widget.pack_forget()

            # 显示目标页面的控件
            self.settings_pages[settings_type].pack(fill=tk.BOTH, expand=True)
            self.current_settings_widget = self.settings_pages[settings_type]
        else:
            # 创建新的设置页面
            if settings_type == "general":
                widget = self.create_general_settings_widgets()
            elif settings_type == "download":
                widget = self.create_download_settings_widgets()
            elif settings_type == "network":
                widget = self.create_network_settings_widgets()
            elif settings_type == "about":
                widget = self.create_about_settings_widgets()
            else:
                return

            # 保存到页面字典
            self.settings_pages[settings_type] = widget

            # 隐藏当前控件（如果有）
            if hasattr(self, 'current_settings_widget'):
                self.current_settings_widget.pack_forget()

            # 显示新控件
            widget.pack(fill=tk.BOTH, expand=True)
            self.current_settings_widget = widget

        # 更新当前页面类型
        self.current_page = settings_type

    def save_current_settings(self):
        """保存当前设置页面的用户输入"""
        if not self.current_page:
            return

        # 这里可以根据页面类型保存特定的设置
        # 例如，下载页面保存路径信息
        if self.current_page == "download" and hasattr(self, 'path_var'):
            INITIAL_DICT["SAVELOCATION"] = self.path_var.get()
            INITIAL_DICT["selection"] = self.get_object.get()
            INITIAL_DICT["audio_format"] = self.Audio_format.get()
            INITIAL_DICT["mp3"] = self.e_.get()

        if self.current_page == "general" and hasattr(self, 'update_check_var'):
            INITIAL_DICT["UPDATE"] = self.update_check_var.get()
            INITIAL_DICT["POSITION"] = self.position_check_var.get()
            INITIAL_DICT["LOGFILE"] = self.log_check_var.get()
            INITIAL_DICT["LOGPATH"] = self.log_var.get()

        if self.current_page == "network" and hasattr(self, 'update_check_var'):
            INITIAL_DICT['IPproxy'] = self.use_proxy_var.get()
            INITIAL_DICT["IP"] = self.proxy_address_var.get()
        logger.info("设置记录")

    def create_general_settings_widgets(self):
        """创建通用设置控件"""
        widget = ttk.Frame(self.content_frame)

        ttk.Label(widget, text="通用设置",
                  font=("微软黑体", 14, "bold")).pack(anchor=tk.W, pady=10)

        frame = ttk.Labelframe(widget, text="界面设置", padding=10)
        frame.pack(fill=tk.X, pady=5)

        log_frame = ttk.Labelframe(widget, text="日志设置", padding=10)
        log_frame.pack(fill=tk.X, pady=5)

        # 使用实例变量保存复选框状态
        self.update_check_var = tk.BooleanVar(value=INITIAL_DICT["UPDATE"])
        self.position_check_var = tk.BooleanVar(value=INITIAL_DICT["POSITION"])
        self.log_check_var = tk.BooleanVar(value=INITIAL_DICT["LOGFILE"])
        if INITIAL_DICT["LOGPATH"] == None:
            self.log_var = tk.StringVar(value=self.set_Features.pathdefault())
        else:
            self.log_var = tk.StringVar(value=INITIAL_DICT["LOGPATH"])

        ttk.Checkbutton(frame, text="启动时检查更新",
                        bootstyle="success",
                        variable=self.update_check_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(frame, text="记住窗口位置",
                        bootstyle="success",
                        variable=self.position_check_var).pack(anchor=tk.W, pady=2)

        ttk.Checkbutton(log_frame, text="记录日志",
                        bootstyle="success-square-toggle",
                        variable=self.log_check_var,
                        command=self.log_font_color).pack(anchor=tk.W, pady=2, padx=7)

        self.log_file_path = ttk.Entry(log_frame, state='disabled', textvariable=self.log_var)
        self.log_file_path.pack(side=tk.LEFT, fill=tk.X, pady=5, padx=5, expand=True)

        self.path_button = ttk.Button(log_frame, text="浏览",
                                      command=lambda: self.browse_download_path(
                                          event=(self.log_file_path, self.log_var)),
                                      padding=(10, 3))
        self.path_button.pack(side=tk.RIGHT)

        self.log_font_color()

        return widget

    def create_download_settings_widgets(self):
        """创建下载设置控件"""
        widget = ttk.Frame(self.content_frame)

        ttk.Label(widget, text="下载设置",
                  font=("微软黑体", 14, "bold")).pack(anchor=tk.W, pady=10)

        frame = ttk.Labelframe(widget, text="下载路径", padding=10)
        frame.pack(fill=tk.X, pady=5)
        path_frame = ttk.Frame(frame)
        path_frame.pack(fill=tk.X)

        frame_1 = ttk.Labelframe(widget, text="解析设置", padding=10)
        frame_1.pack(fill=tk.X, pady=5)

        # 使用实例变量保存路径
        self.path_var = tk.StringVar()
        # 如果有之前保存的路径，就使用它

        if INITIAL_DICT["SAVELOCATION"] == None:
            self.path_var.set(self.set_Features.pathdefault())
        else:
            self.path_var.set(INITIAL_DICT["SAVELOCATION"])

        # 保存区
        self.path = ttk.Entry(path_frame, textvariable=self.path_var, style='Custom.TEntry', state='disabled')
        self.path.pack(side=tk.LEFT, fill=tk.X, expand=True)

        path_button = ttk.Button(path_frame, text="浏览",
                                 command=lambda: self.browse_download_path(event=(self.path, self.path_var)))
        path_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 解析区
        ttk.Label(frame_1, text="输出模式:", font=('微软黑体', 10)).pack(side=tk.LEFT)
        e = ["获取完整视频", "获取音频"]
        self.get_object = ttk.Combobox(frame_1, values=e, state="readonly")
        self.get_object.current(e.index(INITIAL_DICT['selection']))
        self.get_object.pack(side=tk.LEFT)
        # 音频提取
        self.farme = ttk.Frame(frame_1)
        ttk.Label(self.farme, text="输出格式:", font=('微软黑体', 10)).pack(side=tk.LEFT)
        e_1 = ["mp3", "m4a"]
        # 音频格式选择
        self.Audio_format = ttk.Combobox(self.farme, values=e_1, state="readonly", width=5)
        self.Audio_format.current(e_1.index(INITIAL_DICT['audio_format']))
        self.Audio_format.pack(side=tk.LEFT)
        self.get_object.bind("<<ComboboxSelected>>", self.Mode_Selection)
        # 强制转换mp3格式
        self.e_ = tk.BooleanVar(value = INITIAL_DICT["mp3"])
        mp3_button = ttk.Checkbutton(self.farme, text="通用MP3格式转换", bootstyle="round-toggle", variable=self.e_)
        mp3_button.pack(side=tk.RIGHT, padx=(35, 0))
        self.Mode_Selection(event=0)
        return widget

    def create_network_settings_widgets(self):
        """创建网络设置控件"""
        widget = ttk.Frame(self.content_frame)

        ttk.Label(widget, text="网络设置",
                  font=("微软黑体", 14, "bold")).pack(anchor=tk.W, pady=10)

        frame = ttk.Labelframe(widget, text="代理设置", padding=10)
        frame.pack(fill=tk.X, pady=5)

        # 代理设置变量

        self.use_proxy_var = tk.BooleanVar(value=INITIAL_DICT["IPproxy"])
        self.proxy_address_var = tk.StringVar(value=INITIAL_DICT["IP"])

        ttk.Checkbutton(frame, text="使用代理服务器",
                        variable=self.use_proxy_var,
                        command=self.toggle_proxy_fields
                        ).pack(anchor=tk.W, pady=2)

        # 代理地址框架
        proxy_frame = ttk.Frame(frame)
        proxy_frame.pack(fill=tk.X, pady=(10, 2))

        ttk.Label(proxy_frame, text="代理地址:").pack(side=tk.LEFT)
        self.proxy_entry = ttk.Entry(proxy_frame, textvariable=self.proxy_address_var,
                                     state='disabled')
        self.proxy_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        self.toggle_proxy_fields()

        return widget

    def create_about_settings_widgets(self):
        """创建关于页面控件"""
        widget = ttk.Frame(self.content_frame, padding=20)

        # 应用信息区域
        info_frame = ttk.Frame(widget)
        info_frame.pack(fill=tk.X, pady=(0, 20))

        # 标题和副标题
        title_frame = ttk.Frame(info_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            title_frame,
            text="快手无水印解析工具",
            font=("微软雅黑", 18, "bold"),
            bootstyle="primary"
        ).pack(side=tk.LEFT)

        ttk.Label(
            title_frame,
            text="v1.0.0",
            font=("微软雅黑", 12),
            bootstyle="secondary"
        ).pack(side=tk.RIGHT)

        # 版本历史区域
        history_label = ttk.Label(
            widget,
            text="版本更新历史",
            font=("微软雅黑", 14, "bold"),
            bootstyle="info"
        )
        history_label.pack(anchor=tk.W, pady=(0, 10))

        # 版本日志文本框
        log_frame = ttk.Frame(widget)
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_text = ttk.Text(
            log_frame,
            highlightbackground="#e9ecef",
            highlightthickness=1,
            relief="flat",
            font=("微软雅黑", 10),
            spacing1=2,
            spacing3=5,
            padx=15,
            pady=15
        )
        log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        log_text.configure(yscrollcommand=scrollbar.set)

        # 文本样式配置
        log_text.tag_configure("app_name",
                               font=("微软雅黑", 18, "bold"),
                               foreground="#007bff",
                               spacing3=10)
        log_text.tag_configure("version_header",
                               font=("微软雅黑", 12, "bold"),
                               foreground="#28a745",
                               lmargin1=10)
        log_text.tag_configure("date",
                               font=("微软雅黑", 9),
                               foreground="#6c757d",
                               lmargin1=15)
        log_text.tag_configure("separator",
                               font=("微软雅黑", 8),
                               foreground="#dee2e6")  # 添加这行配置
        log_text.tag_configure("change_item",
                               lmargin1=30,
                               lmargin2=30,
                               font=("微软雅黑", 10),
                               spacing1=3)
        log_text.tag_configure("bullet",
                               foreground="#dc3545",
                               font=("微软雅黑", 10))

        # 添加版本信息（移除重复项）
        VersionLog = [
            {
                'Version': 'v1.0.0',
                'time': '2025-12-15',
                'content': [
                    '✨ 视频解析: 支持快手视频无水印解析',
                    '🖼️ 图片解析: 支持图片内容解析',
                    '⚡ 一键下载: 解析后直接下载无水印内容',
                ]
            }
        ]

        for entry in VersionLog:
            log_text.insert(tk.END, f" 版本 {entry['Version']}\n", "version_header")
            log_text.insert(tk.END, f"发布日期: {entry['time']}\n", "date")
            # 替换原来的 "-" * 60
            log_text.insert(tk.END, "───────────────────────────────────────────────────────────────\n", "separator")

            for item in entry["content"]:
                log_text.insert(tk.END, "● ", "bullet")
                log_text.insert(tk.END, item[2:] + "\n", "change_item")
            log_text.insert(tk.END, "\n", "change_item")

        log_text.config(state=tk.DISABLED)

        return widget

    def toggle_proxy_fields(self):
        """切换代理地址输入框的状态"""
        logger.info("切换代理地址输入框的状态")
        # 直接操作预先保存的代理输入框实例
        if hasattr(self, 'proxy_entry'):
            if self.use_proxy_var.get():
                self.proxy_entry.config(state='normal')
            else:
                self.proxy_entry.config(state='disabled')

    def browse_download_path(self, event):
        """浏览并选择下载路径"""
        logger.info("浏览并选择下载路径")
        try:
            from tkinter import filedialog
            event[0].state = 'normal'

            path = filedialog.askdirectory()
            logger.info(f"下载路径：{path}")
            if path:
                event[1].set(path)
            event[0].state = 'disabled'
        except Exception as e:
            logger.info(f"选择路径文件打开失败.详细:{e}")

    def log_font_color(self):
        """
        :return:复选框使用log记录
        """
        if self.log_check_var.get():
            self.log_file_path.config(style="Custom.TEntry")
            self.path_button.config(state='normal')
            logger.info("开启记录日志")
        else:
            self.log_file_path.config(style='TEntry')
            self.path_button.config(state='disabled')
            logger.info("关闭记录日志")

    def Mode_Selection(self, event):
        a1 = self.get_object.get()
        if a1 == "获取音频":
            self.farme.pack(side=tk.LEFT, padx=(20, 0))
        if a1 == "获取完整视频":
            self.farme.pack_forget()

    def show_general_settings(self):
        """显示通用设置"""
        logger.info("显示通用设置")
        self.switch_to_settings("general")
        self.set_Features.Settings_page = "general"

    def show_download_settings(self):
        """显示下载设置"""
        logger.info("显示下载设置")
        self.switch_to_settings("download")
        self.set_Features.Settings_page = "download"

    def show_network_settings(self):
        """显示网络设置"""
        logger.info("显示网络设置")
        self.switch_to_settings("network")
        self.set_Features.Settings_page = "network"

    def show_about_settings(self):
        """显示关于页面"""
        logger.info("显示关于页面")
        self.switch_to_settings("about")
        self.set_Features.Settings_page = "about"


if __name__ == '__main__':
    print("非常规运行方式，仅为UI测试")
    a = KsParserGUI()
    a.run()
