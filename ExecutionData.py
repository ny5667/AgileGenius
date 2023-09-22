from ExecutionLogData import ExecutionLogData
from ExecutionTeam import ExecutionTeam
import logging
from lxml import etree
import definition

class ExecutionProperty:
    name = ""
    start = ""
    end = ""

    def load_property(self, path):
        rsp = definition.session.post(
            url=path, headers=definition.contentHeader)
        html = etree.HTML(rsp.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))
        print('=====exectuion Property=====')
        self.name = html.xpath('//h2[@class="detail-title"]/text()')[1]
        print('name:'+ self.name)
        statistic_rows = html.xpath('//table[@class="table table-data data-stats"]/tbody/tr')
        self.start = statistic_rows[2].xpath('./td[1]/text()')[0]
        print('start:'+ self.start)
        self.end = statistic_rows[3].xpath('./td[1]/text()')[0]
        print('end:'+ self.end)
        print('============================')

class ExecutionData:
    log = ExecutionLogData()
    team = ExecutionTeam()
    property = ExecutionProperty()

    def __init__(self, path):
        self.path = path
        
    def load_data(self):
        # 属性
        self.property.load_property(self.path)

        # 团队
        team_path = self.path.replace('view', 'team')
        self.team.load_team(team_path)

        # 日志
        log_path = self.path.replace('view', 'effortcalendar')
        self.log.load_log(log_path)
