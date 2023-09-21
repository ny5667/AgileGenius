import sys
import requests
import datetime
import logging
import configparser
global account
global password
global contentHeader
global session
global project
global boturl
global name_ids
global forgetRecordPath
global yesterday
global oaAccount
global oaPassword
global product

# 创建 ConfigParser 对象
config = configparser.ConfigParser()

# 读取配置文件
config.read('config.ini', encoding='utf-8')

# 这部分根据自己情况修改
account = config.get('Settings', 'account')
password = config.get('Settings', 'password')
oaAccount = account
oaPassword = password
project = config.get('Settings', 'project')
product = config.get('Settings', 'product')
boturl = config.get('Settings', 'boturl')
name_ids = {'叶蓬': '20181110'} # 项目中的人的名字：工号
forgetRecordPath = '..\\奶茶计数器\\data'# 遗忘次数保存文件夹地址(每个人以人名_id存成一个文件，内容为遗忘次数)

# 这部分保持固定
baseurl = "http://project.rd.supcon.com"
contentPath = "/biz/index-index.html"
contentHeader = {"Referer": baseurl + contentPath}
session = requests.session()
yesterday = (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
logging.basicConfig(filename='./log/log.txt', level=logging.INFO, format='%(levelname)s-%(asctime)s-%(filename)s(%(lineno)s): %(message)s')
def logging_print(message):
    logging.debug(message)
    print(message)