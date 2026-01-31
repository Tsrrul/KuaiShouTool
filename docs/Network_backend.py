#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date：2025/12/27 21:00
# @Author : 等待
# @Version: V1.0
# @File ：Network_backend.py

import requests
import jsonpath
import re


class Network_Backend(object):
    def __init__(self):
        self.version = None
        self.update_url = None
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://share.note.youdao.com/ynoteshare/index.html?id=2eeeb73a17fc2e503b591957d0ea880b&type=note&_time=1767168588364',
            'sec-ch-ua': '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0',
            'x-requested-with': 'XMLHttpRequest',
        }

        params = {
            'method': 'get',
            'shareKey': '2eeeb73a17fc2e503b591957d0ea880b',
            'sec': 'v1',
        }

        self.response = requests.get('https://share.note.youdao.com/yws/api/personal/share', headers=headers,
                                     params=params)

    def requests_data(self):
        data_json = jsonpath.jsonpath(self.response.json(), "$..summary")
        return data_json

    def requests_version(self):
        self.version, self.update_url= re.findall('【version】(.+)【version】.+【URL】(.+)【URL】', self.requests_data()[-1])[0]
        return self

if __name__ == '__main__':
    a = Network_Backend()
    print(a.requests_version().update_url)
