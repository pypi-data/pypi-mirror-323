import datetime
import json
import oracledb
import pymysql
from pylwr.const import *
import pylwr

class Db(object):
    def __init__(self,db_name: int, ) -> object:
        if db_name == DB_HCU:
            self.oracle_init('192.168.1.141','1521','orcl','drg','1')
            self.db_type = DRIVE_ORACLE
        if db_name == DB_SH:
            self.oracle_init_less12('192.168.6.147','1521','orcl','drg','1', PATH_LWR_ROG)
            self.db_type = DRIVE_ORACLE
        if db_name == DB_LICUS:
            self.mysql_init('192.168.6.147','micm_szlg_lhkf','root','root')
            self.db_type = DRIVE_MYSQL
        if db_name == DB_MYSQL:
            self.mysql_init('127.0.0.1','lwr','root','1')
            self.db_type = DRIVE_MYSQL
        if db_name == DB_ORACLE:
            self.oracle_init('127.0.0.1','1521','orcl','lwr','1')
            self.db_type = DRIVE_ORACLE

    def mysql_init(self,host: str, database: str, user: str, password: str, ) -> object:
        self.connection = pymysql.connect(
            host = host,
            database = database,
            user = user,
            password = password,
        )
    def oracle_init(self,host: str, port: int, service_name: str, user: str, password: str, ) -> object:
        dsn = oracledb.makedsn(host, port, service_name)
        self.connection = oracledb.connect(
            dsn = dsn,
            user = user,
            password = password,
        )
        self.cursor = self.connection.cursor()
    def oracle_init_less12(self,host: str, port: int, service_name: str, user: str, password: str, env: int) -> object:
        if env == PATH_LWR_ROG:
            d = r"C:\tool\instantclient_12_2"
            oracledb.init_oracle_client(lib_dir=d)
        dsn = oracledb.makedsn(host, port, service_name)
        self.connection = oracledb.connect(
            dsn = dsn,
            user = user,
            password = password,
        )
        self.cursor = self.connection.cursor()
    def select(self, sql):
        list = []
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        col_name = self.cursor.description
        for row in result:
            dict = {}
            for col in range(len(col_name)):
                key = col_name[col][0]
                value = row[col]
                if isinstance(value,datetime.datetime):
                    dict[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dict[key] = value
                
            list.append(dict)
        return json.dumps(list, ensure_ascii=False, indent=2, separators=(',', ':'))
    
    def select_json(self, sql):
        list = []
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        col_name = self.cursor.description
        for row in result:
            dict = {}
            for col in range(len(col_name)):
                key = col_name[col][0]
                value = row[col]
                if isinstance(value,datetime.datetime):
                    dict[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dict[key] = value
                
            list.append(dict)
        return list

    def execute(self, sql, data= None):
        if self.db_type == DRIVE_MYSQL:
            try:
                if data is None:
                    self.cursor.execute(sql)
                else:
                    self.cursor.execute(sql,data)
                self.connection.commit()
            except Exception as e:
                error_obj, = e.args
                raise Exception(
                    sql + 
                    ' ' + 
                    '\n' 
                    + str(error_obj.code) + 
                    ' ' + str(error_obj.message))
        if self.db_type == DRIVE_ORACLE:
            try:
                if data is None:
                    self.cursor.execute(sql)
                else:
                    self.cursor.execute(sql,data)
                self.connection.commit()
            except Exception as e:
                error_obj, = e.args
                raise Exception(
                    sql + 
                    ' ' + 
                    '\n' 
                    + str(error_obj.code) + 
                    ' ' + str(error_obj.message))
    
    def executemany(self, sql, data=None, batcherrors=True) -> bool: 
        """批量执行 SQL 语句。

        该方法支持 MySQL 和 Oracle 数据库，并在操作出错时进行回滚，确保数据一致性。

        参数:
            sql (str): 要执行的 SQL 语句，必须为参数化查询，防止 SQL 注入。
            data (list[tuple]): 批量执行的数据，格式为元组列表。
            batcherrors (bool, 可选): 是否在出现错误时继续执行剩余 SQL（仅 Oracle 支持，默认为 True）。

        异常:
            pymysql.MySQLError: 如果在 MySQL 执行期间发生错误。
            oracledb.Error: 如果在 Oracle 执行期间发生错误。
            ValueError: 如果传入了不支持的数据库类型。

        返回:
            bool: 如果执行成功返回 True，否则返回 False。
        """
        if not data:
            print("警告：数据为空，未执行 SQL。")
            return False

        if self.db_type == DRIVE_MYSQL:
            try:
                self.cursor.executemany(sql, data)
                self.connection.commit()
                return True
            except Exception as e:
                print(f"MySQL 执行错误：{e}")
                self.connection.rollback()
                return False

        elif self.db_type == DRIVE_ORACLE:
            self.cursor.executemany(sql, data, batcherrors=batcherrors)
            errors = self.cursor.getbatcherrors()
            if len(errors) > 0:
                max_errors = min(10, len(self.cursor.getbatcherrors()))  # 取错误数量与10之间的最小值
                for i in range(max_errors):
                    error = self.cursor.getbatcherrors()[i]
                    print("Error", error.message, "at row offset", error.offset)
                
                self.connection.rollback()
                return False
            self.connection.commit()
            return True
        else:
            raise ValueError("不支持的数据库类型，请使用 'mysql' 或 'oracle'。")
        

    def select_some_param(self, table: str, obj: object, func: str, input: str, sql_type: int, update: str, print_debug: bool) -> list | None:
        '''
        根据表的 JSON 对象循环，判断是否符合条件，拼接符合条件的字段作为 SQL 条件，执行 SQL 语句。

        Args:
            table (str): 表名。
            obj (object): 表数据对象，如 {"A": "NOW IS ABC","B": 1}。
            func (str): 调用的方法名，该方法应返回布尔值。
            input (str): 查询条件内容，默认是字符串。
            sql_type (int): SQL 类型，可选值为 SELECT、DELETE、UPDATE。
            update (str): SQL 更新语句片段，示例: "A=1, B=2, C=3"。
            print_debug (bool): 是否打印调试日志。

        Returns:
            list | None: 返回查询结果的列表，如果没有符合条件的记录，则返回 None。
        '''

        sql = ''
        NOT_ZERO = False
        for key, value in obj.items():
            # 默认入参是字符串
            if pylwr.distribute.target_fun(func, value):
                if NOT_ZERO:
                    sql = sql + ' OR ' + key + '=\'' + input + '\''
                else:
                    sql = sql + key + '=\'' + input + '\''
                    NOT_ZERO = True
        
        if not NOT_ZERO:
            pylwr.warning(f'Now, the table [{table}] does not match rule <{func}>, program will be skipped.')
            return None

        if sql_type == SQL_DELETE:
            sql = f'DELETE FROM {table} WHERE {sql}'
            if print_debug:
                print(sql)
            return self.execute(sql)

        if sql_type == SQL_SELECT:
            sql = f'SELECT * FROM {table} WHERE {sql}'
            if print_debug:
                print(sql)
            return self.select_json(sql)

        if sql_type == SQL_UPDATE:
            sql = f'UPDATE {table} SET {update} WHERE {sql}'
            if print_debug:
                print(sql)
            return self.execute(sql)

        return None


        
        

    def check(self):
        try:
            self.connection.ping()
        except:
            self.connection()

    def close(self):
        self.connection.close()