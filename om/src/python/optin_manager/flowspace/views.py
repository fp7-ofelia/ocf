# Create your views here.
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from optin_manager.flowspace.models import UserOpts, OptsFlowSpace, Experiment, ExperimentFLowSpace, AdminFlowSpace, UserFlowSpace 
from optin_manager.flowspace.models import FlowSpace
from django.template import RequestContext
from django.http import HttpResponse
from optin_manager.flowspace.forms import AdminOptInForm
from django.forms.util import ErrorList
from optin_manager.flowspace.helper import MultiFSIntersect, makeFlowSpace 
from optin_manager.users.models import Priority

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
                    
                    # find flowspace intersection
                    f = MultiFSIntersect(adminFS,[optedFS],FlowSpace)
                    
                    intersected = False
                    tmp = UserOpts(experiment=selexp, user=request.user, priority=request.POST['priority'], nice=False )
                    tmp.save()
                    
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
                                #TODO Match struct and FV call
                                opt.save()
                            
     
                    if (intersected):
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
    else: # A user optin page
        selpri = 0
        if (request.method == "POST"):
            #opt in request received; process it
            selpri = request.POST['priority']
            defexp = request.POST['experiment']
            
             # check if priority is within allowable range
            if selpri > int(profile.max_priority_level):
                msg = "Your maximum priority is %d"%(profile.max_priority_level)
                form._errors["priority"] = ErrorList([msg])
            else:
                selexp = Experiment.objects.get(id = defexp)
                userFS = UserFlowSpace.objects.filter(user = request.user)
                expFS = ExperimentFLowSpace.objects.filter(exp = selexp)
                               
                intersected = False

                tmp = UserOpts.objects.filter(experiment = selexp)
                if (len(tmp) > 0):
                    tmp = tmp[0]
                    tmp.delete()
                    tmp = UserOpts(experiment=selexp, user=request.user, priority=request.POST['priority'], nice=False )
                    tmp.save()
                    
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
                            #TODO Match struct and FV call
                            opt.save()
                                
                if (intersected):     
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
        #if (profile.is_net_admin):
        if (request.method == "POST"):
            for key in request.POST:
                OptsFlowSpace.objects.get(id=key).delete()        
                    
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
    # TODO: add checks for range,...
    errors = 0
    keys = request.POST.keys()
    is_admin = request.user.get_profile().is_net_admin
    max_priority = request.user.get_profile().max_priority_level
    for key in keys:
        if key.startswith("p_"):
            if (int(request.POST[key]) > max_priority):
                errors = "You entered priority %s, which is larger than your maximum(%s)" % (request.POST[key], max_priority)
                continue
            pid = (key[2:len(key)])
            u = UserOpts.objects.get(pk=pid)
            u.priority = request.POST[key]
            if (not is_admin):
                if (request.POST.has_key("n_"+pid)):
                    u.nice = True
                else:
                    u.nice = False
            u.save()

            
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