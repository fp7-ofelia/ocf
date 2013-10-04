# Create your views here.
from models import *
from django.http import HttpResponseRedirect
from forms import AdminOptInForm, UploadFileForm
from openflow.optin_manager.flowspace.helper import *
from openflow.optin_manager.users.models import Priority
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
from django.views.generic import simple
from openflow.optin_manager.opts.helper import opt_fs_into_exp,opt_fses_outof_exp,\
update_match_struct_priority_and_get_fv_args, read_fs
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from openflow.optin_manager.opts.vlans.vlanController import vlanController
from django.contrib.sites.models import Site
from math import ceil as math_ceil
    
def change_priority(request):
    '''
    The view function to change priorities of previous opt-ins.
    request.POST should have a dictionary of "p_" followed by UserOpts database id as key
    and the new priority as value
    '''

    fv_args = []
    error_msg = []
    max_priority = request.user.get_profile().max_priority_level
    profile = UserProfile.get_or_create_profile(request.user)
         
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
                    if (u.priority >= max_priority - Priority.Strict_Priority_Offset):
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
 
    ##################################
    #      Admin Change Priority     #
    ################################## 
    if (profile.is_net_admin):
        return simple.direct_to_template(request, 
                    template = 'openflow/optin_manager/opts/view_opts_admin.html', 
                    extra_context={ 
                        'error_msg':error_msg,
                        'nice_opts':nice_opts , 
                        'strict_opts':strict_opts ,
                        'user':request.user,
                        'max_priority':max_priority,
                    }, 
                ) 
 
    ##################################
    #      User Change Priority      #
    ################################## 
    else:
        return simple.direct_to_template(request, 
                    template = 'openflow/optin_manager/opts/view_opts_user.html', 
                    extra_context={ 
                        'error_msg':error_msg,
                        'nice_opts':nice_opts , 
                        'strict_opts':strict_opts ,
                        'user':request.user,
                        'max_priority':max_priority,
                    }, 
                )           
                  


def add_opt_in(request):
    '''
`	The view function for opting in a user or admin flowspace into an experiment
    FOR USER OPTIN:
    request.POST should contain:
    key: experiment: database id of the experiment to opted in
    FOR ADMIN OPTIN:
    request.POST should contain:
    key: experiment: database id of the experiment to opted in
    key: all flowspace fields as specified in AdminOptInForm
    ''' 
    profile = UserProfile.get_or_create_profile(request.user)
    
    ############################
    #      Admin Opt-In        #
    ############################   
    if (profile.is_net_admin):
        
        # find all experiments that the admin can opt into them.
        all_exps = Experiment.objects.all().order_by('project_name','slice_name')
        admin_fs = AdminFlowSpace.objects.filter(user=request.user)
        exps = []

        for exp in all_exps:
            exp_fs = ExperimentFLowSpace.objects.filter(exp=exp)
            intersection = multi_fs_intersect(exp_fs,admin_fs,FlowSpace)
            if (len(intersection)>0):
                exps.append(exp)

        ######## XXX Experimental: Show allocated VLANs ######
        allocated_vlans = vlanController.get_allocated_vlans()
        requested_vlans = vlanController.get_requested_vlans_by_all_experiments()
        ########################################################################################

        assigned_priority = profile.max_priority_level - Priority.Strict_Priority_Offset - 1
        error_msg = []
        if (request.method == "POST"):
            form = AdminOptInForm(request.POST)
            if form.is_valid():
                all_this_admin_opts = UserOpts.objects.filter(user=request.user,nice=True)
                for admin_opt in all_this_admin_opts:
                    if admin_opt.priority <= assigned_priority:
                        assigned_priority = admin_opt.priority - 1
                        
                if assigned_priority <= 0:
                    error_msg.append("Too many opt-ins")
         
                # check if the selected experiment is valid:
                selected_exp_id = request.POST['experiment']
                try:
                    selexp = Experiment.objects.get(id = selected_exp_id)
                except:
                    error_msg.append("Invalid experiment selected!")
                if len(error_msg)==0:
                    requested_opt = form.get_flowspace(FlowSpace)
                    adminFS = AdminFlowSpace.objects.filter(user = request.user)
                    
                    intersected_flowspace = multi_fs_intersect([requested_opt],adminFS,FlowSpace)
                    #for fs in intersected_flowspace:
                    #    print "\n\nFLOWSPACE"
                    #    print fs.stringify()
                    #    print fs.__unicode__()
                    if len(intersected_flowspace) == 0:
                        error_msg.append("Selected flowspace doesn't have any intersection with admin FS")
                if len(error_msg)==0:
                    try:
                        [fv_args,match_list] = opt_fs_into_exp(intersected_flowspace,
                                selexp,request.user,assigned_priority,True)
                        fv = FVServerProxy.objects.all()[0]
                        try:
                            if len(fv_args) > 0:
                                returned_ids = fv.proxy.api.changeFlowSpace(fv_args)
                                for i in range(len(match_list)):
                                    match_list[i].fv_id = returned_ids[i]
                                    match_list[i].save()
                            try:
                                allopts = UserOpts.objects.filter(user = request.user).order_by('-priority')
                                for opt in allopts:
                                    this_opt_fses = opt.optsflowspace_set.all()
                                    fs_project = opt.experiment.project_name or ""
                                    fs_slice = opt.experiment.slice_name or ""
                                    fs_description = ""
                                    for fs in this_opt_fses:
                                        if fs_description != "":
                                            fs_description = fs_description + "\n%s"%fs
                                        else:
                                            fs_description = "%s"%fs
                                site_domain_url = " You may access your slice page at Expedient's site to check the granted Flowspace."
                                send_mail(
                                         settings.EMAIL_SUBJECT_PREFIX + "Your Flowspace request has been attended",
                                         "Your Flowspace request has been attended.%s\n\nProject: %s\nSlice: %s\nFlowspace granted:\n\n%s" % (site_domain_url, fs_project, fs_slice, fs_description),
                                         from_email=settings.DEFAULT_FROM_EMAIL,
                                         recipient_list= [selexp.owner_email],
                                         #recipient_list=[settings.ROOT_EMAIL],
                                 )
                            except Exception as e:
                                print "User email notification could not be sent. Exception: %s" % str(e)

                            return simple.direct_to_template(request, 
                                template ="openflow/optin_manager/opts/opt_in_successful_admin.html",
                                extra_context = {
                                    'expname':"%s:%s"%(selexp.project_name,selexp.slice_name),
                                },
                            )
                        except Exception,e:
                            import traceback
                            traceback.print_exc()
                            transaction.rollback()
                            error_msg.append("Couldn't opt into the requested experiment, Flowvisor error: %s"%str(e))
                    except Exception,e:
                        import traceback
                        traceback.print_exc()
                        transaction.rollback()
                        error_msg.append("Flowvisor not set: %s"%str(e))
                
        else:
            form = AdminOptInForm()
                        
        # if not a post request, we will start from here            
        if (len(exps)>0):
            exp_exist = True
            first_exp = exps[0].id
        else:
            exp_exist = False
            first_exp = 0
           
        upload_form = UploadFileForm()
        return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/admin_opt_in.html', 
                        extra_context = {
                                'user':request.user,
                                'experiments':exps,
                                'error_msg':error_msg,
                                'exp_exist':exp_exist,
                                'first_exp':first_exp,
                                'form':form,
                                'upload_form':upload_form,
                                'requested_vlans':requested_vlans,
                                # Carolina: ceil function to take into account 0-indexed range [0,4095]
                                # has 1 more element that would be normally displaced to another column
                                # (not 5 columns anymore). Displace one element per column to fit.
                                'vlan_list_length': math_ceil(len(allocated_vlans)/5.0),
                                'allocated_vlans': allocated_vlans,
                            },
                    )  
                    
    ############################
    #      User Opt-In         #
    ############################         
    else: 
        
        #find all the experiemnts that have intersection with this user
        all_exps = Experiment.objects.all().order_by('project_name','slice_name')
        user_fs = UserFlowSpace.objects.filter(user=request.user)
        exps = []
        for exp in all_exps:
            exp_fs = ExperimentFLowSpace.objects.filter(exp=exp)
            intersection = multi_fs_intersect(exp_fs,user_fs,FlowSpace)
            if (len(intersection)>0):
                exps.append(exp)
                
        assigned_priority = Priority.Nice_User - 1
        error_msg = []
        if (request.method == "POST"):
            all_this_user_opts = UserOpts.objects.filter(user=request.user,nice=True)
            for user_opt in all_this_user_opts:
                if user_opt.priority <= assigned_priority:
                    assigned_priority = user_opt.priority - 1
                    
            # check if a valid experiment is selected
            selected_exp_id = request.POST['experiment']
            try:
                selexp = Experiment.objects.get(id = selected_exp_id)
            except:
                error_msg.append("Invalid experiment selected!")
                
            # check if priority is within allowable range
            if assigned_priority <= 0:
                error_msg.append("Too many opt-ins")
            
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
                            template ="openflow/optin_manager/opts/opt_in_successful_user.html",
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
   
def opt_in_from_file(request):
    '''
    This is doing the same as add_opt_in function except the input data
    is coming from an uploaded file
    '''
    
    profile = UserProfile.get_or_create_profile(request.user)
     
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    else:
        # find all experiments that the admin can opt into them.
        all_exps = Experiment.objects.all()
        admin_fs = AdminFlowSpace.objects.filter(user=request.user)
        exps = []
        for exp in all_exps:
            exp_fs = ExperimentFLowSpace.objects.filter(exp=exp)
            intersection = multi_fs_intersect(exp_fs,admin_fs,FlowSpace)
            if (len(intersection)>0):
                exps.append(exp)

        error_msg = []
        
        if (len(exps)>0):
            exp_exist = True
            first_exp = exps[0].id
        else:
            exp_exist = False
            first_exp = 0
        
        if (request.method == "POST"):
            uform = UploadFileForm(request.POST, request.FILES)
            
            # validate upload file form
            if uform.is_valid():
                
                # parse the file and find the list of flowspaces to be opted-in
                result = read_fs(request.FILES['file'])
                
                # check if an error happened while parsing the file, 
                if len(result["error"])==0:
                    
                    # find the priority for first opt-in
                    assigned_priority = profile.max_priority_level - Priority.Strict_Priority_Offset - 1
                    all_this_admin_opts = UserOpts.objects.filter(user=request.user,nice=True)
                    for admin_opt in all_this_admin_opts:
                            if admin_opt.priority <= assigned_priority:
                                assigned_priority = admin_opt.priority - 1
                    
                    fv_args = []
                    match_list = []
                    opt_expression = ""
                    for i in range(len(result['flowspace'])):
                        
                        # check if slice_id is specified
                        if result['slice_id'][i]==None:
                            error_msg.append("No opt-in slice specified for flowspace %s"%result['flowspace'])
                            transaction.rollback()
                            break
                        
                        #check if slice_id is valid
                        exp = Experiment.objects.filter(slice_id=result['slice_id'][i])
                        if exp.count()==0:
                            error_msg.append("No slice exist with id %s"%result['slice_id'][i])
                            transaction.rollback()
                            break
                        elif exp.count()>1:
                            raise Exception("Found more than one slice with the same id: %s. This is unexpected!"%result['slice_id'][i])
                        else:
                            exp = exp[0]
                            
                        if assigned_priority <= 0:
                            error_msg.append("Too many opt-ins")
                            transaction.rollback()
                            break
                            
                        # find the intersection of requested opt-in flowspace, admin's flowspace
                        # and the experiemnt's flowspace:
                        adminFS = AdminFlowSpace.objects.filter(user = request.user)
                        intersected_flowspace = multi_fs_intersect([result['flowspace'][i]],adminFS,FlowSpace)
                                                
                        if len(intersected_flowspace) == 0:
                            error_msg.append("Selected flowspace doesn't have any intersection with admin FS. Admin FS: %s, Selected FS: %s"%\
                                         (adminFS,result['flowspace'][i]))
                            transaction.rollback()
                            break
                        

                        # get the fv args for this opt-in
                        [new_fv_args,new_match_list] = opt_fs_into_exp(intersected_flowspace,
                                            exp,request.user,assigned_priority,True)
                        
                        fv_args = fv_args + new_fv_args
                        match_list = match_list + new_match_list
                        
                        opt_expression = opt_expression + exp.project_name + ":" + exp.slice_name + ", "
                        
                        # decrease assigned priority for next opt-in
                        assigned_priority = assigned_priority - 1
                        

                    if len(fv_args)==0:
                        error_msg.append("Nothing to opt-in!")
                        transaction.rollback()
                        
                    # now send FV Args using an XMLRPC call to FV
                    if len(error_msg)==0:
                        try:
                            fv = FVServerProxy.objects.all()[0]
                            try:
                                returned_ids = fv.proxy.api.changeFlowSpace(fv_args)
                                for i in range(len(match_list)):
                                    match_list[i].fv_id = returned_ids[i]
                                    match_list[i].save()
                                opt_expression = opt_expression[:-2]
                                return simple.direct_to_template(request, 
                                    template ="openflow/optin_manager/opts/opt_in_successful_admin.html",
                                    extra_context = {
                                    'expname':opt_expression,
                                    },
                                )
                            except Exception,e:
                                import traceback
                                traceback.print_exc()
                                transaction.rollback()
                                error_msg.append("Couldn't opt into the requested experiment, Flowvisor error: %s"%str(e))
                        except Exception,e:
                            import traceback
                            traceback.print_exc()
                            transaction.rollback()
                            error_msg.append("Flowvisor not set: %s"%str(e)) 
                        
                        
                    
                    
                # if there is an error while parsing the file         
                else:
                    error_msg = result["error"]

        
        form = AdminOptInForm()
        upload_form = UploadFileForm()
        return simple.direct_to_template(request, 
            template = 'openflow/optin_manager/opts/admin_opt_in.html', 
            extra_context = {
                'user':request.user,
                'experiments':exps,
                'error_msg':error_msg,
                'exp_exist':exp_exist,
                'first_exp':first_exp,
                'form':form,
                'upload_form':upload_form,
            },
        )
        
    
def opt_out(request):
    '''
    The view function for opt-out. 
    the request.POST should contain {UserOpts.id:"checked"} for all the UserOpts
    to be opted out.
    '''
    error_msg = []
    profile = UserProfile.get_or_create_profile(request.user)
    keys = request.POST.keys()
    

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
            next_priority = profile.max_priority_level - Priority.Strict_Priority_Offset - 1
            for opt in nice_opts:
                if opt.priority != next_priority:
                    opt.priority = next_priority
                    opt.save()
                    new_args = update_match_struct_priority_and_get_fv_args(opt)
                    fv_args = fv_args + new_args
                next_priority = next_priority - 1
            strict_opts = UserOpts.objects.filter(user = request.user,nice=False).order_by('priority')
            next_priority = profile.max_priority_level - 1
            for opt in strict_opts:
                if opt.priority != next_priority:
                    opt.priority = next_priority
                    opt.save()
                    new_args = update_match_struct_priority_and_get_fv_args(opt)
                    fv_args = fv_args + new_args
                next_priority = next_priority -1
                        
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
            
    ############################
    #      User Opt-Out        #
    ############################ 
    if (not profile.is_net_admin):
        allopts = UserOpts.objects.filter(user = request.user).order_by('-priority')
        return simple.direct_to_template(request,
            template = 'openflow/optin_manager/opts/user_opt_out.html', 
            extra_context = {'allopts':allopts, 'error_msg':error_msg},
        )
    
    
    ############################
    #      Admin Opt-Out       #
    ############################ 
    else:
        opts_info = []
        allopts = UserOpts.objects.filter(user = request.user).order_by('-priority')
        for opt in allopts:
            this_opt_fses = opt.optsflowspace_set.all()
            fs_description = ""
            for fs in this_opt_fses:
                if fs_description != "":
                    fs_description = fs_description + " & %s"%fs
                else: 
                    fs_description = "%s"%fs
                    
            opts_info.append({"opt":opt,"fs_description":fs_description})
        
        
        return simple.direct_to_template(request,
            template = 'openflow/optin_manager/opts/admin_opt_out.html', 
            extra_context = {'opts_info':opts_info, 'error_msg':error_msg},
        )




def view_experiment(request, exp_id):
    '''
    The view function to see the detail information of an experiment.
    @param exp_id: database id of the experiment to browse
    @type exp_id: integer
    '''
    theexp = Experiment.objects.filter(id=exp_id)
    allfs = ExperimentFLowSpace.objects.filter(exp=theexp[0])
    profile = UserProfile.get_or_create_profile(request.user)
    
    if not profile.is_net_admin:
        return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/view_experiment_user.html', 
                        extra_context = {
                                        'exp':theexp[0],
                                        'allfs':allfs,
                                        'back':request.META['HTTP_REFERER']
                                    }, 
                    )
    else:
        return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/view_experiment_admin.html', 
                        extra_context = {
                                        'exp':theexp[0],
                                        'allfs':allfs,
                                        'back':request.META['HTTP_REFERER'],
                                    }, 
                    )
   

def view_experiment_simple(request, exp_id):
    '''
    provides a basic html detail view of an experiment. This simple
    html-based view is useful in user and admin opt-in views when we want to show
    a quick summary of experiment's detial information, while the user
    is browsing experiments 
    @param exp_id: database id of the experiment to browse
    @type exp_id: integer
    '''
    theexp = Experiment.objects.filter(id=exp_id)
    allfs = ExperimentFLowSpace.objects.filter(exp=theexp[0])
    requested_vlans = vlanController.get_requested_vlans_by_experiment(theexp[0])
    #requested_vlans = {}
    #vranges =  [x for x in theexp[0].experimentflowspace_set.values_list('vlan_id_s','vlan_id_e').distinct()]
    #requested_vlans['ranges'] = [(int(x[0]),int(x[1])) for x in vranges] 
    #requested_vlans['values'] = sum([range(x[0],x[1]+1) for x in vranges],[])
    return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/view_experiment_simple.html', 
                        extra_context = {
                                        'exp':theexp[0],
                                        'allfs':allfs,
                                        'requested_vlans':requested_vlans,
                                        'back':request.META['HTTP_REFERER'],
                                    }, 
                    )
    
    
def simple_opts(request, opt_id):
    '''
    Show a simple information page about the opt-in
    '''
    theopt = UserOpts.objects.filter(id=opt_id)
    if len(theopt)==0:
        return HttpResponseRedirect("/dashboard")
    if not theopt[0].user==request.user:
        return HttpResponseRedirect("/dashboard")
    opt_fs = theopt[0].optsflowspace_set.all()
    allfs = ExperimentFLowSpace.objects.filter(exp=theopt[0].experiment)
    return simple.direct_to_template(request, 
                        template = 'openflow/optin_manager/opts/view_opt_simple.html', 
                        extra_context = {
                                        'opt':theopt[0],
                                        'opt_fs':opt_fs,
                                        'allfs':allfs,
                                    }, 
                    )

def view_experiments(request):
    '''
    The view function to show a list of available experiments.
    '''
    exps = Experiment.objects.all()
    profile = UserProfile.get_or_create_profile(request.user)
    
    if not profile.is_net_admin:
        return simple.direct_to_template(request, 
                            template = 'openflow/optin_manager/opts/view_experiments_user.html',
                            extra_context = {'exps':exps}, 
                            )
    else:
        return simple.direct_to_template(request, 
                            template = 'openflow/optin_manager/opts/view_experiments_admin.html',
                            extra_context = {'exps':exps}, 
                            ) 
    


