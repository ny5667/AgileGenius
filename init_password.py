import keyring
import configparser

# 创建 ConfigParser 对象
config = configparser.ConfigParser()

# 读取配置文件
config.read('config.ini', encoding='utf-8')

# 存储密码
service_name = "my_app"
username = config.get('Settings', 'account')
password = config.get('Settings', 'password')

keyring.set_password(service_name, username, password)
print("Password stored successfully.")

# 检索密码
retrieved_password = keyring.get_password(service_name, username)
if retrieved_password:
    print("Retrieved password:", retrieved_password)
else:
    print("Password not found.")