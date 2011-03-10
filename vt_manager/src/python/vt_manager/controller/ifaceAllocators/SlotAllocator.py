from vt_manager.models import Slot
import thread
from django.db import models
import time

SlotAllocatorMutex = thread.allocate_lock()

class SlotAllocator():
    """
    Admins Project slots
    """
 
    MIN_SLOT = 1
    global SlotAllocatorMutex #as mutex

    @staticmethod
    def acquire(projectID, amID, sliceID):
        slot = Slot()
        if Slot.objects.filter(amID=amID):
            slot.setAMslotID( int(Slot.objects.filter(amID=amID)[0].AMslotID)   )
            #slot.setAMslotID( int(Slot.objects.get(amID=amID).AMslotID)   )
        else:
            slot.setAMslotID(SlotAllocator.MIN_SLOT)


        if Slot.objects.filter(projectID=projectID, sliceID=sliceID):
            return Slot.objects.get(projectID=projectID, sliceID=sliceID)
        else:# project or slice do not exist
            slot.setProjectID(projectID)
            slot.setSliceID(sliceID)
            slot.setAMid(amID)
            print SlotAllocatorMutex.locked()
            SlotAllocatorMutex.acquire()
            SlotAllocator.allocate(slot, projectID)
            SlotAllocatorMutex.release()
            return slot
    
    @staticmethod
    def release(projectID, amID, sliceID):
        Slot.objects.filter(projectID=projectID, sliceID=sliceID, amID = amID).delete()


    @staticmethod
    def allocate(slot, projectID):
        #TODO Not taking into account if it is a different AM slotID can start from zero again
        #TODO Not taking into account number limitations (256 AMs and 256 slotsID)
        
        if not Slot.objects.count():
            slot.setSlotID(SlotAllocator.MIN_SLOT)
            slot.id=1
        
        else:
            free = 0
            for iSlot in range(1, int(Slot.objects.all().order_by('-id')[0].id)+1):
                if not Slot.objects.filter(id=iSlot):
                    free = 1
                    break
        
            #Check if there are not free
            if not free :
                iSlot = iSlot +1
            slot.id=iSlot
            #check if project is alredy present to set the same slotID
            if Slot.objects.filter(projectID=projectID):
                slot.setSlotID(Slot.objects.filter(projectID=projectID)[0].slotID)
            else:
                freeSlot=0
                #if the MIN_SLOT is not used, then that is the one to set 
                if int(min(Slot.objects.all().values('slotID'))['slotID']) > SlotAllocator.MIN_SLOT:
                    freeSlot = SlotAllocator.MIN_SLOT
                else:
                    for index in range( 0 , int(Slot.objects.count())-1 ):
                        if int(Slot.objects.order_by('slotID')[index].slotID)+1 < int(Slot.objects.order_by('slotID')[index+1].slotID):
                            freeSlot = int(Slot.objects.order_by('slotID')[index].slotID)+1
                            break
                        else:
                            freeSlot = int(Slot.objects.order_by('-slotID')[0].slotID)+1
                slot.setSlotID(freeSlot)
        slot.save()
       


 
