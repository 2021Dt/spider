"""
@Project ：TaskQueue.py
@File    ：SmartSQL.py
@Author  ：dp
@Date    ：2024/9/13 11:11
"""

import pymysql
from dbutils.pooled_db import PooledDB
from pymysql import cursors
from urllib import parse
import json
import datetime
from contextlib import contextmanager
from config import MYSQL_IP, MYSQL_PORT, MYSQL_DB, MYSQL_USER_NAME, MYSQL_USER_PASS, init
from loguru import logger

# 初始化配置
init()

class SmartSQL:
    def __init__(self, ip=None, port=None, db=None, user_name=None, user_pass=None, **kwargs):
        """
        初始化 MySQL 数据库连接池
        :param ip: 数据库 IP 地址，默认从环境变量加载或 config 文件配置
        :param port: 数据库端口号，默认从环境变量加载或 config 文件配置
        :param db: 数据库名称，默认从环境变量加载或 config 文件配置
        :param user_name: 数据库用户名，默认从环境变量加载或 config 文件配置
        :param user_pass: 数据库密码，默认从环境变量加载或 config 文件配置
        :param kwargs: 其他可选参数，用于扩展连接配置
        """
        self.ip = ip or MYSQL_IP
        self.port = port or MYSQL_PORT
        self.db = db or MYSQL_DB
        self.user_name = user_name or MYSQL_USER_NAME
        self.user_pass = user_pass or MYSQL_USER_PASS

        try:
            self.connect_pool = PooledDB(
                creator=pymysql,
                mincached=1,
                maxcached=100,
                maxconnections=100,
                blocking=True,
                ping=7,
                host=self.ip,
                port=self.port,
                user=self.user_name,
                passwd=self.user_pass,
                db=self.db,
                charset="utf8mb4",
                cursorclass=cursors.SSCursor,
            )
        except Exception as e:
            logger.error(f"连接数据库失败: {self.ip}:{self.port}，异常: {e}")
        else:
            logger.debug(f"成功连接到 MySQL 数据库 {self.ip}:{self.db}")

    @classmethod
    def from_url(cls, url, **kwargs):
        """
        通过数据库连接 URL 创建 SmartSQL 实例
        :param url: 数据库连接 URL，格式为 mysql://username:password@ip:port/db
        :param kwargs: 其他可选参数，用于扩展连接配置
        :return: SmartSQL 实例
        :raises ValueError: 当 URL 格式不正确时抛出异常
        """
        url_parsed = parse.urlparse(url)
        if url_parsed.scheme.strip() != "mysql":
            raise ValueError(f"URL 错误，预期格式为 mysql://username:password@ip:port/db，实际为 {url}")

        connect_params = {
            "ip": url_parsed.hostname,
            "port": url_parsed.port,
            "user_name": url_parsed.username,
            "user_pass": url_parsed.password,
            "db": url_parsed.path.lstrip("/"),
        }
        connect_params.update(kwargs)
        return cls(**connect_params)

    @contextmanager
    def get_connection(self):
        """
        获取数据库连接和游标的上下文管理器，确保资源正确释放
        :return: 数据库连接和游标
        """
        conn = self.connect_pool.connection(shareable=False)
        cursor = conn.cursor()
        try:
            yield conn, cursor
        finally:
            cursor.close()
            conn.close()

    def size_of_connections(self):
        """
        获取当前活跃的连接数
        :return: 当前活跃连接数
        """
        return len(self.connect_pool._connections)

    def size_of_connect_pool(self):
        """
        获取连接池中所有连接数
        :return: 连接池中的连接数
        """
        return len(self.connect_pool._idle_cache)

    def smart_find(self, table, columns='*', where=None, limit=0, offset=0, to_json=False, convert_col=True):
        """
        智能查询数据
        :param table: 表名
        :param columns: 要查询的列，默认为 '*'，表示查询所有列
        :param where: 查询条件，例如 "age > 30"
        :param limit: 限制返回结果数量，0 为不限制
        :param offset: 查询结果的偏移量，用于分页
        :param to_json: 是否将查询结果转换为 JSON 格式
        :param convert_col: 是否转换列数据类型（如日期类型转字符串）
        :return: 查询结果，默认返回元组，若 to_json=True 则返回字典或字典列表
        """
        sql = f"SELECT {columns} FROM {table}"
        if where:
            sql += f" WHERE {where}"
        if limit > 0:
            sql += f" LIMIT {limit}"
        if offset > 0:
            sql += f" OFFSET {offset}"

        result = self.find(sql, to_json=to_json, convert_col=convert_col)
        return result

    def find(self, sql, params=None, limit=0, to_json=False, convert_col=True):
        """
        查询数据
        :param sql: SQL 查询语句
        :param params: 可选的查询参数，用于参数化查询
        :param limit: 限制返回结果数量，0 为不限制
        :param to_json: 是否将查询结果转换为 JSON 格式
        :param convert_col: 是否转换列数据类型（如日期类型转字符串）
        :return: 查询结果，默认返回元组，若 to_json=True 则返回字典或字典列表
        """
        result = self._execute_sql(sql, params, limit, fetch=True)

        if to_json:
            columns = [col[0] for col in result["cursor"].description]
            if convert_col:
                result["data"] = [self._convert_row(row, columns) for row in result["data"]]
            else:
                result["data"] = [dict(zip(columns, row)) for row in result["data"]]
            result["data"] = self._convert_to_json(result["data"])

        return result["data"]

    def _execute_sql(self, sql, params=None, limit=0, fetch=False):
        """
        执行 SQL 语句的私有方法
        :param sql: SQL 语句
        :param params: SQL 参数
        :param limit: 限制返回结果数量，0 为不限制
        :param fetch: 是否需要获取结果
        :return: 包含游标和数据的字典，若 fetch=False 则返回影响行数
        """
        try:
            with self.get_connection() as (conn, cursor):
                if fetch:
                    cursor.execute(sql, params or ())
                    data = self._fetch_results(cursor, limit)
                    return {"cursor": cursor, "data": data}
                else:
                    affect_count = cursor.execute(sql, params or ())
                    conn.commit()
                    return affect_count
        except pymysql.MySQLError as e:
            logger.error(f"执行 SQL 出错: {e}, SQL: {sql}, 参数: {params}")
            if fetch:
                return {"cursor": None, "data": []}
            return 0
        except Exception as e:
            logger.error(f"执行 SQL 出错: {e}, SQL: {sql}, 参数: {params}")
            if fetch:
                return {"cursor": None, "data": []}
            return 0

    def _fetch_results(self, cursor, limit):
        """
        获取查询结果
        :param cursor: 数据库游标
        :param limit: 限制返回结果数量，0 为不限制
        :return: 查询结果
        """
        if limit == 1:
            return cursor.fetchone()
        elif limit > 1:
            return cursor.fetchmany(limit)
        else:
            return cursor.fetchall()

    def _convert_row(self, row, columns):
        """
        转换行数据的列数据类型
        :param row: 查询结果中的一行数据
        :param columns: 列名列表
        :return: 转换后的行数据
        """
        def convert(col):
            if isinstance(col, (datetime.date, datetime.time)):
                return str(col)
            elif isinstance(col, str) and (col.startswith("{") or col.startswith("[")):
                try:
                    return json.loads(col)
                except Exception:
                    return col
            else:
                return col

        return dict(zip(columns, [convert(col) for col in row]))

    def _convert_to_json(self, result):
        """
        将查询结果转换为 JSON 格式
        :param result: 查询结果
        :return: JSON 格式的结果
        """
        try:
            return json.dumps(result)
        except Exception as e:
            logger.error(f"转换为 JSON 格式失败: {e}")
            return result

    def add(self, sql, params=None):
        """
        添加单条数据到数据库
        :param sql: SQL 插入语句
        :param params: 可选的插入参数，用于参数化插入
        :return: 影响的行数
        """
        return self._execute_sql(sql, params, fetch=False)

    def add_smart(self, table, data, **kwargs):
        """
        根据给定的表名和数据字典，智能生成插入语句并插入数据
        :param table: 表名
        :param data: 要插入的数据，格式为字典 {"column": "value"}
        :param kwargs: 其他参数用于生成插入 SQL 的辅助功能
        :return: 影响的行数
        :raises ValueError: 当数据字典为空时抛出异常
        """
        if not data:
            raise ValueError("插入数据不能为空")

        sql = self._make_insert_sql(table, data, **kwargs)
        params = tuple(data.values())
        return self.add(sql, params)

    def _make_insert_sql(self, table, data, **kwargs):
        """
        生成插入 SQL 语句
        :param table: 表名
        :param data: 数据字典
        :param kwargs: 其他可选参数
        :return: 生成的 SQL 语句
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return sql


    def update(self, sql, params=None):
        """
        更新数据库中的数据
        :param sql: SQL 更新语句
        :param params: 可选的更新参数，用于参数化更新
        :return: 更新成功返回 True，否则返回 False
        """
        try:
            with self.get_connection() as (conn, cursor):
                cursor.execute(sql, params or (()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"更新数据出错: {e}, SQL: {sql}")
            return False

    def delete(self, sql, params=None):
        """
        删除数据库中的数据
        :param sql: SQL 删除语句
        :param params: 可选的删除参数，用于参数化删除
        :return: 删除成功返回 True，否则返回 False
        """
        try:
            with self.get_connection() as (conn, cursor):
                cursor.execute(sql, params or (()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"删除数据出错: {e}, SQL: {sql}")
            return False

    def execute(self, sql, params=None):
        """
        执行任意 SQL 语句
        :param sql: SQL 语句
        :param params: 可选的参数，用于参数化执行
        :return: 执行成功返回 True，否则返回 False
        """
        try:
            with self.get_connection() as (conn, cursor):
                cursor.execute(sql, params or ())
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"执行 SQL 出错: {e}, SQL: {sql}")
            return False

    def execute_smart(self, table, data, **kwargs):
        """
        根据给定的表名和数据字典，智能生成 SQL 语句并执行
        :param table: 表名
        :param data: 要插入的数据，格式为字典 {"column": "value"}
        :param kwargs: 其他参数用于生成 SQL 的辅助功能
        :return: 执行成功返回 True，否则返回 False
        """
        sql = self._make_insert_sql(table, data, **kwargs)
        return self.execute(sql)

    def _make_update_sql(self, table, data, where, **kwargs):
        """
        生成更新 SQL 语句
        :param table: 表名
        :param data: 要更新的数据，格式为字典 {"column": "value"}
        :param where: 更新条件
        :param kwargs: 其他参数用于辅助生成 SQL
        :return: 更新语句字符串
        """
        if not data:
            raise ValueError("更新数据不能为空")
        if not where:
            raise ValueError("更新条件不能为空")

        set_clause = ', '.join([f"{k}=%s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        return sql

    def update_smart(self, table, data, where, **kwargs):
        """
        根据给定的表名、数据字典和条件，智能生成更新 SQL 语句并执行
        :param table: 表名
        :param data: 要更新的数据，格式为字典 {"column": "value"}
        :param where: 更新条件
        :param kwargs: 其他参数用于生成 SQL 的辅助功能
        :return: 执行成功返回 True，否则返回 False
        """
        sql = self._make_update_sql(table, data, where, **kwargs)
        params = list(data.values())
        return self.execute(sql, params)

    def _make_delete_sql(self, table, where, **kwargs):
        """
        生成删除 SQL 语句
        :param table: 表名
        :param where: 删除条件
        :param kwargs: 其他参数用于辅助生成 SQL
        :return: 删除语句字符串
        """
        if not where:
            raise ValueError("删除条件不能为空")

        sql = f"DELETE FROM {table} WHERE {where}"
        return sql

    def delete_smart(self, table, where, **kwargs):
        """
        根据给定的表名和条件，智能生成删除 SQL 语句并执行
        :param table: 表名
        :param where: 删除条件
        :param kwargs: 其他参数用于生成 SQL 的辅助功能
        :return: 执行成功返回 True，否则返回 False
        """
        sql = self._make_delete_sql(table, where, **kwargs)
        return self.execute(sql)


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

# if __name__ == "__main__":
#     test_smart_sql()
