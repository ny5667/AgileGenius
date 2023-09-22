import definition
from lxml import etree
import constants

class TeamMate:
    name=""
    useable_day = 0 # 可用工日
    useable_hour = 0 # 可用工时
    useable_total = 0 # 总计
    def __init__(self, name, day, hour, total):
        self.name = name
        self.useable_day = int(day[:-1])
        self.useable_hour = float(hour[:-2])
        self.useable_total = float(total[:-2])
        definition.logging_print('name:useableDay:usableTotal '+ name + ":"+ day +":"+hour+":" + total)

class ExecutionTeam:
    team_mates = []

    def load_team(self, path):
        rsp = definition.session.post(
            url=path, headers=definition.contentHeader)
        definition.logging_print('executionTeam page: \n' + rsp.content.decode('utf-8'))
        html = etree.HTML(rsp.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))

        rows = html.xpath('//tbody/tr')
        for single_row in rows:
            cells =  single_row.xpath('./td')
            name = cells[0].xpath(constants.TEXT_XPATH)[0]
            name_in_link = cells[0].xpath('./a/text()')
            # 考虑name有两种方式，如果存在Link里面就用里面的
            if len(name_in_link) > 0:
                name = name_in_link[0]
            # 禅道的name有问题，可能会带空格和换行符，做一下兼容
            name = name.strip('\n').strip()
            day = cells[3].xpath(constants.TEXT_XPATH)[0]
            hour = cells[4].xpath(constants.TEXT_XPATH)[0]
            total = cells[5].xpath(constants.TEXT_XPATH)[0]
            self.team_mates.append(TeamMate(name, day, hour, total))
