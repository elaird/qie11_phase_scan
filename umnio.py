import os

def write_setting(data):
    umnio_script = "umnio_user_data.%d" % data
    os.system("cat umnio_user_data.template | sed s@PHASE_SETTING@%d@ > %s " % (data, umnio_script))
    os.system("uMNioTool.exe hcal-uhtr-38-12 -o controlhub-hcal-daq -s %s" % umnio_script)
