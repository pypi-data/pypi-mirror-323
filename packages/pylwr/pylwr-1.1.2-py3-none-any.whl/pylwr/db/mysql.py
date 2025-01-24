import datetime
import pymysql
import json

class Mysql(object):
    def __init__(self,host: str, database: str, user: str, password: str, ) -> object:
        self.connection = pymysql.connect(
            host = host,
            database = database,
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
        
        try:
            if data is None:
                self.cursor.execute(sql)
            else:
                self.cursor.execute(sql,data)
            self.conn.commit()
        except pymysql.Error as e:
            error_obj, = e.args
            raise Exception(
                sql + 
                ' ' + 
                '\n' 
                + str(error_obj.code) + 
                ' ' + str(error_obj.message))
        
    def check(self):
        try:
            self.connection.ping()
        except:
            self.connection()

    def close(self):
        self.connection.close()