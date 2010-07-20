from models import *
from openflow.optin_manager.flowspace.helper import multi_fs_intersect,\
    range_to_match_struct
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
from openflow.optin_manager.users.models import Priority

def opt_fs_into_exp(optedFS, exp, user, priority, nice):
    expFS = ExperimentFLowSpace.objects.filter(exp = exp)
    intersected = False
    # add this opt to useropts
    tmp = UserOpts(experiment=exp, user=user, priority=priority, nice=nice )
    tmp.save()
    
    fv_args = []
    match_list = []
    for fs in expFS:
        opted = multi_fs_intersect([fs],optedFS,OptsFlowSpace)
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
                                    "actions":"Slice=%s:4"%match.optfs.opt.experiment.get_fv_slice_name()}
                    fv_args.append(fv_arg)
                            
                    # If there is any intersection, add them to FV
    if (intersected):
            try:
                fv = FVServerProxy.objects.all()[0]
                return_ids = fv.proxy.api.changeFlowSpace(fv_args)
            except Exception,e:
                opted.delete()
                match_list.delete()
                tmp.delete()
                import traceback
                traceback.print_exc()
                return str(e)
            
            for i in range(0,len(return_ids)):
                match_list[i].fv_id = return_ids[i]
                match_list[i].save()
            return ""
    else:
            tmp.delete()
            return "No flowspace intersection found!"
        
def opt_fses_outof_exp(fses):
    fv_args = []
    for ofs in fses:
        matches = ofs.matchstruct_set.all()
        for match in matches:
            fv_arg={"operation":"REMOVE" , "id":match.fv_id}
            fv_args.append(fv_arg)

    try:
        fv = FVServerProxy.objects.all()[0]
        fv.proxy.api.changeFlowSpace(fv_args)
        for ofs in fses:
            ofs.matchstruct_set.all().delete()
            ofs.delete()
        return ""
    except Exception,e:
        import traceback
        traceback.print_exc()
        return str(e) 
    
def update_user_opts(user):
    user_opts = UserOpts.objects.filter(user=user)
    user_fs = UserFlowSpace.objects.filter(user=user)
    for user_opt in user_opts:
        t_nice = user_opt.nice
        t_priority = user_opt.priority
        t_exp = user_opt.experiment
        ofses = OptsFlowSpace.objects.filter(opt = user_opt)
        msg = opt_fses_outof_exp(ofses)
        if (msg == ""):
            user_opt.delete()
            msg2 = opt_fs_into_exp(user_fs, t_exp, user, t_priority, t_nice)
            if (msg2 == ""):
                return ""
            else:
                return "couldn't re-opt-in user flowspace in update_user_opts. msg was %s"%msg2
        else:
            return "couldn't opt out user flowspace in update_user_opts. msg was %s"%msg
            
        
def update_opts_into_exp(exp):
    '''
    update all the opts into exp and send changes back to FV, 
    return a list of errors that happened 
    '''
    useropts = UserOpts.objects.filter(experiment = exp)
    expFS = ExperimentFLowSpace.objects.filter(exp = exp)
    
    errorlist = []
    
    # for each opted user into this experiemnt
    for useropt in useropts:
        #all the fses opted by this user into this experiemnt:
        optfses = OptsFlowSpace.objects.filter(opt = useropt)
        priority = useropt.priority        

        #delete previous match structs:
        for each_fs in optfses:
            MatchStruct.objects.filter(optfs=each_fs).delete()
        
        #opt back the intersection of previous optin and the new experiemnt flowspace:
        intersected = False
        fv_args = []
        match_list = []
        opted = multi_fs_intersect(expFS,optfses,OptsFlowSpace, True)
        optfses.delete()
        if (len(opted) > 0):
            intersected =True
            for opt in opted:
                opt.opt = useropt
                opt.save() 
                matches = range_to_match_struct(opt)
                for single_match in matches:
                    match = MatchStruct(match = single_match, priority = priority*Priority.Priority_Scale, fv_id=0, optfs=opt)
                    match.save()
                    match_list.append(match)
                    #TODO 4 is hard coded
                    fv_arg = {"operation":"ADD", "priority":"%d"%match.priority,
                                    "dpid":match.optfs.dpid,"match":match.match,
                                    "actions":"Slice=%s:4"%match.optfs.opt.experiment.get_fv_slice_name()}
                    fv_args.append(fv_arg)
                        
        
        if (intersected):
            try:
                fv = FVServerProxy.objects.all()[0]
                return_ids = fv.proxy.api.changeFlowSpace(fv_args)
            except Exception,e:
                opted.delete()
                match_list.delete()
                useropt.delete()
                import traceback
                traceback.print_exc()
                errorlist.append(str(e))
            
            for i in range(0,len(return_ids)):
                match_list[i].fv_id = return_ids[i]
                match_list[i].save()
        else:
            useropt.delete()
    
    return errorlist

def update_match_struct_and_get_fv_args(useropt):
    fv_args = [] 
    ofs = useropt.optsflowspace_set.all()
    for fs in ofs:
        matches = fs.matchstruct_set.all()
        for match in matches:
            match.priority = (match.priority%Priority.Priority_Scale) + \
            useropt.priority*Priority.Priority_Scale
            match.save()
            fv_arg = {"operation":"CHANGE", "id":match.fv_id,
                    "priority":"%d"%match.priority, "dpid":fs.dpid, "match":match.match,
                    "actions": "Slice=%s:4"%fs.opt.experiment.get_fv_slice_name(),
                }
            fv_args.append(fv_arg)
    return fv_args

        
