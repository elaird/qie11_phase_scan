#!/usr/bin/env python

import time, umnio

for data in [999, 64, 999, 78, 999]:
    umnio.write_setting(data)
    time.sleep(1)
