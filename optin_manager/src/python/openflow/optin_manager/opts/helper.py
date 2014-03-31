from models import *
from openflow.optin_manager.flowspace.helper import multi_fs_intersect,\
    range_to_match_struct, singlefs_is_subset_of
from openflow.optin_manager.users.models import Priority
from openflow.optin_manager.flowspace.utils import dotted_ip_to_int,mac_to_int

def opt_fs_into_exp(optedFS, exp, user, priority, nice):
    '''
    Opt the flowspace specified in optedFS into experiment exp
    @param optedFS: Flowpscae to be opted into experiment
    @type: Flowspace object
    @param exp: Experiment to be opted into
    @type exp: Experiemnt object
    @param user: user who is doing the opt-in
    @type user: User object
    @param priority: priority for this opt-in
    @type priority: integer
    @param nice: strict or nice optin
    @type nice: boolean
    @return: return the fv_args and the list of match structs created for this opt
    @type: [list,list] first list is fv_args, second one match_struct_list
    '''
    expFS = ExperimentFLowSpace.objects.filter(exp = exp)
    
    # Slice ID defaults to its UUID, but let us check first the...
    slice_id = exp.slice_id
    # Backwards compatibility: check if slice_id follows the legacy style (= not UUID)
    try:
        import uuid
        uuid.UUID('{%s}' % str(slice_id))
        is_legacy_slice = False
    except Exception as e:
        is_legacy_slice = True
    
    # If legacy, get the older way to name it 
    if is_legacy_slice:
        slice_id = exp.get_fv_slice_name()
    
    intersected = False
    # add this opt to useropts
    tmp = UserOpts(experiment=exp, user=user, priority=priority, nice=nice )
    tmp.save()
    
    fv_args = []
    match_list = []
    some_exception = False
    opted = []
    try:
        for fs in expFS:
            # XXX: lbergesio - This line is to force intersection 
            # between the requested fs by the user and the one granted by the IM which is already the 
            # the intesection between the adminFS (normally ALL) and the granted by the IM in the web form.
            # Most of the times VLAN requested != to the one granted so the fs is not granted nor pushed 
            # to FV.
            # This is due to the original goal of optin and since OFELIA uses it in a different way, this
            # must never happen. So one solution is to replace the VLANS requested by user with the ones
            # granted by the IM.

            for optedfs in optedFS:
                 
                #fs.vlan_id_e = optedfs.vlan_id_e
                #fs.vlan_id_s = optedfs.vlan_id_s
                if fs.vlan_id_e == optedfs.vlan_id_e and fs.vlan_id_s == optedfs.vlan_id_s:
                    opted = multi_fs_intersect([fs],[optedfs],OptsFlowSpace)
            if (len(opted) > 0):
                intersected = True
                for opt in opted:
                    opt.opt = tmp
                    opt.dpid = fs.dpid
                    opt.port_number_s = int(fs.port_number_s)
                    opt.port_number_e = int(fs.port_number_e)
                    opt.direction = fs.direction
                    opt.save()
                    #make Match struct
                    matches = range_to_match_struct(opt)
                    for single_match in matches:
                        match = MatchStruct(match = single_match, priority = priority*Priority.Priority_Scale, fv_id=0, optfs=opt)
                        match.save()
                        match_list.append(match)
                        #TODO 4 is hard coded
                        fv_arg = {"operation":"ADD", "priority":"%d"%match.priority,
                                        "dpid":match.optfs.dpid,"match":match.match,
#                                        "actions":"Slice=%s:4"%match.optfs.opt.experiment.get_fv_slice_name()}
                                        "actions":"Slice=%s:4" % slice_id}
                        fv_args.append(fv_arg)
                            
                        # If there is any intersection, add them to FV
    except Exception as e:
        # If some exception was raised, delete the tmp object and raise another exception
        tmp.delete()
        some_exception = str(e)
        raise Exception(some_exception)

    if (not intersected):
        print "WARNING!!! User FS request and IM granted FS do not match and no FS is being pushed to FV"
        tmp.delete()

    return [fv_args,match_list]
        

def opt_fses_outof_exp(fses):
    '''
    Opt all flowpsaces in fses (of type optsflowspace) out of their 
    experiments. 
    @param fses: array of optsflowspace to be opted out
    @type fses: array
    @return: fv arguments to be passed to the fv
    @type: array
    '''
    fv_args = []
    for ofs in fses:
        matches = ofs.matchstruct_set.all()
        for match in matches:
            fv_arg={"operation":"REMOVE" , "id":match.fv_id}
            fv_args.append(fv_arg)
            
    for ofs in fses:
        ofs.matchstruct_set.all().delete()
        ofs.delete()
    return fv_args

    

def update_user_opts(user):
    '''
    Opt out all the flowspaces opted by user, and re-opt them again into the same experiments
    with same priorities
    @param user: a User object whose opt-ins should be updated
    @type User: User Object
    @return: [fv_args,match_list] flowvisor args to do the update. the fv_args should be passed to
    changeFlowSpace xmlrpc call in flowvisor. match list is the match entries for the first
    arguments in fv_args, so the returned ids from flowvisor should be saved back to them
    @type: [list, list] 
    '''
    fv_args = []
    match_list = []
    user_opts = UserOpts.objects.filter(user=user)
    user_fs = UserFlowSpace.objects.filter(user=user)
    for user_opt in user_opts:
        t_nice = user_opt.nice
        t_priority = user_opt.priority
        t_exp = user_opt.experiment
        ofses = OptsFlowSpace.objects.filter(opt = user_opt)
        del_fv_args = opt_fses_outof_exp(ofses)
        user_opt.delete()
        [add_fv_args,new_match_list] = opt_fs_into_exp(user_fs, t_exp, user, t_priority, t_nice)
        fv_args =  add_fv_args + fv_args + del_fv_args
        match_list = new_match_list + match_list
    return [fv_args,match_list]
            
            
def update_admin_opts(admin):
    '''
    When an adminflowspace is being changed, call this fucntion to opt out all the rules that are no longer
    are under full control of this admin.
    @param adam: The admin whose flowspace is changed and need an update on UserOpts
    '''
    adm_fs = AdminFlowSpace.objects.filter(user=admin)
    opted_fses = OptsFlowSpace.objects.filter(opt__user=admin)
    to_opt_out = []
    for fs in opted_fses:
        if not singlefs_is_subset_of(fs,adm_fs):
            to_opt_out.append(fs)

    fv_args = opt_fses_outof_exp(to_opt_out)
    
    # now delete all the UserOpts that doesn't have any OptsFlowSpace:
    useropts = UserOpts.objects.filter(user=admin)
    for useropt in useropts:
        optfs_set = useropt.optsflowspace_set.all()
        if len(optfs_set) == 0:
            useropt.delete()
    
    return fv_args
    
            
                
def update_opts_into_exp(exp):
    '''
    update all the opts into exp. The updated opt is the intersection of previous
    opt into the same experiment and the experiment's flowspace. Note that this 
    ensures that experiments, by updating their flowspaces after a user optin into 
    them, can not steal unwanted user flowspaces.
    @param exp: the experiment whose flowspace has changed and we need to
    update user opts into that experiment
    @type exp: Experiment object
    @return: [fv_args,match_list] flowvisor args to do the update. the fv_args should be passed to
    changeFlowSpace xmlrpc call in flowvisor. match list is the match entries for the first
    arguments in fv_args, so the returned ids from flowvisor should be saved back to them
    @type: [list, list]  
    '''
    useropts = UserOpts.objects.filter(experiment = exp)
    expFS = ExperimentFLowSpace.objects.filter(exp = exp)
    
    fv_args = []
    match_list = []
    
    # for each opted user into this experiemnt
    for useropt in useropts:
        #all the fses opted by this user into this experiemnt:
        optfses = OptsFlowSpace.objects.filter(opt = useropt)
        t_priority = useropt.priority 
        t_nice = useropt.nice
        t_user = useropt.user
        
        updated_opt = multi_fs_intersect(expFS,optfses,OptsFlowSpace, True)
        opt_fses_outof_exp(optfses)
        useropt.delete()
        
        if len(updated_opt) > 0:
            [add_fv_args,new_match_list] = opt_fs_into_exp(updated_opt, exp, t_user, t_priority, t_nice)
            fv_args = add_fv_args + fv_args 
            match_list = new_match_list + match_list
            
    return [fv_args,match_list]

    

def update_match_struct_priority_and_get_fv_args(useropt):
    '''
    A helper function to update match struct priorities when a useropt priority
    has been changed.
    @param useropt: UserOpts object that have new priority value
    @type useropt: UserOpts
    '''
    fv_args = [] 
    ofs = useropt.optsflowspace_set.all()
    
    # Slice ID defaults to its UUID, but let us check first the...
    exp = ofs[0].opt.experiment
    slice_id = exp.slice_id
    # Backwards compatibility: check if slice_id follows the legacy style (= not UUID)
    try:
        import uuid
        uuid.UUID('{%s}' % str(slice_id))
        is_legacy_slice = False
    except:
        is_legacy_slice = True

    # If legacy, get the older way to name it 
    if is_legacy_slice:
        slice_id = exp.get_fv_slice_name()
    
    for fs in ofs:
        matches = fs.matchstruct_set.all()
        for match in matches:
            match.priority = (match.priority%Priority.Priority_Scale) + \
            useropt.priority*Priority.Priority_Scale
            match.save()
            fv_arg = {"operation":"CHANGE", "id":match.fv_id,
                    "priority":"%d"%match.priority, "dpid":fs.dpid, "match":match.match,
#                    "actions": "Slice=%s:4"%fs.opt.experiment.get_fv_slice_name(),
                    "actions": "Slice=%s:4" % slice_id,
                }
            fv_args.append(fv_arg)
    return fv_args
    
     
def read_fs(f):
    '''
    The function to read and interpret a flowspace description file. 
    For more information on the file format, see the sample file (static/sample_rules.txt)
    '''
    def _same(val):
        return "%s" % val
    
    tags = {
            "mac_src":mac_to_int,
            "mac_dst":mac_to_int,
            "eth_type":int,
            "vlan_id":int,
            "ip_src":dotted_ip_to_int,
            "ip_dst":dotted_ip_to_int,
            "ip_proto":int,
            "tp_src":int,
            "tp_dst":int,
            "opt-in":_same,
            }
    
    result = {'error':[],'flowspace':[],'slice_id':[]}
    line_count = 0
    inside_fs = False
    for line in f:
        line_count = line_count + 1
        line = line.strip()
        
        #ignore comments
        if not line.startswith("#") and not line=="":
            
            # check for open brace:
            if line=="{":
                if inside_fs:
                    result['error'].append("Error at line %d: find '{' in the middle of flowspace definition"%line_count)
                    return result
                else:
                    inside_fs = True
                    slice_id = None
                    new_fs = FlowSpace()
                    continue
            
            # check for close brace:
            if line=="}":
                if not inside_fs:
                    result['error'].append("Error at line %d: find '}' before start of a flowspace definition"%line_count)
                    return result
                else:
                    inside_fs = False
                    result['flowspace'].append(new_fs)
                    result['slice_id'].append(slice_id)
                    continue
            
            # if there is a non-comment line between braces, generate error
            if not inside_fs:
                result['error'].append("Error at line %d: unexpected tag. Expecting '{' instead."%line_count)
                return result
            
            # Find the tag by partitioning the line on the : mark
            [bstr,sep,astr] = line.partition(':')
            if sep=="":
                result['error'].append("Error at line %d: ':' expected after tag"%line_count)
                return result
            
            # check if the tag was valid
            if bstr not in tags.keys():
                result['error'].append("Error at line %d: %s is not a valid tag"%(line_count,bstr))
                return result
            
            # if opt-in found:
            if bstr == "opt-in":
                slice_id = astr.strip()
                continue
            
            # now partition the part of line that comes after 'tag:' and find the range/value
            astr = astr.strip()
            [s_range,dash,e_range] = astr.partition("-")
            
            # single-value case
            if dash=="":
                s_range = s_range.strip()
                convert_func = tags[bstr]
                s_value = convert_func(s_range)
                e_value = convert_func(s_range)
            # range case
            else:
                s_range = s_range.strip()
                e_range = e_range.strip()
                convert_func = tags[bstr]
                s_value = convert_func(s_range)
                e_value = convert_func(e_range)
                
            setattr(new_fs,"%s_s"%bstr,s_value)
            setattr(new_fs,"%s_e"%bstr,e_value)
            
    return result
            
            

        
