#!/usr/bin/env python

# Original author: J. Mariano #
# Refactored Oct. 2017 #

import time
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


def main():
    transition_code = 999  # written to uMNIO during changes of setting
    seconds_per_setting = 300
    nCycles = 20  # number of scan cycles (a negative number will cause permanent looping)
    test_mode = True  # if test_mode == True, then there are no actual writes to hardware
    module = qie11_phases
    # module = tdc_thresholds

    while nCycles:
        for setting in module.settings():
            logfile = open("phasescan_log.txt", "a")
            print("Writing value %d to uMNIO." % transition_code)
            if not test_mode:
                umnio.write_setting(transition_code)

            print("Applying setting: %d" % setting)
            applySetting(module, setting, test_mode=test_mode, logfile=logfile)

            print("Writing value %d to uMNIO." % setting)
            if not test_mode:
                umnio.write_setting(setting)

            print("...sleeping")
            time.sleep(seconds_per_setting)

            print("####################################################################################")

            logfile.close()
        nCycles -= 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("Settings are still at the final scan value.")
    print("Configure a run to restore to default values.")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
