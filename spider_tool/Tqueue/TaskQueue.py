'''
@Project ：TaskQueue.py
@File    ：TaskQueue.py
@Author  ：dp
@Date    ：2024/8/20 18:01
'''

import time
from loguru import logger
import redis
import sys
import os
import configparser
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import psutil

def get_config():
    config_path = 'config.ini'
    if not os.path.exists(config_path):
        logger.error(f"配置文件 '{config_path}' 不存在!")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')

    redis_host = config.get('DEFAULT', 'REDIS_HOST', fallback='localhost')
    redis_port = config.getint('DEFAULT', 'REDIS_PORT', fallback=6379)
    redis_db = config.getint('DEFAULT', 'REDIS_DB', fallback=0)
    level = config.get('DEFAULT', 'LEVEL', fallback='normal')
    log_level = config.get('DEFAULT', 'LOG_LEVEL', fallback='warning').upper()
    max_retries = config.getint('DEFAULT', 'MAX_RETRIES', fallback=3)
    max_ttl = config.getint('DEFAULT', 'MAX_TTL', fallback=60 * 60 * 24 * 30)  # 默认30天

    scheduling_strategy = config.get('SCHEDULING', 'SCHEDULING_STRATEGY', fallback='interval')
    interval_seconds = config.getint('SCHEDULING', 'INTERVAL_SECONDS', fallback=60)
    cron_expression = config.get('DEFAULT', 'CRON_EXPRESSION', fallback='1 * * * *')

    if log_level not in TaskQueue.ALLOWED_LOG_LEVELS:
        logger.warning(f"无效的日志级别 '{log_level}'，使用默认级别 'WARNING'")
        log_level = 'WARNING'

    return {
        'REDIS_HOST': redis_host,
        'REDIS_PORT': redis_port,
        'REDIS_DB': redis_db,
        'LEVEL': level,
        'LOG_LEVEL': log_level,
        'MAX_RETRIES': max_retries,
        'MAX_TTL': max_ttl,
        'SCHEDULING_STRATEGY': scheduling_strategy,
        'INTERVAL_SECONDS': interval_seconds,
        'CRON_EXPRESSION': cron_expression
    }


class TaskQueue:
    ALLOWED_LEVELS = ["normal", "fail", "urgent"]
    ALLOWED_LOG_LEVELS = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]

    def __init__(self, task_name: str, level: str = 'normal', log_level: str = 'warning', config=None):
        config = config or get_config()

        self.task_name = task_name
        self.level = level if level in self.ALLOWED_LEVELS else config['LEVEL']
        self.log_level = log_level.upper() if log_level.upper() in self.ALLOWED_LOG_LEVELS else config['LOG_LEVEL']
        self.max_retries = config['MAX_RETRIES']
        self.max_ttl = config['MAX_TTL']
        self.scheduling_strategy = config.get('SCHEDULING_STRATEGY', None)
        self.interval_seconds = config.get('INTERVAL_SECONDS', 60)
        self.cron_expression = config.get('CRON_EXPRESSION', '0')
        self.scheduler = None

        # 初始化 Redis 连接
        self.conn = redis.Redis(
            host=config['REDIS_HOST'],
            port=config['REDIS_PORT'],
            db=config['REDIS_DB'],
            charset="utf-8",
            decode_responses=True
        )

        logger.remove()
        logger.add(sys.stderr, level=self.log_level)

        # 添加队列名称到 Redis 集合
        if self.task_name:
            if self.conn.sadd("spider_topic_list", self.task_name):
                logger.info(f"新增队列名: {self.task_name}")
            else:
                logger.warning(f"队列名 '{self.task_name}' 已存在。")

    def add_task(self, task: dict = None, level: str = None, is_distinct: bool = True):
        """
        增加单条任务
        :param task: 任务字典
        :param level: 队列类型, 默认 normal
        :param is_distinct: 是否去重插入
        """
        if task is None:
            logger.error("未指定任务字典!!!")
            return

        level = level or self.level

        task_backup = f"spider_task_backup:{self.task_name}"
        task_title = f"spider_task:{self.task_name}:{level}"
        task_data = json.dumps(task, ensure_ascii=False)

        try:
            if is_distinct:
                added = self.conn.sadd(task_backup, task_data)
                if added:
                    self.conn.lpush(task_title, task_data)
                    logger.success(f"添加任务成功: {task}")
                else:
                    logger.warning(f"任务已存在: {task}")
            else:
                self.conn.lpush(task_title, task_data)
                logger.success(f"不去重·添加任务成功: {task}")

            # 设置过期时间
            ttl = self.conn.ttl(task_backup)
            if ttl == -1:
                self.conn.expire(task_backup, self.max_ttl)  # 使用配置中的最大 TTL

        except redis.RedisError as e:
            logger.error(f"操作 Redis 时发生异常: {e}")

    def add_tasks(self, tasks: list = None, level: str = None, is_distinct: bool = True):
        """
        批量增加任务
        :param tasks: 任务字典列表
        :param level: 队列类型, 默认 normal
        :param is_distinct: 是否去重插入
        """
        if not tasks or not isinstance(tasks, list):
            logger.error("任务列表无效或未指定任务列表!!!")
            return

        level = level or self.level
        task_backup = f"spider_task_backup:{self.task_name}"
        task_title = f"spider_task:{self.task_name}:{level}"

        # 使用 pipeline 来减少与 Redis 的交互次数
        pipe = self.conn.pipeline()

        try:
            # 批量添加任务到 Redis 集合中
            for task in tasks:
                if not task.get('retry'):
                    task['retry'] = 0
                task_data = json.dumps(task, ensure_ascii=False)
                pipe.sadd(task_backup, task_data)

            distinct_results = pipe.execute()

            # 使用 pipeline 来处理队列操作
            pipe = self.conn.pipeline()

            for i, task in enumerate(tasks):
                task_data = json.dumps(task, ensure_ascii=False)
                if is_distinct and not distinct_results[i]:
                    logger.warning(f"任务已存在: {task}")
                else:
                    pipe.lpush(task_title, task_data)
                    logger.success(f"{'不去重·' if not is_distinct else ''}任务成功添加: {task}")

            pipe.execute()

            # 设置过期时间
            ttl = self.conn.ttl(task_backup)
            if ttl == -1:
                self.conn.expire(task_backup, self.max_ttl)  # 使用配置中的最大 TTL

        except redis.RedisError as e:
            logger.error(f"操作 Redis 时发生异常: {e}")

    def get_task(self, level: str = None, fifo: bool = True):
        """
        获取单条任务
        :param level: 队列紧急程度
        :param fifo: 是否按先入先出（FIFO）模式获取任务
        :return: 任务字典或 None
        """
        level = level or self.level
        task_title = f"spider_task:{self.task_name}:{level}"

        try:
            task_data = self.conn.lpop(task_title) if fifo else self.conn.rpop(task_title)

            if task_data:
                task = json.loads(task_data)
                logger.info(f"获取任务成功: {task}")
                return task
            else:
                logger.info("没有更多任务可获取。")
                return None

        except redis.RedisError as e:
            logger.error(f"操作 Redis 时发生异常: {e}")
            return None

    def get_tasks(self, level: str = None, num: int = 0, fifo: bool = True):
        """
        批量获取任务
        :param level: 队列紧急程度
        :param num: 获取任务数量, 默认全部获取
        :param fifo: 是否按先入先出（FIFO）模式获取任务
        :return: 任务字典列表
        """
        level = level or self.level
        task_title = f"spider_task:{self.task_name}:{level}"

        # 设置获取数量的默认值
        if num <= 0:
            num = self.conn.llen(task_title)

        try:
            tasks = []
            for _ in range(num):
                task_data = self.conn.lpop(task_title) if fifo else self.conn.rpop(task_title)
                if task_data:
                    tasks.append(json.loads(task_data))
                else:
                    break

            if tasks:
                logger.info(f"获取 {len(tasks)} 个任务成功。")
            else:
                logger.info("没有更多任务可获取。")

            return tasks

        except redis.RedisError as e:
            logger.error(f"操作 Redis 时发生异常: {e}")
            return []

    def retry_task(self, task: dict = None, is_distinct: bool = True):
        """
        单个任务重试, 重试次数达到最大重试次数, 插入失败队列
        :param task: 失败任务
        :param is_distinct: 是否去重插入
        """
        if task is None:
            logger.error("未指定任务字典!!!")
            return

        task_backup = f"spider_task_backup:{self.task_name}"
        task_title = f"spider_task:{self.task_name}:{self.level}"
        fail_task_title = f"spider_task:{self.task_name}:fail"

        task_data = json.dumps(task, ensure_ascii=False)

        try:
            retry_count = task.get('retry', 0)
            if retry_count < self.max_retries:
                task['retry'] = retry_count + 1
                updated_task_data = json.dumps(task, ensure_ascii=False)

                if is_distinct:
                    added = self.conn.sadd(task_backup, updated_task_data)
                    if added:
                        self.conn.lpush(task_title, updated_task_data)
                        logger.success(f"重试任务成功: {task}")
                    else:
                        logger.warning(f"重试任务已存在: {task}")
                else:
                    self.conn.lpush(task_title, updated_task_data)
                    logger.success(f"不去重·重试任务成功: {task}")

            else:
                self.conn.lpush(fail_task_title, task_data)
                logger.error(f"任务重试次数已达上限, 已插入失败队列: {task}")

        except redis.RedisError as e:
            logger.error(f"操作 Redis 时发生异常: {e}")

    def monitor_tasks(self):
        """
        任务预警
        :return:
        """
        task_counts = {
            'urgent': self.conn.llen(f"spider_task:{self.task_name}:urgent"),
            'normal': self.conn.llen(f"spider_task:{self.task_name}:normal"),
            'fail': self.conn.llen(f"spider_task:{self.task_name}:fail")
        }
        logger.info(f"任务统计: {task_counts}")

        # 监控和报警逻辑
        if task_counts['fail'] > 100:
            logger.warning("失败队列中的任务数量超过阈值")

    def monitor_system_resources(self):
        """
        内存管理
        :return:
        """
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        logger.info(f"CPU 使用率: {cpu_usage}%, 内存使用率: {memory_usage}%")

    def setup_scheduler(self, scheduling_strategy=None, interval_seconds=None, cron_expression=None):
        """
        设置调度器，允许用户自定义调度策略和参数。
        :param scheduling_strategy: 调度策略 ('interval' 或 'cron')，优先级高于类属性配置
        :param interval_seconds: 间隔时间，单位秒，仅在使用 'interval' 策略时有效
        :param cron_expression: Cron 表达式，仅在使用 'cron' 策略时有效
        """
        # 使用用户传递的参数，如果没有则使用类属性中的配置
        scheduling_strategy = scheduling_strategy or self.scheduling_strategy
        interval_seconds = interval_seconds or self.interval_seconds
        cron_expression = cron_expression or self.cron_expression

        if not scheduling_strategy:
            logger.info('当前没有调度器配置')
            return

        self.scheduler = BackgroundScheduler()
        if scheduling_strategy == 'interval':
            if interval_seconds is None:
                interval_seconds = self.interval_seconds
            self.scheduler.add_job(self.process_tasks, IntervalTrigger(seconds=interval_seconds))
        elif scheduling_strategy == 'cron':
            if cron_expression is None:
                cron_expression = self.cron_expression
            self.scheduler.add_job(self.process_tasks, CronTrigger.from_crontab(cron_expression))
        else:
            logger.warning(f"未知的调度策略 '{scheduling_strategy}'，使用默认策略 'interval'")
            self.scheduler.add_job(self.process_tasks, IntervalTrigger(seconds=self.interval_seconds))

        self.scheduler.start()

    def process_tasks(self, num: int = 1):
        """
        默认调度方法,这里才是具体实现
        :param num: 默认拿去一条任务
        :return:
        """
        logger.info('调用默认方法')
        return self.get_tasks(num=num)

    def run(self):
        """调度器启动"""
        self.setup_scheduler()
        try:
            while True:
                time.sleep(1)  # 保持主线程运行，调度器才能工作
        except KeyboardInterrupt:
            if self.scheduler:
                self.scheduler.shutdown()
            logger.info("程序已停止")

    def __del__(self):
        self.conn.close()


# if __name__ == '__main__':
#     queue = TaskQueue(task_name='my_queue', level='urgent', log_level='info')
#     queue.monitor_tasks()
