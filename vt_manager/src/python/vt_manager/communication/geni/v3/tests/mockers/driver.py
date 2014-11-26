from vt_manager.communication.geni.v3.tests.mockers.resource import ResourceMocker

class VTAMDriverMocker():

    def __init__(self):
        pass

    def get_specific_server_and_vms(self, urn):
        resources = list()
        for i in range(0,10):
            r = ResourceMocker()
            r.set_component_id("this_is_a_urn_WITH_SLIVER_%d" %i)
            if i > 5:
                r.set_operational_state("geni_ready")
            else:
                r.set_operational_state("geni_failed")
            resources.append(r)
        return resources    

    def get_all_servers(self):
        resources = list()
        for i in range(0,5):
            r = ResourceMocker()
            r.set_component_id("this_is_a_urn_%d" %i)
            resources.append(r)
        return resources

    def create_vms(self, urn):
        resources = list()
        for i in range(0,2):
            r = ResourceMocker()
            r.set_component_id("this_is_a_urn_%d" %i)
            r.set_operational_state = "geni_notready"
            resources.append(r)
        return resources

    def reserve_vms(self, slice_urn, reservation, expiration=None):
        resources = list()
        for i in range(0,2):
            r = ResourceMocker()
            r.set_component_id("this_is_a_urn_%d" %i)
            resources.append(r)
        return resources

    def start_vm(self, urn):
        r = ResourceMocker()
        r.set_operational_state("geni_ready")
        return r 

    def stop_vm(self, urn):
        r = ResourceMocker()
        r.set_operational_state("geni_notready")
        return r

    def reboot_vm(self, urn):
        r = ResourceMocker()
        r.set_operational_state("geni_ready")
        return r

    def delete_vm(self, urn):
        r = ResourceMocker()
        r.set_operational_state("geni_notready")
        return r

    def renew_vms(self, expiration, urn):
        r = ResourceMocker()
        r.set_operational_state("geni_ready")
        return r

    def get_geni_best_effort_mode(self):
        return True

    def set_geni_best_effort_mode(self, value):
        return True


       
