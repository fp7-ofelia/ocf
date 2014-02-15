import sys
sys.path.append("/opt/ofelia/AMsoil/src/vendor/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/")
sys.path.append("/opt/ofelia/AMsoil/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from utils.expirationmanager import ExpirationManager
import unittest
from datetime import datetime, timedelta

class ExpirationManagerCheckValidExpirationTest(unittest.TestCase):

    def given_this_expiration_manager(self):
        manager = ExpirationManager()
        return manager
   
    def test_should_return_expiration_time_given_valid_expiration_time(self):
        manager = self.given_this_expiration_manager()
        param = datetime.now() + timedelta(0, manager.RESERVATION_TIMEOUT) - timedelta(0, 10)
        self.assertEquals(param, manager.check_valid_reservation_time(param))

    def test_should_return_max_expiration_time_given_none_expiration(self):
        manager = self.given_this_expiration_manager()
        self.assertAlmostEquals(datetime.now() + timedelta(0, manager.RESERVATION_TIMEOUT), manager.check_valid_reservation_time(), delta=1)
    
    def test_should_return_max_expiration_time_given_less_than_current_time(self):
        manager = self.given_this_expiration_manager()
        param = datetime.now() - timedelta(0, 10)
        self.assertAlmostEquals(datetime.now() + timedelta(0, manager.RESERVATION_TIMEOUT), manager.check_valid_reservation_time(param), 1)

    def test_should_raise_exception_given_invalid_expiration_time(self):
        manager = self.given_this_expiration_manager()
        param = datetime.now() + timedelta(0, manager.RESERVATION_TIMEOUT) + timedelta(0, 10)
        self.assertRaises(Exception, manager.check_valid_reservation_time, param)

if __name__ == '__main__':
    unittest.main()

