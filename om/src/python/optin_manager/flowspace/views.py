# Create your views here.
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from flowspace.models import UserOpts, OptsFlowSpace, Experiment, ExperimentFLowSpace, AdminFlowSpace, UserFlowSpace 
from flowspace.models import FlowSpace
from django.template import RequestContext
from django.http import HttpResponse
from flowspace.forms import AdminOptInForm
from django.forms.util import ErrorList
from flowspace.helper import MultiFSIntersect, makeFlowSpace 

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
                    result = MultiFSIntersect(expFS,f,OptsFlowSpace)
                    
                    #check if result is empty
                    if (len(result) > 0):
                        # check if user already opted into this experiment,
                        tmp = UserOpts.objects.filter(experiment = selexp)
                        print "before: "
                        print tmp
                        if (len(tmp) == 0):
                            #add this experiment to opted-in experiments
                            tmp = UserOpts(experiment=selexp, user=request.user, priority=request.POST['priority']
                                           ,nice=False )
                            tmp.save()
                        else:
                            tmp = tmp[0]
                            tmp.priority = request.POST['priority']
                            tmp.save()

                        for elem in result:
                            elem.opt = tmp
                            elem.save()
     
                        exp_name = "%s:%s"%(selexp.project_name, selexp.slice_name)
                        return render_to_response('flowspace/opt_in_successful.html', {
                                'expname':exp_name})
                    else:
                        form._errors['general'] = ErrorList(["No intersection between opted-in flowspace,\
                        your flowspace and experiment flowspace"])
        else:
            defexp = exps[0].id
            form = AdminOptInForm()
        return render_to_response('flowspace/admin_opt_in.html', {
            'form': form, 'user':request.user, 'experiments':exps, 'defexp': defexp,
        })
    else:
        #User Opt In
        return HttpResponse("trial")

@login_required
def opt_out(request):
    profile = request.user.get_profile()
    if (profile.is_net_admin):
        if (request.method == "POST"):
            for key in request.POST:
                OptsFlowSpace.objects.get(id=key).delete()
            
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