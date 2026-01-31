#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date：2025/11/30 15:31
# @Author : 等待
# @Version: V1.0
# @File ：sharelink.py

import requests
import re
import json
import jsonpath


class ShareLink(object):
    """
    视频POST请求
    """
    def __init__(self, URL):
        self.movieURL = None
        self.URL = URL
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://www.kuaishou.com',
            'Pragma': 'no-cache',
            'Range': 'bytes=0-',
            'Referer': 'https://www.kuaishou.com/short-video/3xbwparn2c3k356?authorId=3xu5n4mvabdksss&streamSource=brilliant&hotChannelId=00&area=brilliantxxcarefully',
            'Sec-Fetch-Dest': 'video',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
            'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.get()

    def get(self):
        self.response = requests.get(
            self.URL,
            headers=self.headers
        )

    def html_json(self):
        pattern = r'window\.__APOLLO_STATE__\s*=\s*({.*?});'
        match = re.search(pattern, self.response.text, re.DOTALL)
        apollo_state_json = match.group(1)

        # 解析JSON
        apollo_state = json.loads(apollo_state_json)
        photoUrl = jsonpath.jsonpath(apollo_state, "$..photoUrl")[0]
        self.movieURL = photoUrl
        return self

    def video_data(self, url):
        return requests.get(url, headers=self.headers).content


if __name__ == '__main__':
    a = ShareLink('https://www.kuaishou.com/f/X-4a36wtjMLHqF3j')
    print(a.video_data(a.html_json().movieURL))

