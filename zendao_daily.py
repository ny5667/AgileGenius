import logging
import re
import definition
import requests
import json
import sys
from kq import Kq
from execution_data import execution_data
from lxml import etree
from daily_report_generator import report_generator
import datetime

loginPath = "/biz/user-login.html"
global_randomPath = "/biz/user-refreshRandom.html"
projectListPath = "/biz/project-browse.html"
randomPath = "/biz/user-refreshRandom.html"

class Zentao():
    def __init__(self) -> None:
        self.sessionid, self.rand = self.get_sessionid_rand()
        print("sessionid = " + self.sessionid)
        logging.info("sessionid = " + self.sessionid)
        print("rand = " + self.rand.decode('utf-8'))
        logging.info("rand = " + self.rand.decode('utf-8'))

    """
    获取随机码，用于登录
    """
    def get_sessionid_rand(self):
        response = definition.session.get(url=self.url(randomPath), headers={
                                    'X-Requested-With': 'XMLHttpRequest'})
        random = response.content
        sid = response.headers['Set-Cookie']
        result = re.search('zentaosid=(.*?);', sid)

        return result.group(1), random

    @property
    def get_login_data(self):
        return {"account": definition.account,
                "password": definition.password,
                "passwordStrength": 1,
                "referer": "/biz/",
                "verifyRand": self.rand,
                "keepLogin": 1}

    def url(self, path):
        return definition.baseurl + path

    """
    登录
    """
    def login(self):
        response = definition.session.post(url=self.url(loginPath), headers={
                                     'X-Requested-With': 'XMLHttpRequest'}, data=self.get_login_data)
        logging.info('login response:' + response.text)
        logging.info('login data:' + str(self.get_login_data))
        logging.info('login path:' + loginPath)

    """获取团队成员"""

    def get_project_path(self):
        project_list_page = definition.session.post(url=self.url(
            projectListPath), headers=definition.contentHeader)
        project_list_html = etree.HTML(project_list_page.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))
        project_result = project_list_html.xpath(
            '//td[@title="'+definition.project+'"]/div/a/@href')
        project_path = project_result[0]  # 将index替换成team，获取团队页面
        return self.url(project_path)

    def latest_execution_path(self, list_path):
        now_time = datetime.datetime.now()
        execution_list_page = definition.session.post(
            url=list_path, headers=definition.contentHeader)
        execution_list_html = etree.HTML(execution_list_page.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))
        execution_rows = execution_list_html.xpath(
            '//tbody[@id="executionTableList"]/tr')
        # 倒序
        execution_rows.reverse()
        #遍历所有迭代，选取第一个当天所在的迭代
        for execution_row in execution_rows:
            execution_cols = execution_row.xpath('./td')
            start_time = datetime.datetime.strptime(execution_cols[4].text + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.strptime(execution_cols[5].text + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            if start_time > now_time or now_time > end_time:
                continue
            execution_path = execution_cols[0].xpath('./a/@href')[0]
            execution_name = execution_cols[0].xpath('./a/text()')[0]
            if (len(definition.product) > 0) and (definition.product not in execution_name):
                continue

            return self.url(execution_path)

def yesterday_is_holiday():
    kq = Kq()
    return kq.is_holiday(definition.yesterday)

if __name__ == '__main__':
    if yesterday_is_holiday():
        sys.exit(0)

    zentaoApi = Zentao()
    # 登录
    zentaoApi.login()
    print("login zentao success")
    logging.info("login zentao success")
    # 找到项目
    projectListPath = zentaoApi.get_project_path()
    executionListPath = projectListPath.replace('index', 'execution-all') # 将index替换execution-all，获取所有的execution列表
    print('executionListPath: ' + executionListPath)
    logging.info('executionListPath: ' + executionListPath)

    # 找迭代
    latestExecutionPath = zentaoApi.latest_execution_path(executionListPath)
    print('latestExecutionPath: ' + latestExecutionPath)
    logging.info('latestExecutionPath: ' + latestExecutionPath)
    data = execution_data(latestExecutionPath)

    # 加载迭代数据
    data.load_data()
    print('loadData complete')
    logging.info('loadData complete')
    # 生成报告
    reportGenerator = report_generator(data)
    requestData = reportGenerator.generate()

    print('request data:' + json.dumps(requestData, ensure_ascii=False))
    rsp = requests.post(url=definition.boturl, json=requestData, headers={'Content-Type': 'application/json'})
    
    