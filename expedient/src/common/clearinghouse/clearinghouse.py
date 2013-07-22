
class Clearinghouse:

    #XXX: How to manage Expedient's auth 
    #We have to take into account that in every call to the AM we should provide the user credentials.
    #It seems to me that Expedient was created from the GUI. There is no clear separation about GUI functions and "core" functions.
    #We should provide(at least) two APIs: the CH API and the AM API clearly separating the GUI stuff from "core" stuff. 

    def __init__():
        pass # Setup CH connection, URL, add i2CAT island Expedient GID, 


    """
    Expedient Managed Functions
    """ 
    def get_version(self):
        #Should return the version of our CH
        pass
   
    def get_user_credentials(self, username):
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

    """
    Some Useful Functions
    """
    def get_current_island_gid(self):
        pass

    def get_current_hrn(self):
        pass

