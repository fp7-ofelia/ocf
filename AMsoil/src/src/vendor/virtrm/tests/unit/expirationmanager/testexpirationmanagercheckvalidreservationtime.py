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
        # A microsecond error is acceptable due to the execution time
        manager = self.given_this_expiration_manager()
        datetime_values = ['year', 'month', 'day', 'hour', 'minute', 'second']
        value = manager.check_valid_reservation_time()
        param = datetime.now() + timedelta(0, manager.RESERVATION_TIMEOUT)
        expected_value = 0.0
        returned_value = 0.0
        for key in datetime_values:
            expected_value += getattr(param, key)
            returned_value += getattr(value, key)
        self.assertAlmostEquals(expected_value, returned_value, 10)
    
    def test_should_return_max_expiration_time_given_less_than_current_time(self):
        # A microsecond error is acceptable due to the execution time
        manager = self.given_this_expiration_manager()
        param = datetime.now() - timedelta(0, 10)
        datetime_values = ['year', 'month', 'day', 'hour', 'minute', 'second']
        value = manager.check_valid_reservation_time()
        param_expected = datetime.now() + timedelta(0, manager.RESERVATION_TIMEOUT)
        expected_value = 0.0
        returned_value = 0.0
        for key in datetime_values:
            expected_value += getattr(param_expected, key)
            returned_value += getattr(value, key)
        self.assertAlmostEquals(expected_value, returned_value, 10)

    def test_should_raise_exception_given_invalid_expiration_time(self):
        manager = self.given_this_expiration_manager()
        param = datetime.now() + timedelta(0, manager.RESERVATION_TIMEOUT) + timedelta(0, 10)
        self.assertRaises(Exception, manager.check_valid_reservation_time, param)

if __name__ == '__main__':
    unittest.main()

