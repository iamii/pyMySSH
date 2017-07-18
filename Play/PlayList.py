#!/usr/bin/env python
# coding=utf-8

from SSH.MySSHClient import MySSHClient
from MySQL.MySQL import MyMySql

import time
from datetime import datetime
import threading
import logging
log = logging.getLogger("MySSH.Play.PlayList")
log.setLevel(logging.INFO)


class PlayList(MySSHClient, threading.Thread):
    def __init__(self, host, _do_dict, _event, _cond):
        threading.Thread.__init__(self)
        MySSHClient.__init__(self, host)
        self._cond = _cond
        self._event_dict = _event
        #
        self.do_dict = _do_dict
        self._index = []
        # 获取yaml中自定义的"执行命令序列"
        self._func_list = {}
        self._get_func_dict()
        #
        self._global_vars = self.do_dict.get("_const_")
        self._local_vars = {}
        self._vars = {}
        # 可以通过某种方式自动处理关联，目前为手动添加
        self._func2action = {"_do_if_else": ["if", "else", "do"],
                             "_do_pass": ["pass"],
                             "_do_exit": ["exit"],
                             "_do_sleep": ["sleep"],
                             "_do_mysql": ["mysql","dml_sql"],
                             "_do_cmd": ["cmd"],
                             "_do_wait": ["wait"],
                             "_do_wait_event": ["wait_event"],
                             "_do_send_event": ["send_event"],
                             "_do_make_config": ["make_config"],
                             "_do_put_file": ["put_file"],
                             "_do_get_file": ["get_file"],
                             "_do_reboot": ["reboot"]
                             }

    def __del__(self):
        self.close()

    def run(self):
        if not self.connect():
            try:
                self.run_main()
            finally:
                # log.debug(self._index)
                self.show_cmd_history()
        else:
            return

    def _do_exit(self, _do_dict, _index):
        _exit_code = _do_dict.get("exit")
        log.warning("exit: %s", _exit_code)
        time.sleep(1)
        _get_time = datetime.now()
        self.cmd_history[_get_time] = ("exit", _exit_code, None, None)
        self.host["last_return_code"] = _exit_code
        exit(_exit_code)

    def _do_mysql(self, _do_dict, _index):
        log.debug("_do_mysql:%s--%s", _do_dict, _index)
        _conn_str = _do_dict.get("mysql")
        _dml_sql = _do_dict.get("dml_sql")
        _call_proc = _do_dict.get("call_p")

        _call_timeout = _do_dict.get("call_timeout")
        _sc_timeout = _do_dict.get("sc_timeout")

        if _conn_str and (_dml_sql or _call_proc):
            try:
                mysql = MyMySql(**_conn_str)
                if hasattr(mysql, "cnn"):
                    if _dml_sql:
                        for sql in _dml_sql:
                            if self._vars:
                                try:
                                    sql = sql.format(**self._vars)
                                except Exception as e:
                                    log.error("格式化字符串 %s 错误:%s, vars: %s", sql, e.args, self._vars)
                                    exit(-1)
                            for i in range(1000000):
                                pass
                            _get_time = datetime.now()
                            try:
                                _out = mysql.query(sql)
                                _return = 0
                                _err = None
                            except Exception as e:
                                _err = e.args
                                _return = -1
                                _out = None
                            finally:
                                self.cmd_history[_get_time] = ("mysql:" + sql, _return, _out, _err)
                                self.host["last_return_code"] = _return
                    if _call_proc:
                        for _call in _call_proc:
                            _p_name = _call.get("name")
                            _p_args = _call.get("args")
                            if self._vars:
                                try:
                                    _p_name = _p_name.format(**self._vars)
                                    _p_args = [ _arg.format(**self._vars) for _arg in _p_args]
                                except Exception as e:
                                    log.error("格式化字符串错误:%s", e.args)
                                    exit(-1)
                            for i in range(1000000):
                                pass
                            _get_time = datetime.now()
                            _out = []
                            try:
                                # if _return
                                _return = mysql.cursor.callproc(_p_name, _p_args)
                                for e in mysql.cursor.stored_results():
                                    _out.append(e.fetchall())
                                _err = None
                            except Exception as e:
                                _return = -1
                                _out = None
                                _err = e.args
                            finally:
                                self.cmd_history[_get_time] = ("mysql:call_p:" + _p_name , _return, _out, _err)
                                self.host["last_return_code"] = _return
                else:
                    _get_time = datetime.now()
                    self.cmd_history[_get_time] = ("mysql:", -2, None, "Connection failed.")
                    self.host["last_return_code"] = -2
            except Exception as e:
                log.error("Exception: %s", e.args)
                _get_time = datetime.now()
                self.cmd_history[_get_time] = ("mysql:", -3, None, e.args)
                self.host["last_return_code"] = -3

    def _do_send_event(self, _do_dict, _index):
        _event = _do_dict.get("send_event")
        _values = _do_dict.get("send_values")
        if not _values:
            _values = 1
        _cond_wait_out = _do_dict.get("cond_waitout")
        _poll_time = _do_dict.get("poll_time")
        _call_time_out = _do_dict.get("call_timeout")

        log.info("send请求:%s --%s cond_timeout:%s   poll_time:%s   call_timeout:%s",
                  _event, self._event_dict.get(_event),  _cond_wait_out, _poll_time, _call_time_out)
        while True:
            if self._cond.acquire(0):
                log.info("send请求成功")
                _t = self._event_dict.get(_event)
                if type(_t) == int:
                    self._event_dict[_event] += _values
                else:
                    self._event_dict[_event] = _values
                log.info("send_event: %s, values: %d", _event, self._event_dict[_event])
                self._cond.notify()
                self._cond.release()
                _return = 0
                break
            else:
                log.info("send请求失败")
                if _call_time_out > 0 and _poll_time:
                    time.sleep(_poll_time)
                    _call_time_out -= _poll_time
                else:
                    log.info("send call_time_out/poll_time = 0, 或未设置.")
                    _return = 1
                    break

        self.host["last_return_code"] = _return
        _get_time = datetime.now()
        self.cmd_history[_get_time] = ("send_event:%s" % _event, _return, self._event_dict[_event], _call_time_out)

    def _do_wait_event(self, _do_dict, _index):
        _event = _do_dict.get("wait_event")
        _values = _do_dict.get("wait_values")
        if not _values:
            _values = 1
        _cond_wait_out = _do_dict.get("cond_waitout")

        _poll_time = _do_dict.get("poll_time")
        _call_time_out = _do_dict.get("call_timeout")

        log.info("wait请求:%s   cond_timeout:%s   poll_time:%s  call_timeout:%s",
                  _event, _cond_wait_out, _poll_time, _call_time_out)
        while True:
            if self._cond.acquire(0):
                log.info("wait请求成功")
                if self._event_dict.get(_event) == _values:
                    log.info("wait_event: %s, values: %d", _event, self._event_dict[_event])
                    _return = 0
                else:
                    if _call_time_out > 0 and _cond_wait_out:
                        log.info("wait未找到事件%s进入等待_cond.wait(%d)--call_time_out:%d", _event, _cond_wait_out,
                                  _call_time_out)
                        # self._cond.wait(timeout=_cond_wait_out)
                        self._cond.notify()
                        self._cond.release()
                        time.sleep(_cond_wait_out)
                        _call_time_out -= _cond_wait_out
                        continue
                    else:
                        _return = 1
                        log.info("wait call_timeout/cond_waitout = 0, 或未设置.")

                self._cond.notify()
                self._cond.release()
                break
            else:
                log.info("wait请求失败")
                if _call_time_out > 0 and _poll_time:
                    time.sleep(_poll_time)
                    _call_time_out -= _poll_time
                else:
                    log.info("call_timeout/poll_time = 0, 或未设置.")
                    _return = 2
                    break
        self.host["last_return_code"] = _return
        _get_time = datetime.now()
        self.cmd_history[_get_time] = ("wait_event:%s" % _event, _return, self._event_dict.get(_event), _call_time_out)

    def _do_sleep(self):
        pass

    def _do_wait(self, _do_dict, _index):
        time.sleep(_do_dict["wait"])

    def _do_make_config(self, _do_dict, _index):
        from Config.GetConfig import GetConfig
        _files = _do_dict["make_config"]
        _t = _files.get("template")
        _v = _files.get("vars_dict")
        _a = _files.get("add_item")
        _o = _files.get("output")
        try:
            GetConfig(_t, _v, _a, _o)
            _return = 0
            _err = None
        except Exception as e:
            _return = -1
            _err = e.args
        _get_time = datetime.now()
        self.cmd_history[_get_time] = ("make_config: %s" % _o, _return, "template: %s" % _t, _err)
        self.host["last_return_code"] = _return

    def _do_put_file(self, _do_dict, _index):
        if self._vars:
            try:
                _files = _do_dict["put_file"].format(**self._vars).split(",")
            except Exception as e:
                log.error("Host %s get format error: %s, _files: %s", self.host["name"], e.args, _do_dict)
                exit(-1)
        else:
            _files = _do_dict["put_file"].split(",")
        self.put_file(_files[0].strip(), _files[1].strip())

    def _do_get_file(self, _do_dict, _index):
        if self._vars:
            try:
                _files = _do_dict["get_file"].format(**self._vars).split(",")
            except Exception as e:
                log.error("Host %s get format error: %s, _files: %s", self.host, e.args, _do_dict)
                exit(-1)
        else:
            _files = _do_dict["get_file"].split(",")
        self.get_file(_files[0].strip(), _files[1].strip())

    @staticmethod
    def _get_context(_do_dict, _index):  # _do_dict会被改变
        """
        取出_do_dict中，索引为_index的内容
        Args:

        """
        i = None
        try:
            for i in range(0, len(_index)):
                _do_dict = _do_dict[_index[i]]
            return _do_dict
        except Exception, e:
            log.error("ERROR: %s, ---_do_list= %s, i= %s, _index= %s", e.message, _do_dict, i, _index)

    @staticmethod
    def _set_context(_do_dict, _index, _value):
        i = None
        try:
            for i in range(0, len(_index) - 1):
                _do_dict = _do_dict[_index[i]]
            _do_dict[_index[i + 1]] = _value
        except Exception, e:
            log.error(e.message)

    @classmethod
    def _get_index(cls, _do_dict, node_name, _index):
        """获取节点node_name在_do_dict中的索引，保留在_index
        :param _do_dict:
        :param node_name:
        :param _index: 保存各“层级”的列表，如['main', 'test_func'],表示main之下的test_func
        """
        try:
            if type(_do_dict) == str:
                return 0
            if type(_do_dict) == list or type(_do_dict) == dict:
                for key in _do_dict:
                    if key == node_name:
                        _index.append(key)
                        return 1
                    # 如果是字典，继续递归查找
                    elif type(_do_dict[key]) == dict:
                        _index.append(key)
                        if cls._get_index(_do_dict[key], node_name, _index):
                            return 1
                        else:
                            _index.pop()
                    elif type(_do_dict[key]) == list:
                        _index.append(key)
                        for i in range(0, len(_do_dict[key])):
                            _index.append(i)
                            if cls._get_index(_do_dict[key][i], node_name, _index):
                                return 1
                            else:
                                _index.pop()
                        else:  # 遍历完成list，没有找到
                            _index.pop()
            return 0
        except Exception, e:
            log.error(e.message)
            return -1

    def _dispatch(self, _do_dict, _index=None):
        """根据不同的值类型分发处理"""
        log.debug("_dispatch->_do_dict==> %s, _index=%s", _do_dict, _index)
        if type(_do_dict) == str:
            # 如果是str，说明已经到最后结点。此时判断func是否在self._func_list中。
            self._index.append(_do_dict)
            log.debug("_dispatch->str : %s", _do_dict)
            if _do_dict in self._func_list:
                # f_index = []
                # self._get_index(self.do_dict, _do_dict, f_index)
                # 如果是“过程”，则直接指向“过程”下的_cmds_
                self._local_vars = self.do_dict[_do_dict].get("_const_")
                if self._local_vars and self._global_vars:
                    self._vars = dict(self._global_vars, **self._local_vars)
                elif self._local_vars:
                    self._vars = self._local_vars
                else:
                    self._vars = self._global_vars
                self._dispatch(self._get_context(self.do_dict, [_do_dict, '_cmds_']), [_do_dict, '_cmds_'])
            else:
                return "", log.error("Unknown string: %s", _do_dict), None
        elif type(_do_dict) == list:
            self._index.append(_do_dict)
            for i in range(0, len(_do_dict)):
                log.debug("_dispatch->list : %s, _index= %s", i, _index)
                _index.append(i)
                self._dispatch(_do_dict[i], _index)
                _index.pop()
                # return o, e, p
        elif type(_do_dict) == dict:
            for k in _do_dict:
                stop = False
                for key in self._func2action:
                    if k in self._func2action[key]:
                        f = getattr(self, key)
                        if f:
                            stop = True
                            log.debug("call func: %s, _do_dict: %s, _index: %s", f, _do_dict, _index)
                            f(_do_dict, _index)
                        break
                #else:
                #    log.debug("---What is this: %s", _do_dict)
                if stop:
                    break
        else:
            log.error("Unknown func: %s,---type: %s", _do_dict, type(_do_dict))

    def _get_func_dict(self):
        for k in self.do_dict:
            self._func_list[k] = k

    def _do_cmd(self, _do_dict, _index):
        _cmd = _do_dict.get("cmd")
        _call_timeout = _do_dict.get("call_timeout")
        _sc_timeout = _do_dict.get("sc_timeout")
        _std_in = _do_dict.get("std_in")

        if not _call_timeout:
            _call_timeout = 600

        if type(_cmd) == list:
            # self.exec_cmd(_cmd.format(**_vars), sc_timeout=_sc_timeout)
            for _c in _cmd:
                try:
                    if self._vars:
                        try:
                            _c = _c.format(**self._vars)
                        except Exception as e:
                            log.error("Host %s get format error: %s, cmd: %s, _c: %s", self.host, e.args, _cmd, _c)
                            exit(-1)
                    if _std_in:
                        if self._vars:
                            _std_in = [_in.format(**self._vars) for _in in _std_in]
                        _t = threading.Thread(target=self.exec_ia, args=(_c, _std_in, _sc_timeout))
                    else:
                        _t = threading.Thread(target=self.exec_cmd, args=(_c, _sc_timeout))
                except KeyError as ke:
                    log.error("找不到常量定义. %s", ke)
                    exit(-1)
                _t.setDaemon(True)
                _t.start()
                log.debug("----->host: %s _t.join(%s)", self.host["ip"], _call_timeout)
                _t.join(_call_timeout)
                # isAlive()为True表示执行超时，
                if _t.isAlive():
                    log.warning("exec_cmd %s timeout %s", _c, _call_timeout)
                    _get_time = datetime.now()
                    self.cmd_history[_get_time] = ("cmd:" + _c, -2, None, "call_time_out: %s" % _call_timeout)
                    self.host["last_return_code"] = -2
        elif _cmd:
            # self.exec_cmd(_cmd.format(**_vars), sc_timeout=_sc_timeout)
            try:
                if self._vars:
                        _cmd = _cmd.format(**self._vars)
                if _std_in:
                    if self._vars:
                        _std_in = [_in.format(**self._vars) for _in in _std_in]
                    _t = threading.Thread(target=self.exec_ia, args=(_cmd, _std_in, _sc_timeout))
                else:
                    _t = threading.Thread(target=self.exec_cmd, args=(_cmd, _sc_timeout))
            except KeyError as ke:
                log.error("找不到常量定义. %s", ke)
                exit(-1)
            _t.setDaemon(True)
            _t.start()
            log.debug("----->host: %s _t.join(%s)", self.host["ip"], _call_timeout)
            _t.join(_call_timeout)
            # isAlive()为True表示执行超时，
            if _t.isAlive():
                log.warning("exec_cmd %s timeout %s", _cmd, _call_timeout)
                _get_time = datetime.now()
                self.cmd_history[_get_time] = ("cmd:" + _cmd, -2, None, "call_time_out: %s" % _call_timeout)
                self.host["last_return_code"] = -2

    #def _do_cmd_ia(self, _do_dict, _index):
    #    _cmd = _do_dict.get("cmd_ia")
    #    _input = _do_dict.get("std_in")
    #    _tm = _do_dict.get("timeout")
    #    self.exec_ia(_cmd, _input, timeout=_tm)

    def _do_if_else(self, if_else_dict=None, _index=None):
        # try:
        log.debug("----if else dict --- %s", if_else_dict)
        if type(if_else_dict) == dict:
            if_seg = if_else_dict.get('if')
            do_seg = if_else_dict.get('do')
            else_seg = if_else_dict.get('else')
            return_code = if_else_dict.get('return_code')
            if not return_code: return_code = 0

            if if_seg:
                log.debug("found if_seg, do if_seg ...")
                if return_code is None:
                    log.error("No 'return_code' in %s", if_else_dict)
                    return

                if if_seg in self._func_list.keys() or type(if_seg) == dict:  # type(if_seg)==str
                    _index.append('if')
                    self._dispatch(if_seg, _index)
                    _index.pop()
                    if self.host["last_return_code"] == return_code:
                        if do_seg:
                            _index.append('do')
                            self._dispatch(do_seg, _index)
                            _index.pop()
                        else:
                            log.warn("Not found 'do_seg'.")
                    elif self.host["last_return_code"] != return_code:
                        if else_seg:
                            _index.append('else')
                            self._dispatch(else_seg, _index)
                            _index.pop()
                        else:
                            log.error("Not found 'else_seg.")
                    else:
                        log.error("Not found 'else_seg'.")
            elif do_seg and not else_seg:  # if if_seg
                # self._do_if_else(do_seg, _index)
                _index.append('do')
                self._dispatch(do_seg, _index)
                _index.pop()
            elif else_seg and not if_seg:
                log.error("else_seg must match if_seg.")
            else:
                self._dispatch(if_else_dict, _index)
        elif type(if_else_dict) == str:
            self._dispatch(if_else_dict, _index)
        else:
            log.error("Unknown if_else_dict '%s'", if_else_dict)
            return 0
            # except Exception, e:
            #    log.error(e.message)
            #    return -1

    def run_main(self):
        _host_name = self.host["name"]
        _script = self.do_dict["servers"][_host_name]["script"]
        self._dispatch(_script)
