#!/usr/bin/env python2

import time
import fec_jm


def send_commands(cmds, test_mode=None, logfile=None):
    if test_mode:
        for cmd in cmds:
            logfile.write(cmd + "\n")
    else:
        fec_jm.sendAndLog(cmds, logfile)


def cmds_one_channel(rbx, iRm, iBv, bv_off, bv_on):
    return ["put %s-%s-biasvoltage[1-48]_f 48*%d" % (rbx, iRm, bv_off),
            "put %s-%s-biasvoltage%d_f %d" % (rbx, iRm, iBv, bv_on),
            # "get %s-%s-biasmon[1-48]_f" % (rbx, iRm),
            ]


def one_rbx(rbx, seconds_per_setting, bv_off, bv_on, test_mode, logfile):
    for iRm in range(1, 5):
        for iBv in range(1, 49):
            send_commands(cmds_one_channel(rbx, iRm, iBv, bv_off, bv_on), test_mode, logfile)
            if seconds_per_setting:
                print "...sleeping"
                time.sleep(seconds_per_setting)

        send_commands(["put %s-%s-biasvoltage[1-48]_f 48*%d" % (rbx, iRm, bv_off)], test_mode, logfile)


def main():
    seconds_per_setting = 0
    loop = 1  # number of loops. loop = -1 for permanent looping
    test_mode = False  # if test_mode == True, then there are no actual writes to hardware
    set_up = True
    scan_individual = True
    deltaBx = 75
    iRbxFirst = 1
    iRbxLast = 18
    bv_off = 3071
    bv_on = 3480

    while loop:
        logfile = open("led_bv_channelscan_log.txt", "a")
        logfile.write("loop=%d\n" % loop)
        # first disable and delay all
        for iRbx in range(iRbxFirst, 1 + iRbxLast):
            if not set_up:
                continue
            for end in "MP":
                rbx = "HE%s%02d" % (end, iRbx)
                delay = 535 + deltaBx + 18 * deltaBx * (end == "P") + deltaBx * iRbx
                send_commands(["put %s-[1-4]-biasvoltage[1-48]_f 192*%d" % (rbx, bv_off),
                               # "get %s-[1-4]-biasmon[1-48]_f_rr" % rbx,
                               "put %s-pulser-led[A,B]-bxdelay 2*%d" % (rbx, delay),
                              ], test_mode, logfile)

        # then activate one at a time
        for iRbx in range(iRbxFirst, 1 + iRbxLast):
            if not scan_individual:
                continue
            for end in "MP":
                rbx = "HE%s%02d" % (end, iRbx)
                one_rbx(rbx, seconds_per_setting, bv_off, bv_on, test_mode, logfile)
        loop -= 1
        logfile.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

    print
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print "Bias voltages are still at the final scan values."
    print "Configure a run to restore the default values."
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
