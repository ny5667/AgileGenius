import logging
import re
import definition
import requests
import json
import sys
from KQ import KQ
from ExecutionData import ExecutionData
from lxml import etree
from DailyReportGenerator import ReportGenerator
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
        response = definition.session.get(url=self.Url(randomPath), headers={
                                    'X-Requested-With': 'XMLHttpRequest'})
        random = response.content
        sid = response.headers['Set-Cookie']
        result = re.search('zentaosid=(.*?);', sid)

        return result.group(1), random

    @property
    def get_loginData(self):
        return {"account": definition.account,
                "password": definition.password,
                "passwordStrength": 1,
                "referer": "/biz/",
                "verifyRand": self.rand,
                "keepLogin": 1}

    def Url(self, path):
        return definition.baseurl + path

    """
    登录
    """
    def login(self):
        response = definition.session.post(url=self.Url(loginPath), headers={
                                     'X-Requested-With': 'XMLHttpRequest'}, data=self.get_loginData)
        logging.info('login response:' + response.text)

    """获取团队成员"""

    def getProjectPath(self):
        projectListPage = definition.session.post(url=self.Url(
            projectListPath), headers=definition.contentHeader)
        projectListHTML = etree.HTML(projectListPage.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))
        projectResult = projectListHTML.xpath(
            '//td[@title="'+definition.project+'"]/div/a/@href')
        projectPath = projectResult[0]  # 将index替换成team，获取团队页面
        return self.Url(projectPath)

    def latestExecutionPath(self, listPath):
        nowTime = datetime.datetime.now()
        executionListPage = definition.session.post(
            url=listPath, headers=definition.contentHeader)
        executionListHTML = etree.HTML(executionListPage.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))
        executionRows = executionListHTML.xpath(
            '//tbody[@id="executionTableList"]/tr')
        # 倒序
        executionRows.reverse()
        #遍历所有迭代，选取第一个当天所在的迭代
        for executionRow in executionRows:
            executionCols = executionRow.xpath('./td')
            startTime = datetime.datetime.strptime(executionCols[4].text + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            endTime = datetime.datetime.strptime(executionCols[5].text + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            if startTime > nowTime or nowTime > endTime:
                continue
            executionPath = executionCols[0].xpath('./a/@href')[0]
            executionName = executionCols[0].xpath('./a/text()')[0]
            if (len(definition.product) > 0) and (definition.product not in executionName):
                continue

            return self.Url(executionPath)

def YesterdayIsHoliday():
    kq = KQ()
    return kq.isHoliday(definition.yesterday)

if __name__ == '__main__':
    if YesterdayIsHoliday():
        sys.exit(0)

    zentaoApi = Zentao()
    # 登录
    zentaoApi.login()
    print("login zentao success")
    logging.info("login zentao success")
    # 找到项目
    projectListPath = zentaoApi.getProjectPath()
    executionListPath = projectListPath.replace('index', 'execution-all') # 将index替换execution-all，获取所有的execution列表
    print('executionListPath: ' + executionListPath)
    logging.info('executionListPath: ' + executionListPath)

    # 找迭代
    latestExecutionPath = zentaoApi.latestExecutionPath(executionListPath)
    print('latestExecutionPath: ' + latestExecutionPath)
    logging.info('latestExecutionPath: ' + latestExecutionPath)
    data = ExecutionData(latestExecutionPath)

    # 加载迭代数据
    data.loadData()
    print('loadData complete')
    logging.info('loadData complete')
    # 生成报告
    reportGenerator = ReportGenerator(data)
    requestData = reportGenerator.generate('RequestContent.json')

    print('request data:' + json.dumps(requestData, ensure_ascii=False))
    rsp = requests.post(url=definition.boturl, json=requestData, headers={'Content-Type': 'application/json'})
    
    