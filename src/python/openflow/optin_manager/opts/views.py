# Create your views here.
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from models import *
from django.template import RequestContext
from django.http import HttpResponse
from forms import AdminOptInForm
from django.forms.util import ErrorList
from openflow.optin_manager.flowspace.helper import *
from openflow.optin_manager.users.models import Priority
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
from django.views.generic import simple
from openflow.optin_manager.opts.helper import opt_fs_into_exp,opt_fses_outof_exp,\
update_match_struct_priority_and_get_fv_args
from django.db import transaction

    
def change_priority(request):
    '''
    The view function to change priorities of previous opt-ins.
    FOR USER CHANGE PRIORITY:
    request.POST should have a dictionary of "p_" followed by UserOpts database id as key
    and the new priority as value
    '''
    # TODO: make this more user friendly by showing comparative net_admin flowspaces w.r.t. this admin FS
    if request.user.get_profile().is_net_admin:
        error_msg = []
        fv_args = []
        max_priority = request.user.get_profile().max_priority_level
        if (request.method == "POST"):
            keys = request.POST.keys()
            for key in keys:
                if key.startswith("p_"):
                    if (int(request.POST[key]) > max_priority):
                        error_msg.append("You entered priority %s, which is larger than your maximum(%s)" % (request.POST[key], max_priority))
                        continue
                    pid = (key[2:len(key)])
                    u = UserOpts.objects.get(pk=pid)
                    u.priority = int(request.POST[key])
                    
                    ofs = u.optsflowspace_set.all()
                    for fs in ofs:
                        matches = fs.matchstruct_set.all()
                        for match in matches:
                            # TODO: hard coded 4
                            match.priority = (match.priority%Priority.Priority_Scale) + int(request.POST[key])*Priority.Priority_Scale
                            match.save()
                            fv_arg = {"operation":"CHANGE", "id":match.fv_id,
                                      "priority":match.priority, "dpid":fs.dpid, "match":match.match,
                                      "actions": "slice=%s:4"%fs.opt.experiment.get_fv_slice_name(),
                                      }
                            fv_args.append(fv_arg)

            try:
                fv = FVServerProxy.objects.all()[0]
            except Exception,e:
                import traceback
                traceback.print_exc()
                error_msg.append("Flowvisor not set: %s"%str(e))
                
            try:
                fv.proxy.api.changeFlowSpace(fv_args)
            except Exception,e:
                import traceback
                traceback.print_exc()
                error_msg.append("change flowspace call failed in flowvisor: %s"%str(e))
                  
                  
                  
        opts = UserOpts.objects.filter(user=request.user).order_by('-priority')    
        return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/view_opts_admin.html', 
                        extra_context = {
                                'opts':opts ,
                                'user':request.user,
                                'max_priority':max_priority,
                                'error_messages':error_msg,
                            },
                    )
        
    ##################################
    #      User Change Priority      #
    ################################## 
    else: # Not net_admin (User View)
        fv_args = []
        error_msg = []
        max_priority = request.user.get_profile().max_priority_level
        
        keys = request.POST.keys()
        if (request.method == "POST"):
            for key in keys:
                if key.startswith("p_"):
                    try:
                        pid = int(key[2:len(key)])
                        new_priority = int(request.POST[key])
                    except:
                        error_msg.append("Found invalid pair in request.POST: %s:%s"%(key,request.POST[key]))
                        break
                    
                    if (new_priority > max_priority):
                        error_msg.append("Priority %s, is larger than your maximum(%s)"\
                             % (new_priority, max_priority))
                        break
 
                    u = UserOpts.objects.get(pk=pid)
                    if (u.priority != new_priority):
                        u.priority = new_priority
                        if (u.priority >= Priority.Nice_User):
                            u.nice = False
                        else:
                            u.nice = True
                        u.save()
                        new_args = update_match_struct_priority_and_get_fv_args(u)
                        fv_args = fv_args + new_args

            if len(error_msg) == 0:
                try:
                    fv = FVServerProxy.objects.all()[0]
                    try:
                        if len(fv_args) > 0:
                            fv.proxy.api.changeFlowSpace(fv_args)
                        return simple.direct_to_template(request, 
                            template = 'openflow/optin_manager/opts/change_priority_successful.html', 
                            extra_context = {}, 
                        )
                    except Exception,e:
                        import traceback
                        traceback.print_exc()
                        transaction.rollback()
                        error_msg.append("update flowspace priorities failed: %s"%str(e))
                except Exception,e:
                    import traceback
                    traceback.print_exc()
                    transaction.rollback()
                    error_msg.append("Flowvisor not set: %s"%str(e))
            else: #error msg has some content
                transaction.rollback()
        
        nice_opts = UserOpts.objects.filter(user=request.user,nice=True).order_by('-priority')
        strict_opts = UserOpts.objects.filter(user=request.user,nice=False).order_by('-priority')
 
        return simple.direct_to_template(request, 
                    template = 'openflow/optin_manager/opts/view_opts_user.html', 
                    extra_context={ 
                                   'error_msg':error_msg,
                                   'nice_opts':nice_opts , 
                                   'strict_opts':strict_opts ,
                                   'user':request.user,
                                   }, 
                    )           
              


def add_opt_in(request):
    '''
`	The view function for opting in a user or admin flowspace into an experiment
    FOR USER OPTIN:
    request.POST should contain:
    @param experiemnt: database id of the experiment to be opted in
    ''' 
    profile = UserProfile.get_or_create_profile(request.user)
    
    ############################
    #      Admin Opt-In        #
    ############################   
    if (profile.is_net_admin):
        all_exps = Experiment.objects.all()
        admin_fs = AdminFlowSpace.objects.filter(user=request.user)
        exps = []
        for exp in all_exps:
            exp_fs = ExperimentFLowSpace.objects.filter(exp=exp)
            intersection = multi_fs_intersect(exp_fs,admin_fs,FlowSpace)
            if (len(intersection)>0):
                exps.append(exp)

        if (request.method == "POST"):
            #opt in request received; process it
            form = AdminOptInForm(request.POST)
            defexp = request.POST['experiment']
            if form.is_valid():
                # check if priority is within allowable range
                if int(request.POST['priority']) > int(profile.max_priority_level):
                    msg = "Your maximum priority is %d"%(profile.max_priority_level)
                    form._errors["priority"] = ErrorList([msg])
                else:
                    #get admin flowspace, experiment's flow space and convert requested flowspace to FLowSpace
                    # object to find their intersection
                    selexp = Experiment.objects.get(id = defexp)
                    adminFS = AdminFlowSpace.objects.filter(user = request.user)
                    optedFS = make_flowspace(request.POST)
                    
                    # find  intersection of adminFS and opted FS
                    f = multi_fs_intersect(adminFS,[optedFS],FlowSpace)

                    opt_msg = opt_fs_into_exp(f,selexp,request.user,
                                        int(request.POST['priority']),False)
                    if (opt_msg == ""):
                        exp_name = "%s:%s"%(selexp.project_name, selexp.slice_name)
                        return simple.direct_to_template(request, 
                                            template = 'openflow/optin_manager/opts/opt_in_successful.html', 
                                            extra_context = {'expname':exp_name}, 
                                        )
                    else:
                        form._errors['general'] = ErrorList([opt_msg])

        else: #Not a post request
            defexp = 0
            form = AdminOptInForm()
        return simple.direct_to_template(request, 
                                template = 'openflow/optin_manager/opts/admin_opt_in.html', 
                                extra_context = {
                                                'form': form, 
                                                'user':request.user,
                                                'experiments':exps,
                                                'defexp': defexp,
                                        },
                            )   
    ############################
    #      User Opt-In         #
    ############################         
    else: 
        
        #find all the experiemnts that have intersection with this user
        all_exps = Experiment.objects.all()
        user_fs = UserFlowSpace.objects.filter(user=request.user)
        exps = []
        for exp in all_exps:
            exp_fs = ExperimentFLowSpace.objects.filter(exp=exp)
            intersection = multi_fs_intersect(exp_fs,user_fs,FlowSpace)
            if (len(intersection)>0):
                exps.append(exp)
                
        assigned_priority = 1
        error_msg = []
        if (request.method == "POST"):
            all_this_user_opts = UserOpts.objects.filter(user=request.user,nice=True)
            for user_opt in all_this_user_opts:
                if user_opt.priority >= assigned_priority:
                    assigned_priority = user_opt.priority + 1
                    
            # check if a valid experiment is selected
            selecetd_exp_id = request.POST['experiment']
            try:
                selexp = Experiment.objects.get(id = selecetd_exp_id)
            except:
                error_msg.append("Invalid experiment selected!")
                
            # check if priority is within allowable range
            if assigned_priority > profile.max_priority_level:
                error_msg.append("Your maximum priority is %d"%(profile.max_priority_level))
            
            if (len(error_msg)==0):
                userFS = UserFlowSpace.objects.filter(user = request.user)                    

                # check if the user already have opted into this experiment before
                prev_opts = UserOpts.objects.filter(experiment = selexp)
                if (prev_opts.count() > 0):
                    assigned_priority = prev_opts[0].priority
                    all_prev_opts_fs = []
                    for a_prev_opt in prev_opts:
                        a_prev_opt_fses = a_prev_opt.optsflowspace_set.all()
                        for a_prev_opt_fs in a_prev_opt_fses:
                            all_prev_opts_fs.append(a_prev_opt_fs)
                    
                    # now opt out the flowpsaces and clear flowspace and match_struct entries 
                    # from the database:
                    del_fv_args = opt_fses_outof_exp(all_prev_opts_fs)
                    
                    # delete all the previous opts into this experiemnt from the database    
                    prev_opts.delete()
                else:
                    print
                    del_fv_args = []
                    
                # Now opt the user into the selected experiemnt
                [add_fv_args,match_list] = opt_fs_into_exp(userFS,selexp,request.user,
                                        assigned_priority,True)
                    
                try:
                    fv = FVServerProxy.objects.all()[0]
                    try:
                        fv_args = add_fv_args + del_fv_args
                        if len(fv_args) > 0:
                            returned_ids = fv.proxy.api.changeFlowSpace(fv_args)
                            for i in range(len(match_list)):
                                match_list[i].fv_id = returned_ids[i]
                                match_list[i].save()
                        return simple.direct_to_template(request, 
                            template ="openflow/optin_manager/opts/opt_in_successful.html",
                            extra_context = {
                                'expname':"%s:%s"%(selexp.project_name,selexp.slice_name),
                            },
                        )
                    except Exception,e:
                        import traceback
                        traceback.print_exc()
                        transaction.rollback()
                        error_msg.append("Couldn't opt into the requested experiment, either because the new opt-in failed or OM couldn't opt you out of your previous opt into the same experiment: %s"%str(e))
                except Exception,e:
                    import traceback
                    traceback.print_exc()
                    transaction.rollback()
                    error_msg.append("Flowvisor not set: %s"%str(e))
                              

        # if not a post request, we will start from here            
        if (len(exps)>0):
            exp_exist = True
            first_exp = exps[0].id
        else:
            exp_exist = False
            first_exp = 0
        return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/user_opt_in.html', 
                        extra_context = {
                                'user':request.user,
                                'experiments':exps,
                                'error_msg':error_msg,
                                'exp_exist':exp_exist,
                                'first_exp':first_exp,
                            },
                    )      
        
    

def opt_out(request):
    '''
    The view function for opt-out. 
    FOR A USER:
    the request.POST should contain {UserOpts.id:"checked"} for all the UserOpts
    to be opted out.
    '''
    error_msg = []
    profile = request.user.get_profile()
    keys = request.POST.keys()
    if (profile.is_net_admin):
        if (request.method == "POST"):
            fv_args = []
            for key in keys:
                try:
                    int(key)
                    ofs = OptsFlowSpace.objects.get(id=int(key))
                    error = opt_fses_outof_exp([ofs])
                    if error!="":
                        error_msg.append(error)
                except:
                    break

                    
                    
            if (len(error_msg) == 0):
                error_msg = ["Opt Out was Successful"] 
                
        this_user_opts  = UserOpts.objects.filter(user = request.user)
        for useropt in this_user_opts:
            tmpfs = useropt.optsflowspace_set.all()
            if (len(tmpfs) == 0):
                useropt.delete()
                
        allfs = OptsFlowSpace.objects.filter(opt__user = request.user)
            
        return simple.direct_to_template(request,
                    template = 'openflow/optin_manager/opts/admin_opt_out.html', 
                    extra_context = {'allfs':allfs, 'error_msg':error_msg},
                )
        
    ############################
    #      User Opt-Out        #
    ############################ 
    else:
        if (request.method == "POST"):
            fv_args = []
            for key in keys:
                try:
                    # check all the keys that are integer values and opt them out.
                    int(key)
                    opt = UserOpts.objects.get(id=key)
                except:
                    continue
                
                ofs = OptsFlowSpace.objects.filter(opt=opt)
                new_fv_args = opt_fses_outof_exp(ofs)
                fv_args = fv_args + new_fv_args
                opt.delete()  
                  
            if len(error_msg) == 0:            
                # Now make sure the priorities are consequative
                nice_opts = UserOpts.objects.filter(user = request.user,nice=True).order_by('priority')
                next_priority = 1
                for opt in nice_opts:
                    if opt.priority != next_priority:
                        opt.priority = next_priority
                        opt.save()
                        new_args = update_match_struct_priority_and_get_fv_args(opt)
                        fv_args = fv_args + new_args
                    next_priority = next_priority + 1
                strict_opts = UserOpts.objects.filter(user = request.user,nice=False).order_by('priority')
                next_priority = Priority.Nice_User + 1
                for opt in strict_opts:
                    if opt.priority != next_priority:
                        opt.priority = next_priority
                        opt.save()
                        new_args = update_match_struct_priority_and_get_fv_args(opt)
                        fv_args = fv_args + new_args
                    next_priority = next_priority + 1
    
                print "FV_ARGS FOR OPT OUT: %s"%fv_args
                    
                try:
                    fv = FVServerProxy.objects.all()[0]
                    try:
                        if len(fv_args) > 0:
                            fv.proxy.api.changeFlowSpace(fv_args)
                    except Exception,e:
                        import traceback
                        traceback.print_exc()
                        transaction.rollback()
                        error_msg.append("change flowspace in opt_out view failed: %s"%str(e))
                except Exception,e:
                    import traceback
                    traceback.print_exc()
                    transaction.rollback()
                    error_msg.append("Flowvisor not set: %s"%str(e))

                
      
        allopts = UserOpts.objects.filter(user = request.user).order_by('-priority')
            
        return simple.direct_to_template(request,
                    template = 'openflow/optin_manager/opts/user_opt_out.html', 
                    extra_context = {'allopts':allopts, 'error_msg':error_msg},
                )



def view_experiment(request, exp_id):
    theexp = Experiment.objects.filter(id=exp_id)
    allfs = ExperimentFLowSpace.objects.filter(exp=theexp[0])
    return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/view_experiment.html', 
                        extra_context = {
                                        'exp':theexp[0],
                                        'allfs':allfs,
                                        'back':request.META['HTTP_REFERER']
                                    }, 
                    )
   

def view_experiment_simple(request, exp_id):
    theexp = Experiment.objects.filter(id=exp_id)
    allfs = ExperimentFLowSpace.objects.filter(exp=theexp[0])
    return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/view_experiment_simple.html', 
                        extra_context = {
                                        'exp':theexp[0],
                                        'allfs':allfs,
                                    }, 
                    )
    

def view_experiments(request):
    exps = Experiment.objects.all()
    return simple.direct_to_template(request, 
                            template = 'openflow/optin_manager/opts/view_experiments.html',
                            extra_context = {'exps':exps}, 
                            )
    
    