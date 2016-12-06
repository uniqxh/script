#!/usr/bin/python
#coding:utf-8

import urllib,urllib2,io
import Tkinter as tk
from PIL import Image,ImageTk
from Tkinter import BOTH, END, LEFT
import ssl
import json,re,uniout

ssl._create_default_https_context = ssl._create_unverified_context

cookies = urllib2.HTTPCookieProcessor()
#httpHandler = urllib2.HTTPHandler(debuglevel=1)
#httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
opener = urllib2.build_opener(cookies)
urllib2.install_opener(opener)

host = 'https://kyfw.12306.cn/otc/'

initurl = 'https://kyfw.12306.cn/otn/login/init'
opener.open(initurl)

url = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand'
purl = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=passenger&rand=randp'
checkurl = 'https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn'
loginurl = 'https://kyfw.12306.cn/otn/login/loginAysnSuggest'
initdcurl = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
checkorderurl = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
confirmurl = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'

def query():
    print '正在查询列车信息...'
    res = opener.open('https://kyfw.12306.cn/otn/leftTicket/queryX?leftTicketDTO.train_date=2017-01-04&leftTicketDTO.from_station=SZQ&leftTicketDTO.to_station=WHN&purpose_codes=ADULT')
    jsonData = json.loads(res.read())
    print '查询成功'
    submitOrder(jsonData['data'][0]['secretStr'])

def submitOrder(ss):
    print '正在提交订单...'
    url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
    cm = 'secretStr=' + ss + '&train_date=2016-12-29&tour_flag=dc&purpose=ADULT&query_from_station_name=%E6%B7%B1%E5%9C%B3&query_to_station_name=%E6%AD%A6%E6%B1%89&undefined'
    jd = json.loads(opener.open(url, cm).read())
    if jd['messages'] != []:
        print jd['messages'][0]
        return
    initDc()

gp = re.compile(r'globalRepeatSubmitToken = \'([^\']+)')
tp = re.compile(r'ticketInfoForPassengerForm=([^;]+)')
token = ''
info = {}
def initDc():
    global token
    global info
    html = opener.open(initdcurl).read()
    token = gp.search(html).group(1)
    info = json.loads(tp.search(html).group(1).replace("'", '"'))
    refreshCode(purl, confirm)

def confirm():
    code = getCode()
    if code == '':
        return
    co = {'randCode': code, 'rand': 'randp'}
    jd = json.loads(opener.open(checkurl, urllib.urlencode(co)).read())
    if jd['data']['msg'] != 'TRUE':
        print '验证码错误'
        refreshCode(purl, initDc)
        return
    print '验证码校验成功'
    co = {
       'cancel_flag': 2,
       'bed_level_order_num': '000000000000000000000000000000',
       'passengerTicketStr': 'O,0,1,周新华,1,421023199112232039,18575581356,N',
       'oldPassengerStr': '周新华,1,421023199112232039,1_',
       'tour_flag': 'dc',
       'randCode': code,
       'REPEAT_SUBMIT_TOKEN': token
    }
    opener.open(checkorderurl, urllib.urlencode(co))
    print '正在确认订单...'
    data = {
        'passengerTicketStr': 'O,0,1,周新华,1,421023199112232039,18575581356,N',
        'oldPassengerStr': '周新华,1,421023199112232039,1_',
        'purpose_codes': info['purpose_codes'],
        'key_check_isChange': info['key_check_isChange'],
        'leftTicketStr': info['leftTicketStr'],
        'train_location': info['train_location'],
        'seatDetailType': '1A',
        'roomType': '00',
        'dwAll': 'N',
        'REPEAT_SUBMIT_TOKEN': token,
        'randCode': code
    }
    res = opener.open(confirmurl, urllib.urlencode(data));
    print '订单提交成功'

w = tk.Tk()
l = tk.Label(w, bg='brown')
l.pack(padx=5, pady=5)

def hide():
    w.withdraw()

def show():
    w.update()
    w.deiconify()

lists = []
def clear():
    if len(lists) == 0:
        return
    for i in lists:
        i.destroy()
    del lists[:]

def refreshCode(u, f):
    b.config(command=f)
    show()
    res = urllib2.urlopen(u).read()
    ds = io.BytesIO(res)
    im = Image.open(ds)
    tkImg = ImageTk.PhotoImage(im)
    l.configure(image=tkImg)
    l.image = tkImg
    clear()
    print '请输入验证码...'

lIm = Image.open('./label.png')
lImg = ImageTk.PhotoImage(lIm)

def getCode():
    res = ''
    for i in lists:
        info = i.place_info()
        res = res + str(int(info['x']) + 10) + ',' + str(int(info['y']) - 30) + ','
    if res == '':
        return ''
    return res[0:len(res) - 1]

def destroy(e):
    lists.remove(e.widget)
    e.widget.destroy()

def motion(e):
    if e.y < 40:
        return
    ll = tk.Label(w, image=lImg)
    ll.pack()
    ll.place(x=e.x - 10, y=e.y - 10)
    ll.bind('<Button-1>', destroy)
    lists.append(ll)
def submit():
    code = getCode()
    if code == '':
        return
    jsonDt = opener.open(checkurl, urllib.urlencode({'randCode': code, 'rand': 'sjrand'}))
    res = json.loads(jsonDt.read())
    if res['data']['msg'] != 'TRUE':
        print '验证码错误'
        refreshCode(url, submit)
        return
    print '验证码校验成功'
    print '正在登陆...'
    data = {}
    data['loginUserDTO.user_name'] = '525799145@qq.com'
    data['userDTO.password'] = 'xinhua192245151'
    data['randCode'] = code
    res = opener.open(loginurl, urllib.urlencode(data)).read()
    jd = json.loads(res)
    if jd['data'] == {}:
        print jd['messages'][0]
        refreshCode(url, submit)
        return
    if jd['data']['loginCheck'] != 'Y':
        print jd['data']['otherMsg'] + ', 请重新登陆'
        refreshCode(url, submit)
        return
    opener.open('https://kyfw.12306.cn/otn/login/init')
    print '登陆成功'
    query()

l.bind('<Button-1>', motion)

b = tk.Button(w, text='提交', command=submit)
b.pack()
refreshCode(url, submit)

w.mainloop()
