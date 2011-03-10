import thread
from django.db import models
import time
from vt_manager.controller.ifaceAllocators.MacAllocator import MACallocator
from vt_manager.models import Ip, VTServer

IPallocatorMutex = thread.allocate_lock()

class IPallocator():

    MIN_HOST = 1
    AM_ID_BITS = 6
    HOST_ID_BITS = 26
    

    @staticmethod
    def setSlots(ip, projectID, amID, sliceID, vmID):
        '''
        '''
        IPallocatorMutex.acquire()
        
        if not Ip.objects.all():
            ip.setAMslotID(IPallocator.MIN_HOST)
            ip.setHostID(IPallocator.MIN_HOST)        

        #if there is already a slot for the AM then look for the host part of the ip
        elif Ip.objects.filter(amID = amID):
            ipsWithAMid = Ip.objects.filter(amID = amID)
            ip.setAMslotID(ipsWithAMid[0].AMslotID)
            
            #from the MIN_HOST to the MAX present, look for one is free
            for i in range(IPallocator.MIN_HOST, max(ipsWithAMid.values('hostID'))['hostID']+1):
                if not Ip.objects.filter(amID = amID, hostID = i):
                    ip.setHostID(i)
                    break
            #if the index i is equal to the max host, it is because there was none free, so host should be the following
            if i == max(ipsWithAMid.values('hostID'))['hostID'] :
                ip.setHostID(i+1)
            
        else:
            maxAMslotID = max(Ip.objects.values('AMslotID'))['AMslotID']
            for i in range(IPallocator.MIN_HOST, maxAMslotID+1):
                if not Ip.objects.filter(AMslotID = i):
                    ip.setAMslotID(i)
                    break
            if i == maxAMslotID:
                ip.setAMslotID(i+1)
            
            ip.setHostID(IPallocator.MIN_HOST)

        IPallocatorMutex.release()

    @staticmethod
    def acquire(serverID, projectID, amID, sliceID, vmID, ifaceName, isMgmt):
        
        try:
            server = VTServer.objects.get(name = serverID)
        except Exception as e:
            print "[EXCEPTION]  No Server with name %s" % serverID
            print e
            return       

        ip = Ip()
        ip.setProjectID(projectID)
        ip.setSliceID(sliceID)
        ip.setAMid(amID)
        ip.setVMid(vmID)
        ip.setServerID(serverID)
        ip.ifaceName = ifaceName
        ip.isMgmt = isMgmt
        IPallocator.setSlots(ip, projectID, amID, sliceID, vmID)
        ip.setIp(IPallocator.ipString(server.ipRange, ip.AMslotID, ip.hostID))

        ip.gw = server.getGW()
        ip.mask = server.getMask()
        ip.dns1 = server.getDNS1()
        ip.dns2 = server.getDNS2()
        print "%s %s %s %s" %(ip.gw,ip.mask,ip.dns1,ip.dns2)
        ip.save()
        return ip

    @staticmethod
    def release(ip):
        IPallocatorMutex.acquire()
        #if ip instance
        ip.delete()
        IPallocatorMutex.release()

    



    @staticmethod
    def ipString(serverRange, AMslotID, hostID):

        s = str(serverRange)
        s = s.split('.')
        prefix = ''
        for p in s:
            if p is not '0':
                prefix = prefix + MACallocator.Denary2Binary(int(p) ,8)         
        
        add = prefix + MACallocator.Denary2Binary(AMslotID, IPallocator.AM_ID_BITS) + MACallocator.Denary2Binary(hostID, IPallocator.HOST_ID_BITS - len(prefix))
        add2 = []
        for i in range(4):
            add2.append(add[i*8:i*8+8])          
            add2[i]= str(MACallocator.StrToInt(add2[i]))
        return add2[0]+ '.'+ add2[1] + '.' + add2[2] + '.' + add2[3]                    
