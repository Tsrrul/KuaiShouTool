#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date：2025/12/6 10:43
# @Author : 等待
# @Version: V1.0
# @File ：ks_image_parser.py.py

import execjs
import requests
import os
import jsonpath
import logging

def file_path():
    current_file = os.path.abspath(__file__)
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(current_file)
    logger = logging.getLogger(__name__)
    logger.debug(current_dir)
    return current_dir


class KsImage(object):
    """
    图片POST请求
    """
    def __init__(self, url):
        self.title = None
        self.image_url = None
        self.data_url = None
        self.url = url
        self.post_headers()

    def post_headers(self):
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://dy.kukutool.com',
            'Pragma': 'no-cache',
            'Referer': 'https://dy.kukutool.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
            'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        with open(file_path()+"\\"+"ks_decrypt_image.js", "r", encoding="utf-8") as data:
            read = data.read()
        cl = execjs.compile(read)
        json_data = cl.call("json_data", self.url)

        self.response = requests.post('https://dy.kukutool.com/api/parse',  headers=headers, json=json_data)



    def decrypt(self):
        with open(file_path()+"\\"+"image_Decrypt.js", "r", encoding="utf-8") as data:
            read = data.read()
        cl = execjs.compile(read)
        decrypt_data = cl.call("akk", self.response.text)
        return decrypt_data


    def get_image(self):
        decrypt_data = self.decrypt()
        self.title = jsonpath.jsonpath(decrypt_data, '$..title')
        self.image_url = jsonpath.jsonpath(decrypt_data, '$..pics')[0]
        return self

if __name__ == '__main__':
    a = KsImage(url="https://v.kuaishou.com/KGWQ9m5a")
    c = a.get_image()
    print(c.image_url)
    print(c.title)
    pass
