#!/usr/bin/env python

import pexpect
from datetime import datetime
from time import time,sleep
from re import search, escape
from os import system


##############################################
############### SCAN SETTINGS ################
##############################################
logfile_name = "phasescan_log.txt" # note, log file is APPENDED, not overwritten
phase_array = [78, 92, 42, 70, 84, 34, 48, 76, 90, 40, 68, 82, 32, 46, 74, 88, 38, 66, 80, 30, 44, 72, 86, 36, 64]
transition_code = 999 # wrtitten to uMNIO during phase changes
seconds_per_phase = 300
loop = 100 # number of loops. loop = -1 for permanent looping
test_mode = 0 # if testmode == 1 then there are no actual writes to hardware


################################################
############### SERVER SETTINGS ################
################################################
host = "hcalngccm02"
port = 64000

def sendngFECcommands(cmds=['quit']):
        # HARDCODE FOR HE PHASE SCAN
        # host = "hcalngccm02"
        # port = 64000
        script = False
        raw = False

	# Arguments and variables
	output = []
	raw_output = ""
	# if script: 
	# 	print 'Using script mode'
	# else: 
	# 	print 'Not using script mode'

	# print cmds

	if host != False and port:		# Potential bug if "port=0" ... (host should be allowed to be None.)
		## Parse commands:
		if isinstance(cmds, str):
			cmds = [cmds]
		if not script:
			if "quit" not in cmds:
				cmds.append("quit")
		else:
			cmds = [c for c in cmds if c != "quit"]		# "quit" can't be in a ngFEC script.
			cmds_str = ""
			for c in cmds:
				cmds_str += "{0}\n".format(c)
			file_script = "ngfec_script"
			with open(file_script, "w") as out:
				out.write(cmds_str)
		
		# Prepare the ngfec arguments:
		ngfec_cmd = 'ngFEC.exe -z -c -p {0}'.format(port)
		if host != None:
			ngfec_cmd += " -H {0}".format(host)
		
		# Send the ngfec commands:
		p = pexpect.spawn(ngfec_cmd)

		if not script:
			for i, c in enumerate(cmds):
				if 'wait' in c:
					# waitTime = int(c.split()[-1])
					# sleep(waitTime/1000.)
					continue
				p.sendline(c)
				if c != "quit":
					t0 = time()
					p.expect("{0}\s?#((\s|E)[^\r^\n^#]*)".format(escape(c)))
					t1 = time()
#					print [p.match.group(0)]
					output.append({
						"cmd": c,
						"result": p.match.group(1).strip().replace("'", ""),
						"times": [t0, t1],
						"raw": p.before+p.after
					})
					raw_output += p.before + p.after
		else:
			p.sendline("< {0}".format(file_script))
			for i, c in enumerate(cmds):
				# Deterimine how long to wait until the first result is expected:
				if i == 0:
					timeout = max([30, int(0.2*len(cmds))])
#					print i, c, timeout
				else:
					timeout = 30		# pexpect default
#					print i, c, timeout
#				print i, c, timeout
				
				# Send commands:
				t0 = time()
				p.expect(["{0}\s?#((\s|E)[^\r^\n^#]*)".format(escape(c)),'bingo'], timeout=timeout)
				t1 = time()
#				print [p.match.group(0)]
				output.append({
					"cmd": c,
					"result": p.match.group(1).strip().replace("'", ""),
					"times": [t0, t1],
					"raw": p.before+p.after
				})
				raw_output += p.before + p.after
			p.sendline("quit")
		p.expect(pexpect.EOF)
		raw_output += p.before
#		sleep(1)		# I need to make sure the ngccm process is killed.
		p.close()
#		print "closed"
		if raw:
			return raw_output
		else:
			return output

def logResponse(responses,logfile):
        for response in responses:
                logline =  str(response["cmd"]) + " ===> " + str(response["result"]) + "  --  " + str(datetime.now())
                print logline
                logfile.write(logline + "\n")

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
        for phase in phase_array:

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
