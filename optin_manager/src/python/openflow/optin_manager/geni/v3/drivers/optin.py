from am.rspecs.src.geni.v3.openflow.container.group import Group
from am.rspecs.src.geni.v3.openflow.container.match import Match
from am.rspecs.src.geni.v3.openflow.container.flowspace import FlowSpace
from am.rspecs.src.geni.v3.openflow.container.dpid import DPID
from am.rspecs.src.geni.v3.openflow.container.link import Link
from am.rspecs.src.geni.v3.openflow.container.port import Port
from am.rspecs.src.geni.v3.openflow.container.controller import Controller

from geniutils.src.xrn.xrn import hrn_to_urn
from geniutils.src.xrn.xrn import urn_to_hrn

from openflow.optin_manager.opts.models import Experiment
from openflow.optin_manager.opts.models import ExperimentFLowSpace
from openflow.optin_manager.opts.models import Reservation
from openflow.optin_manager.opts.models import ReservationFlowSpace
from openflow.optin_manager.opts.models import ExpiringFlowSpaces


from openflow.optin_manager.geni.v3.utils.optin import OptinUtils
from openflow.optin_manager.geni.v3.utils.sliver import SliverUtils
from openflow.optin_manager.geni.v3.utils.flowvisor import FlowVisorWrap

from openflow.optin_manager.xmlrpc_server.models import FVServerProxy

import threading
import copy
import uuid

import traceback
import random
from datetime import datetime
from datetime import timedelta
import dateutil.parser
import re

class OptinDriver:

    def __init__(self):
        self.__geni_best_effort_mode = True
        self.__mutex = threading.Lock()
        self.GENI_ALLOCATED = "geni_allocated"
        self.GENI_UNALLOCATED = "geni_unallocated"
        self.GENI_PROVISIONED = "geni_provisioned"
        self.GENI_READY = "geni_ready"
        self.GENI_NOT_READY = "geni_notready"
        self.GENI_CONFIGURING = "geni_configuring"
        self.GENI_FAILED = "geni_failed"
        
        self.PENDING_OF_PROVISION = "Pending of Provisioning"
        self.PENDINF_OF_APPROVAL = "Pending of Approval"

        self.__config = None
        self.__sliver_manager = SliverUtils

    def get_version(self):
        #TODO Add F4F Extensions
        #TODO Add FELIX Extesions, if any
        version = {"urn" : self.__generate_component_manager_id()}
    

    def get_specific_devices(self, urn,geni_available=True):
        try:
            urn = self.__generate_sliver_urn_from_slice_urn(urn)
            #flowspace = FlowSpace()
            #exps = ExperimentFLowSpace.objects.filter(slice_urn = urn)
            #exp = exps[0].exp
            #return self.__parse_to_fs_object(urn, exp, exps)
            return self.__convert_to_resource(urn)
        except Exception as e:
            import traceback
            traceback.print_exc()    

    def __get_specific_devices(self, urn, geni_available=True):
        fv_wrap = FlowVisorWrap()
        fspaces = fv_wrap.flow_space_by_slice(urn)
        formatted_fs = dict()
        for fspace in fspaces:
            if fs[dpid] in formatted_fs.keys():
                if not fs["match"]["in_port"] in formatted_fs[dpid]["ports"]:
                    formatted_fs[dpid]["ports"].append(fs["match"]["in_port"])
                if not fs["match"]["headers"] in  formatted_fs[dpid]["match"]:
                    formatted_fs[dpid]["match"].append(fs["match"]["headers"])
            else:
                formatted_fs[dpid]["ports"] = [fs["match"]["in_port"]]
                formatted_fs[dpid]["matches"] = [fs["match"]["headers"]]
               
        flowspace = self.__flowvisor_fs_to_instance(formatted_fs)

    def __flowvisor_fs_to_instance(self, fs_dict):
        flowspace = FlowSpace()
        group = Group()
        for datapath in fs_dict.keys():
            dpid = DPID()
            dpid.datapath = datapath
            for port in fs_dict[datapath]["ports"]: 
                of_port = Port()
                of_port.set_num(port)
                dpid.add_port(of_port)
            group.add_dpid(dpid)
            for match in fs_dict[datapath]["matches"]:
                of_match = Match()
                if match.has_key("dl_vlan"):
                    of_match.add_dl_vlan(match["dl_vlan"])
                    group.add_match(of_match)
        flowspace.set_group(group) 
        return flowspace

    def get_all_devices(self, geni_available = True):
        devices = list()
        devices.extend(self.__get_switches())
        devices.extend(self.__get_links()) 
        return devices
    
    def create_flowspace(self, urn, expiration=None, users=list(), geni_best_effort=True):
        try:
            urn = self.__generate_sliver_urn_from_slice_urn(urn)
            params = self.__urn_to_fs_params(urn)
            #res = Reservation.objects.filter(slice_urn=urn)[0] 
            res = Reservation.objects.filter(**params)[0]       
            rfs = res.reservationflowspace_set.all()#ReservationFlowSpace.objects.filter(urn=urn)
            slivers = self.__get_create_slice_params(rfs)
            self.__sliver_manager.create_of_sliver(urn, res.project_name, res.project_desc, res.slice_name, res.slice_desc, res.controller_url, res.owner_email, res.owner_password, slivers) 
            ExpiringFlowSpaces(slice_urn=urn, expiration=expiration).save()
            manifest = self.__convert_to_resource(urn, expiration)
            rfs.delete()
            res.delete()
        except Exception as e:
            print traceback.print_exc()
            raise e
        #manifest = self.__convert_to_resource(urn) 
        return manifest 
    
    def reserve_flowspace(self, slice_urn, reservation, expiration=None, users=list()):
        try:
            if not expiration:
                expiration = datetime.utcnow() + timedelta(hours=1)
            
            reservation_params = self.__get_experiment_params(reservation,slice_urn) 
            #reservation_params['slice_urn'] = slice_urn
            r = Reservation(**reservation_params)
            r.expiration = expiration
            r.save()

            for group in reservation.get_groups():
                for dpid in group.get_dpids():
                    for port in dpid.get_ports():
                        for match in group.get_matches():
                            req_params = self.__translate_to_flow_space_model(match, dpid, port)
                            for param in req_params:
                                param = self.__format_params_to_reservation_model(param)
                                reservation_flowspace = ReservationFlowSpace(**param)
                                reservation_flowspace.dpid = dpid.get_datapath()           
                                reservation_flowspace.res = r
                                reservation_flowspace.expiration = expiration
                                reservation_flowspace.slice_urn = slice_urn
 
                                reservation_flowspace.save()
        except Exception as e:
            print traceback.print_exc()
            raise e
        reservation.set_urn(reservation_params["slice_urn"])
        reservation.set_state("Pending of Provision")

        reservation.set_expiration(expiration)
        reservation.set_allocation_status(self.GENI_ALLOCATED)
        reservation.set_operational_status(self.GENI_NOT_READY)
        return reservation 
    
    def renew_fs(self, urn, expiration):
        urn = self.__generate_sliver_urn_from_slice_urn(urn)
        flowspaces = ExpiringFlowSpaces.objects.filter(slice_urn=urn)
#        if flowspaces:
#            flowspace = flowspaces[0]
        for flowspace in flowspaces:
            flowspace.expiration = expiration
            flowspace.save()
	    return self.__convert_to_resource(urn, expiration)
        else:
            reservations = Reservation.objects.filter(slice_urn=urn)
#            if reservations:
                #reservation = reservations[0]
            for reservation in reservations:
                reservation.expiration = expiration
                reservation.save()
                return self.__convert_to_resource(urn, expiration)
        raise Exception("Sliver not Found")
   
    def start_flow_space(self, urn):
        return self.__crud_flow_space(urn, "start") 

    def stop_flow_space(self, urn):
        return self.__crud_flow_space(urn, "stop")

    def reboot_flow_space(self, urn):
        return self.__crud_flow_space(urn, "reboot")

    def delete_flow_space(self, urn):
        return self.__crud_flow_space(urn, "delete")

    def get_geni_best_effort_mode(self):
        return self.__geni_best_effort_mode

    def set_geni_best_effort_mode(self, value):
        self.__geni_best_effort_mode = value

    def __get_geni_status(self, urn):
        urn = self.__generate_sliver_urn_from_slice_urn(urn)
        exps = Experiment.objects.filter(slice_urn=urn)
        if exps:
            exp_fss = exps[0].experiementflowspace_set.all()
            opts = exps[0].useropts_set.all()
            opts_fs = opts[0].optsflowspace_set.all()
            if len(opts_fs) == len(exp_fss):
                return self.GENI_READY, self.GENI_PROVISIONED
            else:
                return self.GENI_NOT_READY, self.GENI_PROVISIONED

        res = Reservation.objects.filter(slice_urn = urn)
        if res:
            return self.GENI_NOT_READY, self.GENI_ALLOCATED
        raise Exception("Slice Does Not Exists")    

    def __crud_flow_space(self, urn, action):
        """
        PerformOperationalAction-related logic.
        """
        try:
            urn = self.__generate_sliver_urn_from_slice_urn(urn)
            slivers = self.__convert_to_resource(urn)
            prov_status, alloc_status = self.__get_geni_status(urn)
            # Special case for deleting allocated slivers
            if alloc_status == self.GENI_ALLOCATED and action == "delete":
#                res = Reservation.objects.filter(slice_urn=urn)[0]
                reservations = Reservation.objects.filter(slice_urn=urn)
                for res in reservations:
                    rfs = res.reservationflowspace_set.all()
                    rfs.delete()
                    res.delete()
                efs = ExpiringFlowSpaces.objects.filter(slice_urn=urn)
                efs.delete()
                # Needed for coherent output
                slivers.set_operational_status(self.GENI_NOT_READY)
                slivers.set_allocation_status(self.GENI_UNALLOCATED)
                return slivers
            if not alloc_status == self.GENI_PROVISIONED:
                raise Exception("Operational Actions can be only performed to provisioned slivers")
            if action == "delete":
                efs = ExpiringFlowSpaces.objects.filter(slice_urn=urn)
                efs.delete()
                self.__sliver_manager.delete_of_sliver(urn)
                slivers.set_operational_status(self.GENI_NOT_READY)
                slivers.set_allocation_status(self.GENI_UNALLOCATED)
            elif action == "start" or action == "reboot":
                if not prov_status in [self.GENI_READY, self.GENI_CONFIGURING]:
                    self.__sliver_manager.opt_in(urn)
                    prov_status, alloc_status = self.__get_geni_status(urn)
                    slivers.set_operational_status(prov_status)
                    slivers.set_allocation_status(alloc_status)
            elif action == "stop":
                self.__sliver_manager.opt_out(urn)
                slivers.set_operational_status(self.GENI_NOT_READY)
                slivers.set_allocation_status(self.GENI_PROVISIONED)
                expiring_fs = ExpiringFlowSpaces.objects.filter(slice_urn=urn)[0]
                if prov_status == self.GENI_READY:  
                    expiring_fs.was_granted = True
                    expiring_fs.save()
            return slivers
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e

    def __convert_to_resource(self, urn, expiration=None):
        sliver_urn = self.__generate_sliver_urn_from_slice_urn(urn)
        exps = Experiment.objects.filter(slice_urn=urn)
        if expiration:
            expiration = str(expiration)
        if exps:
            experiment = exps[0]
            if not expiration:
                expiration = ExpiringFlowSpaces.objects.filter(slice_urn=experiment.slice_urn)[0].expiration
            efs = experiment.experimentflowspace_set.all()     
            return self.__parse_to_fs_object(urn, experiment, efs, expiration)
        elif Reservation.objects.filter(slice_urn=urn):
            reservation = Reservation.objects.filter(slice_urn=sliver_urn)[0]
            if not expiration:
                expiration = reservation.expiration
            efs = reservation.reservationflowspace_set.all()
            return self.__parse_to_fs_object(sliver_urn, reservation, efs, expiration, slice_urn=urn)
        return None

    def __parse_to_fs_object(self,urn=None, experiment=None, exp_flowspace=None, expiration=None, slice_urn=None):
        flowspace = FlowSpace()
        flowspace.set_description(experiment.slice_desc)
        flowspace.set_urn(urn)
        flowspace.set_email(str(experiment.owner_email))
        flowspace.set_slice_urn(urn) # slice_urn == urn (optin)
        flowspace.set_state(self.GENI_NOT_READY)
        provisioning_status, allocation_status = self.__get_geni_status(urn)
        flowspace.set_allocation_status(allocation_status)
#        flowspace.set_expiration(self.__get_slice_expiration(expiration))
        flowspace.set_operational_status(provisioning_status)
        flowspace.set_expiration(expiration)
        controller = Controller()
        controller.parse_url(experiment.controller_url)
        flowspace.set_controller(controller)
        return flowspace

    def __get_geni_status(self, urn):
        exps = Experiment.objects.filter(slice_urn=urn)
        if exps:
            exp_fss = exps[0].experimentflowspace_set.all()
            opts = exps[0].useropts_set.all()
            if opts:
                opts_fs = opts[0].optsflowspace_set.all()
                return self.GENI_READY, self.GENI_PROVISIONED
            else:
                return self.GENI_NOT_READY, self.GENI_PROVISIONED
        res = Reservation.objects.filter(slice_urn = urn)
        if res:
            return self.GENI_NOT_READY, self.GENI_ALLOCATED
        raise Exception("Slice Does Not Exist")

    def __get_switches(self):
        fv =  FVServerProxy.objects.all()[0]
        switches = fv.get_switches()
        return self.__parse_to_switches(switches) 
    
    def __get_links(self):
        fv =  FVServerProxy.objects.all()[0]
        links = fv.get_links()
        return self.__parse_to_links(links) 
   
    def __parse_to_switches(self, switches):
        dpids = list()
        for switch in switches:
            dpid = DPID()
            dpid.set_datapath(switch[0])
            dpid.set_ports(self.__parse_to_ports(switch[1])) 
            dpid.set_component_manager_id(self.__generate_component_manager_id(dpid))
            dpid.set_component_id(self.__generate_dpid_component_id(dpid))
            dpid.set_type("Device")
            dpids.append(dpid)
        return dpids

    def __parse_to_ports(self, ports):
        port_list = ports["portNames"].split(',')
        dpid_ports = list()
        for port in port_list: 
            dpid_port = Port()
            match = re.match(r'[\s]*(.*)\((.*)\)', port)
            dpid_port.set_name(match.group(1))
            dpid_port.set_num(match.group(2))
            dpid_ports.append(dpid_port)
        return dpid_ports

    def __parse_to_links(self, links):
        dpid_links = list()
        for link in links:
            src_dpid = DPID()
            src_port = Port()
            src_port.set_num(link[1])
            src_dpid.add_port(src_port)
            src_dpid.set_datapath(link[0])
            src_dpid.set_component_id(self.__generate_dpid_component_id(src_dpid))
            src_dpid.set_component_manager_id(self.__generate_component_manager_id(src_dpid))            
 
            dst_dpid = DPID()
            dst_port = Port()
            dst_port.set_num(link[3])
            dst_dpid.add_port(dst_port)
            dst_dpid.set_datapath(link[2])
            dst_dpid.set_component_id(self.__generate_dpid_component_id(dst_dpid))
            dst_dpid.set_component_manager_id(self.__generate_component_manager_id(dst_dpid))

            link = Link()
            link.set_src_dpid(src_dpid)
            link.set_dst_dpid(dst_dpid)
            link.set_src_port(src_port)
            link.set_dst_port(dst_port)
            link.set_type("Link")
            link.set_component_id(self.__generate_link_component_id(link))
            dpid_links.append(link)
        
        return dpid_links
     
    #URN Stuff
    def __generate_component_manager_id(self, server=None):
        hrn = "openflow." + self.__config.CM_HRN
        return hrn_to_urn(hrn, "authority+cm")
    
    def __generate_component_manager_name(self, server):
        hrn = "openflow." + self.__config.CM_HRN
        return hrn_to_urn(hrn, "authority+cm")

    def __generate_dpid_component_id(self, dpid):
        hrn = "openflow." + self.__config.CM_HRN + "." + str(dpid.get_datapath())
        return hrn_to_urn(hrn,"datapath")

    def __generate_dpid_component_name(self, dpid):
        hrn = "openflow." + self.__config.CM_HRN + "." + str(dpid.get_datapath())
        return hrn_to_urn(hrn,"datapath")
    
    def __generate_link_component_id(self, link):
        hrn = self.__config.HRN.replace(".", ":")
        return "urn:publicid:IDN+openflow:%s+link+%s_%s_%s_%s" %(self.__config.HRN,str(link.get_src_dpid().get_datapath()), str(link.get_src_port().get_num()),str(link.get_dst_dpid().get_datapath()),str(link.get_dst_port().get_num()))

    def __generate_sliver_urn(self, vm):
        return hrn_to_urn(self.__config.CM_HRN+"."+str(vm.id), "sliver")

    def __select_sliver_expiration(self, user_expiration, slice_expiration=None, **kwargs):
        if not slice_expiration:
            current_time = datetime.utcnow()
            if "extension_timedelta" in kwargs:
                extension_timedelta = kwargs["extension_timedelta"]
            else:
                extension_timedelta = {"days": 31} # Default set to one month
            slice_expiration = current_time + timedelta(**extension_timedelta)
            slice_expiration = slice_expiration.replace(tzinfo=dateutil.tz.tzutc()).strftime("%Y-%m-%d %H:%M:%S")
            slice_expiration = slice_expiration.replace(" ", "T")+"Z"
        # Retrieve expiration = minimum ( user expiration, slice expiration )
        extended_expiration = min(user_expiration, slice_expiration)
        return extended_expiration

    def __get_slice_expiration(self, expiration=None):
        max_exp = datetime.utcnow() + timedelta(days=31)
        if expiration:
            expiration = expiration.replace("T", " ")
            expiration = expiration.replace("Z", "")
            try:
               expiration = datetime.strptime(str(expiration),"%Y-%m-%d %H:%M:%S.%f")
            except:
                expiration = datetime.strptime(str(expiration),"%Y-%m-%d %H:%M:%S")
            selected =  str(max(expiration, max_exp)) 
            return selected.replace(" ", "T") + "Z"
        return str(max_exp).replace(" ", "T") + "Z"

    def __get_experiment_params(self, fs,slice_urn=None ,extra_params=dict()):
        experiment_params = dict()
        experiment_params['slice_desc'] = fs.get_description()
        experiment_params['controller_url'] = fs.get_controller().get_url()
        experiment_params['owner_email'] = fs.get_email()
        experiment_params['project_desc'] = fs.get_description()
        experiment_params['project_name'] = slice_urn
        experiment_params['slice_name'] = slice_urn
        experiment_params['slice_urn'] = self.__generate_sliver_urn_from_slice_urn(slice_urn) 
        experiment_params['slice_id'] = uuid.uuid4() 
        return experiment_params

    def __generate_sliver_urn_from_slice_urn(self, slice_urn):
        hrn, urn_type = urn_to_hrn(slice_urn)
        leaf = hrn.split(".")[-1]
        return hrn_to_urn(self.__config.CM_HRN+"."+str(leaf), "sliver") 

    def __urn_to_fs_params(self, urn):
        hrn, urn_type = urn_to_hrn(urn)
        if urn_type == "sliver":
            return {"slice_urn":urn}
        elif urn_type == "slice":
            return {"project_name":urn}
              
    def __translate_to_flow_space_model(self, match, dpid, port, model=None):
        fs = OptinUtils.format_flowspaces(match, port.get_num())
        return fs

    def __get_create_slice_params(self, rfs):
        slivers = dict()
        for rf in rfs:
            if rf.dpid in slivers.keys():
                slivers[rf.dpid].append(self.__get_flow_space_info(rf))
            else:
                slivers[rf.dpid] = [self.__get_flow_space_info(rf)]

        output = list()
         
        for dpid in slivers.keys():
            output.append({"datapath_id":dpid, "flowspace": slivers[dpid]})
        return output

    def __get_flow_space_info(self, rf):
        fs = {'dl_dst_end': rf.mac_dst_e ,
              'dl_dst_start': rf.mac_dst_s,
              'dl_src_end': rf.mac_src_e,
              'dl_src_start': rf.mac_src_s,
              'dl_type_end': rf.eth_type_e,
              'dl_type_start': rf.eth_type_s,
              'id': rf.id,
              'nw_dst_end':rf.ip_dst_e ,
              'nw_dst_start': rf.ip_dst_s,
              'nw_proto_end': rf.ip_proto_e,
              'nw_proto_start': rf.ip_proto_s,
              'nw_src_end': rf.ip_src_e,
              'nw_src_start': rf.ip_src_s,
              'port_num_end': rf.port_number_e,
              'port_num_start': rf.port_number_s,
              'tp_dst_end': rf.tp_dst_e,
              'tp_dst_start': rf.tp_dst_s,
              'tp_src_end': rf.tp_src_e,
              'tp_src_start': rf.tp_src_s,
              'vlan_id_end': rf.vlan_id_e,
              'vlan_id_start': rf.vlan_id_s}
        return fs

    def __format_params_to_reservation_model(self, req_params):
        fs = {"mac_src_s": req_params['dl_src_start'],           
              "mac_src_e": req_params['dl_src_end'],          
              "mac_dst_s": req_params['dl_dst_start'],           
              "mac_dst_e": req_params['dl_dst_end'],           
              "eth_type_s": req_params['dl_type_start'],        
              "eth_type_e": req_params['dl_type_end'],         
              "vlan_id_s": req_params['vlan_id_start'],        
              "vlan_id_e": req_params['vlan_id_end'],       
              "ip_src_s": req_params['nw_src_start'],        
              "ip_src_e": req_params['nw_src_end'],        
              "ip_dst_s": req_params['nw_dst_start'],        
              "ip_dst_e": req_params['nw_dst_end'],         
              "ip_proto_s": req_params['nw_proto_start'],     
              "ip_proto_e": req_params['nw_proto_end'],      
              "tp_src_s": req_params['tp_src_start'],           
              "tp_src_e": req_params['tp_src_end'],          
              "tp_dst_s": req_params['tp_dst_start'],         
              "tp_dst_e": req_params['tp_dst_end'],
              "port_number_e": req_params['port_num_end'],
              "port_number_s": req_params["port_num_start"],
              "id": req_params["id"],}
        return fs

    def get_config(self):
        return self.__config
    
    def set_config(self, value):
        self.__config = value
