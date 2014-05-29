import uuid

from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
from openflow.optin_manager.opts.models import Experiment, ExperimentFLowSpace
from django.db import transaction
from django.conf import settings
from openflow.optin_manager.xmlrpc_server.ch_api import convert_star, om_ch_translate
from openflow.optin_manager.flowspace.utils import parseFVexception
from openflow.optin_manager.sfa.openflow_utils.ServiceThread import ServiceThread

'''Same "create_slice" function from xmlrpc_server/ch_api.py without decorators'''

def CreateOFSliver(slice_urn,project_name,project_description,slice_name,slice_description,controller_url,owner_email,owner_password,switch_slivers,**kwargs):

    #slice_id = Experiment.objects.get(slice_urn=slice_urn).slice_id
    e = Experiment.objects.filter(slice_urn=slice_urn)
     
    if (e.count()>0):
        old_e = e[0]
        old_fv_name = old_e.slice_id
        update_exp = True
        old_exp_fs = ExperimentFLowSpace.objects.filter(exp=old_e)
    else:
        update_exp = False
        
    e = Experiment()
    slice_id = uuid.uuid4()    
    e.slice_id = slice_id
    e.project_name = project_name
    e.project_desc = project_description
    e.slice_name = slice_name
    e.slice_desc = slice_description
    e.controller_url = controller_url
    e.owner_email = owner_email
    e.owner_password = owner_password
    e.slice_urn = slice_urn
    e.save()
       
    all_efs = [] 
    for sliver in switch_slivers:
        if "datapath_id" in sliver:
            dpid = sliver['datapath_id']
        else:
            dpid = "00:" * 8
            dpid = dpid[:-1]
            
        if len(sliver['flowspace'])==0:
            # HACK:
            efs = ExperimentFLowSpace()
            efs.exp  = e
            efs.dpid = dpid
            efs.direction = 2
            all_efs.append(efs)
        else:
            for sfs in sliver['flowspace']:
                efs = ExperimentFLowSpace()
                efs.exp  = e
                efs.dpid = dpid
                if "direction" in sfs:
                    efs.direction = get_direction(sfs['direction'])
                else:
                    efs.direction = 2
                        
                fs = convert_star(sfs)
                for attr_name,(to_str, from_str, width, om_name, of_name) in \
                om_ch_translate.attr_funcs.items():
                    ch_start ="%s_start"%(attr_name)
                    ch_end ="%s_end"%(attr_name)
                    om_start ="%s_s"%(om_name)
                    om_end ="%s_e"%(om_name)

                    try:
                        setattr(efs,om_start,from_str(fs[ch_start]))
                    except:
                        setattr(efs,om_start,from_str(int(fs[ch_start],16)))
                    try:
                        setattr(efs,om_end,from_str(fs[ch_end]))
                    except:
                        setattr(efs,om_end,from_str(int(fs[ch_end],16)))
                all_efs.append(efs)
        
    fv = FVServerProxy.objects.all()[0]
    if (update_exp):
        # delete previous experiment from FV
        try:
            fv_success = fv.proxy.api.deleteSlice(old_fv_name)
            old_exp_fs.delete()
            old_e.delete()
        except Exception, exc:
            import traceback
            traceback.print_exc()
            if "slice does not exist" in str(exc):
                fv_success = True
                old_exp_fs.delete()
                old_e.delete()
            else:
                e.delete()
                print exc
                raise Exception(parseFVexception(exc,"While trying to update experiment, FV raised exception on the delete previous experiment step: "))
                
        if (not fv_success):
            e.delete()
            raise Exception("While trying to update experiment, FV returned False on the delete previous experiment step")
            
    # create the new experiment on FV
    try:   
        fv_success = fv.proxy.api.createSlice(
            "%s" % slice_id,
            "%s" % owner_password,
            "%s" % controller_url,
            "%s" % owner_email,
        )
        for fs in all_efs:
            fs.save()
        print "Created slice with %s %s %s %s" % (
        slice_id, owner_password, controller_url, owner_email)
    except Exception,exc:
        import traceback
        traceback.print_exc()
        e.delete()
        print exc
        if (update_exp):
            raise Exception(parseFVexception(exc,"Could not create slice at the Flowvisor, after deleting old slice. Error was: "))
        else:
            raise Exception(parseFVexception(exc,"Could not create slice at the Flowvisor. Error was: "))
            
    if not fv_success:
        e.delete()
        if (update_exp):
            raise Exception(
            "Could not create slice at the Flowvisor, after deleting old slice. FV Returned False in createSlice call")
        else:
            raise Exception(
            "Could not create slice at the Flowvisor. FV Returned False in createSlice call")

    if (update_exp):
        from openflow.optin_manager.opts.helper import update_opts_into_exp
        [fv_args,match_list] = update_opts_into_exp(e)
        if len(fv_args) > 0:
            # update previous opt-ins into this updated experiment
            try:
                returned_ids = fv.proxy.api.changeFlowSpace(fv_args)
                for i in range(len(match_list)):
                    match_list[i].fv_id = returned_ids[i]
                    match_list[i].save()
            except Exception, exc:
                from openflow.optin_manager.opts.helper import opt_fses_outof_exp
                import traceback
                traceback.print_exc()
                all_opts = UserOpts.objects.filter(experiment=e)
                for opt in all_opts:
                    optfses = OptsFlowSpace.objects.filter(opt = opt)
                    opt_fses_outof_exp(optfses)
                all_opts.delete()
                print exc
                raise Exception(parseFVexception(exc,"Couldn't re-opt into updated experiment. Lost all the opt-ins: "))
             
    try:
        # Get project detail URL to send via e-mail
        from openflow.optin_manager.opts import urls
        from django.core.urlresolvers import reverse
        project_detail_url = reverse("opt_in_experiment") or "/"
        # No "https://" check should be needed if settings are OK
        site_domain_url = "https://" + Site.objects.get_current().domain + project_detail_url
        # Tuple with the requested VLAN range
        try:
            vlan_range = "\nVLAN range: %s\n\n" % str((all_efs[0].vlan_id_s, all_efs[0].vlan_id_e))
        except:
            vlan_range = "\n\n"
        send_mail(settings.EMAIL_SUBJECT_PREFIX+" Flowspace Request: OptinManager '"+str(project_name)+"'", "Hi, Island Manager\n\nA new flowspace was requested:\n\nProject: " + str(project_name) + "\nSlice: " + str(slice_name) + str(vlan_range) + "You may add a new Rule for this request at: %s" % site_domain_url, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[settings.ROOT_EMAIL],)
    except:
        pass

    #transaction.commit()       
    return {'error_msg': "",'switches': []}

