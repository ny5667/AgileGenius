# 考勤列表参考自@施尹志 考勤统计
import re
import json
import base64
import definition
from lxml import etree

import sys
sys.path.append("C:\\Lib")  # 用于指定Python依赖模块路径
import requests


userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
header = {
    "User-Agent": userAgent
}

class kq():
    def __init__(self):
        # 创建Session
        self.a_session = requests.session()
        # 登陆信息  
        self.login(self.a_session, definition.oaAccount, definition.oaPassword)
        self.staff_id = self.get_staff_id()

    #@pysnooper.snoop("debug.log")
    def get_staff_id(self):
        url = "https://ehr.supcon.com/RedseaPlatform/PtPortal.mc?method=classic"
        response_res = self.a_session.get(url)


        staffid_content = response_res.text
        get_staffid_pattern = re.compile(r"staffId: '(.*?)'", re.S | re.M)
        _staffid = re.findall(get_staffid_pattern, staffid_content)

        #print(f"staffId = {_staffid[0]}")
        if len(_staffid) < 1:
            print("用户名或密码错误，请在网站（https://portal.supcon.com）检查脚本所使用的用户名和密码")
            exit()

        return _staffid[0]

    #@pysnooper.snoop("debug.log")
    def get_lt(self):
        first_url = "https://portal.supcon.com/cas-web/login?service=https%3A%2F%2Fehr.supcon.com%2FRedseaPlatform%2F"
        response_res = self.a_session.get(first_url)
        # 无论是否登录成功，状态码一般都是 statusCode = 200
        #print(f"statusCode = {responseRes.status_code}")
        #print(f"text = {responseRes.text}")

        html = etree.HTML(response_res.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))

        _lt = html.xpath('//input[@name="lt"]/@value')

        #print(f"lt = {_lt[0]}")
        return _lt[0]


    #@pysnooper.snoop("debug.log")
    def login(self, a_session, username, password):

        b64password = base64.b64encode(password.encode())

        lt = self.get_lt()

        post_data = {
            "portal_username": username,
            "password": b64password,
            "bakecookie": "on",
            "lt": lt,
            "_eventId": "submit",
            "username": username,
        }

        login_url = "https://portal.supcon.com/cas-web/login?service=https%3A%2F%2Fehr.supcon.com%2FRedseaPlatform%2F"
        a_session.post(login_url, data=post_data, headers=header)



    #@pysnooper.snoop("debug.log")
    def is_holiday(self, date):

        post_data = {
            "staff_id": self.staff_id,
            "begin": date,
            "end": date
        }

        query_url = "https://ehr.supcon.com/RedseaPlatform/getList/kq_count_abnormal_SelectStaffID/CoreRequest.mc?"

        response_res = self.a_session.post(query_url, data=post_data, headers=header)

        workdat_infos = json.loads(response_res.text)

        return workdat_infos["result"]["#result-set-1"][0]["kq_status_total_name"] == '休息'


