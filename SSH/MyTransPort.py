#!/usr/bin/env python
# coding=utf-8

import os
import paramiko
from datetime import datetime
import logging as log

log.basicConfig(format='%(levelname)s==> %(filename)s [line:%(lineno)d] %(threadName)s %(message)s',
                datefmt=' %m %d %Y %H:%M:%S')


class MyTransPort:
    def __init__(self, host, recv_size=255):
        self.host = host
        # {time:{cmd:return(o,e)}}
        self.cmd_history = {}
        self.recv_size = recv_size

    def connect(self):
        # type: () -> object
        host = self.host
        try:
            tp = paramiko.Transport((host["ip"], host["port"]))
            tp.start_client()
            tp.auth_password(host["user"], host["passwd"])
            self.host["tp"] = tp
        except Exception as e:
            log.error(e.message)
            return -1
        return 0

    def exec_cmd(self, cmd):
        session = self.host["tp"].open_session()
        # session.settimeout(3) # try catch timeout
        session.exec_command(cmd)

        _get_time = datetime.now()
        _return = session.recv_exit_status()
        _out = session.recv(self.recv_size)
        _err = session.recv_stderr(self.recv_size)

        self.cmd_history[_get_time] = (cmd, _return, _out, _err)
        self.host["last_return_code"] = _return
        # 可不用close,
        session.close()
        log.debug("\n### %s ###_cmd = %s#_return = %d#_out = %s#_err = %s", _get_time, cmd, _return, _out, _err)

    def get_file(self, remote_file, local_file):
        sftp_client = self.host["tp"].open_sftp_client()
        try:
            sftp_client.get(remote_file, local_file)
        except IOError as e:
            log.warn(e.message)
        finally:
            sftp_client.close()

        _get_time = datetime.now()
        if os.path.exists(local_file):
            _return = 0
        elif not os.path.getsize(local_file):
            _return = -1
        else:
            _return = -2
        self.cmd_history[_get_time] =("get_file", _return, remote_file, local_file)
        self.host["last_return_code"] = _return

    def put_file(self, local_file, remote_file):
        sftp_client = self.host["tp"].open_sftp_client()
        _return = -2
        try:
            _return = sftp_client.put(local_file, remote_file)
        except Exception as e:
            log.warn(e.message)
        _get_time = datetime.now()
        if _return:
            _return = 0
        else:
            _return = -1
        self.cmd_history[_get_time] = ("put_file", _return, local_file, remote_file)
        self.host["last_return_code"] = _return

    def show_cmd_history(self):
            log.info("server: %s, ip: %s", self.host["name"], self.host["ip"])
            items = self.cmd_history.items()
            items.sort()
            for t in items:
                log.info("--->%s", t)

    def close(self):
        if "tp" in self.host:
            self.host["tp"].close()

if __name__ == "__main__":
    ms = MyTransPort(host=dict(name="server1", ip='192.168.2.200', port=22, user='root', passwd='123', timeout=3))
    ms.connect()
    ms.exec_cmd("w")
    ms.exec_cmd("whoami")
    ms.get_file("aa.txt", r"d:\aabbcc.txt")
    ms.put_file(r"d:\aabbcc.txt", "aaa1.txt")
    ms.show_cmd_history()
    ms.close()
