#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date：2025/12/13 15:06
# @Author : 等待
# @Version: V1.0
# @File ：Download_Preview.py
import sys
import random
from pathlib import Path

from ttkbootstrap.dialogs import Messagebox
import imageio_ffmpeg as ffmpeg
import subprocess
import tempfile
import locale
import os
import re
import ffmpeg as f
import logging

logger = logging.getLogger(__name__)

def ffmpegexe_path():
    try:
        if not getattr(sys, "frozen", False):
            path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
            if os.path.exists(path):
                return path
        else:
            path = os.path.join(Path(sys.executable).parent, "ffmpeg", "bin", "ffmpeg.exe")
            if os.path.exists(path):
                return path
        logger.error("无法找到ffmpeg")
    except Exception as e:
        logger.error(f"无法找到ffmpeg：{e}")
        # 可以选择不设置图标，使用默认图标

class MessageBox(object):
    """
    弹窗工具类，用于存放各种类型的弹窗
    """

    @staticmethod
    def show_info(title, message, parent=None):
        """
        显示信息弹窗
        :param title: 弹窗标题
        :param message: 弹窗内容
        :param parent: 父窗口对象
        """
        Messagebox.show_info(title=title, message=message, parent=parent)

    @staticmethod
    def show_warning(title, message, parent=None):
        """
        显示警告弹窗
        :param title: 弹窗标题
        :param message: 弹窗内容
        :param parent: 父窗口对象
        """
        Messagebox.show_warning(title=title, message=message, parent=parent)

    @staticmethod
    def show_error(title, message, parent=None):
        """
        显示错误弹窗
        :param title: 弹窗标题
        :param message: 弹窗内容
        :param parent: 父窗口对象
        """
        Messagebox.show_error(title=title, message=message, parent=parent)

    @staticmethod
    def ask_yes_no(title, message, parent=None):
        """
        显示确认弹窗
        :param title: 弹窗标题
        :param message: 弹窗内容
        :param parent: 父窗口对象
        :return: True/False
        """
        return Messagebox.show_question(title=title, message=message, parent=parent)


def random_num():
    """
    :return:9位混淆英文数字的随机数
    """
    random_letter = [random.choice([
        'q', 'w', 'e', 'r', 't', 'y', 'u',
        'i', 'o', 'p', 'a', 'b', 'c', 'd',
        'f', 'g', 'h', 'k', 'l', 'z', 'x',
        'c', 'v', 'b', 'n', 'm', '&', '^'
    ]) for i in range(4)]
    random_num = str(random.randint(0, 100))
    return random_num.join(random_letter)


def size_tool(main, width, height):
    """
    :param main: 要调整的窗口对象
    :param width: 宽度
    :param height: 高度
    :return: 调整窗口居中
    """
    w, h = main.maxsize()
    return int((w - width) / 2), int((h - height) / 2)


def window_out(Window):
    Window.destroy()


def Download(content, Format: str, save: str = None):
    if save is None:
        with open(random_num() + Format, "wb") as file:
            file.write(content)
    else:
        with open(save + "/" + random_num() + Format, "wb") as file:
            file.write(content)


def merge_with_imageio_ffmpeg(video_path, audio_path):
    """
    修复编码问题的版本
    """

    # 确保路径是字符串，并且是有效的编码
    def ensure_str_path(path):
        if isinstance(path, bytes):
            # 尝试解码，如果失败则使用临时文件
            try:
                return path.decode('utf-8')
            except UnicodeDecodeError:
                # 如果是二进制数据，写入临时文件
                temp_file = tempfile.NamedTemporaryFile(
                    suffix='.temp', delete=False, mode='wb'
                )
                temp_file.write(path)
                temp_file.close()
                return temp_file.name
        elif isinstance(path, str):
            return path
        else:
            raise TypeError(f"不支持的路径类型: {type(path)}")

    # 转换路径
    video_path_str = ensure_str_path(video_path)
    audio_path_str = ensure_str_path(audio_path)

    # 创建临时输出文件
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        output_path = tmp.name

    temp_files = []
    if video_path_str != video_path:
        temp_files.append(video_path_str)
    if audio_path_str != audio_path:
        temp_files.append(audio_path_str)

    try:
        # 获取ffmpeg可执行文件路径
        ffmpeg_exe = ffmpeg.get_ffmpeg_exe()

        # 构建命令 - 确保所有参数都是字符串
        cmd = [
            ffmpeg_exe,
            '-i', video_path_str,
            '-i', audio_path_str,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-y',  # 覆盖输出文件
            output_path
        ]

        print(f"执行命令: {' '.join(cmd)}")

        # 使用subprocess运行，指定编码
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,  # 以文本模式捕获输出
            encoding=sys.getdefaultencoding()  # 使用系统默认编码
        )

        # 读取输出文件
        with open(output_path, 'rb') as f:
            content = f.read()

        return content

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg错误: {e.stderr}")
        return None
    finally:
        # 清理所有临时文件
        if os.path.exists(output_path):
            os.unlink(output_path)
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


def extract_audio_from_video(video_path, output_position, audio_format='mp3'):
    """
    从视频文件中提取音频

    Args:
        video_path (str): 视频文件路径
        audio_format (str): 输出音频格式，默认为'mp3'

    Returns:
        str: 提取的音频文件路径，失败返回None
        :param output_position: 文件保存位置
    """

    # 确保路径是字符串
    def ensure_str_path(path):
        if isinstance(path, bytes):
            try:
                return path.decode('utf-8')
            except UnicodeDecodeError:
                temp_file = tempfile.NamedTemporaryFile(
                    suffix='.temp', delete=False, mode='wb'
                )
                temp_file.write(path)
                temp_file.close()
                return temp_file.name
        elif isinstance(path, str):
            return path
        else:
            raise TypeError(f"不支持的路径类型: {type(path)}")

    video_path_str = ensure_str_path(video_path)

    # 创建临时音频文件
    with tempfile.NamedTemporaryFile(suffix=f'.{audio_format}', delete=False, dir=output_position) as tmp:
        audio_output_path = tmp.name

    try:
        # 获取ffmpeg可执行文件路径
        ffmpeg_exe = ffmpeg.get_ffmpeg_exe()

        # 构建命令 - 从视频中提取音频
        cmd = [
            ffmpeg_exe,
            '-i', video_path_str,  # 输入视频文件
            '-vn',  # 禁用视频录制
            '-acodec', 'copy',  # 复制原始音频编解码器
            '-y',  # 覆盖输出文件
            audio_output_path  # 输出音频文件
        ]

        logger.info(f"执行音频提取命令: {' '.join(cmd)}")

        # 运行命令
        import subprocess

        # 使用 Popen 手动处理
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            errors='ignore'
        )

        # 读取输出，避免缓冲区溢出
        stdout, stderr = process.communicate(timeout=30)
        return_code = process.returncode

        if return_code != 0:
            logger.error(f"FFmpeg 错误: {stderr}")
            return None

        return audio_output_path

    except subprocess.CalledProcessError as e:

        logger.exception(f"FFmpeg分离错误: {e.stderr}")

        # 清理可能创建的不完整文件
        os.unlink(video_path_str)

        if audio_output_path and os.path.exists(audio_output_path):
            os.unlink(audio_output_path)
        return None
    except Exception as e:

        logger.exception(f"分离过程中发生错误: {str(e)}")

        # 清理可能创建的不完整文件
        os.unlink(video_path_str)

        if audio_output_path and os.path.exists(audio_output_path):
            os.unlink(audio_output_path)
        return None




def check_ffmpeg_environment():
    """检查ffmpeg-python和底层ffmpeg是否都可用"""
    try:
        # 指定ffmpeg完整路径
        ffmpeg_path = ffmpegexe_path() # 根据实际安装路径修改
        logger.info(ffmpeg_path)
        if os.path.exists(ffmpeg_path):
            # 设置环境变量或直接使用完整路径
            os.environ['PATH'] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ['PATH']
            return True
        else:
            logger.error(f"FFmpeg未找到，请检查路径: {ffmpeg_path}")
            return False
    except Exception as e:
        logger.error(f"FFmpeg环境检查失败: {e}")
        return False


def convert_m4a_to_mp3(input_file, output_file, bitrate="320k"):
    """
    使用ffmpeg-python库将单个m4a文件转换为mp3
    :param input_file: 输入m4a文件路径
    :param output_file: 输出mp3文件路径
    :param bitrate: 输出mp3比特率，默认320k
    """
    try:
        # 构建ffmpeg转码流程（原生Python API方式）
        (
            f
            .input(input_file)  # 输入文件
            .output(
                output_file,
                audio_bitrate=bitrate,  # 音频比特率
                format='mp3',  # 输出格式
                y=None  # 覆盖已存在的文件（等同于-y参数）
            )
            .overwrite_output()  # 显式指定覆盖输出
            .run(
                capture_stdout=True,
                capture_stderr=True,
                quiet=True  # 静默运行，不输出冗余日志
            )
        )
        return True, f"转换成功: {os.path.basename(input_file)} -> {os.path.basename(output_file)}"
    except Exception as e:
        return False, f"转换异常: {os.path.basename(input_file)}, 错误: {str(e)[:100]}..."


def batch_convert(file_path):
    """
    批量转换指定文件夹下的所有m4a文件
    :param file_path: 目标文件路径
    """
    output_path = re.findall("(.+)\..+", file_path)[0]+'.mp3'
    logger.info(f"正在处理: {file_path}")
    success, msg = convert_m4a_to_mp3(file_path, output_path)
    logger.info(f"{msg}")
    return success, msg





