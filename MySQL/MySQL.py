#!/usr/bin/env python
# coding=utf-8

import mysql.connector
import logging

log = logging.getLogger("MySSH.MySQL.MySQL")
ch = logging.StreamHandler()
log_format = logging.Formatter('%(asctime)s %(levelname)s==> %(filename)s [line:%(lineno)d] %(threadName)s %(message)s')
ch.setFormatter(log_format)
log.addHandler(ch)
log.setLevel(logging.DEBUG)


class MyMySql:
    def __init__(self, **__config):
        """
        self.config = {'host': '192.168.18.99',  # 默认127.0.0.1
                       'user': 'root',
                       'password': '123456',
                       'port': 3306,  # 默认为3306
                       'database': 'test',
                       'charset': 'utf8'  # 默认为utf8
                       }
        """
        self.config = __config
        # try:
        self.cnn = mysql.connector.connect(**self.config)
        # self.cursor = self.cnn.cursor(dictionary=True)
        self.cursor = self.cnn.cursor()
        # except mysql.connector.Error as e:
        #    log.error('connect fails!{}'.format(e))

    def __del__(self):
        if hasattr(self, "cnn"):
            if hasattr(self.cnn, "cursor"):
                self.cursor.close()
            self.cnn.close()

    def query(self, querystring):
        # try:
        self.cursor.execute(querystring)
        _result = self.cursor.fetchall()
        return _result
        # except Exception as _err:
        #    log.error("Exception:%s", _err.args)

    def call_p(self, p_name, p_args):
        self.cursor.callproc(p_name, p_args)
        print self.cursor.stored_results()

if __name__ == "__main__":
    config = {'host': '192.168.18.99',  # 默认127.0.0.1
              'user': 'root',
              'password': '123456',
              'port': 3306,  # 默认3306
              'database': 'mysql',
              'charset': 'utf8'  # 默认为utf8
              }

    m = MyMySql(**config)
    sql = ("show tables;")
    result = m.query(sql)
    if result:
        for k in result:
            print k
