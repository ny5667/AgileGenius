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

    def load_log(self,path):
        # 拼接Url
        log_data_path = path.replace("effortcalendar", "effort")[:-5]+'-all--date_desc-0-1000-0'+'.html'
        log_list_page = definition.session.post(
            url=log_data_path, headers=definition.contentHeader)
        logging.info('logPage data:\n'+ log_list_page.content.decode('utf-8'))
        log_list_html = etree.HTML(log_list_page.content.decode(
            'utf-8'), etree.HTMLParser(encoding='utf-8'))
        # 从开始时间解析
        log_elements = log_list_html.xpath('//table[@id="effortList"]/tbody/tr')
        
        for log_element in log_elements:
            log = ExecutionLog()
            log.parse(log_element)
            if log.spend == 0:
                continue
            self.logs.append(log)

