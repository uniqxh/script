#!/usr/bin/python
#coding:utf-8

import urllib,urllib2,io
import Tkinter as tk
from PIL import Image,ImageTk
from Tkinter import BOTH, END, LEFT
import ssl
import json,re,uniout,ConfigParser
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

class config:
    user = ''
    pwd  = ''
    def __init__(self, f):
        cf = ConfigParser.ConfigParser()
        if cf.read(f) == []:
            raise Exception('config文件不存在')
        try:
            self.user = cf.get('info', 'user')
            self.pwd  = cf.get('info', 'pwd')
        except:
            raise Exception('user/pwd未配置')
#check config file
try:
    cfg = config('config')
except Exception, e:
    print e
    exit()

ssl._create_default_https_context = ssl._create_unverified_context

class _12306():
    host = 'https://kyfw.12306.cn/otn/'
    psg = []
    def __init__(self):
        cookies = urllib2.HTTPCookieProcessor()
        #httpHandler = urllib2.HTTPHandler(debuglevel=1)
        #httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
        self. opener = urllib2.build_opener(cookies)
        urllib2.install_opener(self.opener)
        #init page 
        self.opener.open(self.host + 'login/init')
        
        self.w = tk.Tk()
        self.l = tk.Label(self.w, bg='brown')
        self.l.pack(padx=5, pady=5)
    
        self.l.bind('<Button-1>', self.motion)
    
        self.b = tk.Button(self.w, text='提交')
        self.b.pack()
        
        self.lIm = Image.open('./label.png')
        self.lImg = ImageTk.PhotoImage(self.lIm)
    
        self.refreshCode(self.url, self.submit)
    
        self.w.mainloop()
    
    url = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand'
    purl = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=passenger&rand=randp'
    checkurl = 'https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn'
    loginurl = 'https://kyfw.12306.cn/otn/login/loginAysnSuggest'
    checkorderurl = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
    confirmurl = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
    
    def query(self):
        print '正在查询列车信息...'
        res = self.opener.open(self.host + 'leftTicket/query?leftTicketDTO.train_date=2017-01-04&leftTicketDTO.from_station=SZQ&leftTicketDTO.to_station=WHN&purpose_codes=ADULT')
        jsonData = json.loads(res.read())
        print '查询成功'
        self.submitOrder(jsonData['data'][0]['secretStr'])
    
    def submitOrder(self, ss):
        print '正在提交订单...'
        action = 'leftTicket/submitOrderRequest'
        cm = 'secretStr=' + ss + '&train_date=2016-12-29&tour_flag=dc&purpose=ADULT&query_from_station_name=%E6%B7%B1%E5%9C%B3&query_to_station_name=%E6%AD%A6%E6%B1%89&undefined'
        jd = json.loads(self.opener.open(self.host + action, cm).read())
        if jd['messages'] != []:
            print jd['messages'][0]
            return
        res = self.opener.open(self.host + 'confirmPassenger/getPassengerDTOs').read()
        self.psg = json.loads(res)['data']['normal_passengers']
        self.initDc()
    
    gp = re.compile(r'globalRepeatSubmitToken = \'([^\']+)')
    tp = re.compile(r'ticketInfoForPassengerForm=([^;]+)')
    token = ''
    info = {}
    def initDc(self):
        html = self.opener.open(self.host + 'confirmPassenger/initDc').read()
        self.token = self.gp.search(html).group(1)
        self.info = json.loads(self.tp.search(html).group(1).replace("'", '"'))
        self.refreshCode(self.purl, self.confirm)
    
    def confirm(self):
        self.hide()
        code = self.getCode()
        if code == '':
            return
        co = {'randCode': code, 'rand': 'randp'}
        jd = json.loads(self.opener.open(self.checkurl, urllib.urlencode(co)).read())
        if jd['data']['msg'] != 'TRUE':
            print '验证码错误'
            self.refreshCode(self.purl, self.confirm)
            return
        print '验证码校验成功'
        pg = self.psg[0]
        tstr = 'O,0,1,'+ pg['passenger_name'] +',1,'+ pg['passenger_id_no'] +','+ pg['mobile_no'] +',N'
        ostr = pg['passenger_name'] + ',1,'+ pg['passenger_id_no'] +',1_'
        co = {
           'cancel_flag': 2,
           'bed_level_order_num': '000000000000000000000000000000',
           'passengerTicketStr': tstr,
           'oldPassengerStr': ostr,
           'tour_flag': 'dc',
           'randCode': code,
           'REPEAT_SUBMIT_TOKEN': self.token
        }
        self.opener.open(self.checkorderurl, urllib.urlencode(co))
        print '正在确认订单...'
        data = {
            'passengerTicketStr': tstr,
            'oldPassengerStr': ostr,
            'purpose_codes': self.info['purpose_codes'],
            'key_check_isChange': self.info['key_check_isChange'],
            'leftTicketStr': self.info['leftTicketStr'],
            'train_location': self.info['train_location'],
            'seatDetailType': '1A',
            'roomType': '00',
            'dwAll': 'N',
            'REPEAT_SUBMIT_TOKEN': self.token,
            'randCode': code
        }
        res = self.opener.open(self.confirmurl, urllib.urlencode(data));
        print res.read()
        print '订单提交成功'
        exit()
    
    def hide(self):
        self.w.withdraw()
    
    def show(self):
        self.w.update()
        self.w.deiconify()
    
    lists = []
    def clear(self):
        if len(self.lists) == 0:
            return
        for i in self.lists:
            i.destroy()
        del self.lists[:]
    
    def refreshCode(self, u, f):
        self.b.config(command=f)
        self.show()
        res = urllib2.urlopen(u).read()
        ds = io.BytesIO(res)
        im = Image.open(ds)
        tkImg = ImageTk.PhotoImage(im)
        self.l.configure(image=tkImg)
        self.l.image = tkImg
        self.clear()
        print '请输入验证码...'
    
    def getCode(self):
        res = ''
        for i in self.lists:
            info = i.place_info()
            res = res + str(int(info['x']) + 10) + ',' + str(int(info['y']) - 30) + ','
        if res == '':
            return ''
        return res[0:len(res) - 1]
    
    def destroy(self, e):
        self.lists.remove(e.widget)
        e.widget.destroy()
    
    def motion(self, e):
        if e.y < 40:
            return
        ll = tk.Label(self.w, image=self.lImg)
        ll.pack()
        ll.place(x=e.x - 10, y=e.y - 10)
        ll.bind('<Button-1>', self.destroy)
        self.lists.append(ll)
    def submit(self):
        self.hide()
        code = self.getCode()
        if code == '':
            return
        jsonDt = self.opener.open(self.checkurl, urllib.urlencode({'randCode': code, 'rand': 'sjrand'}))
        res = json.loads(jsonDt.read())
        if res['data']['msg'] != 'TRUE':
            print '验证码错误'
            self.refreshCode(self.url, self.submit)
            return
        print '验证码校验成功'
        print '正在登陆...'
        data = {}
        data['loginUserDTO.user_name'] = cfg.user
        data['userDTO.password'] = cfg.pwd
        data['randCode'] = code
        res = self.opener.open(self.loginurl, urllib.urlencode(data)).read()
        jd = json.loads(res)
        if jd['data'] == {}:
            print jd['messages'][0]
            self.refreshCode(self.url, self.submit)
            return
        if jd['data']['loginCheck'] != 'Y':
            print jd['data']['otherMsg'] + ', 请重新登陆'
            self.refreshCode(self.url, self.submit)
            return
        self.opener.open('https://kyfw.12306.cn/otn/login/init')
        print '登陆成功'
        self.query()
    
try:
    _12306()
except:
    exit()
