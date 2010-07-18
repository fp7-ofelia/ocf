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
from openflow.optin_manager.opts.helper import opt_fs_into_exp,opt_fses_outof_exp

@login_required     
def change_priority(request):
    
    
    if request.user.get_profile().is_net_admin:
        opts = UserOpts.objects.filter(user=request.user).order_by('-priority')
        pass
    
    else:
        error_msg = []

        
        if (request.method == "POST"):
            pass
            
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
              
@login_required
def view_opt_in(request, error_msg):
    #return HttpResponse("view opt in")
    opts = UserOpts.objects.filter(user=request.user).order_by('-priority')
    max_priority = request.user.get_profile().max_priority_level

    if request.user.get_profile().is_net_admin:
        return simple.direct_to_template(request,
                 template='openflow/optin_manager/opts/view_opts_admin.html',
                 extra_context={'max_priority':max_priority, 
                               'opts':opts ,
                                'user':request.user
                                },
                    )
    else:
        return simple.direct_to_template(request, 
                    template = 'openflow/optin_manager/opts/view_opts_user.html', 
                    extra_context={ 
                                   'opts':opts , 
                                   'user':request.user,
                                   }, 
                    )

@login_required
def add_opt_in(request):

    all_exps = Experiment.objects.all()
    user_fs = UserFlowSpace.objects.filter(user=request.user)
    exps = []
    for exp in all_exps:
        exp_fs = ExperimentFLowSpace.objects.filter(exp=exp)
        intersection = multi_fs_intersect(exp_fs,user_fs,FlowSpace)
        if (len(intersection)>0):
            exps.append(exp)
        
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
    else: # A user opt-in page
        selpri = 1
        error_msg = ""
        if (request.method == "POST"):
            #opt in request received; process it
            all_this_user_opts = UserOpts.objects.filter(user=request.user,nice=True)
            for user_opt in all_this_user_opts:
                if user_opt.priority >= selpri:
                    selpri = user_opt.priority + 1
                    
            defexp = request.POST['experiment']
            
            # check if priority is within allowable range
            if int(selpri) > profile.max_priority_level:
                error_msg = "Your maximum priority is %d"%(profile.max_priority_level)
            else:
                selexp = Experiment.objects.get(id = defexp)
                userFS = UserFlowSpace.objects.filter(user = request.user)

                tmp = UserOpts.objects.filter(experiment = selexp)
                if (len(tmp) > 0):
                    tmp = tmp[0]
                    # first delete all previous opts into this experiment
                    ofses = tmp.optsflowspace_set.all()
                    opt_fses_outof_exp(ofses)
                
                tmp.delete()    
                
                opt_msg = opt_fs_into_exp(userFS,selexp,request.user,
                                    int(selpri),True)
                if (opt_msg == ""):
                    exp_name = "%s:%s"%(selexp.project_name, selexp.slice_name)
                    return simple.direct_to_template(request, 
                                        template = 'openflow/optin_manager/opts/opt_in_successful.html', 
                                        extra_context = {'expname':exp_name,}, 
                                    )
                else:
                    tmp.delete()
                    error_msg = ErrorList([opt_msg])
              
                    
        else: #Not a post request
            defexp = 0     
        return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/user_opt_in.html', 
                        extra_context = {
                                'user':request.user,
                                'experiments':exps,
                                'defexp': defexp,
                                'selpri':selpri,
                                'error_msg':error_msg,
                            },
                    )      
        
    
@login_required
def opt_out(request):
    error_msg = ""
    profile = request.user.get_profile()
    if (profile.is_net_admin):
        if (request.method == "POST"):
            fv_args = []
            for key in request.POST:
                try:
                    int(key)
                except:
                    continue
                ofs = OptsFlowSpace.objects.get(id=key)
                error_msg = opt_fses_outof_exp([ofs])
                    
                    
            if (error_msg == ""):
                error_msg = "Opt Out was Successful" 
                
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
        
        
    else: #normal user
        if (request.method == "POST"):
            fv_args = []
            for key in request.POST:
                try:
                    int(key)
                except:
                    continue
                opt = UserOpts.objects.get(id=key)
                ofs = OptsFlowSpace.objects.filter(opt=opt)
                error_msg = opt_fses_outof_exp(ofs)
                    
                    
            if (error_msg == ""):
                error_msg = "Opt Out was Successful" 
                opt.delete()
                
        allopts = UserOpts.objects.filter(user = request.user)
            
        return simple.direct_to_template(request,
                    template = 'openflow/optin_manager/opts/user_opt_out.html', 
                    extra_context = {'allopts':allopts, 'error_msg':error_msg},
                )


@login_required
def update_opts(request):
    errors = []
    keys = request.POST.keys()
    is_admin = request.user.get_profile().is_net_admin
    max_priority = request.user.get_profile().max_priority_level
    
    fv_args = []
    for key in keys:
        if key.startswith("p_"):
            if (int(request.POST[key]) > max_priority):
                errors.append("You entered priority %s, which is larger than your maximum(%s)" % (request.POST[key], max_priority))
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
                    
            if (not is_admin):
                if (request.POST.has_key("n_"+pid)):
                    u.nice = True
                else:
                    u.nice = False
            u.save()

    error_msg = ""
    try:
        fv = FVServerProxy.objects.all()[0]
    except Exception,e:
        import traceback
        traceback.print_exc()
        errors.append("Flowvisor not set: %s"%str(e))
        
    try:
        fv.proxy.api.changeFlowSpace(fv_args)
    except Exception,e:
        import traceback
        traceback.print_exc()
        errors.append("change flowspace call failed in flowvisor: %s"%str(e))
          
    opts = UserOpts.objects.filter(user=request.user).order_by('-priority')
    if (is_admin):
        return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/view_opts_admin.html', 
                        extra_context = {
                                'opts':opts ,
                                'user':request.user,
                                'max_priority':max_priority,
                                'error_messages':errors
                            },
                    )
    else:
        return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/view_opts_user.html', 
                        extra_context =  {
                                'opts':opts,
                                'user':request.user,
                                'max_priority':max_priority,
                                'error_messages':errors
                            },
                    )


@login_required
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
   

@login_required
def view_experiments(request):
    exps = Experiment.objects.all()
    return simple.direct_to_template(request, 
                            template = 'openflow/optin_manager/opts/view_experiments.html',
                            extra_context = {'exps':exps}, 
                            )
    
    