from openflow.optin_manager.opts.models import UserFlowSpace, AdminFlowSpace
from openflow.optin_manager.flowspace.helper import multifs_is_subset_of, singlefs_is_subset_of
from openflow.optin_manager.users.models import UserProfile
from openflow.optin_manager.opts.helper import update_user_opts
from openflow.optin_manager.flowspace.helper import copy_fs


def accept_user_fs_request(fs_request):
    '''
    accepts a user flowspace request and adds it to user flowpscae.
    If a previous user flowspace is subset of what is being accepted, replace it
    with new flowpsace only to avoid duplicate.
    @param fs_request:  flowspace request to be accepted
    @type fs_request: list of RequestedUserFlowSpace
    @return: [fv_args,match_list] to be xmlrpc-called to fv
    @note: all fs_requests should belong to one user
    '''
    if len(fs_request) == 0:
         return [[],[]]
     
    #check which of the previous user flowspaces are a subset of this flowspace
    ufs = UserFlowSpace.objects.filter(user=fs_request[0].user)
    for fs in ufs:
        if (singlefs_is_subset_of(fs,fs_request)):
            fs.delete()
     
    for single_fs in fs_request:
        user = single_fs.user
        ufs = UserFlowSpace(user=single_fs.user, approver=single_fs.admin)
        copy_fs(single_fs,ufs)
        ufs.save()
        single_fs.delete()
        
    [fv_args,match_list] = update_user_opts(user)

    return [fv_args,match_list]
    

def find_supervisor(fses):
    '''
    find the admin who has the full control over all the flowspace elements in the
    fses. It does this selection by finding the admin whose flowspace is a superset of
    fses but is not a superviosr of another admin who also owns a flowspace that is
    a superset of fses.
    @param fses: the list of flowspaces we want to find an admin for
    @type fses: list of FlowSpace objects
    @return: the User object for the admin who has full control over fses
    '''
    admins_list = UserProfile.objects.filter(is_net_admin=True)
    intersected_admins = []
    intersected_supervisors = []

    for admin in admins_list:
        adminfs = AdminFlowSpace.objects.filter(user=admin.user)
        if multifs_is_subset_of(fses,adminfs):
            intersected_admins.append(admin)
            intersected_supervisors.append(admin.supervisor)
                        
    selected_admin = None
    super_admin = None
    for admin in intersected_admins:
        if (admin not in intersected_supervisors): 
            selected_admin = admin
            break
        if (admin.supervisor==admin.user):
            super_admin = admin
    
    if (selected_admin):
        return selected_admin.user
    elif (super_admin):
        return super_admin.user
    else:
        return None
    
def convert_dict_to_flowspace(list_of_dics, objectType):
    '''
    Converts a list of dicst whose key-value pairs are FlowSpace attributes, 
    into a corresponding list of FlowSpace-superclass objects specified by objectType
    @param list_of_dics: a list of dictionaries where each dict. is has key-value
    pairs corresponding to a FlowSpace object
    @type list_of_dics: List of Dictionaries
    @param objectType: the return Type of function
    @return: a list of FlowSpace-superclass objects
    '''
    returned_list = []
    for dic in list_of_dics:
        new_fs = objectType()
        for key in dic.keys():
            setattr(new_fs,key,dic[key])
        returned_list.append(new_fs)
    return returned_list
    