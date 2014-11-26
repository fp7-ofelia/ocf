from am.ambase.src.geni.v3.handler.handler import GeniV3Handler as Handler
from am.ambase.src.geni.v3.delegate.delegate import GeniV3Delegate as Delegate
from am.rspecs.src.geni.v3.openflow.manager import OpenFlowRSpecManager as RSpecManager
from am.credentials.src.manager.gcfmanager import GCFCredentialManager
from am.ambase.src.geni.exceptions.manager import GENIExceptionManager

from openflow.optin_manager.geni.v3.managers.optin import OptinRM
from openflow.optin_manager.geni.v3.drivers.optin import OptinDriver
from openflow.optin_manager.geni.v3.settings.optin import OptinConfig

class HandlerConfigurator:

    """
    Class devoted to configure the structure of every module and return the Handler
    instance ready to be used to understand the GENI World.
    """

    @staticmethod
    def configure_handler():
        handler = Handler()
        delegate = HandlerConfigurator.get_optin_delegate()
        rspec_manager = HandlerConfigurator.get_optin_rspec_manager()
        cred_manager = HandlerConfigurator.get_optin_credential_manager()
        exc_manager = HandlerConfigurator.get_optin_exception_manager()
        handler.set_credential_manager(cred_manager)
        handler.set_rspec_manager(rspec_manager)
        handler.set_delegate(delegate)
        handler.set_geni_exception_manager(exc_manager)
        handler.set_config(OptinConfig)
        return handler

    @staticmethod
    def get_optin_delegate():
        delegate = Delegate()
        delegate.set_config(OptinConfig)
        delegate.set_resource_manager(HandlerConfigurator.get_optin_resource_manager())
        return delegate

    @staticmethod
    def get_optin_resource_manager():
        rm = OptinRM()
        rm.set_driver(HandlerConfigurator.get_optin_driver())
        return rm

    @staticmethod
    def get_optin_driver():
        driver = OptinDriver()
        driver.set_config(OptinConfig)
        return driver

    @staticmethod
    def get_optin_credential_manager():
        cred_manager = GCFCredentialManager()
        cred_manager.set_config(OptinConfig)
        return cred_manager

    @staticmethod
    def get_optin_rspec_manager():
        rspec_manager = RSpecManager()
        return rspec_manager

    @staticmethod
    def get_optin_exception_manager():
        exc_manager = GENIExceptionManager()
        return exc_manager

