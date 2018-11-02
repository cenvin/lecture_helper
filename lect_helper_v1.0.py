#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import requests
import random
from io import BytesIO
from PIL import Image
from aip import AipOcr

# type your login username&password
USER = '**************'
PASS = '**************'

# type lecture id
CLASS = '{************************************}'

# baidu orc, see api at:https://cloud.baidu.com/doc/OCR/OCR-Python-SDK.html
APP_ID = '********'
API_KEY = '************************'
SECRET_KEY = '********************************'

t = lambda: int(round(time.time()*1000))


def logon():
    t_str = str(t())
    payload = {
        'callback': 'jQuery18002515287049104974_'+t_str,
        'UserName': USER,
        'Password': PASS,
        'RememberMe': 'true',
        '_': ''
        }
    t_str = str(t())
    payload['_'] = t_str
    res = requests.get("http://account.soe.xmu.edu.cn/WcfServices/SSOService.svc/Account/Logon", params=payload)
    cookies = res.cookies
    return cookies


def token():
    cookies = logon()
    t_str = str(t())
    payload = {
        'callback': 'jQuery180035813158977832227_'+t_str,
        '_': ''
        }
    t_str = str(t())
    payload['_'] = t_str
    res = requests.get("http://account.soe.xmu.edu.cn/WcfServices/SSOService.svc/Account/RequestToken",
                       params=payload, cookies=cookies)
    res_str = res.text
    token = res_str[76: -5]
    return token


def auth():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    }
    payload = {'token': token(), 'rememberMe': 'true'}
    res = requests.post("http://event.soe.xmu.edu.cn/Authenticate.aspx", data=payload, headers=headers)
    cookies = res.cookies
    ASPXAUTH = cookies['.ASPXAUTH']
    sessionId = cookies['ASP.NET_SessionId']
    return ASPXAUTH, sessionId


def vcoder(ASPXAUTH, sessionId):
    cookies = {'.ASPXAUTH': ASPXAUTH, 'ASP.NET_SessionId': sessionId}
    para = str(random.random)
    res = requests.get("http://event.soe.xmu.edu.cn/ImageHandler.ashx?"+para, cookies=cookies)
    f = BytesIO(res.content)
    im = Image.open(f)
    im.save('vcode.bmp')
    image = get_file_content('vcode.bmp')
    certcode = aiorc(image)
    return certcode


def submit(vcode, ASPXAUTH, sessionId):
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    cookies = {'.ASPXAUTH': ASPXAUTH, 'ASP.NET_SessionId': sessionId}
    t_str = str(t())
    payload = {
        'Id': CLASS,
        'vcode': vcode,
        '_': t_str}
    res = requests.get("http://event.soe.xmu.edu.cn/LectureOrderAjax.aspx",
                       params=payload, cookies=cookies, headers=headers)
    return res.text


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def aiorc(image):
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    vcode = client.basicAccurate(image)['words_result']
    if vcode:
        print(vcode[0]['words'])
        return vcode[0]['words']
    return 1234


def get_time():
    return time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime(time.time()))


print("Welcome to xmu lecture helper! Powered by cc")
print("当前时间是：" + get_time())


if __name__ == "__main__":
    ASPXAUTH, sessionId = auth()
    while True:
        vcode = vcoder(ASPXAUTH, sessionId)
        result = submit(vcode, ASPXAUTH, sessionId)
        print("当前时间是：" + get_time())
        print(result)
        if '已' in result:
            break
