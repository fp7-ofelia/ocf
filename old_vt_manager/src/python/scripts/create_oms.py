'''
Created on Jun 27, 2010

@author: jnaous
'''

from openflow.dummyom.models import DummyOM

def run():
    for om in DummyOM.objects.all():
        om.delete()
    for i in xrange(3):
        om = DummyOM.objects.create()
        om.populate_links(10, 20)
