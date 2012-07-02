import os
import sys
from os.path import dirname, join
from django.conf import *

#configobj
try:
        from configobj import ConfigObj
except:
        #FIXME: ugly
        os.system("apt-get update && apt-get install python-configobj -y")
        from configobj import ConfigObj


PYTHON_DIR = join(dirname(__file__), '../../../../../../src/python')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'expedient.clearinghouse.settings'
#os.environ['DJANGO_SETTINGS_MODULE'] = sys.argv[2]

sys.path.insert(0,PYTHON_DIR)

from expedient.common.permissions.shortcuts import *
from expedient.clearinghouse.aggregate.models import *
from django.contrib.auth.models import User
from expedient.clearinghouse.roles.models import *


##Delete can_delete_slices in the existing researcher roles 
for rRole in ProjectRole.objects.filter(name="researcher"):
	for permission in rRole.obj_permissions.all():
		if permission.permission.name == "can_delete_slices":
			rRole.remove_permission(permission)
			#This line deletes the permission from the database
			#permission.permission.delete()
			#print "I will remove permission %s from role %s in project %s" %(str(permission),str(rRole),str(rRole.project))

#Delete can_delete_slices permission over the project if the user is not a project owner
for project in Project.objects.all():
	for member in project.members.exclude(is_superuser=True):
		if member not in project.owners and not has_permission(member, project, "can_delete_slices"):
			#print "I will remove permission can_delete_slice for member %s in project %s because userIsProjectOwner=%s" %(member.username, project.name, "true" if unicode(member) in project.owners else "false")
			delete_permission("can_delete_slices", project, member)
#give permission can_delete_slices over the slice to the slice owner
		for slice in project._getSlices():
			if member == slice.owner and has_permission(member, slice, "can_delete_slices"):
				#print "I will give permission can_delete_slices to %s over slice %s" %(member.username, slice.name)
				give_permission_to("can_delete_slices", slice, member, giver=None, can_delegate=False)

##Remove can_use_aggregate if user is not member of any other project using the aggregates of this project or give it to the user if it is member and does not have it
for agg in Aggregate.objects.all():
	agg = agg.as_leaf_class()
	for user in User.objects.exclude(is_superuser=True):
		userUsesAgg = False
		for project in Project.objects.all():
			if user in project.members and unicode(agg.name) in project._get_aggregates().values_list("name",flat=True):
				userUsesAgg = True
				if has_permission(user, agg, "can_use_aggregate"):
					#print "I will give can_use_aggregate permission to %s for agg %s" % (user.username, agg.name)
					give_permission_to("can_use_aggregate", agg, user, giver=None, can_delegate=False)
				#else:
					#       print user.username+" uses the Agg but he already has permission"
				break;
		if not userUsesAgg and not has_permission(user, agg, "can_use_aggregate"):
			#print "I will remove can_use_aggregate permission to %s for agg %s" % (user.username, agg.name)
			agg.remove_from_user(user,"/")
