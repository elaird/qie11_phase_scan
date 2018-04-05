import pexpect
from datetime import datetime
from time import time,sleep
from re import search, escape

# Author: J. Mariano, 2017 #

################################################
############### SERVER SETTINGS ################
################################################
ngfec = "/nfshome0/hcalpro/ngFEC/ngFEC.exe"
host = "hcalngccm02"
port = 64000

def sendngFECcommands(cmds=['quit']):
        # HARDCODE FOR HE PHASE SCAN
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
		ngfec_cmd = '{0} -z -t -c -p {1}'.format(ngfec, port)
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
                                        try:
                                                p.expect("{0}\s?#((\s|E)[^\r^\n^#]*)".format(escape(c)))
                                        except pexpect.EOF:
                                                print "Caught problem with", c
                                                continue
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


def sendAndLog(cmds, logfile):
        logResponse(sendngFECcommands(cmds), logfile)
