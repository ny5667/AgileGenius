from asyncio.windows_events import NULL
import datetime
from doctest import FAIL_FAST
import string
import definition
import logging
import os
import sys

class report_generator:
    logs_by_person = {}
    logs_by_day = {}
    valid_team_mates = []
    def __init__(self, data):
        # 按人归类
        for log in data.log.logs:
            person_log = self.logs_by_person.get(log.person)
            if person_log == None:
                self.logs_by_person[log.person] = []
            self.logs_by_person[log.person].append(log)
        # 按天归类
        for log in data.log.logs:
            daily_log = self.logs_by_day.get(log.time)
            if daily_log == None:
                self.logs_by_day[log.time] = []
            self.logs_by_day[log.time].append(log)

        # 有效人
        for team_mate in data.team.team_mates:
            if team_mate.useable_total > 0:
                self.valid_team_mates.append(team_mate)

    def forget_record(self, mention_list):
        if len(sys.argv) <= 1 or sys.argv.count("r") <= 0 :
            return

        if definition.forgetRecordPath == "":
            return
        if os.path.exists (definition.forgetRecordPath) == False:
            os.makedirs(definition.forgetRecordPath)

        for person in mention_list:
            path = definition.forgetRecordPath + '\\' + person + '_' + mention_list[person]
            count = 0
            # 读文件
            try:
                with open(path, 'r') as record_file:
                    record_data = record_file.read()
                    if record_data != "":
                        lines = record_data.split('\n')
                        count = int(lines[1])
            except Exception:
                print("文件" + path + "不存在")
            
            # 写文件
            with open(path, 'w') as record_file:
                today = datetime.datetime.now().strftime('%Y-%m-%d')
                record_file.write(today + "\n" + str(count + 1))

    def generate(self):
        yesterday_logs = self.logs_by_day.get(definition.yesterday)
        # 本迭代统计工作量
        execution_recorded = {}
        for person in self.logs_by_person.keys():
            person_spend =  execution_recorded.get(person)
            if person_spend == None:
                person_spend = 0
            for log in self.logs_by_person[person]:
                person_spend += log.spend
            execution_recorded[person] = person_spend
        
        # 昨日统计工作量
        recorded = {}
        for log in yesterday_logs:
            person_time_spend = recorded.get(log.person)
            if person_time_spend == None:
                person_time_spend = 0
            person_time_spend += log.spend
            recorded[log.person] = person_time_spend

        # 未填工作量名单
        mention_list = {}
        for person in self.valid_team_mates:
            if recorded.get(person.name) is None:
                name = person.name.strip(string.digits)
                personid = definition.name_ids.get(name)
                if personid is None:
                    personid = name
                mention_list[name] = personid

        
        # 记录遗忘次数
        self.forget_record(mention_list)

        # 生成md
        text= "# 敏捷不止催催\n## 本迭代工作量统计:"
        for person in execution_recorded.keys():
            text += "\n" + person + '共消耗<font color="info">' + "{:.1f}".format(execution_recorded[person]) + "</font>小时"

        text += '\n## ' + definition.yesterday +" 工作量录入情况"
        for person in recorded.keys():
            text += "\n" + person + '录入<font color="info">' + "{:.1f}".format(recorded[person]) + "</font>小时"

        if len(mention_list) <= 0:
            text += ";\n**撒花*★,°*:.☆(￣▽￣)/$:*.°★* 。**"
        else:
            text += ";\n请以下未填工时的人及时补填:\n>"
            for person in mention_list:
                text += '<@' + mention_list[person] + '>'

        request_data = {
            "msgtype" : "markdown", 
            "markdown":{
                "content": text
            }
        }

        return request_data