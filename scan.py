#!/usr/bin/env python

import argparse, time
import fec_jm, umnio
import qie11_phases, tdc_thresholds


def applySetting(module, setting, test_mode=None, logfile=None):
    cmds1 = module.commands(setting, put=True)
    cmds2 = module.commands(setting, put=False)

    if test_mode:
        logfile.write("Test mode enabled. The following commands would be sent to the ngccm server otherwise:\n")
        for cmd in cmds1 + cmds2:
            logfile.write(cmd + "\n")
    else:
        fec_jm.sendAndLog(cmds1, logfile)
        fec_jm.sendAndLog(cmds2, logfile)
    logfile.write("############################################\n")


def parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", help="code written to uMNio during change of setting", metavar="N", type=int, default=999)
    parser.add_argument("--cycles", help="number of cycles (negative will permanently loop)", type=int, default=20)
    parser.add_argument("--logfile", help="log file to append to", default="scan_log.txt")
    parser.add_argument("--seconds", help="number of seconds to sleep per setting", type=int, default=300)
    parser.add_argument("--tdc-threshold", help="Scan TDC threshold rather than phase", action='store_true', default=False)
    parser.add_argument("--test-mode", help="Don't interact with hardware", action='store_true', default=False)
    return parser.parse_args()


def main(args):
    module = tdc_thresholds if args.tdc_threshold else qie11_phases

    while args.cycles:
        for setting in module.settings():
            logfile = open(args.logfile, "a")
            print("Writing value %d to uMNIO." % args.code)
            if not args.test_mode:
                umnio.write_setting(args.code)

            print("Applying setting: %d" % setting)
            applySetting(module, setting, test_mode=args.test_mode, logfile=logfile)

            print("Writing value %d to uMNIO." % setting)
            if not args.test_mode:
                umnio.write_setting(setting)

            print("...sleeping")
            time.sleep(args.seconds)

            print("####################################################################################")

            logfile.close()
        args.cycles -= 1


if __name__ == "__main__":
    args = parsed_args()
    try:
        main(args)
    except KeyboardInterrupt:
        pass

    if not args.test_mode:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Settings are still at the final scan value.")
        print("Configure a run to restore to default values.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
