# 考勤列表参考自@施尹志 考勤统计
import re
import json
import base64
import definition
from datetime import date
from datetime import datetime
from lxml import etree

import sys
sys.path.append("C:\\Lib")  # 用于指定Python依赖模块路径
import requests
#import pysnooper

#RECORDS_DUMP_FILE = r"D:\records.json"
#WORKDAY_DUMP_FILE = r"D:\workday_info.json"

#RECORDS_DEBUG_FILE = r"D:\records.json"
#WORKDAY_DEBUG_FILE = r"D:\workday_info.json"


userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
header = {
    "User-Agent": userAgent
}

class KQ():
    def __init__(self):
        # 创建Session
        self.aSession = requests.session()
        # 登陆信息  
        self.login(self.aSession, definition.oaAccount, definition.oaPassword)
        self.staffId = self.getStaffId()

    #@pysnooper.snoop("debug.log")
    def getStaffId(self):
        url = "https://ehr.supcon.com/RedseaPlatform/PtPortal.mc?method=classic"
        responseRes = self.aSession.get(url)

        #print(f"statusCode = {responseRes.status_code}")
        #print(f"text = {responseRes.text}")

        staffid_content = responseRes.text
        get_staffid_pattern = re.compile(r"staffId: '(.*?)'", re.S | re.M)
        _staffid = re.findall(get_staffid_pattern, staffid_content)

        #print(f"staffId = {_staffid[0]}")
        if len(_staffid) < 1:
            print("用户名或密码错误，请在网站（https://portal.supcon.com）检查脚本所使用的用户名和密码")
            exit()

        return _staffid[0]

    #@pysnooper.snoop("debug.log")
    def getLt(self):
        firstUrl = "https://portal.supcon.com/cas-web/login?service=https%3A%2F%2Fehr.supcon.com%2FRedseaPlatform%2F"
        responseRes = self.aSession.get(firstUrl)
        # 无论是否登录成功，状态码一般都是 statusCode = 200
        #print(f"statusCode = {responseRes.status_code}")
        #print(f"text = {responseRes.text}")

        html = etree.HTML(responseRes.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))

        _lt = html.xpath('//input[@name="lt"]/@value')

        #print(f"lt = {_lt[0]}")
        return _lt[0]


    #@pysnooper.snoop("debug.log")
    def login(self, aSession, username, password):

        b64password = base64.b64encode(password.encode())

        lt = self.getLt()

        postData = {
            "portal_username": username,
            "password": b64password,
            "bakecookie": "on",
            "lt": lt,
            "_eventId": "submit",
            "username": username,
        }

        # JSESSIONID = aSession.cookies.get_dict()["JSESSIONID"]
        # print(f"JSESSIONID = {JSESSIONID}")

        # loginUrl = "https://portal.supcon.com/cas-web/login;jsessionid="+ JSESSIONID + "?service=https%3A%2F%2Fehr.supcon.com%2FRedseaPlatform%2F"
        loginUrl = "https://portal.supcon.com/cas-web/login?service=https%3A%2F%2Fehr.supcon.com%2FRedseaPlatform%2F"
        responseRes = aSession.post(loginUrl, data=postData, headers=header)



    #@pysnooper.snoop("debug.log")
    def isHoliday(self, date):

        postData = {
            "staff_id": self.staffId,
            "begin": date,
            "end": date
        }

        queryUrl = "https://ehr.supcon.com/RedseaPlatform/getList/kq_count_abnormal_SelectStaffID/CoreRequest.mc?"

        responseRes = self.aSession.post(queryUrl, data=postData, headers=header)

        workdatInfos = json.loads(responseRes.text)

        return workdatInfos["result"]["#result-set-1"][0]["kq_status_total_name"] == '休息'


