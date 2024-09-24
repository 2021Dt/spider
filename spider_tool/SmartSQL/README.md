# SmartSQL

`SmartSQL` 是一个用于简化 MySQL 数据库操作的 Python 类，提供了一系列智能 SQL 操作方法，包括插入、更新、查询和删除。它基于 pymysql 和 dbutils 连接池库，支持使用连接池优化数据库连接的性能。

## 特性
* 连接池管理：使用连接池优化数据库连接。
* 智能 SQL 生成：自动生成插入、更新、删除 SQL 语句。
* 数据转换：支持将查询结果转换为 JSON 格式，并处理日期和 JSON 字符串数据。
* 上下文管理：通过上下文管理器确保数据库连接和游标的正确释放。

## 安装
```pip install pymysql dbutils```

## 配置
请确保在 `config.ini` 文件中定义以下配置项：
```
config.ini
[mysql]
ip = your_ip
port = your_port
db = your_db
user_name = your_user_name
user_pass = your_pass

[logging]
level = DEBUG
```
同时可以通过`config.py`中的`init_logging`函数自定义日志配置

## 使用
### 初始化
```
from SmartSQL import SmartSQL

# 使用默认配置
db = SmartSQL()

# 使用自定义配置
db = SmartSQL(ip='localhost', port=3306, db='test_db', user_name='root', user_pass='password')
```

### 通过 URL 初始化
```
db = SmartSQL.from_url('mysql://username:password@ip:port/db')
```

## 数据操作
### 添加数据
```
data = {'user': 'admin', 'age': 30}
affected_rows = db.add_smart('test_table', data)
```

### 更新数据
```
update_data = {'age': 31}
update_success = db.update_smart('test_table', update_data, "user='admin'")
```

### 查询数据
```
result = db.find("SELECT * FROM test_table WHERE user=%s", params=("admin",), to_json=True)
```

### 智能查询
```
smart_result = db.smart_find(
    table='test_table',
    columns='*',
    where='age > 30',
    to_json=True
)
```

### 删除数据
```
delete_success = db.delete_smart('test_table', "user='admin'")

```

## 测试案例
```
def test_smart_sql():
    # 创建数据库连接
    db = SmartSQL()

    # 创建测试表
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS test_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user VARCHAR(50),
        age INT
    );
    """
    db.execute(create_table_sql)

    # 添加数据
    data_to_add = {'user': 'admin', 'age': 30}
    add_result = db.add_smart("test_table", data_to_add)
    print(f"添加数据影响的行数: {add_result}")

    # 更新数据
    data_to_update = {"age": 31}
    update_result = db.update_smart("test_table", data_to_update, "user='admin'")
    print(f"更新数据成功: {update_result}")

    # 查询数据
    find_result = db.find("SELECT * FROM test_table WHERE user=%s", params=("admin",), to_json=True)
    print(f"查询数据结果: {find_result}")

    # 智能查找
    smart_find_result = db.smart_find(
        table='test_table',
        columns='*',
        where='age > 30',
        to_json=True
    )
    print(f"智能查找结果: {smart_find_result}")

    # 删除数据
    delete_result = db.delete_smart("test_table", "user='admin'")
    print(f"删除数据成功: {delete_result}")

    # 验证数据是否删除
    find_after_delete_result = db.find("SELECT * FROM test_table WHERE user=%s", params=("admin",), to_json=True)
    print(f"删除后的查询结果: {find_after_delete_result}")

    # 清理测试表（可选）
    drop_table_sql = "DROP TABLE IF EXISTS test_table;"
    db.execute(drop_table_sql)

if __name__ == "__main__":
    test_smart_sql()

```
