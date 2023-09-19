import logging
import string
import definition
from lxml import etree

class ExecutionLog:
    def parse(self, html):
        cols = html.xpath('./td')
        self.time = cols[1].xpath('./text()')[0]
        self.person = cols[2].xpath('./text()')[0]
        self.context = cols[3].xpath('./a/text()')[0]
        spend = cols[4].xpath('./text()')[0]
        self.spend = float(spend)
        print('time:name:context:spend='+  self.time + ":"+self.person + ":"+ self.context +":"+spend)
        logging.info('time:name:context:spend='+  self.time + ":"+self.person + ":"+ self.context +":"+spend)

class ExecutionLogData:
    logs = []

    def loadLog(self,path):
        # 拼接Url
        logDataPath = path.replace("effortcalendar", "effort")[:-5]+'-all--date_desc-0-1000-0'+'.html'
        logListPage = definition.session.post(
            url=logDataPath, headers=definition.contentHeader)
        logging.info('logPage data:\n'+ logListPage.content.decode('utf-8'))
        logListHTML = etree.HTML(logListPage.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))
        # 从开始时间解析
        logElements = logListHTML.xpath('//table[@id="effortList"]/tbody/tr')
        
        for logElement in logElements:
            log = ExecutionLog()
            log.parse(logElement)
            if log.spend == 0:
                continue
            self.logs.append(log)

