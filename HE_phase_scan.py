#!/usr/bin/env python

from time import sleep
from os import system
import qie11_phase_scan as qps

from fec_jm import sendngFECcommands, logResponse

##############################################
############### SCAN SETTINGS ################
##############################################
logfile_name = "phasescan_log.txt" # note, log file is APPENDED, not overwritten
transition_code = 999 # wrtitten to uMNIO during phase changes
seconds_per_phase = 300
loop = 100 # number of loops. loop = -1 for permanent looping
test_mode = 0 # if testmode == 1 then there are no actual writes to hardware


def setPhase(phase):
	logfile = open(logfile_name,"a")
        if (test_mode != 1):
                logResponse(sendngFECcommands(["put HEP17-[1-4]-QIE[1-48]_PhaseDelay 192*" + str(phase),"put HEP17-[1-4]-Qie[1-48]_ck_ph 192*" + str(phase)]),logfile)
                logResponse(sendngFECcommands(["get HEP17-[1-4]-QIE[1-48]_PhaseDelay_rr","get HEP17-[1-4]-Qie[1-48]_ck_ph_rr"]),logfile)
        else:
                logfile.write("Test mode enabled. The following commands would be sent to the ngccm server otherwise:\n")        
                logfile.write("put HEP17-[1-4]-QIE[1-48]_PhaseDelay 192*" + str(phase))
                logfile.write("put HEP17-[1-4]-Qie[1-48]_ck_ph 192*" + str(phase))
                logfile.write("get HEP17-[1-4]-QIE[1-48]_PhaseDelay_rr")
                logfile.write("get HEP17-[1-4]-Qie[1-48]_ck_ph_rr")
        logfile.write("############################################\n")
	logfile.close()

system("touch " + logfile_name)

umnio_script = "umnio_script.%d" % transition_code
print "Generating uMNIO script for phase " + str(transition_code) + " {transition}." 
system("cat umnio_user_data.template | sed s@PHASE_SETTING@%d@ > %s " % (transition_code, umnio_script))

while (loop != 0):
        for phase in qps.settings():

                print "Writing phase " +  str(transition_code) + " {transition} to uMNIO."
                system("uMNioTool.exe hcal-uhtr-38-12 -o controlhub-hcal-daq -s %s" % "umnio_script." + str(transition_code))
                
                print "Setting phase: " + str(phase)
                setPhase(phase)
                
                umnio_script = "umnio_script.%d" % phase
                if (test_mode != 1):
                        system("cat umnio_user_data.template | sed s@PHASE_SETTING@%d@ > %s " % (phase, umnio_script))
                
                print "Writing phase " + str(phase) + " to uMNIO."
                if (test_mode != 1):
                        system("uMNioTool.exe hcal-uhtr-38-12 -o controlhub-hcal-daq -s %s" % umnio_script)
                
                print "...sleeping"
                sleep(seconds_per_phase)
                
                print "####################################################################################"

                loop =  loop - 1

print "Phase scan complete. Cleaning temporary uMNIO scripts."
print
print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
print
print "Phases are still in the final scan value."
print "Configure a run to restore to default values."
print
print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
