from django.db import models
from expedient.clearinghouse.aggregate.models import Aggregate
from vt_plugin.models import VTServer


# Virtualization Plugin class
class VtPlugin(Aggregate):
    '''
    Virtualization Plugin that communicates the Virtualization Aggregate Manager with Expedient
    '''
    # VT Aggregate information field
    information = "An aggregate of VT servers "
    
    class Meta:
        app_label = 'vt_plugin'
        verbose_name = "Virtualization Aggregate"
    
    client = models.OneToOneField('xmlrpcServerProxy', editable = False, blank = True, null = True)


    def start_slice(self, slice):
        super(VtPlugin, self).start_slice(slice)
        try:
            from vt_plugin.controller.dispatchers.GUIdispatcher import startStopSlice
            startStopSlice("start",slice.uuid)
        except:
            raise

    def stop_slice(self, slice):
        super(VtPlugin, self).start_slice(slice)
        try:
            from vt_plugin.controller.dispatchers.GUIdispatcher import startStopSlice
            startStopSlice("stop",slice.uuid)
        except:
            raise
