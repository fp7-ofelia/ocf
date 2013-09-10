from openflow.optin_manager.opts.models import Experiment, ExperimentFLowSpace, UserOpts, OptsFlowSpace, MatchStruct
from openflow.optin_manager.xmlrpc_server.models import CallBackServerProxy, FVServerProxy

def delete_slice(slice_urn):
    try:
        mult_exp = Experiment.objects.all()
        for exp in mult_exp:
            print exp.slice_id
        single_exp = Experiment.objects.get(slice_id = slice_urn)
    except Experiment.DoesNotExist:
        raise "" #RecordNotFound exception
    fv = FVServerProxy.objects.all()[0]
    try:
        success = fv.proxy.api.deleteSlice(single_exp.get_fv_slice_name())
    except Exception,e:
        
        if "slice does not exist" in str(e):
            success = True
        else:
            raise "" #TODO: think how to solve this. 

    # get all flowspaces opted into this exp
    ofs = OptsFlowSpace.objects.filter(opt__experiment = single_exp)

    # delete all match structs for each flowspace
    for fs in ofs:
        MatchStruct.objects.filter(optfs = fs).delete()

    # delete all flowspaces opted into this exp
    ofs.delete()
    try:
        UserOpts.objects.filter(experiment = single_exp).delete()
    except:
        pass #Probably is the best for now
    ExperimentFLowSpace.objects.filter(exp = single_exp).delete()

    single_exp.delete()
    return 1

