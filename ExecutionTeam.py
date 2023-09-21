import definition
from lxml import etree
import logging
class TeamMate:
    name=""
    useableDay = 0 # 可用工日
    useableHour = 0 # 可用工时
    useableTotal = 0 # 总计
    def __init__(self, name, day, hour, total):
        self.name = name
        self.useableDay = int(day[:-1])
        self.useableHour = float(hour[:-2])
        self.useableTotal = float(total[:-2])
        definition.logging_print('name:useableDay:usableTotal '+ name + ":"+ day +":"+hour+":" + total)

class ExecutionTeam:
    teamMates = []

    def loadTeam(self, path):
        rsp = definition.session.post(
            url=path, headers=definition.contentHeader)
        definition.logging_print('executionTeam page: \n' + rsp.content.decode('utf-8'))
        html = etree.HTML(rsp.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))

        rows = html.xpath('//tbody/tr')
        for singleRow in rows:
            cells =  singleRow.xpath('./td')
            name = cells[0].xpath('./text()')[0]
            nameInLink = cells[0].xpath('./a/text()')
            # 考虑name有两种方式，如果存在Link里面就用里面的
            if len(nameInLink) > 0:
                name = nameInLink[0]
            # 禅道的name有问题，可能会带空格和换行符，做一下兼容
            name = name.strip('\n').strip()
            day = cells[3].xpath('./text()')[0]
            hour = cells[4].xpath('./text()')[0]
            total = cells[5].xpath('./text()')[0]
            self.teamMates.append(TeamMate(name, day, hour, total))
