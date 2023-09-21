from ExecutionLogData import ExecutionLogData
from ExecutionTeam import ExecutionTeam
import logging
from lxml import etree
import definition

class ExecutionProperty:
    name = ""
    start = ""
    end = ""

    def loadProperty(self, path):
        rsp = definition.session.post(
            url=path, headers=definition.contentHeader)
        html = etree.HTML(rsp.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))
        print('=====exectuion Property=====')
        self.name = html.xpath('//h2[@class="detail-title"]/text()')[1]
        print('name:'+ self.name)
        statisticRows = html.xpath('//table[@class="table table-data data-stats"]/tbody/tr')
        self.start = statisticRows[2].xpath('./td[1]/text()')[0]
        print('start:'+ self.start)
        self.end = statisticRows[3].xpath('./td[1]/text()')[0]
        print('end:'+ self.end)
        print('============================')

class ExecutionData:
    log = ExecutionLogData()
    team = ExecutionTeam()
    property = ExecutionProperty()

    def __init__(self, path):
        self.path = path
        
    def loadData(self):
        # 属性
        self.property.loadProperty(self.path)

        # 团队
        teamPath = self.path.replace('view', 'team')
        self.team.loadTeam(teamPath)

        # 日志
        logPath = self.path.replace('view', 'effortcalendar')
        self.log.loadLog(logPath)
