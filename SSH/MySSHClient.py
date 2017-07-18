#!/usr/bin/env python
# coding=utf-8

import os
import time
import paramiko
from datetime import datetime
import logging
log = logging.getLogger("MySSH.SSH.MySSHClient")
log.setLevel(logging.INFO)


class MySSHClient:
    def __init__(self, host):
        self.host = host
        if not self.host.get("timeout"):
            self.host["timeout"] = 3
        # {time:{cmd:return(o,e)}}
        self.cmd_history = {}

    def connect(self):
        _host = self.host
        try:
            sc = paramiko.SSHClient()
            sc.set_missing_host_key_policy(paramiko.WarningPolicy())
            sc.connect(hostname=_host["ip"], port=_host["port"],
                       username=_host["user"], password=_host["passwd"], timeout=_host["timeout"])
            self.host["sc"] = sc
        except Exception as e:
            log.error("Get: %s from %s-%s", e.message, self.host["name"], self.host["ip"])
            return -1
        return 0

    def exec_ia(self, cmd, input_list=None, timeout=3):
        def set_history():
            _get_time = datetime.now()
            _return = _out.channel.recv_exit_status()
            self.cmd_history[_get_time] = (cmd, _return, _out.readlines(), _err.readlines())
            self.host["last_return_code"] = _return
            log.debug(self.cmd_history[_get_time])

        log.debug("cmd_ia:%s, input_list:%s", cmd, input_list)
        sc = self.host["sc"]
        _in, _out, _err = sc.exec_command(cmd, timeout)
        for _input in input_list:
            _in.write(_input + "\n")
        set_history()
        _in.channel.close()
        _out.channel.close()
        _err.channel.close()

    def exec_cmd(self, _cmd, sc_timeout=5):
        sc = self.host["sc"]
        log.debug("SSH_exec_cmd: %s, timeout:%s", _cmd, sc_timeout)
        _in, _out, _err = sc.exec_command(_cmd, timeout=sc_timeout)
        _return = _out.channel.recv_exit_status()
        _get_time = datetime.now()
        self.cmd_history[_get_time] = (_cmd, _return, _out.readlines(), _err.readlines())
        self.host["last_return_code"] = _return
        log.debug(self.cmd_history[_get_time])
        _in.channel.close()
        _out.channel.close()
        _err.channel.close()

    def get_file(self, remote_file, local_file):
        sftp_client = self.host["sc"].get_transport().open_sftp_client()
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
        sftp_client = self.host["sc"].get_transport().open_sftp_client()
        _return = -2
        try:
            _return = sftp_client.put(local_file, remote_file)
        except Exception as e:
            log.warn(e.message)
        _get_time = datetime.now()
        if _return != -2:
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
                log.info("-->%s", t)
                # log.info("\n" + self.show_utf8(t[1][2]))

    def show_utf8(self, obj):
        _t = ""
        if type(obj) == str:
            return obj
        elif type(obj) == unicode:
            return "%-20s" % obj.encode("utf-8")
        elif type(obj) == dict:
            for k in obj:
                _t += "|%s:%+s" % (self.show_utf8(k), self.show_utf8(obj[k]))
            return _t + "\n"
        elif type(obj) == list or type(obj) == tuple:
            for e in obj:
                _t += self.show_utf8(e)
            return _t + "\n"
        else:
            return "%-10s" % obj

    def close(self):
        if "sc" in self.host:
            self.host["sc"].close()

if __name__ == "__main__":
    ms = MySSHClient(host=dict(name="server1", ip='192.168.18.128', port=22, user='root', passwd='321', timeout=3))
    ms.connect()
    time.sleep(3)
    ms.exec_ia("passwd", ["321\n", "321\n"])
    ms.show_cmd_history()
    ms.close()
