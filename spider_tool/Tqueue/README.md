# TaskQueue 使用说明

`TaskQueue` 是一个用于管理任务队列的 Python 类，利用 Redis 作为任务存储后端。它支持添加、获取、重试任务，并能根据配置文件的设置控制最大重试次数和最大生存时间。

## 配置文件

配置文件 `config.ini` 包含以下设置：

```ini
[DEFAULT]
REDIS_HOST = localhost
REDIS_PORT = 6379
REDIS_DB = 0
LEVEL = normal
LOG_LEVEL = warning
MAX_RETRIES = 3
MAX_TTL = 2592000  # 默认 30 天（以秒为单位）

# 日志配置
[LOGGING]
LOG_LEVEL = warning

#调度配置
[SCHEDULING]
SCHEDULING_STRATEGY = interval  ; 或 cron
INTERVAL_SECONDS = 60  ; 间隔调度的时间间隔（秒）
CRON_EXPRESSION = 0  ; Cron 表达式（仅在调度策略为 cron 时有效）
```
* **REDIS_HOST**: Redis 服务器的主机地址，默认为 `localhost`。      
* **REDIS_PORT**: Redis 服务器的端口，默认为 6379。    
* **REDIS_DB**: Redis 数据库的编号，默认为 0。    
* **LEVEL**: 默认队列级别，选择范围包括 `normal`、`fail` 和 `urgent`。    
* **LOG_LEVEL**: 日志级别，支持 `TRACE`、`DEBUG`、`INFO`、`SUCCESS`、`WARNING`、`ERROR` 和 `CRITICAL`，默认为 `WARNING`。    
* **MAX_RETRIES**: 单个任务的最大重试次数，默认为 3。    
* **MAX_TTL**: 任务备份的最大生存时间（秒），默认为 2592000（30 天）。    
* **SCHEDULING_STRATEGY**:调度策略（`interval` 或 `cron`）。如果未指定调度策略，则不创建调度器。
* **INTERVAL_SECONDS**: 间隔调度的时间间隔（秒）。仅在 `SCHEDULING_STRATEGY` 为 `interval` 时有效。
* **CRON_EXPRESSION**: `Cron` 表达式（仅在 `SCHEDULING_STRATEGY` 为 `cron` 时有效）。

> `interval` 调度策略根据固定的时间间隔执行任务。这意味着任务将在指定的时间间隔后重复执行。例如，如果你将间隔设置为 1 秒，那么任务将在每秒钟执行一次。    
> `cron` 调度策略基于 `cron` 表达式定义任务的执行时间。`Cron` 表达式允许你指定复杂的时间安排，例如每天的某个特定时间、每周的某天、每月的某天等。

## 重写调度策略
初始调度策略并不能满足大部分的开发需求，支持用户自定义设计调度策略

## 队列级别

`TaskQueue` 支持以下队列级别：

`normal`: 常规任务队列，处理普通优先级的任务。   
`fail`: 失败任务队列，用于存储重试次数达到上限的任务。   
`urgent`: 紧急任务队列，处理高优先级的任务。   
队列级别用于控制任务的处理顺序和优先级。可以根据任务的重要性或紧急程度选择合适的队列级别。   

## 备份队列
`TaskQueue` 使用备份队列来避免重复任务。每个任务在添加到主要队列之前，会先被存储在一个备份集合中，防止重复插入。备份队列的名称格式为 `spider_task_backup:{task_name}`，其中 `{task_name}` 是队列的名称。

备份队列的 `TTL`: 备份队列的最大生存时间由配置文件中的 `MAX_TTL` 参数控制，默认为 30 天。备份队列在超过 `TTL` 后会自动过期，清除不再需要的任务数据。


## 安装依赖
确保您已安装了 loguru 和 redis 库。可以使用以下命令安装这些依赖：
```
pip install loguru redis
```

## 使用示例
以下是一个示例，展示如何使用 TaskQueue 类：
```
import TaskQueue

if __name__ == '__main__':
    # 初始化队列
    queue = TaskQueue(task_name='my_queue', level='urgent', log_level='info')
    
    # 添加任务
    tasks = [{'key': i} for i in range(10)]
    queue.add_tasks(tasks)
    
    # 获取任务
    task = queue.get_task()
    print(task)
    
    # 重试任务
    if task:
        queue.retry_task(task)
```

## 方法说明
* `add_task(task: dict, level: str = None, is_distinct: bool = True)`: 添加单个任务到队列。可以选择是否去重插入。   
* `add_tasks(tasks: list, level: str = None, is_distinct: bool = True)`: 批量添加任务到队列。可以选择是否去重插入。    
* `get_task(level: str = None, fifo: bool = True)`: 获取单个任务。可以选择是否按 FIFO 模式获取。    
* `get_tasks(level: str = None, num: int = 0, fifo: bool = True)`: 批量获取任务。可以选择是否按 FIFO 模式获取。    
* `retry_task(task: dict, is_distinct: bool = True)`: 重试单个任务。如果重试次数达到最大限制，则将任务插入失败队列。    
* `monitor_tasks()`: 监视当前任务数量。


## 日志
日志将根据配置文件中的 `LOG_LEVEL` 级别输出到标准错误流。可用的日志级别包括 `TRACE`、`DEBUG`、`INFO`、`SUCCESS`、`WARNING`、`ERROR` 和 `CRITICAL`。

## 注意事项
1. 确保 Redis 服务正在运行，并且配置文件中的 Redis 连接信息正确。    
2. 在添加任务之前，请确保 Redis 中相关的队列和备份集合未被占用或清空。    
3. 如果配置文件中 MAX_TTL 设置较大，确保 Redis 配置允许较长的键生存时间。    