#!/usr/bin/env python

import time
import fec_jm, qie11_phase_scan, umnio

##############################################
############### SCAN SETTINGS ################
##############################################
logfile_name = "phasescan_log.txt" # note, log file is APPENDED, not overwritten
transition_code = 999  # wrtitten to uMNIO during phase changes
seconds_per_phase = 10
loop = 100  # number of loops. loop = -1 for permanent looping
test_mode = False  # if test_mode == True, then there are no actual writes to hardware
igloo = True  # write phases not only to QIEs but also to igloos


def setPhase(phase):
        cmds1 = qie11_phase_scan.commands(phase, put=True, igloo=igloo)
        cmds2 = qie11_phase_scan.commands(phase, put=False, igloo=igloo)

        if test_mode:
                logfile.write("Test mode enabled. The following commands would be sent to the ngccm server otherwise:\n")        
                for cmd in cmds1 + cmds2:
                        logfile.write(cmd)
        else:
                fec_jm.sendAndLog(cmds1, logfile)
                fec_jm.sendAndLog(cmds2, logfile)
        logfile.write("############################################\n")

logfile = open(logfile_name, "a")

while (loop != 0):
        for phase in qie11_phase_scan.settings():
                print "Writing phase " + str(transition_code) + " to uMNIO."
                if not test_mode:
                        umnio.write_setting(transition_code)
                
                print "Setting phase: " + str(phase)
                setPhase(phase)
                
                print "Writing phase " + str(phase) + " to uMNIO."
                if not test_mode:
                        umnio.write_setting(phase)
                
                print "...sleeping"
                time.sleep(seconds_per_phase)
                
                print "####################################################################################"

                loop =  loop - 1
logfile.close()

print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
print
print "Phases are still in the final scan value."
print "Configure a run to restore to default values."
print
print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
