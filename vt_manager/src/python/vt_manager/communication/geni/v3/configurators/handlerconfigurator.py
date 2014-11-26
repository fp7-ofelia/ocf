from am.ambase.src.geni.v3.handler.handler import GeniV3Handler as Handler
from am.ambase.src.geni.v3.delegate.delegate import GeniV3Delegate as Delegate
from am.rspecs.src.geni.v3.manager import RSpecManager
from am.credentials.src.manager.gcfmanager import GCFCredentialManager
from am.ambase.src.geni.exceptions.manager import GENIExceptionManager

from vt_manager.communication.geni.v3.managers.vtam import VTAMRM
from vt_manager.communication.geni.v3.drivers.vtam import VTAMDriver
from vt_manager.communication.geni.v3.settings.vtam import VTAMConfig

class HandlerConfigurator:

    """
    Class devoted to configure the structure of every module and return the Handler
    instance ready to be used to understand the GENI World.
    """

    @staticmethod
    def configure_handler():
        # XXX How and from which module is this invoked?
        handler = Handler()
        delegate = HandlerConfigurator.get_vt_am_delegate()
        rspec_manager = HandlerConfigurator.get_vt_am_rspec_manager()
        cred_manager = HandlerConfigurator.get_vt_am_credential_manager()
        exc_manager = HandlerConfigurator.get_vt_am_exception_manager()
        handler.set_credential_manager(cred_manager)
        handler.set_rspec_manager(rspec_manager)
        handler.set_delegate(delegate)
        handler.set_geni_exception_manager(exc_manager)
        handler.set_config(VTAMConfig)
        return handler

    @staticmethod
    def get_vt_am_delegate():
        delegate = Delegate()
        delegate.set_config(VTAMConfig)
        delegate.set_resource_manager(HandlerConfigurator.get_vt_am_resource_manager())
        return delegate

    @staticmethod
    def get_vt_am_resource_manager():
        rm = VTAMRM()
        rm.set_driver(HandlerConfigurator.get_vt_am_driver())
        return rm

    @staticmethod
    def get_vt_am_driver():
        driver = VTAMDriver()
        driver.set_config(VTAMConfig)
        return driver

    @staticmethod
    def get_vt_am_credential_manager():
        cred_manager = GCFCredentialManager()
        cred_manager.set_config(VTAMConfig)
        return cred_manager

    @staticmethod
    def get_vt_am_rspec_manager():
        rspec_manager = RSpecManager()
        return rspec_manager

    @staticmethod
    def get_vt_am_exception_manager():
        exc_manager = GENIExceptionManager()
        return exc_manager
