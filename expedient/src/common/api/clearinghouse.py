from common.permissions.models import Permittee
#from modules.slice.models import Slice 


class Clearinghouse:

    #XXX: How to manage Expedient's auth 
    #We have to take into account that in every call to the AM we should provide the user credentials.
    #It seems to me that Expedient was created from the GUI. There is no clear separation about GUI functions and "core" functions.
    #We should provide(at least) two APIs: the CH API and the AM API clearly separating the GUI stuff from "core" stuff. 

    def __init__(self):
        pass # Setup CH connection, URL, add i2CAT island Expedient GID, 


    """
    Expedient Managed Functions
    """ 
    def get_version(self):
        #Should return the version of our CH
        pass

    def list(self,hrn):
        #This call should return the records linked to the HRN. 
        #If the hrn is a subauthority(project), this call should return the slices and the users of that subauthority
        pass
  
    def get_credentials(self, hrn):
        #The user name might be a HRN. for example( ocf.i2cat.username)
        #probably we should need a DB to store users,pass?,credential/role. Or we can just generate these credentials on the fly
        #This method should get in someway the credentials and expand the expiration time if required.
        #we could base this approach on trust/Hierarchy modules availables in SFAWrap.
        #If already is a user on the current island could we manage to trust him, but I don't like it
        pass

    def register(self, record):
        #Register will create new users or subauthorities(projects) or SLICES? we could separate this call but probably the CH will contenin a main Register Function 
        #First approach, I'm just wondering what we are going to need to register users/projects in our island
        pass

    def update(self, old_param, new_parms):
        #Useful function to allow CRUD functions to users, Slices, subauthorities.
        pass

    def delete(self, param):
        #the same thing here, param might be a HRN/URN or UUID. We should take into account the entities below that if we delete a subauthority we sould delete the slices and the slivers)
        pass

    def delegate_credentials(self, credentials, delegating_hrn):
        #GENI does not delegate credentials, it applies "Speak for" concept. Almost hte same.
        pass
 
    """
    AM Managed functions
    """
    def check_credentials(self, creds):
        #Call to the clearinghouse to validate the provided credentials of the user.
        #probably we should have to send also our GID too.
        pass

    """
    Some useful Functions
    """

    def get_current_island_gid(self):
        pass

    def get_current_hrn(self):
        pass

    def get_slices(self,model_instance,credentials=None):
        from modules.slice.models import Slice
        #If the credentials param is the list of credentials of the island slice authority, this method should return all the slices of the island.
        #If the credentials param is the list of credentials of a common user (PI,Researcher) this method should return the assigned slices to that user
        #FIXME HACK from Permittes, required to delete used slices form AMs.
        return Permittee.objects.filter_for_class_and_permission_name(
               klass=Slice,
               permission="can_use_aggregate",
               target_obj_or_class=model_instance,
             ) 
        
    def check_role(self,user,role):
        #This method should return true if the param user has the role in role param(admin,pi,researcher)
        pass

    def get_subauthorities(self,filter):
        from modules.project.models import Project
        qs = Project.objects.get_for_user(filter.get('user')).order_by('id')
        return qs

    def get_admins(self):
        #returns a list of users with admin or Island Manager role.
        pass

    def get_principal_investigators(self):
        #returns a list of users with principal investigator role
        pass

    def get_researchers(self):
        #returns a list of useres with researcher role
        pass

    """
    Functions to deprecate
    """
  
    def remove_from_instance(self,permission,instance, from_instance):
        from common.permissions.shortcuts import delete_permission
        delete_permission("can_use_aggregate", instance, from_instance)

    def add_aggregate_to_project(self,permission,aggregate,project):
        from common.permissions.shortcuts import \
    give_permission_to, delete_permission, must_have_permission, has_permission,\
    get_permittee_from_threadlocals
        give_permission_to(permission,aggregate,project) 

    def add_aggregate_to_slice(slef,permission,aggregate,slice):
        from common.permissions.shortcuts import give_permission_to
        give_permission_to(permission,aggregate,slice)

    def remove_user_record(user,project):
        from modules.roles.models import ProjectRole,ProjectRoleRequest
        from common.permissions.models import ObjectPermission,PermissionOwnership, Permittee
        from modules.project.models import Project

        #XXX use generic remove_record call with hrns.
        member = Permittee.objects.get_as_permittee(member)
        #Remove the roles
        for role in ProjectRole.objects.filter(project=project):
            role.remove_from_permittee(member)
        # Remove other permissions
        PermissionOwnership.objects.delete_all_for_target(project, member)

        #Remove can_use_aggregate if user is not member of any other project using the aggregates of this project
        for projectAgg in project._get_aggregates():
            aggNotUsedAnymoreByMember=1
            for p in Project.objects.exclude(id=project.id):
                if projectAgg in p._get_aggregates() and unicode(member) in p.members.values_list("username", flat=True):
                    aggNotUsedAnymoreByMember=0
                    break;
            if aggNotUsedAnymoreByMember and not has_permission(member, projectAgg, "can_use_aggregate"):
                projectAgg.remove_from_user(member,"/")

