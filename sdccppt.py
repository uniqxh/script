#!/usr/bin/python
#coding:utf-8

import urllib
import urllib2
import json
import re
import os

#设置cookie
cookies = urllib2.HTTPCookieProcessor()
opener = urllib2.build_opener(cookies)
data = {}
data['ref'] = 'toolbar'
data['username'] = 'xinhua11'
data['password'] = '525799145'
data['_eventId'] = 'submit'
f = opener.open("https://passport.csdn.net/account/login")
ss =  f.read()
#获取csdn登陆流水号
data['lt'] = re.compile(r'LT-[^\"]*').search(ss).group()
data['execution'] = re.compile(r'e[0-9]s[0-9]').search(ss).group()
f = opener.open("https://passport.csdn.net/account/login", urllib.urlencode(data))

def download(url, i):
    print "%d downloading %s"%(i, url)
    filepath = "./sdcc/sdcc_%d.pdf"%i
    if os.path.exists(filepath) == False:
        urllib.urlretrieve(url, filepath)

url = "http://download.csdn.net/index.php/meeting/do_download_speech/"
cnt = 0
for i in range(27, 238):
    filepath = url + str(i)
    req = urllib2.Request(filepath)
    res = opener.open(req).read()
    if res.strip() == '' :
        continue
    data = json.loads(res)
    if data['msg'].find('meet.download.csdn.net') == -1:
        continue
    download(data['msg'], i)
    cnt = cnt + 1

print "总共下载 %d 个文件"%cnt

