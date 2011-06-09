from vt_manager.controller.SlotAllocator import SlotAllocator, SlotAllocatorLocker
from vt_manager.models import Slot
from threading import Thread
import sys

def func1():
    c = SlotAllocatorLocker()
    a = c.acquire("first", "am1", "s1")
    

def func2():
    l = SlotAllocator()
    b = l.acquire("second", "am1", "s1")
    


t1= Thread(target=func1)
t2 = Thread(target=func2)
t1.start()
t2.start()
