from asyncio.windows_events import NULL
import datetime
from doctest import FAIL_FAST
import string
import definition
import logging
import os
import sys

class ReportGenerator:
    logsByPerson = {}
    logsByDay = {}
    validTeamMates = []
    def __init__(self, data):
        # 按人归类
        for log in data.log.logs:
            personLog = self.logsByPerson.get(log.person)
            if personLog == None:
                self.logsByPerson[log.person] = []
            self.logsByPerson[log.person].append(log)
        # 按天归类
        for log in data.log.logs:
            dailyLog = self.logsByDay.get(log.time)
            if dailyLog == None:
                self.logsByDay[log.time] = []
            self.logsByDay[log.time].append(log)

        # 有效人
        for teamMate in data.team.teamMates:
            if teamMate.useableTotal > 0:
                self.validTeamMates.append(teamMate)

    def forgetRecord(self, mentionList):
        if len(sys.argv) <= 1 or sys.argv.count("r") <= 0 :
            return

        if definition.forgetRecordPath == "":
            return
        if os.path.exists (definition.forgetRecordPath) == False:
            os.makedirs(definition.forgetRecordPath)

        for person in mentionList:
            path = definition.forgetRecordPath + '\\' + person + '_' + mentionList[person]
            count = 0
            # 读文件
            try:
                with open(path, 'r') as recordFile:
                    recordData = recordFile.read()
                    if recordData != "":
                        lines = recordData.split('\n')
                        count = int(lines[1])
            except Exception as e:
                print("文件" + path + "不存在")
            
            # 写文件
            with open(path, 'w') as recordFile:
                today = datetime.datetime.now().strftime('%Y-%m-%d')
                recordFile.write(today + "\n" + str(count + 1))

    def generate(self, file):
        yesterdayLogs = self.logsByDay.get(definition.yesterday)
        # 本迭代统计工作量
        executionRecorded = {}
        for person in self.logsByPerson.keys():
            personSpend =  executionRecorded.get(person)
            if personSpend == None:
                personSpend = 0
            for log in self.logsByPerson[person]:
                personSpend += log.spend
            executionRecorded[person] = personSpend
        
        # 昨日统计工作量
        recorded = {}
        for log in yesterdayLogs:
            personTimeSpend = recorded.get(log.person)
            if personTimeSpend == None:
                personTimeSpend = 0
            personTimeSpend += log.spend
            recorded[log.person] = personTimeSpend

        # 未填工作量名单
        mentionList = {}
        for person in self.validTeamMates:
            if recorded.get(person.name) is None:
                name = person.name.strip(string.digits)
                personid = definition.name_ids.get(name)
                if personid is None:
                    personid = name
                mentionList[name] = personid

        
        # 记录遗忘次数
        self.forgetRecord(mentionList)

        # 生成md
        text= "# 敏捷不止催催\n## 本迭代工作量统计:"
        for person in executionRecorded.keys():
            text += "\n" + person + '共消耗<font color="info">' + "{:.1f}".format(executionRecorded[person]) + "</font>小时"

        text += '\n## ' + definition.yesterday +" 工作量录入情况"
        for person in recorded.keys():
            text += "\n" + person + '录入<font color="info">' + "{:.1f}".format(recorded[person]) + "</font>小时"

        if len(mentionList) <= 0:
            text += ";\n**撒花*★,°*:.☆(￣▽￣)/$:*.°★* 。**"
        else:
            text += ";\n请以下未填工时的人及时补填:\n>"
            for person in mentionList:
                text += '<@' + mentionList[person] + '>'

        requestData = {
            "msgtype" : "markdown", 
            "markdown":{
                "content": text
            }
        }

        return requestData