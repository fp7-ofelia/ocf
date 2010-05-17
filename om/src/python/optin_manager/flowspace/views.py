# Create your views here.
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from optin_manager.flowspace.models import *
from django.template import RequestContext
from django.http import HttpResponse
from optin_manager.flowspace.forms import AdminOptInForm
from django.forms.util import ErrorList
from optin_manager.flowspace.helper import *
from optin_manager.users.models import Priority
from optin_manager.xmlrpc_server.models import FVServerProxy

@login_required
def view_opt_in(request, error_msg):
    #return HttpResponse("view opt in")
    opts = UserOpts.objects.filter(user=request.user).order_by('-priority')
    max_priority = request.user.get_profile().max_priority_level

    if request.user.get_profile().is_net_admin:
        return render_to_response('flowspace/view_opts_admin.html', 
                                  {'max_priority':max_priority, 'opts':opts , 'user':request.user},
                              context_instance=RequestContext(request))
    else:
        return render_to_response('flowspace/view_opts_user.html',
                                  {'max_priority':max_priority, 'opts':opts , 'user':request.user},
                              context_instance=RequestContext(request))


@login_required
def add_opt_in(request):

    exps = Experiment.objects.all()
    profile = request.user.get_profile()
    
    if (profile.is_net_admin):
    
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
                    optedFS = makeFlowSpace(request.POST)
                    expFS = ExperimentFLowSpace.objects.filter(exp = selexp)
                    
                    # find  intersection of adminFS and opted FS
                    f = MultiFSIntersect(adminFS,[optedFS],FlowSpace)
                    intersected = False
                    # add this opt to useropts
                    tmp = UserOpts(experiment=selexp, user=request.user, priority=request.POST['priority'], nice=False )
                    tmp.save()
                    
                    fv_args = []
                    match_list = []
                    for fs in expFS:
                        opted = MultiFSIntersect([fs],f,OptsFlowSpace)
                        if (len(opted) > 0):
                            intersected = True
                            for opt in opted:
                                opt.opt = tmp
                                opt.dpid = fs.dpid
                                opt.port_numebr_s = fs.port_number_s
                                opt.port_numebr_e = fs.port_number_e
                                opt.direction = fs.direction
                                opt.save()
                                #make Match struct
                                matchstr = RangeToMatchStruct(opt)
                                # relative priority for this match struct is 0, because
                                # right now, we just have one match struct.
                                # TODO: consider multi-match structs
                                match = MatchStruct(match = matchstr, priority = int(request.POST['priority'])*Priority.Priority_Scale, fv_id=0, optfs=opt)
                                match.save()
                                match_list.append(match)
                                #TODO 4 is hard coded
                                fv_arg = {"operation":"ADD", "priority":match.priority,
                                            "dpid":match.optfs.dpid,"match":match.match,
                                             "action":"slice=%s:4"%match.optfs.opt.experiment.slice_id}
                                fv_args.append(fv_arg)
                            
                    # If there is any intersection, add them to FV
                    if (intersected):
                        #TODO: if multi flowvisor, change this    
                        fv = FVServerProxy.objects.all()[0]
                        # TODO: check for errors in the following call
                        return_ids = fv.changeFlowSpace(fv_args)
                        for i in range(0,len(return_ids)):
                            match_list[i].fv_id = return_ids[i]
                            match_list[i].save()

                        exp_name = "%s:%s"%(selexp.project_name, selexp.slice_name)
                        return render_to_response('flowspace/opt_in_successful.html', {
                                'expname':exp_name})
                    else:
                        tmp.delete()
                        form._errors['general'] = ErrorList(["No intersection between opted-in flowspace,\
                        your flowspace and experiment flowspace"])
        else: #Not a post request
            defexp = exps[0].id
            form = AdminOptInForm()
        return render_to_response('flowspace/admin_opt_in.html', {
            'form': form, 'user':request.user, 'experiments':exps, 'defexp': defexp,
        })
        
        
    else: # A user opt-in page
        
        selpri = 0
        error_msg = ""
        if (request.method == "POST"):
            #opt in request received; process it
            selpri = request.POST['priority']
            defexp = request.POST['experiment']
            
            # check if priority is within allowable range
            if int(selpri) > profile.max_priority_level:
                error_msg = "Your maximum priority is %d"%(profile.max_priority_level)
            else:
                selexp = Experiment.objects.get(id = defexp)
                userFS = UserFlowSpace.objects.filter(user = request.user)
                expFS = ExperimentFLowSpace.objects.filter(exp = selexp)
                               
                intersected = False

                fv_args = []
                tmp = UserOpts.objects.filter(experiment = selexp)
                if (len(tmp) > 0):
                    tmp = tmp[0]
                    # first delete all previous opts into this experiment
                    ofses = tmp.optsflowspace_set.all()
                    for ofs in ofses:
                        matches = ofs.matchstruct_set.all()
                        for match in matches:
                            fv_arg={"operation":"REMOVE" , "id":match.fv_id}
                            fv_args.append(fv_arg)
                        matches.delete()
                    ofses.delete()
                    tmp.delete()
                    fv = FVServerProxy.objects.all()[0]
                    # TODO: Check for errors
                    fv.changeFlowSpace(fv_args)        
                tmp = UserOpts(experiment=selexp, user=request.user, priority=request.POST['priority'], nice=False )
                tmp.save()
                
                match_list = []
                fv_args = []    
                for fs in expFS:
                    opted = MultiFSIntersect([fs],userFS,OptsFlowSpace)
                    if (len(opted) > 0):
                        intersected = True
                        for opt in opted:
                                opt.opt = tmp
                                opt.dpid = fs.dpid
                                opt.port_numebr_s = fs.port_number_s
                                opt.port_numebr_e = fs.port_number_e
                                opt.direction = fs.direction
                                opt.save()
                                #make Match struct
                                matchstr = RangeToMatchStruct(opt)
                                # relative priority for this match struct is the same as overall priority, because
                                # right now, we just have one match struct.
                                # TODO: consider multi-match structs
                                match = MatchStruct(match = matchstr, priority = int(request.POST['priority'])*Priority.Priority_Scale, fv_id=0, optfs=opt)
                                match.save()
                                match_list.append(match)
                                fv_arg = {"operation":"ADD", "priority":match.priority,
                                            "dpid":match.optfs.dpid,"match":match.match,
                                             "action":"slice=%s:4"%match.optfs.opt.experiment.slice_id}
                                fv_args.append(fv_arg)
                                
                                
                if (intersected):   
                    fv = FVServerProxy.objects.all()[0]
                    # TODO: check for errors in the following call
                    return_ids = fv.changeFlowSpace(fv_args)
                    for i in range(0,len(return_ids)):
                        match_list[i].fv_id = return_ids[i] 
                        match_list[i].save() 

                    exp_name = "%s:%s"%(selexp.project_name, selexp.slice_name)
                    return render_to_response('flowspace/opt_in_successful.html', {
                                'expname':exp_name})
                else:
                    tmp.delete()
                    error_msg = ErrorList(["No intersection between opted-in flowspace,\
                        your flowspace and experiment flowspace"]) 
              
                    
        else: #Not a post request
            defexp = exps[0].id       
        return render_to_response('flowspace/user_opt_in.html', {
                'user':request.user, 'experiments':exps, 'defexp': defexp, 'selpri':selpri, 'error_msg':error_msg
            })  
        
    
@login_required
def opt_out(request):
        profile = request.user.get_profile()
        # TODO
        #if (profile.is_net_admin):
        if (request.method == "POST"):
            fv_args = []
            for key in request.POST:
                ofs = OptsFlowSpace.objects.get(id=key)
                for match in ofs.matchstruct_set.all():
                    fv_arg = {"operation":"REMOVE", "id":match.fv_id}
                    fv_args.append(fv_arg)
                    match.delete()
                ofs.delete() 
            if (len(fv_args)>0):
                fv = FVServerProxy.objects.all()[0]
                #TODO: check return error
                fv.changeFlowSpace(fv_args)
                       
                    
        this_user_opts  = UserOpts.objects.filter(user = request.user)
        for useropt in this_user_opts:
            tmpfs = useropt.optsflowspace_set.all()
            if (len(tmpfs) == 0):
                useropt.delete()
            
                     
        allfs = OptsFlowSpace.objects.filter(opt__user = request.user)
        
        return render_to_response('flowspace/admin_opt_out.html', {
                'allfs':allfs})
        



@login_required
def update_opts(request):
    errors = 0
    keys = request.POST.keys()
    is_admin = request.user.get_profile().is_net_admin
    max_priority = request.user.get_profile().max_priority_level
    
    fv_args = []
    for key in keys:
        if key.startswith("p_"):
            if (int(request.POST[key]) > max_priority):
                errors = "You entered priority %s, which is larger than your maximum(%s)" % (request.POST[key], max_priority)
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
                              "actions": "slice=%s:4"%fs.opt.experiment.slice_id,
                              }
                    fv_args.append(fv_arg)
                    
            if (not is_admin):
                if (request.POST.has_key("n_"+pid)):
                    u.nice = True
                else:
                    u.nice = False
            u.save()

    fv = FVServerProxy.objects.all()[0]
    fv.changeFlowSpace(fv_args)
          
    opts = UserOpts.objects.filter(user=request.user).order_by('-priority')
    if (is_admin):
        return render_to_response('flowspace/view_opts_admin.html', {'opts':opts , 'user':request.user,
                                                      'max_priority':max_priority, 'error_message':errors},
                              context_instance=RequestContext(request))
    else:
        return render_to_response('flowspace/view_opts_user.html', {'opts':opts , 'user':request.user,
                                                      'max_priority':max_priority, 'error_message':errors},
                              context_instance=RequestContext(request))

@login_required
def view_experiment(request, exp_id):
    theexp = Experiment.objects.filter(id=exp_id)
    allfs = ExperimentFLowSpace.objects.filter(exp=theexp[0])
    return render_to_response('flowspace/view_experiment.html', {
            'exp':theexp[0], 'allfs':allfs, 'back':request.META['HTTP_REFERER']})     

@login_required
def view_experiments(request):
    exps = Experiment.objects.all()
    return render_to_response('flowspace/view_experiments.html', {
            'exps':exps})   