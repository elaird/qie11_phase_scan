#!/usr/bin/env python

import os, time


def write_setting(data):
    template = "umnio_user_data.template"
    script = template.replace(".template", ".%d" % data)
    os.system("cat %s | sed s@THE_VALUE@%d@ > %s " % (template, data, script))
    os.system("uMNioTool.exe hcal-uhtr-38-12 -o bridge-ho -s %s" % script)


def test():
    for data in [999, 64, 999, 78, 999]:
        write_setting(data)
        time.sleep(1)

if __name__ == "__main__":
    test()
