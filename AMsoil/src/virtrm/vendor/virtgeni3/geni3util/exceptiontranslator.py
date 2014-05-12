import amsoil.core.pluginmanager as pm
import amsoil.core.log

logging=amsoil.core.log.getLogger('ExceptionTranslator')


"""
Translate Exceptions from one type to another
"""

class ExceptionTranslator():
   
    @staticmethod
    def virtexception2GENIv3exception(virt_ex, **kwargs):
        # Obtain the Exceptions we want
        geniv3_exception = pm.getService('geniv3exceptions')
        virt_exception = pm.getService('virtexceptions')              
        # List here the Sentence related to every kind of Exception 
        S_VM_NAME_TAKEN = ("name", "The desired VM name(s) is already taken (%s).")
        S_NO_SERVER = ("server", "The desired Server UUID(s) could no be found (%s).")
        S_EXPIRATION_EXCEDED = ("urn", "VM allocation can not be extended that long (%s).")
        S_NO_TEMPLATE = ("server", "The desired Template could not be found for the given Server (%s).")
        S_ALLOCATION_ERROR = ("urn", "The VM could not be allocated (%s).")
        S_NO_SLICE = ("urn", "The desired urn(s) cloud not be found (%s).")
        S_NO_RESOURCES_IN_SLICE = ("urn", "There are no resources in the given slice(s) (%s).")
        S_PROVISIONING_ERROR = ("urn", "Error while provisioning (%s).")
        S_MALFORMED_URN = ("urn", "Urn has a type unable to create (%s).")
        S_DEALLOCATION_ERROR = ("urn", "VM could not be deallocated properly (%s).")
        S_INVALID_ACTION = ("action", "Action not suported in this AM (%s).")
        S_DATABASE_ERROR = ("default", "Could not obtain the data from the DataBase (%s).")
        S_EXPIRED_VM = ("urn", "Could not obtain the desired VM, problably it has expired (%s).")
        S_DEFAULT_ERROR = ("default", "Unexpected error occurred (%s).")
        # Now define the Exception Tuples
        VM_NAME_TAKEN = (geniv3_exception.GENIv3AlreadyExistsError, S_VM_NAME_TAKEN)
        EXPIRED_VM = (geniv3_exception.GENIv3ExpiredError, S_EXPIRED_VM)
        NO_SERVER = (geniv3_exception.GENIv3SearchFailedError, S_NO_SERVER)
        EXPIRATION_EXCEDED = (geniv3_exception.GENIv3BadArgsError, S_EXPIRATION_EXCEDED)
        NO_TEMPLATE = (geniv3_exception.GENIv3BadArgsError, S_NO_TEMPLATE)
        ALLOCATION_ERROR = (geniv3_exception.GENIv3GeneralError, S_ALLOCATION_ERROR) 
        NO_SLICE = (geniv3_exception.GENIv3SearchFailedError, S_NO_SLICE)
        NO_RESOURCES_IN_SLICE = (geniv3_exception.GENIv3SearchFailedError, S_NO_RESOURCES_IN_SLICE)
        PROVISIONING_ERROR = (geniv3_exception.GENIv3GeneralError, S_PROVISIONING_ERROR)
        MALFORMED_URN = (geniv3_exception.GENIv3BadArgsError, S_MALFORMED_URN)
        DEALLOCATION_ERROR = (geniv3_exception.GENIv3GeneralError, S_DEALLOCATION_ERROR)
        INVALID_ACTION = (geniv3_exception.GENIv3OperationUnsupportedError, S_INVALID_ACTION)
        DATABASE_ERROR = (geniv3_exception.GENIv3DatabaseError, S_DATABASE_ERROR)
        DEFAULT_ERROR = (geniv3_exception.GENIv3GeneralError, S_DEFAULT_ERROR)
        # Make the dictionary
        error_dictionary = {
            virt_exception.VirtVmNameAlreadyTaken : VM_NAME_TAKEN,
            virt_exception.VirtServerNotFound : NO_SERVER,
            virt_exception.VirtMaxVMDurationExceeded : EXPIRATION_EXCEDED,
            virt_exception.VirtTemplateNotFound : NO_TEMPLATE,
            virt_exception.VirtVMAllocationError : ALLOCATION_ERROR,
            virt_exception.VirtContainerNotFound : NO_SLICE,
            virt_exception.VirtNoResourcesInContainer : NO_RESOURCES_IN_SLICE,
            virt_exception.VirtVMNotFound : EXPIRED_VM
        }
        # Get the Exception according the input
        tuple_exception = error_dictionary.get(virt_ex, DEFAULT_ERROR)
        key_exception = tuple_exception[1][0]
        message_exception = tuple_exception[1][1]
        type_exception = tuple_exception[0]
        # Generate the Exception
        geni_exception = type_exception(message_exception % str(kwargs[key_exception]))
        return geni_exception

