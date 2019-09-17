# -*- coding: utf-8 -*-
from cqhttp import CQHttp
import time
import re
import requests 
import multiprocessing
import json
from requests.packages import urllib3
urllib3.disable_warnings()
import random
import pymongo
import datetime
import os,io
from multiprocessing import Process
import threading  
member = []
message_list =[]
proxy_list =[]

bot = CQHttp(api_root='http://127.0.0.1:5700/')


qq_id = 0
mongoAddr = "mongodb://127.0.0.1:27017/elm"

proxy=None

last_time= datetime.datetime.now()

def Check_Live(): 
    global last_time   
    while 1:        
        try:
            if (datetime.datetime.now()-last_time) >datetime.timedelta(seconds=80):
                last_time= datetime.datetime.now()
                print ("掉线，重新连接。。。")
                bot.send_private_msg(user_id=qq_id,message="掉线",auto_escape=False)
                #os.system('taskkill /f /t /im CQA.exe')
                #cmd_str = '"C:\Documents and Settings\Administrator\桌面\酷Q Air\CQA.exe" /account 3410860300'
                #os.system(cmd_str) 
                
                
        except Exception:
            pass
        #print(last_time)
        time.sleep(1)
        
def Update_Time():    
    global last_time
    last_time= datetime.datetime.now()
    

def DropCollection(name):
    client=pymongo.MongoClient(mongoAddr,connect=False)
    client['elm'].drop_collection(name)
    
def DelMongo(data,collection="logs"):
    client=pymongo.MongoClient(mongoAddr,connect=False)
    db = client['elm']
    db[collection].remove(data)
    
def SaveMongo(data,collection="logs"):
    client=pymongo.MongoClient(mongoAddr,connect=False)
    db = client['elm']
    if db[collection].insert(data):
        return 0
    else:
        return 1

def SearchMongo(dict,num,collection="logs",sort_status=-1):
    client=pymongo.MongoClient(mongoAddr,connect=False)
    db = client['elm']
    if dict==None:
        if num:
            return db[collection].find({}).sort('time', sort_status).limit(num)
        else:
            return db[collection].find({}).sort('time', sort_status)
    else:
        if num:
            return db[collection].find(dict).sort('time', sort_status).limit(num)
        else:
            return db[collection].find(dict).sort('time', sort_status) 



def GetCurrentPhoneNum(url,sign,proxies): 
    Referer = "https://h5.ele.me/hongbao/"
    X = "eosid=3012646382330477600"
    headers ={"User-Agent":"Mozilla/5.0 (Linux; Android 6.0.1; Mi-4c Build/MOB31K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043508 Safari/537.36","Referer":Referer,"X-Shard":X} 
    url = url+"/phone"
    payload = {"sign":sign}
    rev = requests.get(url,params=payload,headers=headers,verify=False,proxies=proxies,timeout=(3,30))
    phone_data = json.loads(rev.text)
    return phone_data["phone"]
    
def RandomPhoneNum(url_raw,sign,proxies):
    #https://restapi.ele.me/v1/weixin/96E5431BDBEF9A225CDA45B23F52DEF7/phone?sign=7ea48e832e9f3f01c4fbaef59a2364ad    
    Referer = "https://h5.ele.me/hongbao/"
    X = "eosid=3012959054758444000"
    
    headers ={"User-Agent":"Mozilla/5.0 (Linux; Android 6.0.1; Mi-4c Build/MOB31K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043508 Safari/537.36","Content-Length":"300","Referer":Referer,"X-Shard":X} 
    url = url_raw+"/phone"
    phone = "1736720"+str(random.randint(1000,9999))
    phone_pass = GetCurrentPhoneNum(url_raw,sign,proxies)
    
    data={"sign":sign,"phone":phone}
    rev = requests.put(url,json=data,headers=headers,verify=False,proxies=proxies,timeout=(3,30))
    
    phone_current = GetCurrentPhoneNum(url_raw,sign,proxies)
    
    if phone_current == phone_pass:
        print("Failed to Change Phone,prepare to try again!!!")
        time.sleep(1)
        return RandomPhoneNum(url_raw,sign,proxies)
        
    else:
        print(phone_pass,"--->",phone_current)
        print("Suss Change Phone !!!")
        return phone_current

def GetLuck(data,sign,proxies):
    time.sleep(0.2)
    phonenum=data[0]
    payload=data[2]
    X="eosid=3013025494731821000"
    headers ={"User-Agent":"Mozilla/5.0 (Linux; Android 6.0.1; Mi-4c Build/MOB31K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043508 Safari/537.36","Content-Length":"300","Referer":"https://h5.ele.me/hongbao/","Origin":"https://h5.ele.me","Cookie":"","X-Shard":X}#data[3]"} 

    
   
    num =0
    rev = requests.post(data[4],headers=headers,verify=False,json=payload,stream=False,proxies=proxies,timeout=(3,30))
    print("---","Proxy:",proxies["http"],"Code:",rev.status_code,"---",)
    json_data = json.loads(rev.text)
    if json_data =={'message': '操作太频繁', 'name': 'TOO_BUSY'}:
        #time.sleep(10)
        return GetLuck(data,0,proxies)
    num = len(json_data['promotion_records'])
    
    if json_data["ret_code"]==1:
        return 454
    
    if json_data["promotion_items"]==[]:
        print("Warring phone: %s use times out"%(data[0],))
        phone = RandomPhoneNum(data[4].replace("marketing/promotion","v1"),data[2]["sign"],proxies)
        #data[2]["phone"]= phone
        return GetLuck(data,0,proxies)
    
    if sign==1:
        if "is_lucky" in json_data.keys():
            if json_data["is_lucky"] ==True:
                if json_data["lucky_status"]==3:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!今天领取次数太多!!!!!!!!!!!!!!!!!!!!")
                    return 9999

    #print(rev.text)
    #rev.text =re.findall("{.*?}", rev.text,re.S)
#     print(json_data)
    
#     if not json_data["ret_code"]==4 or json_data["ret_code"]==3 :
#         print("1")
#         #exit()
#         return [1,num]
    print("------------------------")
    #print(json_data)
    print(json_data['account'],num)        
    print("------------------------")    
    return num
    
def main(url,proxies):
    try:
        lucknum = int(re.findall("&lucky_number=(.*?)&", url)[0],10)
        if lucknum >10:
            return 888
        
        
        
        snnum = re.findall("&sn=(.*?)&", url)[0]
        
    
        print("Luck Num:%d"%(lucknum,))
        data =[['1','256919559',{"method":"phone","group_sn":snnum,"sign":"7ea48e832e9f3f01c4fbaef59a2364ad","phone":"","device_id":"","hardware_id":"","platform":0,"track_id":"undefined","weixin_avatar":"https://restapi.ele.me/marketing/promotion/weixin/DDEC1EF5920D3E2515421CE94C63305C","weixin_username":"Robot_01","unionid":"fuck"},"ubt_ssid=m9bocnk6p10hadpdu2ixpm4s23dzdtgk_2017-09-25; perf_ssid=2qxgfx7k1o9fb1k1buucgaa5e8wvye68_2017-09-25; _utrace=8633bf9bf398c9d97065683dc5f3094b_2017-09-25; snsInfo=%7B%22city%22%3A%22%E9%98%9C%E9%98%B3%22%2C%22eleme_key%22%3A%227ea48e832e9f3f01c4fbaef59a2364ad%22%2C%22figureurl%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F96E5431BDBEF9A225CDA45B23F52DEF7%2F30%22%2C%22figureurl_1%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F96E5431BDBEF9A225CDA45B23F52DEF7%2F50%22%2C%22figureurl_2%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F96E5431BDBEF9A225CDA45B23F52DEF7%2F100%22%2C%22figureurl_qq_1%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F96E5431BDBEF9A225CDA45B23F52DEF7%2F40%22%2C%22figureurl_qq_2%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F96E5431BDBEF9A225CDA45B23F52DEF7%2F100%22%2C%22gender%22%3A%22%E5%A5%B3%22%2C%22is_lost%22%3A0%2C%22is_yellow_vip%22%3A%220%22%2C%22is_yellow_year_vip%22%3A%220%22%2C%22level%22%3A%220%22%2C%22msg%22%3A%22%22%2C%22nickname%22%3A%229gPCu%22%2C%22openid%22%3A%2296E5431BDBEF9A225CDA45B23F52DEF7%22%2C%22province%22%3A%22%E5%AE%89%E5%BE%BD%22%2C%22ret%22%3A0%2C%22vip%22%3A%220%22%2C%22year%22%3A%222000%22%2C%22yellow_vip_level%22%3A%220%22%2C%22name%22%3A%229gPCu%22%2C%22avatar%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F96E5431BDBEF9A225CDA45B23F52DEF7%2F40%22%7D","https://restapi.ele.me/marketing/promotion/weixin/96E5431BDBEF9A225CDA45B23F52DEF7"],
               ['2','256935532',{"method":"phone","group_sn":snnum,"sign":"6fa398995c3b6d46728d48320e2d774b","phone":"","device_id":"","hardware_id":"","platform":0,"track_id":"undefined","weixin_avatar":"https://restapi.ele.me/marketing/promotion/weixin/DDEC1EF5920D3E2515421CE94C63305C","weixin_username":"Robot_02","unionid":"fuck"},"ubt_ssid=31wjg7ntw9uma34b2mlmfp23h0cvyfwh_2017-09-25; perf_ssid=dzcoczxgogswmwrktrn5jl7bch9qp588_2017-09-25; _utrace=2d520d3e90e29377e66116e04f49d739_2017-09-25; snsInfo=%7B%22city%22%3A%22%E9%98%9C%E9%98%B3%22%2C%22eleme_key%22%3A%226fa398995c3b6d46728d48320e2d774b%22%2C%22figureurl%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FFFEA967E1B2CA2D83559D9D2B1880AE3%2F30%22%2C%22figureurl_1%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FFFEA967E1B2CA2D83559D9D2B1880AE3%2F50%22%2C%22figureurl_2%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FFFEA967E1B2CA2D83559D9D2B1880AE3%2F100%22%2C%22figureurl_qq_1%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FFFEA967E1B2CA2D83559D9D2B1880AE3%2F40%22%2C%22figureurl_qq_2%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FFFEA967E1B2CA2D83559D9D2B1880AE3%2F100%22%2C%22gender%22%3A%22%E5%A5%B3%22%2C%22is_lost%22%3A0%2C%22is_yellow_vip%22%3A%220%22%2C%22is_yellow_year_vip%22%3A%220%22%2C%22level%22%3A%220%22%2C%22msg%22%3A%22%22%2C%22nickname%22%3A%22fPT2Z%22%2C%22openid%22%3A%22FFEA967E1B2CA2D83559D9D2B1880AE3%22%2C%22province%22%3A%22%E5%AE%89%E5%BE%BD%22%2C%22ret%22%3A0%2C%22vip%22%3A%220%22%2C%22year%22%3A%222000%22%2C%22yellow_vip_level%22%3A%220%22%2C%22name%22%3A%22fPT2Z%22%2C%22avatar%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FFFEA967E1B2CA2D83559D9D2B1880AE3%2F40%22%7D","https://restapi.ele.me/marketing/promotion/weixin/FFEA967E1B2CA2D83559D9D2B1880AE3"],
               ['3','256935596',{"method":"phone","group_sn":snnum,"sign":"1ddef021f50f22fa349e18803639f547","phone":"","device_id":"","hardware_id":"","platform":0,"track_id":"undefined","weixin_avatar":"https://restapi.ele.me/marketing/promotion/weixin/DDEC1EF5920D3E2515421CE94C63305C","weixin_username":"Robot_03","unionid":"fuck"},"ubt_ssid=wn90801t2ud9526do7vexvml4u0atuqp_2017-09-25; perf_ssid=tuwpr09k7quq3i21uxx6jgeeg9hr9kxl_2017-09-25; _utrace=3eb99447da8c88a77d12bd1377de4220_2017-09-25; snsInfo=%7B%22city%22%3A%22%E9%98%9C%E9%98%B3%22%2C%22eleme_key%22%3A%221ddef021f50f22fa349e18803639f547%22%2C%22figureurl%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FDDEC1EF5920D3E2515421CE94C63305C%2F30%22%2C%22figureurl_1%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FDDEC1EF5920D3E2515421CE94C63305C%2F50%22%2C%22figureurl_2%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FDDEC1EF5920D3E2515421CE94C63305C%2F100%22%2C%22figureurl_qq_1%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FDDEC1EF5920D3E2515421CE94C63305C%2F40%22%2C%22figureurl_qq_2%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FDDEC1EF5920D3E2515421CE94C63305C%2F100%22%2C%22gender%22%3A%22%E5%A5%B3%22%2C%22is_lost%22%3A0%2C%22is_yellow_vip%22%3A%220%22%2C%22is_yellow_year_vip%22%3A%220%22%2C%22level%22%3A%220%22%2C%22msg%22%3A%22%22%2C%22nickname%22%3A%22SE4sW%22%2C%22openid%22%3A%22DDEC1EF5920D3E2515421CE94C63305C%22%2C%22province%22%3A%22%E5%AE%89%E5%BE%BD%22%2C%22ret%22%3A0%2C%22vip%22%3A%220%22%2C%22year%22%3A%221911%22%2C%22yellow_vip_level%22%3A%220%22%2C%22name%22%3A%22SE4sW%22%2C%22avatar%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FDDEC1EF5920D3E2515421CE94C63305C%2F40%22%7D","https://restapi.ele.me/marketing/promotion/weixin/DDEC1EF5920D3E2515421CE94C63305C"],
               ['4','256937842',{"method":"phone","group_sn":snnum,"sign":"ab6966530606a1759123daf64d77410d","phone":"","device_id":"","hardware_id":"","platform":0,"track_id":"undefined","weixin_avatar":"https://restapi.ele.me/marketing/promotion/weixin/DDEC1EF5920D3E2515421CE94C63305C","weixin_username":"Robot_04","unionid":"fuck"},"ubt_ssid=xt4u74kfppo4n21kagv1ysrr1rsoy682_2017-09-25; perf_ssid=48dm3d6k9g3hak3lzz9gg5uudvj4nevf_2017-09-25; _utrace=f118057deec18a54e2821107744220ed_2017-09-25; snsInfo=%7B%22city%22%3A%22%E9%98%9C%E9%98%B3%22%2C%22eleme_key%22%3A%22ab6966530606a1759123daf64d77410d%22%2C%22figureurl%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F615AAAF2D4C5586BB2AC2A6487DD54F1%2F30%22%2C%22figureurl_1%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F615AAAF2D4C5586BB2AC2A6487DD54F1%2F50%22%2C%22figureurl_2%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F615AAAF2D4C5586BB2AC2A6487DD54F1%2F100%22%2C%22figureurl_qq_1%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F615AAAF2D4C5586BB2AC2A6487DD54F1%2F40%22%2C%22figureurl_qq_2%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F615AAAF2D4C5586BB2AC2A6487DD54F1%2F100%22%2C%22gender%22%3A%22%E5%A5%B3%22%2C%22is_lost%22%3A0%2C%22is_yellow_vip%22%3A%220%22%2C%22is_yellow_year_vip%22%3A%220%22%2C%22level%22%3A%220%22%2C%22msg%22%3A%22%22%2C%22nickname%22%3A%22DW5ze%22%2C%22openid%22%3A%22615AAAF2D4C5586BB2AC2A6487DD54F1%22%2C%22province%22%3A%22%E5%AE%89%E5%BE%BD%22%2C%22ret%22%3A0%2C%22vip%22%3A%220%22%2C%22year%22%3A%222000%22%2C%22yellow_vip_level%22%3A%220%22%2C%22name%22%3A%22DW5ze%22%2C%22avatar%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F615AAAF2D4C5586BB2AC2A6487DD54F1%2F40%22%7D","https://restapi.ele.me/marketing/promotion/weixin/615AAAF2D4C5586BB2AC2A6487DD54F1"],
               ['5','256947889',{"method":"phone","group_sn":snnum,"sign":"8e7e57320d36f35e0398370b4b17941c","phone":"","device_id":"","hardware_id":"","platform":0,"track_id":"undefined","weixin_avatar":"https://restapi.ele.me/marketing/promotion/weixin/DDEC1EF5920D3E2515421CE94C63305C","weixin_username":"Robot_05","unionid":"fuck"},"ubt_ssid=zk8jcsoyypjlze8g8r7zpz4kbo3u5ccw_2017-09-25; perf_ssid=ifygamqx216feas80p4e0n35ycjdw5tf_2017-09-25; _utrace=0b70906176cb54611ac8e38a5e02f912_2017-09-25; snsInfo=%7B%22city%22%3A%22%E9%98%9C%E9%98%B3%22%2C%22eleme_key%22%3A%228e7e57320d36f35e0398370b4b17941c%22%2C%22figureurl%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FB128960FC4D06F4CA2666AD4E79EC26F%2F30%22%2C%22figureurl_1%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FB128960FC4D06F4CA2666AD4E79EC26F%2F50%22%2C%22figureurl_2%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FB128960FC4D06F4CA2666AD4E79EC26F%2F100%22%2C%22figureurl_qq_1%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FB128960FC4D06F4CA2666AD4E79EC26F%2F40%22%2C%22figureurl_qq_2%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FB128960FC4D06F4CA2666AD4E79EC26F%2F100%22%2C%22gender%22%3A%22%E5%A5%B3%22%2C%22is_lost%22%3A0%2C%22is_yellow_vip%22%3A%220%22%2C%22is_yellow_year_vip%22%3A%220%22%2C%22level%22%3A%220%22%2C%22msg%22%3A%22%22%2C%22nickname%22%3A%22GAYRG%22%2C%22openid%22%3A%22B128960FC4D06F4CA2666AD4E79EC26F%22%2C%22province%22%3A%22%E5%AE%89%E5%BE%BD%22%2C%22ret%22%3A0%2C%22vip%22%3A%220%22%2C%22year%22%3A%221911%22%2C%22yellow_vip_level%22%3A%220%22%2C%22name%22%3A%22GAYRG%22%2C%22avatar%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FB128960FC4D06F4CA2666AD4E79EC26F%2F40%22%7D","https://restapi.ele.me/marketing/promotion/weixin/B128960FC4D06F4CA2666AD4E79EC26F"],
               ['6','256955258',{"method":"phone","group_sn":snnum,"sign":"625acac9ea720c8e167404a3b9bc2c61","phone":"","device_id":"","hardware_id":"","platform":0,"track_id":"undefined","weixin_avatar":"https://restapi.ele.me/marketing/promotion/weixin/DDEC1EF5920D3E2515421CE94C63305C","weixin_username":"Robot_06","unionid":"fuck"},"ubt_ssid=9an7lwhdt7ypsr9ik71i4wdyfhtoa8y7_2017-09-25; perf_ssid=jvldquwj9uuho5iy0bdma7najsx15fdj_2017-09-25; _utrace=d2e5a92ac08d3a5c6f32f1b2b1ed412b_2017-09-25; snsInfo=%7B%22city%22%3A%22%E9%98%9C%E9%98%B3%22%2C%22eleme_key%22%3A%22625acac9ea720c8e167404a3b9bc2c61%22%2C%22figureurl%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F3FBDD1AD8396CC48FC9E0F8AE0C70E02%2F30%22%2C%22figureurl_1%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F3FBDD1AD8396CC48FC9E0F8AE0C70E02%2F50%22%2C%22figureurl_2%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F3FBDD1AD8396CC48FC9E0F8AE0C70E02%2F100%22%2C%22figureurl_qq_1%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F3FBDD1AD8396CC48FC9E0F8AE0C70E02%2F40%22%2C%22figureurl_qq_2%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F3FBDD1AD8396CC48FC9E0F8AE0C70E02%2F100%22%2C%22gender%22%3A%22%E5%A5%B3%22%2C%22is_lost%22%3A0%2C%22is_yellow_vip%22%3A%220%22%2C%22is_yellow_year_vip%22%3A%220%22%2C%22level%22%3A%220%22%2C%22msg%22%3A%22%22%2C%22nickname%22%3A%22F1BMB%22%2C%22openid%22%3A%223FBDD1AD8396CC48FC9E0F8AE0C70E02%22%2C%22province%22%3A%22%E5%AE%89%E5%BE%BD%22%2C%22ret%22%3A0%2C%22vip%22%3A%220%22%2C%22year%22%3A%221911%22%2C%22yellow_vip_level%22%3A%220%22%2C%22name%22%3A%22F1BMB%22%2C%22avatar%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F3FBDD1AD8396CC48FC9E0F8AE0C70E02%2F40%22%7D","https://restapi.ele.me/marketing/promotion/weixin/3FBDD1AD8396CC48FC9E0F8AE0C70E02"],
               ['7','256957818',{"method":"phone","group_sn":snnum,"sign":"8b6d6117cb81df46e71424492e22fea4","phone":"","device_id":"","hardware_id":"","platform":0,"track_id":"undefined","weixin_avatar":"https://restapi.ele.me/marketing/promotion/weixin/DDEC1EF5920D3E2515421CE94C63305C","weixin_username":"Robot_07","unionid":"fuck"},"ubt_ssid=k6s7sppksqk71vwyowwl2x00u19awczw_2017-09-25; perf_ssid=tyccj4wqutpg1z2bkiv3bwx275w02b0j_2017-09-25; _utrace=6243f986a8ab3b1c0622978c9827b8c2_2017-09-25; snsInfo=%7B%22city%22%3A%22%E9%98%9C%E9%98%B3%22%2C%22eleme_key%22%3A%228b6d6117cb81df46e71424492e22fea4%22%2C%22figureurl%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F5F8961EA9B8788E1F42C9B00FF82FCAE%2F30%22%2C%22figureurl_1%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F5F8961EA9B8788E1F42C9B00FF82FCAE%2F50%22%2C%22figureurl_2%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F5F8961EA9B8788E1F42C9B00FF82FCAE%2F100%22%2C%22figureurl_qq_1%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F5F8961EA9B8788E1F42C9B00FF82FCAE%2F40%22%2C%22figureurl_qq_2%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F5F8961EA9B8788E1F42C9B00FF82FCAE%2F100%22%2C%22gender%22%3A%22%E5%A5%B3%22%2C%22is_lost%22%3A0%2C%22is_yellow_vip%22%3A%220%22%2C%22is_yellow_year_vip%22%3A%220%22%2C%22level%22%3A%220%22%2C%22msg%22%3A%22%22%2C%22nickname%22%3A%220ffiG%22%2C%22openid%22%3A%225F8961EA9B8788E1F42C9B00FF82FCAE%22%2C%22province%22%3A%22%E5%AE%89%E5%BE%BD%22%2C%22ret%22%3A0%2C%22vip%22%3A%220%22%2C%22year%22%3A%221911%22%2C%22yellow_vip_level%22%3A%220%22%2C%22name%22%3A%220ffiG%22%2C%22avatar%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F5F8961EA9B8788E1F42C9B00FF82FCAE%2F40%22%7D","https://restapi.ele.me/marketing/promotion/weixin/5F8961EA9B8788E1F42C9B00FF82FCAE"], 
               ['8','256962003',{"method":"phone","group_sn":snnum,"sign":"fc7527f8f1bc4c0f6d5d4ae8a16415ea","phone":"","device_id":"","hardware_id":"","platform":0,"track_id":"undefined","weixin_avatar":"https://restapi.ele.me/marketing/promotion/weixin/DDEC1EF5920D3E2515421CE94C63305C","weixin_username":"Robot_08","unionid":"fuck"},"ubt_ssid=0x06rc82dglthvolbvw32huzdtt85ifh_2017-09-25; perf_ssid=22j7y37r4h1sallumc828tkogdplk0hu_2017-09-25; _utrace=7031ba8877cd1a2875fbd9cbef84af93_2017-09-25; snsInfo=%7B%22city%22%3A%22%E9%98%9C%E9%98%B3%22%2C%22eleme_key%22%3A%22fc7527f8f1bc4c0f6d5d4ae8a16415ea%22%2C%22figureurl%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FDCF5ECE5D47216BECA5BC25A56BD4C26%2F30%22%2C%22figureurl_1%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FDCF5ECE5D47216BECA5BC25A56BD4C26%2F50%22%2C%22figureurl_2%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2FDCF5ECE5D47216BECA5BC25A56BD4C26%2F100%22%2C%22figureurl_qq_1%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FDCF5ECE5D47216BECA5BC25A56BD4C26%2F40%22%2C%22figureurl_qq_2%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FDCF5ECE5D47216BECA5BC25A56BD4C26%2F100%22%2C%22gender%22%3A%22%E5%A5%B3%22%2C%22is_lost%22%3A0%2C%22is_yellow_vip%22%3A%220%22%2C%22is_yellow_year_vip%22%3A%220%22%2C%22level%22%3A%220%22%2C%22msg%22%3A%22%22%2C%22nickname%22%3A%22eRIWY%22%2C%22openid%22%3A%22DCF5ECE5D47216BECA5BC25A56BD4C26%22%2C%22province%22%3A%22%E5%AE%89%E5%BE%BD%22%2C%22ret%22%3A0%2C%22vip%22%3A%220%22%2C%22year%22%3A%221911%22%2C%22yellow_vip_level%22%3A%220%22%2C%22name%22%3A%22eRIWY%22%2C%22avatar%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2FDCF5ECE5D47216BECA5BC25A56BD4C26%2F40%22%7D","https://restapi.ele.me/marketing/promotion/weixin/DCF5ECE5D47216BECA5BC25A56BD4C26"],
               ['9','256973185',{"method":"phone","group_sn":snnum,"sign":"1b532f7f00ba66cf2b32459ad59608fd","phone":"","device_id":"","hardware_id":"","platform":0,"track_id":"undefined","weixin_avatar":"https://restapi.ele.me/marketing/promotion/weixin/DDEC1EF5920D3E2515421CE94C63305C","weixin_username":"Robot_09","unionid":"fuck"},"ubt_ssid=z5hdegfklioonlwcj8gbsk92hdyo3mzk_2017-09-25; perf_ssid=0owbkngcn4sswfkhjfw4fjdtoyn78kmk_2017-09-25; _utrace=f344c8fa87f1b8d2796c20f3a44fa182_2017-09-25; snsInfo=%7B%22city%22%3A%22%E9%98%9C%E9%98%B3%22%2C%22eleme_key%22%3A%221b532f7f00ba66cf2b32459ad59608fd%22%2C%22figureurl%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F8952DB1B45EE58E422D8DA67C8CEE523%2F30%22%2C%22figureurl_1%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F8952DB1B45EE58E422D8DA67C8CEE523%2F50%22%2C%22figureurl_2%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F8952DB1B45EE58E422D8DA67C8CEE523%2F100%22%2C%22figureurl_qq_1%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F8952DB1B45EE58E422D8DA67C8CEE523%2F40%22%2C%22figureurl_qq_2%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F8952DB1B45EE58E422D8DA67C8CEE523%2F100%22%2C%22gender%22%3A%22%E5%A5%B3%22%2C%22is_lost%22%3A0%2C%22is_yellow_vip%22%3A%220%22%2C%22is_yellow_year_vip%22%3A%220%22%2C%22level%22%3A%220%22%2C%22msg%22%3A%22%22%2C%22nickname%22%3A%22Hppq4%22%2C%22openid%22%3A%228952DB1B45EE58E422D8DA67C8CEE523%22%2C%22province%22%3A%22%E5%AE%89%E5%BE%BD%22%2C%22ret%22%3A0%2C%22vip%22%3A%220%22%2C%22year%22%3A%222000%22%2C%22yellow_vip_level%22%3A%220%22%2C%22name%22%3A%22Hppq4%22%2C%22avatar%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F8952DB1B45EE58E422D8DA67C8CEE523%2F40%22%7D","https://restapi.ele.me/marketing/promotion/weixin/8952DB1B45EE58E422D8DA67C8CEE523"],
               ['10','256973185',{"method":"phone","group_sn":snnum,"sign":"d2d45210ef51e3bc38b757f9f2c0942d","phone":"","device_id":"","hardware_id":"","platform":0,"track_id":"undefined","weixin_avatar":"https://restapi.ele.me/marketing/promotion/weixin/DDEC1EF5920D3E2515421CE94C63305C","weixin_username":"Robot_10","unionid":"fuck"},"ubt_ssid=njqsjramrzgmfez54xipw6gotxlu25dl_2017-09-25; perf_ssid=6799fgf3kr4py755i1w83paact1n8v44_2017-09-25; _utrace=b4dddf7c80c29158a4b0de0d186e175f_2017-09-25; snsInfo=%7B%22city%22%3A%22%E9%98%9C%E9%98%B3%22%2C%22eleme_key%22%3A%22d2d45210ef51e3bc38b757f9f2c0942d%22%2C%22figureurl%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F1C54A6FBFE7BDD986E81DF75F2768755%2F30%22%2C%22figureurl_1%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F1C54A6FBFE7BDD986E81DF75F2768755%2F50%22%2C%22figureurl_2%22%3A%22http%3A%2F%2Fqzapp.qlogo.cn%2Fqzapp%2F101204453%2F1C54A6FBFE7BDD986E81DF75F2768755%2F100%22%2C%22figureurl_qq_1%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F1C54A6FBFE7BDD986E81DF75F2768755%2F40%22%2C%22figureurl_qq_2%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F1C54A6FBFE7BDD986E81DF75F2768755%2F100%22%2C%22gender%22%3A%22%E5%A5%B3%22%2C%22is_lost%22%3A0%2C%22is_yellow_vip%22%3A%220%22%2C%22is_yellow_year_vip%22%3A%220%22%2C%22level%22%3A%220%22%2C%22msg%22%3A%22%22%2C%22nickname%22%3A%22zmIgW%22%2C%22openid%22%3A%221C54A6FBFE7BDD986E81DF75F2768755%22%2C%22province%22%3A%22%E5%AE%89%E5%BE%BD%22%2C%22ret%22%3A0%2C%22vip%22%3A%220%22%2C%22year%22%3A%222000%22%2C%22yellow_vip_level%22%3A%220%22%2C%22name%22%3A%22zmIgW%22%2C%22avatar%22%3A%22http%3A%2F%2Fq.qlogo.cn%2Fqqapp%2F101204453%2F1C54A6FBFE7BDD986E81DF75F2768755%2F40%22%7D","https://restapi.ele.me/marketing/promotion/weixin/1C54A6FBFE7BDD986E81DF75F2768755"],
            ]
    
    
        for i in (0,len(data)-1):
            data[i][3]=""
        for num in range(0,lucknum):
            datar = data[num]
            human_num = GetLuck(datar,0,proxies)
            if human_num == 454:
                return 454
            
            
            
            
            if human_num+1==lucknum:
                print("----Got Luck----")
    #             status = GetLuck(Q_MyData,1)
    #             if status==99999:
    #                 return 
                return 666
            elif human_num>=lucknum:
                print("手慢了一步!!!")
                return 555 
    except Exception as e:
                
        return main(url,get_verify_proxy())


def get_proxy():
    pass
@bot.on_message()
def msg_handle(context):
    
    
    Update_Time()
    if context["message"] == '查看运行状态':
        if str(context["user_id"])==str(qq_id):
            money =0
            count =0
            for count,data_tmp in enumerate(SearchMongo(None,None,"logs",1)):
                if count==0:
                    start_time = data_tmp["time"]
                money+=int(data_tmp["lucknum"])
                

            today =datetime.datetime.today()    
            nowmidnight = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
            now = datetime.datetime.now()
            today_money =0
            today_count=0
            for today_count,data_tmp in enumerate(SearchMongo({"time":{"$gte":nowmidnight,"$lt":now}},None)):
                today_money +=int(data_tmp["lucknum"])
                
            
            endtime = datetime.datetime.now()  
        #(endtime-start_time).days
            bot.send(context,"--  运行了:%s天  总次数%s 总金额:%s 总平均金额:%s  --\n                  --  今天次数%s 金额:%s 平均金额:%s  --" %((endtime-start_time).days,count+1,money,round(money/(count+1),1),today_count+1,today_money,round(today_money/(today_count+1),1)))
        return
    
    
    elif str(context["message"]) == '机器人':
        #print(context["message"])
        if context["user_id"]==977081887:  
            return()          
            
        
        bot.send(context, '在呢!!!')
        return
    elif str(context["message"]) == '我的红包记录': 
        record="由于减小服务器资源消耗，仅显示最近5条信息:\n"   
        for one in SearchMongo({"id":context["user_id"]},5):
            record+="SN:{0} 时间:{1} 金额:{2}\n".format(one["sn"],one["time"].strftime('%m-%d %H:%M:%S'),one['lucknum'])        

        bot.send(context,record)
        return
    elif str(context["message"]) == '查看剩余人数':
        people = []
        last_five = []
        last_five_text = ""
        now_time =datetime.datetime.now()   
        for one in SearchMongo(None,None,collection="member",sort_status=-1):
            if one['expire_time']>now_time:
                
                people.append({'user_id':one['user_id'],'nickname':one['nickname'],"days_left":(one['expire_time']-datetime.datetime.now()).days})
        #print("剩余人数：",len(people))
        last_five_text += "剩余人数："+str(len(people))+"\n"
        for j in range(5):
            tmp =0
            num =None
            for i in range(len(people)):
                if int(people[i]["days_left"]) >tmp:
                    
                    tmp=int(people[i]["days_left"])
                    num =i
            if not num == None:
                last_five.append({'user_id':people[num]['user_id'],'nickname':people[num]['nickname'],"days_left":people[num]["days_left"]})
                last_five_text+="QQ:"+str(people[num]['user_id'])+" 昵称: "+people[num]['nickname']+" | 剩余天数: "+str(people[num]["days_left"])+"天"+'\n'

                people[num]["days_left"]=0
                
        bot.send(context,last_five_text)    
        return 
    elif str(context["message"]) == '修复数据库':
        if not str(context["user_id"])==str(qq_id):
            return
        member_data =[]
        now = datetime.datetime.now()
        exp_time = now + datetime.timedelta(days=30) 
        for tmp in bot.get_group_member_list(group_id=620737779):
            tmp["expire_time"]= exp_time
            member_data.append(tmp)
        

        menber_mongo_data=[one['user_id'] for one in SearchMongo(None,None,"member")]
        
        if not len(member_data)==len(menber_mongo_data): 
            list_tmp =[]
            err =0
            list_err=[]
            for tmp in  menber_mongo_data:
                if not tmp  in list_tmp:
                    list_tmp.append(tmp)
                else:
                    err+=1 
                    list_err.append(tmp)
            if not err==0:
                bot.send(context, '数据库重复,请手动修复,错误%s个,如下：%s'%(err,str(list_err)))
        err =0
        now = datetime.datetime.now()
        exp_time = now + datetime.timedelta(days=2)
        for member in member_data:
            if member['user_id'] in menber_mongo_data:
                pass
            else:  
                err+=1
                member["expire_time"]= exp_time
                
                SaveMongo(member,'member')
        if err ==0:
            bot.send(context, '数据库正常') 
        else:
            bot.send(context, '修复了个%s错误'%(err))
        return          
        

                    
    else :
        pass
    
    if "CQ:share" in context["message"] or "CQ:rich" in context["message"]:
        url = (re.findall(".*?url=(.*?)]", context["message"].replace('&amp;','&'))[0]).strip()
        #url = (re.findall(".*?url=(.*?),.*?", context["message"].replace('&amp;','&'))[0]).strip()旧版

        
        if "https://" in url or "http://url.cn" in url:
            if "http://url.cn" in url:
                
                html = requests.get(url, allow_redirects=False,proxies=None,timeout=(3,30))
                
                url =  html.headers['Location']
            else:
                pass
            try:
                
                nickname = [n['nickname'] for n in SearchMongo({'user_id':context['user_id']},1,"member")][0]
                
            except Exception:
                bot.send(context,"你还没有加群，请加群620737779后操作\n若加群后还是提示错误，请联系管理员!!!" ) 
                return
            try:
            #if 1:

                lucknum = int(re.findall("&lucky_number=(.*?)&", url)[0],10)

                sn = re.findall("&sn=(.*?)&", url)[0]#sn=29d0a4d59fadf88c&
                
                if [tmp["expire_time"] for tmp in SearchMongo({'user_id':context['user_id']},None,"member")][0]<datetime.datetime.now():
                    #bot.send(context, "{0}---效期已过，退群重新进群即可。".format(nickname))
                    #return
                    pass
                
                for one in SearchMongo({"sn":sn},1): #判断重复
                    bot.send(context, "{0}---在{1}时候已经发过了!!!".format(nickname,one["time"].strftime('%m-%d %H:%M')))
                    return

                if context['message_type']=='group':#踢人                       
                    #bot.set_group_kick(group_id=context['group_id'],user_id=context['user_id'],reject_add_request=True)
                    #Ban_Data = {'user_id':context['user_id']}
                    #SaveMongo(Ban_Data,'ban')
                    #DelMongo({'user_id':context['user_id']},'member')
                    bot.send(context,"-{0}-不要发在群里哦，私发我哦。".format(context['user_id']) )  
                    return
                today =datetime.datetime.today()    
                nowmidnight = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
                now = datetime.datetime.now()
                if len( [tmp for tmp in SearchMongo({"time":{"$gte":nowmidnight,"$lt":now},"id":context["user_id"]},None)])>=5:
                    if not str(context["user_id"])==str(qq_id):                       
                        bot.send(context, "{0}---你今天可以领得太多了，已经达到限制数目!!!".format(nickname))
                        return
                else:
                    pass
                    #bot.send(context,"收到来自-{0}-的{1}，请注意查看机器人和你的对话!!!".format(nickname,lucknum) )    
    
            except Exception as e:
                if context['message_type']=='group':
                    bot.send(context,"-{0}-只支持拼手气H。B,请不要发到群里!!!\n还有的话就是要加我好友偷偷然后发给我...这样子的话不会被别人抢哦。。".format(context['user_id']) )     
                    return  
                else:
                    bot.send(context, "{0}---只支持拼手气H。B".format(nickname))
                    return
                
            
            code=main(url,get_verify_proxy())
#             except Exception:
#                 disconnect()
#                 connect()
#                 code=main(url)
            #code=666
            #return
            
            if code==666: # 555手气慢了 666 OK  454
                SaveMongo({"id":context['user_id'],"time":datetime.datetime.now(),"sn":sn,"lucknum":lucknum})
                bot.send_private_msg(user_id=context['user_id'],message="{0},私聊你啦,快领取你的H。B。吧!!!".format(nickname))#,lucknum))
            elif code ==555:
                bot.send(context,"{0}---手慢了一步额!!!".format(nickname))
            elif code ==454:
                bot.send(context,"{0}---人数超过限制!!!".format(nickname))
            elif code ==888:
                bot.send(context,"{0}---大于10￥,暂时不支持,请等待更新!!!".format(nickname))
            else :
                bot.send(context,"{0}---系统错误请联系管理维护!!!".format(nickname))
        
            return        

@bot.on_event('group_increase')
def handle_group_increase(context): 
    if [b['user_id'] for b in SearchMongo({'user_id':context['user_id']},1,"ban")]:
        bot.set_group_kick(group_id=context['group_id'],user_id=context['user_id'],reject_add_request=True)
    else:        
        member = bot.get_group_member_info(group_id=context['group_id'],user_id=context['user_id'])  
        now = datetime.datetime.now()
        exp_time = now + datetime.timedelta(days=30) 
        member["expire_time"]= exp_time
        #while SearchMongo({'user_id':context['user_id']},None,collection='member',sort_status=-1): 
        for one in SearchMongo({'user_id':context['user_id']},None,collection='member',sort_status=-1):
            print("删除成员")
            DelMongo({'user_id':context['user_id']},'member')
        print("增加成员")  
        SaveMongo(member,'member')
    return

@bot.on_event('group_decrease')
def handle_group_decrease(context):
    #while SearchMongo({'user_id':context['user_id']},None,collection='member',sort_status=-1):
    for one in SearchMongo({'user_id':context['user_id']},None,collection='member',sort_status=-1):
        print("删除成员")
        DelMongo({'user_id':context['user_id']},'member')      
    
    return
    
#bot.on_request('group', 'friend')
@bot.on_request('friend')
def handle_request(context):
    return {'approve': True}  # 同意所有加群、加好友请求

@bot.on_message()
def handle_msg(context):
    #if "CQ:share" in context["message"] or "CQ:rich" in context["message"]:
        #bot.send(context,"收到,请耐心等待。")  
    global message_list
    message_list.append(context)
    #print(message_list)
    
def bot_run():
    bot.run(host='127.0.0.1', port=8099)
def msg_check():
    global message_list
    while(1):
        if len(message_list) ==0:
            time.sleep(0.2)
            continue
        else:
            try:
                threading.Thread(target=msg_handle,args=(message_list[0],)).start()

            except Exception as e:
                print(e)
            message_list=message_list[1:]
            
def get_verify_proxy():
    global proxy_list
    

    while(1):
        used = proxy_list[0]
        proxy_list = proxy_list[1:]

        try:
            rev = requests.get('https://www.baidu.com/', proxies={"http":"http://%s"%(used,)},timeout=(3,10))
            print(rev.status_code)
        except:
            return get_verify_proxy()
        else:
            return {"http":"http://%s"%(used,),'https': "https://%s"%(used,),}
        time.sleep(0.2)    

        
        

def get_proxy_from_server():
    global proxy_list
    
    rev = requests.get("http://api.zdaye.com/?api=201711131242112244&sleep=2&gb=4&https=1&post=1&rtype=1&ct=100")
    if rev.status_code ==200:
        if "<bad>" in rev.text:
            time.sleep(1)
        else:
            print(rev.text)
            proxy_data =io.StringIO(rev.text.strip()).readlines()
            
            for one in proxy_data:
                proxy_list.append(one.strip())
            print(len(proxy_list))

    
    
def proxy_pool():
    while(1):
        
        if len(proxy_list)<100:
            print("代理池增加代理...")
            try:
                get_proxy_from_server()
            except Exception:
                print("ERROR CODE:",4567)
        time.sleep(0.2)
        
                
if __name__ =="__main__":
    threading.Thread(target=proxy_pool).start()
    #threading.Thread(target=Check_Live).start()
    threading.Thread(target=bot_run).start()
    msg_check()
