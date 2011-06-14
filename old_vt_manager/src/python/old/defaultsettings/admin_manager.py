'''
Created on Sep 4, 2010

@author: expedient
'''

# local modules for auto-approving users's flowspace request used in admin_manager app.
# note: module file name should exist in the auto_approve_scripts directory in the 
# vt_manager.
AUTO_APPROVAL_MODULES = {
    # "module display name":"module file name",
    # note: module name shouldn't be "Manual" or "Remote"
    "Approve All Requests":"approve_all",
    "Reject All":"reject_all",
    "Approve Sender IP":"approve_sender_ip",             
}

# Send notification e-mail when flowspace requested being approved or rejected
SEND_EMAIL_WHEN_FLWOSPACE_APPROVED = False