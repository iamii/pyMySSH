#! /usr/bin/env python
# coding=utf-8

import os
import yaml
from jinja2 import Environment, PackageLoader


class GetConfig:
    def __init__(self, template, dict_file=None, var_dict=None, out_put=None):
        self.env = Environment(loader=PackageLoader("Config"))
        # self.env.trim_blocks = True
        self.tpl = self.env.get_template(template)
        self.var_dict = var_dict
        if dict_file:
            self._read_yamlfile(dict_file)
        self.out_put = None
        self._render(out_put)

    def _read_yamlfile(self, yaml_file):
        # try:
        pf = open(yaml_file, 'r')
        # try:
        _d = yaml.safe_load(pf)
        if self.var_dict:
            for k in self.var_dict["template"]:
                _d["template"][k] = self.var_dict["template"][k]
        self.var_dict = _d

        # except Exception, e:
        # log.error(e.message)
        # finally:
        pf.close()

    def _render(self, conf_file):
        self.out_put = self.tpl.render(self.var_dict["template"])
        if conf_file:
            output = open(conf_file, 'w')
            output.write(self.out_put)
            output.close()

if __name__ == "__main__":
    gc = GetConfig("./httpd/httpd.tpl", "./templates/httpd/httpd.dict", None, "./templates/httpd/httpd.conf")
