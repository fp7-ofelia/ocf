def auto_fs_granter(selexp):
    """
    Grants flowspaces for previously conflictive slices at Flowvisor.
    Used in conjunction **and after** the script with the same name
    at expedient.
    
    Flow:
        1. Expedient: manage.py standardize_flowvisor_slices stop
        2. Expedient: manage.py standardize_flowvisor_slices start
        3. Opt-in: manage.py standardize_flowvisor_slices
    """
    from django.conf import settings
    from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
    from openflow.optin_manager.users.models import Priority, UserProfile
    from django.contrib.auth.models import User
    from openflow.optin_manager.opts.helper import opt_fs_into_exp
    from openflow.optin_manager.flowspace.helper import multi_fs_intersect, single_fs_intersect
    from openflow.optin_manager.opts.models import Experiment, ExperimentFLowSpace, UserFlowSpace, AdminFlowSpace, UserOpts

    # If 'slice_ids_to_grant_fs' file exists, do the following.
    # Otherwise warn and skip.
    try:
        user = User.objects.filter(username=settings.ROOT_USERNAME)[0]
        adminFS = AdminFlowSpace.objects.filter(user = user)
        profile = UserProfile.get_or_create_profile(user)
        fv = FVServerProxy.objects.all()[0]
        assigned_priority = profile.max_priority_level - Priority.Strict_Priority_Offset - 1
        all_this_admin_opts = UserOpts.objects.filter(user=user,nice=True)
        for admin_opt in all_this_admin_opts:
            if admin_opt.priority <= assigned_priority:
                assigned_priority = admin_opt.priority - 1
        # Filter by slice "keywords" (name), same as in the previous steps
        flow_space = ExperimentFLowSpace.objects.filter(exp=selexp.id)
        if not flow_space:
            print "No matched flowspaces for slice %s" % selexp.slice_id
            raise Exception('No matched flowspaces for slice %s' % selexp.slice_id)		
        #intersected_flowspace = multi_fs_intersect(flow_space,adminFS,FlowSpace)
        intersected_flowspace = get_used_fs(flow_space)
        fv_args,match_list = opt_fs_into_exp(intersected_flowspace,selexp,user,assigned_priority,True)
        returned_ids = fv.proxy.api.changeFlowSpace(fv_args)
        for i in range(len(match_list)):
            match_list[i].fv_id = returned_ids[i]
            match_list[i].save()
        allopts = UserOpts.objects.filter(user = user).order_by('-priority')
     
        for opt in allopts:
            this_opt_fses = opt.optsflowspace_set.all()
            fs_project = opt.experiment.project_name or ""
            fs_slice = opt.experiment.slice_name or ""
            fs_description = ""
            for fs in this_opt_fses:
                if fs_description != "":
                    fs_description = fs_description + "\n%s" % fs
                else:
                    fs_description = "%s" % fs
        print "Flowspace for slice %s was successfully granted" % selexp.slice_id 
    except Exception as e:
        raise e 

def filter_own_experiment(slice_iden):
    filtered_exp = None
    try:
        # Check that experiment contains the keywords
        # to verify it was CREATED at our island.
        # Otherwise, leave
        filtered_exp = Experiment.objects.get(slice_id = slice_iden['id'])
        for keyword in slice_iden['keywords']:
            if keyword not in filtered_exp.slice_name:
                filtered_exp = None   # If this does not exist, ignore
                break
    except Exception as e:
        print "Could not find opted experiment %s. Details: %s" % (str(slice_iden['id']), str(e))
    return filtered_exp

def get_used_fs(flow_space):
    forbidden_keys = ["id","dpid","direction","port_number_s", "port_number_e", "exp_id","_state"]
    intersections_return = list()
    intersection_dicts = list()
    for flow in flow_space:
        intersection = dict()
        for key in flow.__dict__.keys():
            if key in forbidden_keys:
                continue
            else:
                intersection[key] = flow.__dict__[key]
        if intersection not in intersection_dicts:
            intersection_dicts.append(intersection)
    for intersection in intersection_dicts: 
        int_fs = intersection_fs()
        for key in intersection.keys():
            setattr(int_fs, key, intersection[key])
        intersections_return.append(int_fs) 
    return intersections_return

class intersection_fs:
    pass

