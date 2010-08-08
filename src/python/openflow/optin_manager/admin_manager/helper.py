from openflow.optin_manager.opts.models import UserFlowSpace, AdminFlowSpace
from openflow.optin_manager.flowspace.helper import multifs_is_subset_of, singlefs_is_subset_of
from openflow.optin_manager.users.models import UserProfile
from openflow.optin_manager.opts.helper import update_user_opts
from openflow.optin_manager.flowspace.helper import copy_fs
from openflow.optin_manager.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD,\
    SITE_NAME, EMAIL_HOST, EMAIL_PORT
import smtplib
from email.MIMEText import MIMEText
import logging

logger = logging.getLogger("AdminManagerHelper")

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

import re
def validateEmail(email):
    '''
    Taken from: http://code.activestate.com/recipes/65215-e-mail-address-validation/
    '''
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0


def send_mail(to, subject, text):
    '''
    Taken from http://kutuma.blogspot.com/2007/08/sending-emails-via-gmail-with-python.html
    '''
    logger.debug("sending flowspace approval email to: %s"%to)
    msg = MIMEText(text)

    msg['From'] = EMAIL_HOST_USER
    msg['To'] = to
    msg['Subject'] = subject

    [username,atsign,domain] = EMAIL_HOST_USER.partition("@")
    if (len(atsign) == 0):
        return False

    mailServer = smtplib.SMTP(EMAIL_HOST,EMAIL_PORT)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, EMAIL_HOST_PASSWORD)
    mailServer.sendmail(EMAIL_HOST_USER, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
    return True


def send_approve_or_reject_emial(approved_fs,approve):
    if (len(approved_fs)==0):
        return False
    if validateEmail(approved_fs[0].user.email):
        if (approve):
            text = ""
            if approved_fs[0].user.first_name != "" or approved_fs[0].user.last_name != "":
                text = text + "Hi %s %s,\n\n"%(approved_fs[0].user.first_name,approved_fs[0].user.last_name)
            else:
                text = text + "Hi there,\n\n"
                
            text = text + "Your flowspace requests listed below has been approved.\n"
            text = text + "You can control these flowspaces and opt them into or out of available experiments:\n\n"
            text = text + "Flowspaces: \n"
            for fs in approved_fs:
                if hasattr(fs,"approver"):
                    appr = fs.approver
                elif hasattr(fs,"admin"):
                    appr = fs.admin
                else:
                    return False
                
                if appr.first_name != "" or appr.last_name != "":
                    approver = "%s %s"%(appr.first_name,appr.last_name)
                else:
                    approver = "%s"%appr.username
        
                text = text + "%s\t apprved by %s\n"%(fs,approver)
                
            text = text + "\nRegards,\n%s"%SITE_NAME
            return send_mail(approved_fs[0].user.email,"Flowspace Request Approved",text)
        else:
            text = ""
            if approved_fs[0].user.first_name != "" or approved_fs[0].user.last_name != "":
                text = text + "Hi %s %s,\n\n"%(approved_fs[0].user.first_name,approved_fs[0].user.last_name)
            else:
                text = text + "Hi there,\n\n"
                
            text = text + "Your flowspace requests listed below has been rejected by the admin.\n\n"
            text = text + "Flowspaces: \n"
            for fs in approved_fs:
                if hasattr(fs,"approver"):
                    appr = fs.approver
                elif hasattr(fs,"admin"):
                    appr = fs.admin
                else:
                    return False
                
                if appr.first_name != "" or appr.last_name != "":
                    approver = "%s %s"%(appr.first_name,appr.last_name)
                else:
                    approver = "%s"%appr.username
        
                text = text + "%s\t rejected by %s\n"%(fs,approver)
                
            text = text + "\nRegards,\n%s"%SITE_NAME
            return send_mail(approved_fs[0].user.email,"Flowspace Request Rejected",text)
 
    else:
        return False