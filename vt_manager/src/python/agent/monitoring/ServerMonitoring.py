'''
        @author: lbergesio

        Sever Monitoring. Basically the interface to speecific allowed admin shell commands to the
	system. Command outputs are parsed and returned as an instance of the server-type class of
	vtRspecInterface.
'''

import subprocess
import re 

class ServerMonitoring:

	@staticmethod
	def getTopStatics(server):
		task=subprocess.Popen('top -n1 | egrep "(Cpu|Mem)"',shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err=task.communicate()

		## Parsing ##
		out = out.split('\n')
		for i,o in enumerate(out):
			out[i] = re.sub('\x1b.*?(m|$|\[K)', '', o) 	


		## Populating server-rspec structure ##
		## out2 = [
		## 'Cpu(s):  7.3%us,  1.9%sy,  0.0%ni, 89.8%id,  0.9%wa,  0.0%hi,  0.0%si,  0.0%st', 
		## 'Mem:   4019680k total,  3640424k used,   379256k free,   322516k buffers', '']
		cpu = server.status.cpu
		cpu.user = out[0][0]				
		cpu.sys= out[0][1]				
		cpu.idle = out[0][3]				
		mem = server.status.memory
		mem.used = out[1][1]
		mem.free = out[1][2]
		mem.total = out[1][0]
		mem.buffers = out[1][3]

		return server


	@staticmethod
	def getTopStatics(server):
		exceptions = ["none", "tmpfs", "udev"]
		cmd = "df | tail -n +2 "
		for exc in exceptions:
			cmd = cmd + " | grep -v "+exc

		task=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err=task.communicate()

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
			part.size= o[1]
			part.used = o[2]
			part.available = o[3]
			part.used_ratio = o[4].replace('%','')
			partition.append(part)

		return server

			
