import sys
from pathlib import Path

import requests
import json
import os
from lxml import etree
import re
from jsonpath import jsonpath



class BiliBili(object):
    def __init__(self, URL):
        self.URL = URL
        self.BlBl_URL = self.URL

        # 请求url
        self.User_GENT = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'referer': 'https://www.bilibili.com/',
            'user-agent': 'ozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        }
        # url参数
        self.Cookie = requests.Session()
        self._set_cookie()
        print(self.Cookie.cookies)
        # 获取cookie

    def _request_grt_URL(self):
        self.res_1 = self.Cookie.get(self.BlBl_URL, headers=self.User_GENT)

    def _text(self):
        self._request_grt_URL()
        self.Wen_Ben = self.res_1.text

    def _HTNL(self):
        self._text()
        WB_HTML = etree.HTML(self.Wen_Ben)
        listS_html = WB_HTML.xpath('//style[@id="setSizeStyle"]/following::script/text()')
        self.js = json.loads(re.findall('window.__playinfo__=(.+)', listS_html[0])[0])

    def _set_cookie(self):
            if not getattr(sys, "frozen", False):
                print(os.getcwd() + "\\" + "cookie.txt")
                if os.path.exists(os.getcwd() + "\\" + "cookie.txt"):
                    with open(os.getcwd() + "\\" + "cookie.txt", 'r') as cokie:
                        read_cookie = cokie.read()
                        self.User_GENT['Cookie'] = read_cookie
            else:
                path = os.path.join(Path(sys.executable).parent, "cookie.txt")
                if os.path.exists(os.getcwd() + "\\" + "cookie.txt"):
                    with open(path, 'r') as cokie:
                        read_cookie = cokie.read()
                        self.User_GENT['Cookie'] = read_cookie

    def move_audio(self):
        self._HTNL()
        self.XUN_hao = jsonpath(self.js, '$..id')
        self.URL_MOve_audio = jsonpath(self.js, '$..baseUrl')
        print(self.URL_MOve_audio)
        Video_HVC1 = self.Cookie.get(self.URL_MOve_audio[4], headers=self.User_GENT).content
        Audio_AAC = self.Cookie.get(self.URL_MOve_audio[-2], headers=self.User_GENT).content
        return Video_HVC1, Audio_AAC



if __name__ == '__main__':
    print('请输入B站分享链接')
    user_in = input('请输入：')
    movie_name = re.findall('【(.+)】', user_in)[0]
    movie_url = re.findall('【.+】\s(.+)', user_in)[0]
    ob = BiliBili(movie_url)
    print('1.获取视频\t2.获取音频\t3.获取完整视频\t4.更改保存路径')
    user_it = input('请输入功能码：')
    if user_it == '1':
        pass

