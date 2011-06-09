from vt_manager.models import Slot, Mac
import thread
from django.db import models
import time
from vt_manager.controller.ifaceAllocators.SlotAllocator import SlotAllocator

MACallocatorMutex = thread.allocate_lock()

class MACallocator():    
    """
    Admins Host MACs
    """
    MIN_HOST = 1
    AM_ID_BITS = 6
    SLOT_ID_BITS = 9#7
    HOST_ID_BITS = 9#11
    
    @staticmethod
    def acquire(projectID, amID, sliceID, vmID, ifaceName, isMgmt = False):
        '''
        At this moment it always returns a new MAC for a host, the existence of project, slice and aggregate are made with SlotAllocator
        and MACalloctor always add a new host and mac for the (AM,project,slice) combination
        '''

        slot = SlotAllocator.acquire(projectID, amID, sliceID)
        mac = MACallocator.getMAC(slot, vmID, ifaceName, isMgmt)
        
        return mac.getMAC()
        
    @staticmethod
    def getMAC (slot, vmID, ifaceName, isMgmt):   
        mac = Mac()
        mac.setProjectID(slot.projectID)
        mac.setSliceID(slot.sliceID)
        mac.setAMid(slot.amID)
        mac.setAMslotID(slot.AMslotID)
        mac.setSlotID(slot.slotID)
        mac.setVMid(vmID)
        mac.ifaceName = ifaceName
        mac.isMgmt = isMgmt
        MACallocatorMutex.acquire()
        if (Mac.objects.filter(amID=slot.amID, projectID = slot.projectID) ):
            #if there is already a host for this AM and project
            #TODO check quantity of hosts
            mac.setHostID( int(max(Mac.objects.filter(amID=slot.amID, projectID = slot.projectID).values('HostID'))['HostID'])+1)
        else:
            mac.setHostID(MACallocator.MIN_HOST)
        mac.setMAC(MACallocator.macString(slot, mac))           
        mac.save()
        MACallocatorMutex.release()
        return mac

    @staticmethod
    def release(mac):
        MACallocatorMutex.acquire()
        mac.delete()
        MACallocatorMutex.release()


    @staticmethod
    def Denary2Binary(n,l):
        '''convert denary integer n to binary string bStr'''
        return str(bin(n))[2:].zfill(l)

    @staticmethod
    def Dec2Hex(n):
        return str(hex(n))[2:]

    @staticmethod
    def StrToInt(s):
        result=0
        for i in range(len(s)):
            result = result +int(s[i])* (int(s[i]) <<(len(s) -i))
        return result >>1

    @staticmethod
    def macString(slot, mac):
        add = '000000000001011000111110'+ MACallocator.Denary2Binary(slot.AMslotID, MACallocator.AM_ID_BITS) + MACallocator.Denary2Binary(slot.slotID, MACallocator.SLOT_ID_BITS)+ MACallocator.Denary2Binary(mac.HostID, MACallocator.HOST_ID_BITS)

        add2 = []
        for i in range(12):
            add2.append(add[i*4:i*4+4])
            add2[i]= str(hex(MACallocator.StrToInt(add2[i])))[2:]

        return add2[0]+add2[1]+':' +add2[2]+add2[3]+':'+add2[4]+add2[5]+':'+add2[6]+add2[7]+':'+add2[8]+add2[9]+':'+add2[10]+add2[11]

