#!/usr/bin/env python
# coding=utf-8

import os
import threading
import yaml
from PlayList import PlayList

import logging
log = logging.getLogger("MySSH")
ch = logging.StreamHandler()
log_format = logging.Formatter('%(asctime)s %(levelname)s==> %(filename)s [line:%(lineno)d] %(threadName)s %(message)s')
ch.setFormatter(log_format)
log.addHandler(ch)
log.setLevel(logging.INFO)

class PlayBook:
    def __init__(self, config_file="./Play/dhcpd_server.yaml"):
        self.play_list = None
        self.config_file = config_file
        self._read_yamlfile()
        self._event = {}
        self._cond = threading.Condition()

    def start(self):
        for host in self.play_list["servers"]:
            #
            _host = self.play_list["servers"][host]
            # _script = self.play_list["servers"][host]["script"]
            # _global_sub = self.play_list["_global_sub_"]

            #if "name" not in _host:
            _host["name"] = host
            #
            pl = PlayList(_host, self.play_list, self._event, self._cond)
            pl.start()

    def _read_yamlfile(self):
        # try:
        pf = open(self.config_file, 'r')
        # try:
        self.play_list = yaml.safe_load(pf)
        # except Exception, e:
        # log.error(e.message)
        # finally:
        pf.close()

if __name__ == "__main__":
    #dhcp_pb = PlayBook(config_file="./books/dhcpd_server.yaml")
    #dhcp_pb.start()
    #ntp_pb = PlayBook(config_file="./books/ntp_test.yaml")
    #ntp_pb.start()
    #nfs_pb = PlayBook(config_file="./books/nfsd.yaml")
    #nfs_pb.start()
    #ftpd_pb = PlayBook(config_file="./books/ftp_test.yaml")
    #ftpd_pb.start()
    smb_pb = PlayBook(config_file="./books/samba_test.yaml")
    smb_pb.start()
    #dnsd_pb = PlayBook(config_file="./books/dnsd.yaml")
    #dnsd_pb.start()
    #httd_pb = PlayBook(config_file="./books/httpd.yaml")
    #httd_pb.start()
    #ip_pb = PlayBook(config_file="./books/iptables.yaml")
    #ip_pb.start()
    # squid_pb = PlayBook(config_file="./books/squid.yaml")
    # squid_pb.start()
    # uc_pb = PlayBook(config_file="./books/uc.yaml")
    # uc_pb.start()
    # mysql218_pb = PlayBook(config_file="./books/mysql2.18.yaml")
    # mysql218_pb.start()
    # mysql219_pb = PlayBook(config_file="./books/mysql2.19.yaml")
    # mysql219_pb.start()
    # mysql224_pb = PlayBook(config_file="./books/mysql2.24.yaml")
    # mysql224_pb.start()
    # mysql225_pb = PlayBook(config_file="./books/mysql2.25.yaml")
    # mysql225_pb.start()
    #mysql226_pb = PlayBook(config_file="./books/mysql2.26.yaml")
    #mysql226_pb.start()
