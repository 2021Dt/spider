'''
@Project ：TaskQueue.py 
@File    ：config.py.py
@Author  ：dp
@Date    ：2024/9/13 11:27 
'''
import configparser
from loguru import logger

# 读取 config.ini 配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# 加载 MySQL 配置
MYSQL_IP = config.get('mysql', 'ip', fallback='localhost')
MYSQL_PORT = config.getint('mysql', 'port', fallback=3306)
MYSQL_DB = config.get('mysql', 'db', fallback='test_db')
MYSQL_USER_NAME = config.get('mysql', 'user_name', fallback='root')
MYSQL_USER_PASS = config.get('mysql', 'user_pass', fallback='password')

# 加载日志配置
LOG_LEVEL = config.get('logging', 'level', fallback='DEBUG')

def init_logging():
    logger.remove()
    logger.add(
        "app.log",
        level=LOG_LEVEL,
        rotation="1 week",
        retention="1 month",
        compression="zip"
    )
    logger.info("日志系统初始化完成")

# 初始化配置
def init():
    init_logging()
    logger.info("配置初始化完成")


