'''
        @author: lbergesio

        Sever Monitoring. Basically the interface to speecific allowed admin shell commands to the
	system. Command outputs are parsed and returned as an instance of the server-type class of
	vtRspecInterface.
'''

import subprocess
import re 
import copy
from utils.Logger import Logger
#from settings.settingsLoader import *
#from settings.settingsLoader import FILEHD_NICE_PRIORITY,OXA_FILEHD_IONICE_CLASS, OXA_FILEHD_IONICE_PRIORITY

class ServerMonitoring:

	logger = Logger.getLogger()

#	@staticmethod
#        def subprocessCall(command, priority=OXA_FILEHD_NICE_PRIORITY, ioPriority=OXA_FILEHD_IONICE_PRIORITY, ioClass=OXA_FILEHD_IONICE_CLASS, stdout=None):
#                try:
#                        wrappedCmd = '/usr/bin/nice -n '+str(priority)+' /usr/bin/ionice -c '+str(ioClass)+' -n '+str(ioPriority)+' '+command
#                        FileHdManager.logger.debug('Executing: '+wrappedCmd)
#                        subprocess.check_call(wrappedCmd, shell=True, stdout=stdout)
#                except Exception as e:
#                        ServerMonitoring.logger.error('Unable to execute command: '+command)
#                        raise e
	@staticmethod
	def getTopStatistics(server):
		try:
			task=subprocess.Popen('/usr/bin/top -b -n1 | /bin/egrep "(Cpu|Mem)"',shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err=task.communicate()
                        if err:
				raise Exception(err)
		except:
			raise	
			
		## Parsing ##
		out = out.split('\n')
		for i,o in enumerate(out):
			ot = re.sub('\x1b.*?(m|$|\[K)', '', o)
			ot = ot.replace('Cpu(s):','').replace(' ','')
			ot = ot.replace('Mem:','')
			ot = ot.split(',')
			for j,ot2 in enumerate(ot):
				m = re.compile("%..").findall(ot2)
				if m:
					ot2 = ot2.replace(m[0],'')
				ot[j] =  re.match('[0-9]*\.*[0-9]*', ot2 ).group(0)
			out[i] = ot
			ServerMonitoring.logger.error(out[i][0])

		## Populating server-rspec structure ##
		## out2 = [
		## 'Cpu(s):  7.3%us,  1.9%sy,  0.0%ni, 89.8%id,  0.9%wa,  0.0%hi,  0.0%si,  0.0%st', 
		## 'Mem:   4019680k total,  3640424k used,   379256k free,   322516k buffers', '']
		ServerMonitoring.logger.error("\n\n\nLEODEBUG OUTPUT")
		ServerMonitoring.logger.error(out)
		cpu = server.status.cpu
		cpu.user = float(out[0][0])
		cpu.sys= float(out[0][1])
		cpu.idle = float(out[0][3])
		mem = server.status.memory
		mem.used = long(out[1][1])
		mem.free = long(out[1][2])
		mem.total = long(out[1][0])
		mem.buffers = long(out[1][3])
		ServerMonitoring.logger.error("\n\n\nLEODEBUG OUTPUT COMANDO")
		ServerMonitoring.logger.error(str(cpu.user))
		ServerMonitoring.logger.error(str(cpu.sys))
		ServerMonitoring.logger.error(str(cpu.idle))
		ServerMonitoring.logger.error(str(mem.used))
		ServerMonitoring.logger.error(str(mem.free))
		ServerMonitoring.logger.error(str(mem.total))
		ServerMonitoring.logger.error(str(mem.buffers))

		return server


	@staticmethod
	def getDfStatistics(server):
		exceptions = ["none", "tmpfs", "udev"]
		cmd = "/bin/df | /usr/bin/tail -n +2 "
		for exc in exceptions:
			cmd = cmd + " | /bin/grep -v "+exc

		try:
			task=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err=task.communicate()
                       
			if err:
				raise Exception(err)
		except:
			raise	
		## Parsing ##
		out = out.split('\n')
		out = [o.split() for o in out if o is not '']
		#[['/dev/sda5', '18491260', '14654748', '2897200', '84%', '/'], 
		#['/dev/sda3', '223734304', '123910524', '99823780', '56%', '/media/OS']]
		model_partition = copy.deepcopy(server.status.hd_space.partition[0])
		partition = server.status.hd_space.partition
		partition.pop()
		
		for o in out:
			part = copy.deepcopy(model_partition)
			part.name = o[0]
			part.size= long(o[1])
			part.used = long(o[2])
			part.available = long(o[3])
			part.used_ratio = int(o[4].replace('%',''))
			partition.append(part)
		return server

			
