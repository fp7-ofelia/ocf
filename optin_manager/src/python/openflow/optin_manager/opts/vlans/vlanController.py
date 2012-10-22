from openflow.optin_manager.opts.models import Experiment
from openflow.optin_manager.opts.models import OptsFlowSpace
from django.conf import settings

settings.UNALLOWED_VLANS=list(set(settings.UNALLOWED_VLANS+[0,4096]))

class vlanController():

    @staticmethod
    def get_requested_vlans_by_experiment(exp):
        '''
        Returns the VLAN tags requested by the experiment exp. exp can be an id or an instance.
        '''
        requested_vlans = {}
 
        if not isinstance(exp, Experiment):
            try:
                exp = Experiment.objects.get(id=exp)
            except:
                raise Exception("vlanController could not find Experiment")

        vranges =  [x for x in exp.experimentflowspace_set.values_list('vlan_id_s','vlan_id_e').distinct()]
        requested_vlans['ranges'] = [(int(x[0]),int(x[1])) for x in vranges]
        requested_vlans['values'] = sum([range(x[0],x[1]+1) for x in vranges],[])
        return requested_vlans

    @staticmethod
    def get_requested_vlans_by_all_experiments():
        requested_vlans = {}
        vranges = {}
        for exp in Experiment.objects.all():
            vranges[int(exp.id)] =  [x for x in exp.experimentflowspace_set.values_list('vlan_id_s','vlan_id_e').distinct()]
            requested_vlans[int(exp.id)]=sum([range(x[0],x[1]+1) for x in vranges[int(exp.id)]],[])
        return requested_vlans


    @staticmethod
    def get_allocated_vlans():
    
        used_vlans = sum([range(x[0],x[1]+1) for x in OptsFlowSpace.objects.all().values_list('vlan_id_s','vlan_id_e').distinct()],[])
        used_vlans.sort()
        return used_vlans

    @staticmethod
    def get_allocated_vlans_sorted():
        used_vlans = vlanController.get_allocated_vlans()
        sorted_vlans = [0 for x in xrange(4)] 
        sorted_vlans[0] = [x for x in used_vlans if x <= 1000]
        sorted_vlans[1] = [x for x in used_vlans if x > 1000 and x <= 2000]
        sorted_vlans[2] = [x for x in used_vlans if x > 2000 and x <= 3000]
        sorted_vlans[3] = [x for x in used_vlans if x > 3000]
        return sorted_vlans

    @staticmethod
    def offer_vlan_tags(set=None):
        if not set:
            return [x for x in range(1,4096) if x not in vlanController.get_allocated_vlans() and x not in settings.UNALLOWED_VLANS]
        elif set in range(1,4095):
            return [x for x in range(1,4096) if x not in vlanController.get_allocated_vlans() and x not in settings.UNALLOWED_VLANS][:set]  
      
        
